from PIL import Image
import numpy as np
import math
import time

from numpy.lib.twodim_base import tri

def model_world(translation, rotation, scale):
    print("Model world matrix ...")

    scale_matrix = np.matrix([
        [scale[0], 0, 0, 0], 
        [0, scale[1], 0, 0],
        [0, 0, scale[2], 0],
        [0, 0, 0, 1]
    ])

    translation_matrix = np.matrix([
        [1, 0, 0, translation[0]], 
        [0, 1, 0, translation[1]],
        [0, 0, 1, translation[2]],
        [0, 0, 0, 1]
    ])

    rotation_matrix = get_quaternion_rotation_matrix(rotation)
    return translation_matrix.dot(rotation_matrix).dot(scale_matrix)

def world_view_lookat(at, eye, up):
    print("World view matrix ...")

    eye = np.matrix([eye[0], eye[1], eye[2]])
    up = np.matrix([up[0], up[1], up[2]])

    at_eye = np.subtract(eye, at)
    w = np.divide(at_eye, np.linalg.norm(at_eye))

    w_up = np.cross(w, up)
    u = np.divide(w_up, np.linalg.norm(w_up))

    u_w = np.cross(u, w)
    v = np.divide(u_w, np.linalg.norm(u_w))

    view_to_world = np.matrix([
        [u[0, 0], v[0, 0], -w[0, 0], eye[0, 0]], 
        [u[0, 1], v[0, 1], -w[0, 1], eye[0, 1]],
        [u[0, 2], v[0, 2], -w[0, 2], eye[0, 2]],
        [0, 0, 0, 1]
    ])

    return np.linalg.inv(view_to_world)

def world_view_lookat_simple(translation, rotation):
    print("World view matrix ...")

    rotation_matrix = get_quaternion_rotation_matrix(rotation)
    translation_matrix = np.matrix([
        [1, 0, 0, translation[0]], 
        [0, 1, 0, translation[1]],
        [0, 0, 1, translation[2]],
        [0, 0, 0, 1]
    ])

    translation_matrix_inv = np.linalg.inv(translation_matrix)
    rotation_matrix_inv = np.linalg.inv(rotation_matrix)

    return rotation_matrix_inv.dot(translation_matrix_inv)

def view_point(fovx, near, far, width, height):
    print("View point matrix ...")

    width = width * Rasterizer.sampling
    height = height * Rasterizer.sampling

    fovy = 2 * math.atan(math.tan(fovx / 2) * height / math.sqrt(height ** 2 + width ** 2))
    top = near * math.tan(fovy)
    right = top * width / height

    return np.matrix([
        [near / right, 0, 0, 0], 
        [0, near / top, 0, 0],
        [0, 0, -((far + near) / (far - near)), ((- 2 * far * near)/(far - near))],
        [0, 0, -1, 0]
    ])

