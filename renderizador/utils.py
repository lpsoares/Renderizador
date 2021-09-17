from xml.etree.ElementTree import register_namespace
import numpy as np
import math
import time

def model_world(translation, rotation, scale):
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
    width = width * Rasterizer.sampling
    height = height * Rasterizer.sampling

    return np.matrix([
        [width / 2, 0, 0, width / 2], 
        [0, - height / 2, 0, height / 2],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def mvp(gl):
    return gl.view_to_point.dot(gl.world_to_view).dot(gl.model_to_world[len(gl.model_to_world) - 1])

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
    
    return screen_point

def transform_points(point, gl):
    screen_points = []

    for i in range(0, len(point) - 2, 3):
        p = [point[i], point[i + 1], point[i + 2]]
        screen_points += [apply_point_transformations(p, gl)]
    
    # print(screen_points)
    return screen_points

class Rasterizer:

    width = None
    height = None
    gpu_instance = None
    frame_buffer = []
    sampling = 1

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
    def setup(gpu_instance, width, height, sampling):
        Rasterizer.gpu_instance = gpu_instance
        Rasterizer.width = width
        Rasterizer.height = height
        Rasterizer.sampling = sampling
        Rasterizer.frame_buffer = [[0, 0, 0]] * ((sampling ** 2) * width * height)
    
    @staticmethod
    def raster(triangles, colors):

        for triangle in triangles:
            start_time = time.time()

            line1 = (triangle[2][0] - triangle[0][0], triangle[2][1] - triangle[0][1])
            line2 = (triangle[1][0] - triangle[2][0], triangle[1][1] - triangle[2][1])
            line3 = (triangle[0][0] - triangle[1][0], triangle[0][1] - triangle[1][1])

            normals = [(line1[1], - line1[0]), (line2[1], - line2[0]), (line3[1], - line3[0])]
            triangle_AABB = Rasterizer.AABB(int(triangle[0][0, 0]), int(triangle[0][1, 0]), math.ceil(triangle[0][0, 0]), math.ceil(triangle[0][1, 0]))

            for p in range(1, len(triangle)):
                if triangle[p][0] > triangle_AABB.max_x: triangle_AABB.max_x = math.ceil(triangle[p][0, 0])
                if triangle[p][0] < triangle_AABB.min_x: triangle_AABB.min_x = int(triangle[p][0, 0])
                if triangle[p][1] > triangle_AABB.max_y: triangle_AABB.max_y = math.ceil(triangle[p][1, 0])
                if triangle[p][1] < triangle_AABB.min_y: triangle_AABB.min_y = int(triangle[p][1, 0])

            Rasterizer.render(triangle, normals, colors, triangle_AABB)
            print("--- Time to render triangle: %s seconds ---" % (time.time() - start_time))
        
        Rasterizer.sample()
    
    @staticmethod
    def render(triangle, normals, colors, triangle_AABB):

        P1 = [0, 0]
        P2 = [0, 0]
        P3 = [0, 0]
        height = Rasterizer.height
        frame_buffer = Rasterizer.frame_buffer
        sampling = Rasterizer.sampling

        for x in range(triangle_AABB.min_x, triangle_AABB.max_x):
            P1[0] = x - triangle[0][0] + 1/2
            P2[0] = x - triangle[2][0] + 1/2
            P3[0] = x - triangle[1][0] + 1/2

            for y in range(triangle_AABB.min_y, triangle_AABB.max_y):
                P1[1] = y - triangle[0][1] + 1/2
                P2[1] = y - triangle[2][1] + 1/2
                P3[1] = y - triangle[1][1] + 1/2

                if Rasterizer.is_inside([P1, P2, P3], normals):
                    offset = x * height * sampling + y
                    tri_color = [colors[0] * 255, colors[1] * 255, colors[2] * 255]
                    frame_buffer[offset] = tri_color

        Rasterizer.frame_buffer = frame_buffer
    
    @staticmethod
    def is_inside(points, normals):
        for i in range(len(normals)):
            if points[i][0] * normals[i][0] + points[i][1] * normals[i][1] > 0: return 0
        
        return 1
    
    @staticmethod
    def sample():
        sampling = Rasterizer.sampling
        frame_buffer = Rasterizer.frame_buffer
        sampled_size_x = Rasterizer.width * sampling
        sampled_size_y = Rasterizer.height * sampling
        size_y = Rasterizer.height
        
        sampling_square = sampling ** 2
        pixel = [[0, 0, 0]] * sampling_square

        for x in range(0, sampled_size_x, sampling):
            for y in range(size_y):
                y_offset = x * sampled_size_y + y * sampling

                for i in range(sampling):
                    for j in range(sampling):
                        offset = i * sampled_size_y + j + y_offset
                        if offset == len(frame_buffer): break 
                        pixel[i + j] = frame_buffer[offset]

                sum_pixel = np.sum([pixel], axis=1)
                r_mean = sum_pixel[0, 0] / sampling_square
                g_mean = sum_pixel[0, 1] / sampling_square
                b_mean = sum_pixel[0, 2] / sampling_square

                if r_mean > 0 or g_mean > 0 or b_mean > 0:
                    Rasterizer.gpu_instance.draw_pixels([int(x/sampling), y], Rasterizer.gpu_instance.RGB8, [r_mean, g_mean, b_mean])