def point_screen(width, height):
    print("Point screen matrix ...")

    width = width * Rasterizer.sampling
    height = height * Rasterizer.sampling

    return np.matrix([
        [width / 2, 0, 0, width / 2], 
        [0, - height / 2, 0, height / 2],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def mvp(gl):
    print("MVP matrix ...")
    return gl.view_to_point.dot(gl.world_to_view).dot(gl.transformation_matrix_stack)

def get_quaternion_rotation_matrix(rotation):
    theta = rotation[3]
    qi = rotation[0] * math.sin(theta / 2)
    qj = rotation[1] * math.sin(theta / 2)
    qk = rotation[2] * math.sin(theta / 2)
    qr = math.cos(theta / 2)

    return np.matrix([
        [1 - 2 * (qj ** 2 + qk ** 2), 2 * (qi * qj - qk * qr), 2 * (qi * qk + qj * qr), 0], 
        [2 * (qi * qj + qk * qr), 1 - 2 * (qi ** 2 + qk ** 2), 2 * (qj * qk - qi * qr), 0],
        [2 * (qi * qk - qj * qr), 2 * (qj * qk + qi * qr), 1 - 2 * (qi ** 2 + qj ** 2), 0],
        [0, 0, 0, 1]
    ])

def apply_point_transformations(point, gl):
    homogenous_p = np.matrix([[point[0]], [point[1]], [point[2]], [1]])
    clip_point = gl.mvp.dot(homogenous_p)
    normalized_clip_point = np.divide(clip_point, clip_point[3][0])
    screen_point = gl.point_to_screen.dot(normalized_clip_point)

    screen_point[3][0] = screen_point[2][0]
    screen_point[2][0] = clip_point[2][0]
    return screen_point

def transform_points(point, gl):
    print("\n--> Transforming Points")
    start_time = time.time()
    screen_points = []

    for i in range(0, len(point) - 2, 3):
        p = [point[i], point[i + 1], point[i + 2]]
        screen_points += [apply_point_transformations(p, gl)]
    
    print("::: Time to transform points: %s seconds :::\n" % (time.time() - start_time))
    return screen_points

def hermite_interpolation(key, keyValue, closed, set_fraction):
    Rasterizer.clear_flag = True
    s = 0
    list_size = 3

    for k in range(len(key)):
        if set_fraction < key[k]:
            k -= 1
            s = (set_fraction - key[k]) / (key[k + 1] - key[k])
            break

    k_offset = (k) * list_size
    k_plus_one_offset = (k + 1) * list_size
    k_plus_two_offset = (k + 2) * list_size
    k_minus_one_offset = (k - 1) * list_size

    if k_plus_one_offset >= len(keyValue):
        if not closed: return [0, 0, 0]
        k_plus_one_offset = 0
        k_plus_two_offset = list_size

    if k_plus_two_offset >= len(keyValue):
        if not closed: return [0, 0, 0]
        k_plus_two_offset = 0

    v_k_minus_one = [0, 0, 0]
    if k_minus_one_offset >= 0:
        v_k_minus_one = keyValue[k_minus_one_offset : k_minus_one_offset + list_size]

    v_k = keyValue[k_offset : k_offset + list_size]
    v_k_plus_one = keyValue[k_plus_one_offset : k_plus_one_offset + list_size]
    v_k_plus_two = keyValue[k_plus_two_offset : k_plus_two_offset  + list_size]

    T_0 = [(v_k_plus_one[i] - v_k_minus_one[i]) / 2 for i in range(list_size)]
    T_1 = [(v_k_plus_two[i] - v_k[i]) / 2 for i in range(list_size)]

    hermite_H = np.matrix([
        [2, -2, 1, 1], 
        [-3, 3, -2, -1],
        [0, 0, 1, 0],
        [1, 0, 0, 0]
    ])

    S = np.matrix([[s ** 3, s ** 2, s, 1]])
    C = np.matrix([v_k, v_k_plus_one, T_0, T_1])
    V_s = np.dot(S, np.dot(hermite_H, C))

    return V_s.tolist()[0]

def linear_interpolation(key, keyValue, set_fraction):
    Rasterizer.clear_flag = True
    t = 0

    for k in range(len(key)):
        if set_fraction < key[k]:
            t = (set_fraction - key[k - 1]) / (key[k] - key[k - 1])
            break
    
    prev_value = keyValue[(k - 1) * 4 + 3]
    k *= 4
    value_changed = [keyValue[k], keyValue[k + 1], keyValue[k + 2], prev_value + (t * (keyValue[k + 3] - prev_value))]

    return value_changed

class RenderProcesses:

    pre_render = []
    post_render = []
    scene = None
    
    @staticmethod
    def setup(scene):
        RenderProcesses.scene = scene

    @staticmethod
    def run_pre_render():
        print("\n*************** Pre rendering ***************\n")
        for process in RenderProcesses.pre_render:
            process()
        print("*************** Rendering ***************")
        
    @staticmethod
    def run_post_render():
        print("\n*************** Post rendering ***************\n")
        for process in RenderProcesses.post_render:
            process()
        print("*************** Done ***************\n")

class Light:
    
    # considering just directional light implelented
    has_light = False
    ambient_intensity = None
    color = None
    intensity = None
    direction = None
    
    @staticmethod
    def setup(ambient_intensity, color, intensity, direction):
        Light.ambient_intensity = ambient_intensity
        Light.direction = [-d for d in direction]
        Light.intensity = intensity
        Light.has_light = True
        Light.color = color

class Rasterizer:

    width = None
    height = None
    z_test = False
    sampling = None
    gpu_instance = None
    buffer_length = None
    clear_flag = False
    z_buffer = []
    frame_buffer = []
    mip_maps_textures = {}

    class AABB:
        min_x = None
        min_y = None
        max_x = None
        max_y = None

        def __init__(self, min_x, min_y, max_x, max_y):
            self.min_x = min_x
            self.min_y = min_y
            self.max_x = max_x
            self.max_y = max_y
    
    @staticmethod
    def setup(gpu_instance, width, height, sampling, z_test):
        Rasterizer.gpu_instance = gpu_instance
        Rasterizer.width = width
        Rasterizer.height = height
        Rasterizer.sampling = sampling
        Rasterizer.z_test = z_test
        Rasterizer.buffer_length = (Rasterizer.sampling ** 2) * width * height
        RenderProcesses.pre_render += [Rasterizer.mip_maps]
        RenderProcesses.post_render += [Rasterizer.sample]
        Rasterizer.prepare_frame()

    @staticmethod
    def prepare_frame():
        Rasterizer.frame_buffer = [[0, 0, 0]] * (Rasterizer.buffer_length)

        if Rasterizer.z_test:
            Rasterizer.z_buffer = [None] * (Rasterizer.buffer_length)

    @staticmethod
    def render(triangles, colors, vertex_color=False, texture=None, uv=None, has_texture=False):
        start_time_render = time.time()
        if Rasterizer.clear_flag: Rasterizer.prepare_frame()
        raster = Rasterizer.raster
        has_light = Light.has_light

        for i in range(len(triangles)):
            start_time_raster = time.time()
            if vertex_color: raster(triangle=triangles[i], colors=colors[i], vertex_color=vertex_color)
            elif has_texture: raster(triangle=triangles[i], texture=texture[0], uv=uv[i], has_texture=has_texture)
            elif has_light: raster(triangle=triangles[i], colors=colors, has_light=has_light)
            else: raster(triangle=triangles[i], colors=colors)

            print("=== Time to raster triangle: %s seconds ===\n" % (time.time() - start_time_raster))

        print("--- Time to render triangles: %s seconds ---" % (time.time() - start_time_render))
        print("======================================================================\n")

    @staticmethod
    def mip_maps():

        scene = RenderProcesses.scene
        if scene.current_appearance == None or scene.current_appearance.texture == None: return
        
        start_mip_maps_time = time.time()
        start_time_mip_maps_prep = time.time()

        textures = scene.current_appearance.texture.url
        current_texture = textures[0]
        Rasterizer.mip_maps_textures[current_texture] = []
        texture = Rasterizer.gpu_instance.load_texture(current_texture)

        Rasterizer.mip_maps_textures[current_texture] += [texture.copy()]
        # im = Image.fromarray(texture)
        # im.save("renderizador/mip_maps_textures_debug/test0.png")

        d = 1
        shape = texture.shape[0] if texture.shape[0] < texture.shape[1] else texture.shape[1]
        levels = int(math.log(shape)/math.log(2))
        
        points = []

        print("Name of texture: " + current_texture)
        print("Numer of mip maps levels: " + str(levels))
        print("--> Time to prep mip maps %s seconds" % (time.time() - start_time_mip_maps_prep))

        for level in range(1, levels + 1):
            start_time_mip_maps_process = time.time()
            d = d * 2
            d_squared = d ** 2
            shape_normalized = int(shape / d)
            new_texture = texture[:shape_normalized][:shape_normalized, :shape_normalized].copy()

            shape_column = len(texture) - d + 1
            shape_row = len(texture[0]) - d + 1

            for column in range(0, shape_column, d):
                points = [c for c in range(column, column + d)]

                for row in range(0, shape_row, d):
                    for r in range(row, row + d):
                        points += [r] * d

                    r_mean = 0
                    g_mean = 0
                    b_mean = 0

                    for i in range(d):
                        tex_p0 = texture[points[i]]

                        for j in range(d):
                            tex_p0_p1 = tex_p0[points[d + j * d]]

                            r_mean += tex_p0_p1[0]
                            g_mean += tex_p0_p1[1]
                            b_mean += tex_p0_p1[2]

                    r_mean /= d_squared
                    g_mean /= d_squared
                    b_mean /= d_squared
                    
                    new_texture[int(column / d)][int(row / d)] = [r_mean, g_mean, b_mean, 255]
                    points = points[:d]
            
            print("--> Time to process mip maps level %d is %s seconds" % (level, time.time() - start_time_mip_maps_process))
            
            Rasterizer.mip_maps_textures[current_texture] += [new_texture.copy()]
            # im = Image.fromarray(new_texture)
            # im.save("renderizador/mip_maps_textures_debug/test%d.png" % (level))

        print("|||| Time to pre process mip maps levels: %s seconds ||||\n" % (time.time() - start_mip_maps_time))

    @staticmethod
    def raster(triangle, colors=None, vertex_color=False, texture=None, uv=None, has_texture=False, has_light=False):

        start_time_raster_prep = time.time()
        
        ##!! For optimization purposes
        height = Rasterizer.height
        frame_buffer = Rasterizer.frame_buffer
        z_buffer = Rasterizer.z_buffer
        z_test = Rasterizer.z_test
        sampling = Rasterizer.sampling

        triangle_A_y = triangle[0][1][0, 0]
        triangle_B_y = triangle[2][1][0, 0]
        triangle_C_y = triangle[1][1][0, 0]
        triangle_A_x = triangle[0][0][0, 0]
        triangle_B_x = triangle[2][0][0, 0]
        triangle_C_x = triangle[1][0][0, 0]
        triangle_A_z = 1 / triangle[0][2][0, 0]
        triangle_B_z = 1 / triangle[2][2][0, 0]
        triangle_C_z = 1 / triangle[1][2][0, 0]

        B_x_minus_A_x = triangle_B_x - triangle_A_x
        B_y_minus_A_y = triangle_B_y - triangle_A_y

        C_x_minus_B_x = triangle_C_x - triangle_B_x
        C_y_minus_B_y = triangle_C_y - triangle_B_y

        A_x_minus_C_x = triangle_A_x - triangle_C_x
        A_y_minus_C_y = triangle_A_y - triangle_C_y

        line1 = (B_x_minus_A_x, B_y_minus_A_y)
        line2 = (C_x_minus_B_x, C_y_minus_B_y)
        line3 = (A_x_minus_C_x, A_y_minus_C_y)

        normal1 = (line1[1], - line1[0])
        normal2 = (line2[1], - line2[0])
        normal3 = (line3[1], - line3[0])

        dot = [[0, 0], [0, 0], [0, 0]]

        alpha_denominator = -(triangle_A_x - triangle_B_x) * (C_y_minus_B_y) + (triangle_A_y - triangle_B_y) * (C_x_minus_B_x)
        betha_denominator = -(triangle_B_x - triangle_C_x) * (A_y_minus_C_y) + (triangle_B_y - triangle_C_y) * (A_x_minus_C_x)
        
        triangle_AABB = Rasterizer.AABB(int(triangle[0][0, 0]), int(triangle[0][1, 0]), int(triangle[0][0, 0] + 1), int(triangle[0][1, 0] + 1))
        for p in range(1, len(triangle)):
            if triangle[p][0] > triangle_AABB.max_x: triangle_AABB.max_x = int(triangle[p][0, 0] + 1)
            if triangle[p][0] < triangle_AABB.min_x: triangle_AABB.min_x = int(triangle[p][0, 0])
            if triangle[p][1] > triangle_AABB.max_y: triangle_AABB.max_y = int(triangle[p][1, 0] + 1)
            if triangle[p][1] < triangle_AABB.min_y: triangle_AABB.min_y = int(triangle[p][1, 0])
        
        if vertex_color:
            for color in colors:
                color[0] *= 255
                color[1] *= 255
                color[2] *= 255

            vertex_color_1 = [i * triangle_A_z for i in colors[0]]
            vertex_color_2 = [i * triangle_C_z for i in colors[1]]
            vertex_color_3 = [i * triangle_B_z for i in colors[2]]
        
        elif has_texture:

            texture = Rasterizer.mip_maps_textures[texture]
            uv_1 = [i * triangle_A_z for i in uv[0]]
            uv_2 = [i * triangle_C_z for i in uv[1]]
            uv_3 = [i * triangle_B_z for i in uv[2]]

            def get_uv(x, y):
                alpha = (-(x - triangle_B_x) * (C_y_minus_B_y) + (y - triangle_B_y) * (C_x_minus_B_x)) / alpha_denominator
                betha = (-(x - triangle_C_x) * (A_y_minus_C_y) + (y - triangle_C_y) * (A_x_minus_C_x)) / betha_denominator
                gamma = 1 - alpha - betha
                z = triangle_A_z * alpha + triangle_C_z * gamma + triangle_B_z * betha

                # return u, v
                return ((uv_1[0] * alpha + uv_2[0] * gamma + uv_3[0] * betha) / z), ((uv_1[1] * alpha + uv_2[1] * gamma + uv_3[1] * betha) / z)

            x_center = (triangle_A_x + triangle_B_x + triangle_C_x) / 3
            y_center = (triangle_A_y + triangle_B_y + triangle_C_y) / 3

            u00, v00 = get_uv(x_center, y_center)
            u10, v10 = get_uv(x_center + 1, y_center)
            u01, v01 = get_uv(x_center, y_center - 1)
            
            du_dx = (u10 - u00) * texture[0].shape[0]
            du_dy = (u01 - u00) * texture[0].shape[0]
            dv_dx = (v10 - v00) * texture[0].shape[0]
            dv_dy = (v01 - v00) * texture[0].shape[0]

            L = max(math.sqrt(du_dx ** 2 + dv_dx ** 2), math.sqrt(du_dy ** 2 + dv_dy ** 2))
            D = round(math.log2(L))

            print("--> Mip maps level chosen for triangle: %d" % (D))
            texture = texture[D]
            tex_shape_x = texture.shape[0] - 1
            tex_shape_y = texture.shape[1] - 1

        elif has_light:
            I_ia = Light.ambient_intensity
            I_i = Light.intensity
            I_Lrgb = Light.color

            O_Ergb = colors["emissiveColor"]
            O_Drgb = colors["diffuseColor"]
            O_Srgb = colors["specularColor"]

            # do not exist
            O_a = 0
            shiness = colors["shininess"]

            L = np.asarray(Light.direction)
            v = np.array([0, 0, 1])

            # normal vector, flat shading, change after? 
            A_z = triangle[0][2][0, 0]
            B_z = triangle[2][2][0, 0]
            C_z = triangle[1][2][0, 0]

            V0 = np.matrix([C_x_minus_B_x, C_y_minus_B_y, C_z - B_z])
            V1 = np.matrix([B_x_minus_A_x, B_y_minus_A_y, B_z - A_z])

            # normalize ??
            # N = np.cross(V1, V0)[0]
            V0_cross_V1 = np.cross(V1, V0)
            N = np.divide(V0_cross_V1, np.linalg.norm(V0_cross_V1))[0]

            N_dot_L = np.dot(N, L)
            L_plus_V = np.add(L, v)
            L_plus_V_normalized = np.divide(L_plus_V, np.linalg.norm(L_plus_V))
            
            proximity = L_plus_V_normalized.dot(N)
            diffuse_i = [c * I_i * N_dot_L for c in O_Drgb]
            ambient_i = [c * I_ia * O_a for c in O_Drgb]
            specular_i = [c * I_i * proximity ** (shiness * 128) for c in O_Srgb]
            
            I_rgb = [255 * (O_Ergb[c] + I_Lrgb[c] * (ambient_i[c] + specular_i[c] + diffuse_i[c])) for c in range(3)]
            colors = I_rgb

        else:
            colors = [colors[0] * 255, colors[1] * 255, colors[2] * 255]

        print("--> Time to prep raster %s seconds" % (time.time() - start_time_raster_prep))
        start_time_raster_process = time.time()

        for x in range(triangle_AABB.min_x, triangle_AABB.max_x):
            x_minus_xA = x - triangle_A_x
            x_minus_xB = x - triangle_B_x
            x_minus_xC = x - triangle_C_x

            dot[0][0] = x_minus_xA * normal1[0]
            dot[1][0] = x_minus_xB * normal2[0]
            dot[2][0] = x_minus_xC * normal3[0]
            
            for y in range(triangle_AABB.min_y, triangle_AABB.max_y):
                y_minus_yA = y - triangle_A_y
                y_minus_yB = y - triangle_B_y
                y_minus_yC = y - triangle_C_y

                dot[0][1] = y_minus_yA * normal1[1]
                dot[1][1] = y_minus_yB * normal2[1]
                dot[2][1] = y_minus_yC * normal3[1]

                is_inside = True
                for product in dot:
                    if product[0] + product[1] > 0:
                        is_inside = False
                        break

                if is_inside:
                    alpha = (-(x_minus_xB) * (C_y_minus_B_y) + (y_minus_yB) * (C_x_minus_B_x)) / alpha_denominator
                    betha = (-(x_minus_xC) * (A_y_minus_C_y) + (y_minus_yC) * (A_x_minus_C_x)) / betha_denominator
                    gamma = 1 - alpha - betha

                    z = triangle_A_z * alpha + triangle_C_z * gamma + triangle_B_z * betha
                    offset = x * height * sampling + y

                    if z_test:
                        if z_buffer[offset] == None or z_buffer[offset] < z: z_buffer[offset] = z
                        else: continue

                    if vertex_color:
                        colors = [
                            (vertex_color_1[0] * alpha + vertex_color_2[0] * gamma + vertex_color_3[0] * betha) / z,
                            (vertex_color_1[1] * alpha + vertex_color_2[1] * gamma + vertex_color_3[1] * betha) / z,
                            (vertex_color_1[2] * alpha + vertex_color_2[2] * gamma + vertex_color_3[2] * betha) / z]

                    elif has_texture:
                        u = ((uv_1[0] * alpha + uv_2[0] * gamma + uv_3[0] * betha) / z) * tex_shape_x
                        v = ((uv_1[1] * alpha + uv_2[1] * gamma + uv_3[1] * betha) / z) * - tex_shape_y

                        # colors = [int(v) * 255, int(u) * 255, 0]
                        colors = texture[int(v)][int(u)]

                    elif has_light:
                        pass

                    frame_buffer[offset] = colors

        print("--> Time to process raster %s seconds" % (time.time() - start_time_raster_process))
        Rasterizer.frame_buffer = frame_buffer

    @staticmethod
    def sample():
        
        start_time_sample = time.time()
        start_time_sample_prep = time.time()

        ##!! For optimization purposes
        size_y = Rasterizer.height
        sampling = Rasterizer.sampling
        sampling_square = sampling ** 2
        frame_buffer = Rasterizer.frame_buffer
        gpu_instance = Rasterizer.gpu_instance
        frame_buffer_len = len(frame_buffer)
        sampled_size_x = Rasterizer.width * sampling
        sampled_size_y = Rasterizer.height * sampling

        print("--> Time to prep sampling %s seconds" % (time.time() - start_time_sample_prep))
        start_time_sampling_process = time.time()
        
        for x in range(0, sampled_size_x, sampling):
            x_offset = x * sampled_size_y
            
            for y in range(size_y):
                y_offset = x_offset + y * sampling
                r_mean = 0
                g_mean = 0
                b_mean = 0
                
                for i in range(sampling):
                    offset_x = i * sampled_size_y + y_offset

                    for j in range(sampling):
                        offset = offset_x + j
                        
                        if offset == frame_buffer_len: break
                        color = frame_buffer[offset]
                        r_mean += color[0]
                        g_mean += color[1]
                        b_mean += color[2]

                if r_mean > 0 or g_mean > 0 or b_mean > 0:
                    r_mean /= sampling_square
                    g_mean /= sampling_square
                    b_mean /= sampling_square

                    gpu_instance.draw_pixels([int(x / sampling), y], gpu_instance.RGB8, [r_mean, g_mean, b_mean])
        
        print("--> Time to process sampling %s seconds" % (time.time() - start_time_sampling_process))
        print("!!! Time to sample: %s seconds !!!\n" % (time.time() - start_time_sample))
