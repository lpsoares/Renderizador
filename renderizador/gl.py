#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: <SEU NOME AQUI>
Disciplina: Computação Gráfica
Data: <DATA DE INÍCIO DA IMPLEMENTAÇÃO> 
"""

import time         # Para operações com tempo
import gpu          # Simula os recursos de uma GPU
import math         # Funções matemáticas
import numpy as np  # Biblioteca do Numpy
import math
import cv2

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante
    projection_matrix = None  # Armazena a matriz de projeção
    transformation_stack = [np.identity(4)]  # Pilha para armazenar as matrizes de transformação
    view_matrix = None  # Armazena a matriz de visualização

    @staticmethod
    def setup(width, height, ssaa_factor, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far
        GL.ssaa_factor = ssaa_factor

    @staticmethod
    def polypoint2D(point, colors):
        """Função usada para renderizar Polypoint2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polypoint2D
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
        # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
        # você pode assumir inicialmente o desenho dos pontos com a cor emissiva (emissiveColor).

        print(f"Tamanho da tela: {GL.width} x {GL.height}")

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Polypoint2D : pontos = {0}".format(point)) # imprime no terminal pontos
        print("Polypoint2D : colors = {0}".format(colors)) # imprime no terminal as cores
        print([round(n*255) for n in colors['emissiveColor']])

        for i in range(0, len(point), 2):
            pos_x = round(point[i])
            pos_y = round(point[i+1])
            if 0 <= pos_x < GL.width and 0 <= pos_y < GL.height:
                gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [round(n*255) for n in colors['emissiveColor']])
            else:
                print(f"Coordenada fora dos limites: ({pos_x}, {pos_y})")


        # # Exemplo:
        
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 0])  # altera pixel (u, v, tipo, r, g, b)
        # # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)
        
    @staticmethod
    def polyline2D(lineSegments, colors):
        """Função usada para renderizar Polyline2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polyline2D
        # Nessa função você receberá os pontos de uma linha no parâmetro lineSegments, esses
        # pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o valor da
        # coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é
        # a coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista. A quantidade mínima de pontos são 2 (4 valores), porém a
        # função pode receber mais pontos para desenhar vários segmentos. Assuma que sempre
        # vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polyline2D
        # você pode assumir inicialmente o desenho das linhas com a cor emissiva (emissiveColor).


        for i in range(0, len(lineSegments), 4):
            x1 = lineSegments[i]
            y1 = lineSegments[i+1]
            x2 = lineSegments[i+2]
            y2 = lineSegments[i+3]

            # Calculate deltas
            dx = x2 - x1
            dy = y2 - y1

            # Check if the line is more horizontal or vertical
            if abs(dx) > abs(dy):
                # Line is more horizontal
                slope = dy / dx
                print(f"Slope: {slope}, im more horizontal")
                if x1 > x2:  # Ensure we always iterate from left to right
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1

                y = y1
                for x in range(round(x1-0.5), round(x2-0.5) + 1):
                    drawx = round(x)
                    drawy = round(y-0.5)
                    print(f"x: {x}, y: {y}")
                    print(f"Drawing at ({drawx}, {drawy})")
                    if 0 <= drawx < GL.width and 0 <= drawy < GL.height:
                        gpu.GPU.draw_pixel([drawx, drawy], gpu.GPU.RGB8, [round(n * 255) for n in colors["emissiveColor"]])
                    y += slope
            else:
                # Line is more vertical
                slope = dx / dy
                print(f"Slope: {slope}, im more vertical")
                if y1 > y2:  # Ensure we always iterate from bottom to top
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1

                x = x1
                for y in range(round(y1-0.5), round(y2-0.5) + 1):
                    drawx = round(x-0.5)
                    drawy = round(y)
                    print(f"Drawing at ({drawx}, {drawy})")
                    if 0 <= drawx < GL.width and 0 <= drawy < GL.height:
                        gpu.GPU.draw_pixel([drawx, drawy], gpu.GPU.RGB8, [round(n * 255) for n in colors["emissiveColor"]])
                    x += slope


                

        print("Polyline2D : lineSegments = {0}".format(lineSegments)) # imprime no terminal
        print("Polyline2D : colors = {0}".format(colors)) # imprime no terminal as cores


        
        # # Exemplo:
        # pos_x = GL.width//2
        # pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 255])  # altera pixel (u, v, tipo, r, g, b)
        # # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Circle2D
        # Nessa função você receberá um valor de raio e deverá desenhar o contorno de
        # um círculo.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Circle2D
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        # Cor emissiva
        emissive_color = [round(n * 255) for n in colors.get("emissiveColor", [1, 1, 1])]

        # Posição do centro do círculo (assumido como centro da tela)
        pos_x = 0
        pos_y = 0

        # Midpoint Circle Algorithm (Bresenham's Circle Algorithm)
        x = radius
        y = 0
        decision_over_2 = 1 - x  # decision parameter to determine the next pixel position

        while y <= x:
            # Define a list of all the symmetric points
            points = [
                (pos_x + x, pos_y + y),
                (pos_x + y, pos_y + x),
                (pos_x - y, pos_y + x),
                (pos_x - x, pos_y + y),
                (pos_x - x, pos_y - y),
                (pos_x - y, pos_y - x),
                (pos_x + y, pos_y - x),
                (pos_x + x, pos_y - y)
            ]

            # Draw each point if it's within the framebuffer boundaries
            for px, py in points:
                px = int(px)  # Ensure the x-coordinate is an integer
                py = int(py)  # Ensure the y-coordinate is an integer
                if 0 <= px < GL.width and 0 <= py < GL.height:
                    gpu.GPU.draw_pixel([px, py], gpu.GPU.RGB8, emissive_color)

            y += 1
            if decision_over_2 <= 0:
                decision_over_2 += 2 * y + 1  # move to the next pixel in y direction
            else:
                x -= 1
                decision_over_2 += 2 * (y - x) + 1  # move to the next pixel in both x and y directions

        print("Circle2D : radius = {0}".format(radius))  # imprime no terminal
        print("Circle2D : colors = {0}".format(colors))  # imprime no terminal as cores




    @staticmethod
    def triangleSet2D(vertices, colors):
        """Função usada para renderizar TriangleSet2D."""

            # Assume we want to scale the coordinates based on a reference resolution
        reference_width = GL.width / GL.ssaa_factor  # Set your base/reference width (adjust as needed)
        reference_height = GL.height / GL.ssaa_factor   # Set your base/reference height (adjust as needed)
        
        # Scaling factors based on current resolution compared to reference
        scale_x = GL.width / reference_width
        scale_y = GL.height / reference_height

        print(f'GL.width: {GL.width}, GL.height: {GL.height}')


        for i in range(0, len(vertices), 6):
            x1 = vertices[i] * scale_x
            y1 = vertices[i+1] * scale_y
            x2 = vertices[i+2] * scale_x
            y2 = vertices[i+3] * scale_y
            x3 = vertices[i+4] * scale_x
            y3 = vertices[i+5] * scale_y

        def L1(x, y):
            return (y2-y1)*x - (x2-x1)*y + y1*(x2-x1) - x1*(y2-y1)
        
        def L2(x, y):
            return (y3-y2)*x - (x3-x2)*y + y2*(x3-x2) - x2*(y3-y2)
        
        def L3(x, y):
            return (y1-y3)*x - (x1-x3)*y + y3*(x1-x3) - x3*(y1-y3)
        
        for x in range(0, GL.width):
            for y in range(0, GL.height):
                if L1(x+0.5, y+0.5) >= 0 and L2(x+0.5, y+0.5) >= 0 and L3(x+0.5, y+0.5) >= 0:
                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, [round(n * 255) for n in colors["emissiveColor"]])

        print("TriangleSet2D : vertices = {0}".format(vertices)) # imprime no terminal
        print("TriangleSet2D : colors = {0}".format(colors)) # imprime no terminal as cores
    
    @staticmethod
    def generate_mipmaps(image_texture, max_levels=5, target_channels=4):
        """Função para gerar mipmaps a partir de uma imagem original.
        
        Args:
            image_texture: A imagem original.
            max_levels: O número máximo de níveis de mipmap a serem gerados.
            target_channels: O número desejado de canais (3 para RGB, 4 para RGBA).
            
        Returns:
            mipmaps: Lista de mipmaps gerados.
        """
        
        # Verificar o número de canais da imagem e converter se necessário
        if len(image_texture.shape) == 2:  # Imagem em escala de cinza
            print("Converting grayscale image to RGB")
            image_texture = cv2.cvtColor(image_texture, cv2.COLOR_GRAY2RGB)
        elif image_texture.shape[2] == 3 and target_channels == 4:
            print("Converting RGB image to RGBA")
            image_texture = cv2.cvtColor(image_texture, cv2.COLOR_RGB2RGBA)
        elif image_texture.shape[2] == 4 and target_channels == 3:
            print("Converting RGBA image to RGB")
            image_texture = cv2.cvtColor(image_texture, cv2.COLOR_RGBA2RGB)

        # Inicializar lista de mipmaps com a textura original
        mipmaps = [image_texture]
        current_texture = image_texture

        for level in range(1, max_levels):
            # Reduz o tamanho da textura pela metade para criar o próximo nível do mipmap
            next_texture = cv2.resize(current_texture, 
                                    (max(1, current_texture.shape[1] // 2), 
                                    max(1, current_texture.shape[0] // 2)), 
                                    interpolation=cv2.INTER_LINEAR)
            mipmaps.append(next_texture)
            current_texture = next_texture

        return mipmaps

    @staticmethod
    def draw_filled_triangle(p1, p2, p3, colors, zs, colorPerVertex, textureFlag, tex_coords, image_texture):
        """Função usada para renderizar TriangleSet2D com bounding box para melhorar a performance."""

        if textureFlag:
            texture_mipmaps = GL.generate_mipmaps(image_texture)


        def L1(x, y):
            return (p2[1] - p1[1]) * x - (p2[0] - p1[0]) * y + p1[1] * (p2[0] - p1[0]) - p1[0] * (p2[1] - p1[1])
        
        def L2(x, y):
            return (p3[1] - p2[1]) * x - (p3[0] - p2[0]) * y + p2[1] * (p3[0] - p2[0]) - p2[0] * (p3[1] - p2[1])
        
        def L3(x, y):
            return (p1[1] - p3[1]) * x - (p1[0] - p3[0]) * y + p3[1] * (p1[0] - p3[0]) - p3[0] * (p1[1] - p3[1])
        
        def area(p1, p2, p3):
            return 0.5 * np.abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]))
        
        def barycentric(p1, p2, p3, p):
            A = area(p1, p2, p3)
            A1 = area(p, p2, p3)
            A2 = area(p1, p, p3)
            A3 = area(p1, p2, p)
            return A1 / A, A2 / A, A3 / A
        
        def perspective_color(p1, p2, p3, p, colors, zs):
            alpha, beta, gamma = barycentric(p1, p2, p3, p)

            z0 = abs(zs[0])
            z1 = abs(zs[1])
            z2 = abs(zs[2])

            Z = 1/(alpha/z0 + beta/z1 + gamma/z2)


            R0, G0, B0 = colors[:3]
            R1, G1, B1 = colors[3:6]
            R2, G2, B2 = colors[6:]

            R = round(Z*(R0 * alpha / z0 + R1 * beta / z1 + R2 * gamma / z2)*255)
            G = round(Z*(G0 * alpha / z0 + G1 * beta / z1 + G2 * gamma / z2)*255)
            B = round(Z*(B0 * alpha / z0 + B1 * beta / z1 + B2 * gamma / z2)*255)

            return [R, G, B]
        
        def texture_perspective_coords(p1, p2, p3, p, tex_coords, zs):
            alpha, beta, gamma = barycentric(p1, p2, p3, p)

            u0, v0 = tex_coords[0], tex_coords[1]
            u1, v1 = tex_coords[2], tex_coords[3]
            u2, v2 = tex_coords[4], tex_coords[5]

            z0 = abs(zs[0])
            z1 = abs(zs[1])
            z2 = abs(zs[2])

            Z = 1/(alpha/z0 + beta/z1 + gamma/z2)

            u = Z*(u0 * alpha / z0 + u1 * beta / z1 + u2 * gamma / z2)
            v = Z*(v0 * alpha / z0 + v1 * beta / z1 + v2 * gamma / z2)

            return [u, v]
        
        z0 = abs(zs[0])
        z1 = abs(zs[1])
        z2 = abs(zs[2])

        transparency = colors['transparency']

        # Encontra a bounding box da triangle
        min_x = int(max(0.0, min(p1[0], p2[0], p3[0])))
        max_x = int(min(GL.width - 1, max(p1[0], p2[0], p3[0])))
        min_y = int(max(0.0, min(p1[1], p2[1], p3[1])))
        max_y = int(min(GL.height - 1, max(p1[1], p2[1], p3[1])))

        # print(f"Drawing triangle with vertices {p1}, {p2}, {p3}")

        mip_level_print = 0
        for x in range(min_x, max_x + 1):  # Include the max_x by adding 1 to the range
            for y in range(min_y, max_y + 1):  # Include the max_y by adding 1 to the range
                if L1(x + 0.5, y + 0.5) >= 0 and L2(x + 0.5, y + 0.5) >= 0 and L3(x + 0.5, y + 0.5) >= 0:

                    alpha, beta, gamma = barycentric(p1, p2, p3, [x, y])

                    if textureFlag:
                        [u, v] = texture_perspective_coords(p1, p2, p3, [x, y], tex_coords, zs)

                        # Clamp u and v to the [0, 1] range
                        # u = np.clip(u, 0, 1)
                        # v = np.clip(v, 0, 1)
                        x_00 = x
                        y_00 = y
                        x_10 = x + 1
                        y_10 = y
                        x_01 = x
                        y_01 = y + 1

                        [u_00, v_00] = texture_perspective_coords(p1, p2, p3, [x_00, y_00], tex_coords, zs)
                        [u_10, v_10] = texture_perspective_coords(p1, p2, p3, [x_10, y_10], tex_coords, zs)
                        [u_01, v_01] = texture_perspective_coords(p1, p2, p3, [x_01, y_01], tex_coords, zs)
                    

                        # Calculando as derivadas (dudx, dudy, dvdx, dvdy) para o cálculo do LOD
                        dudx = (u_10 - u_00)/(x_10 - x_00)*image_texture.shape[0]  # texture.shape[1] é a largura da textura
                        dudy = (u_01 - u_00)/(y_01 - y_00)*image_texture.shape[0]
                        
                        dvdx = (v_10 - v_00)/(x_10 - x_00)*image_texture.shape[1]  # texture.shape[0] é a altura da textura
                        dvdy = (v_01 - v_00)/(y_01 - y_00)*image_texture.shape[1]


                        # Calculando o nível de Mipmap baseado nas derivadas
                        L = max(np.sqrt(dudx ** 2 + dvdx ** 2), np.sqrt(dudy ** 2 + dvdy ** 2))
                        D = np.log2(L)

                        
                        mip_level = round(np.clip(D, 0, len(texture_mipmaps) - 1))
                        if mip_level_print != mip_level:
                            print(f'Mip level: {mip_level_print}')
                        mip_level_print = mip_level

                        # Selecionando a textura do nível de mipmap apropriado
                        texture = texture_mipmaps[mip_level]

                        u = int(u * (texture.shape[0] - 1))  # texture.shape[1] é a largura da textura
                        v = int(-v * (texture.shape[1] - 1) + texture.shape[0])  # texture.shape[0] é a altura da textura

                    Z = 1/(alpha/z0 + beta/z1 + gamma/z2)
                    Z_stored = gpu.GPU.read_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F)

                    # if x == 5 and y == 6:
                    #     print(f'Z_stored: {Z_stored}')
                    #     print(f'Z: {Z}')

                    if Z < Z_stored[0]:
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F, [Z])
                        prev_color = gpu.GPU.read_pixel([x, y], gpu.GPU.RGB8) * transparency
                        if colorPerVertex:
                            new_color = np.array(perspective_color(p1, p2, p3, [x, y], colors["polarColor"], zs)) * (1 - transparency)
                        else:
                            new_color = np.array([round(n * 255) for n in colors["emissiveColor"]]) * (1 - transparency)
                        # if x == 5 and y == 6:
                        #     print(f'prev_color: {prev_color}')
                        #     print(f'new_color: {new_color}')
                        final_color = (prev_color + new_color).astype(np.uint8)
                        if textureFlag:
                            
                            final_color = texture[u, v]
                            if len(final_color) > 3:
                                final_color = final_color[:3]
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, final_color)

    @staticmethod
    def triangleSet(point, colors, triangle_texture=None, image_texture=None, colorPerVertex=False, textureFlag=False):
        """Função usada para renderizar TriangleSet."""
        
        # Iterate over each triangle (each group of 3 points)
        print("Drawing triangle")
        for i in range(0, len(point), 9):  # 9 values for each triangle (3 points x 3 coordinates)
            print("Drawing triangle")
            # Extract the three vertices of the triangle
            p1 = np.array([point[i], point[i+1], point[i+2], 1])  # Homogeneous coordinates
            p2 = np.array([point[i+3], point[i+4], point[i+5], 1])
            p3 = np.array([point[i+6], point[i+7], point[i+8], 1])


            # Apply the current transformation matrix from the stack
            current_transform = GL.transformation_stack[-1]
            p1_transformed = current_transform @ p1
            p2_transformed = current_transform @ p2
            p3_transformed = current_transform @ p3

            # Apply view
            p2_view = GL.view_matrix @ p2_transformed
            p1_view = GL.view_matrix @ p1_transformed
            p3_view = GL.view_matrix @ p3_transformed

            # Apply projection
            p1_projected = GL.projection_matrix @ p1_view
            p2_projected = GL.projection_matrix @ p2_view
            p3_projected = GL.projection_matrix @ p3_view

            # Convert from homogeneous to 2D coordinates
            p1_screen = p1_projected[:2] / p1_projected[3]
            p2_screen = p2_projected[:2] / p2_projected[3]
            p3_screen = p3_projected[:2] / p3_projected[3]

            # Convert to screen space and map to integer pixel positions with y-axis inversion
            p1_screen = np.array([(p1_screen[0] + 1) * (GL.width / 2), (1 - p1_screen[1]) * (GL.height / 2)])
            p2_screen = np.array([(p2_screen[0] + 1) * (GL.width / 2), (1 - p2_screen[1]) * (GL.height / 2)])
            p3_screen = np.array([(p3_screen[0] + 1) * (GL.width / 2), (1 - p3_screen[1]) * (GL.height / 2)])

            z1_camera = p1_view[2]
            z2_camera = p2_view[2]
            z3_camera = p3_view[2]
            zs = [z1_camera, z2_camera, z3_camera]
            
            
            GL.draw_filled_triangle(p1_screen, p2_screen, p3_screen, colors, zs, colorPerVertex, textureFlag, triangle_texture, image_texture)
        


    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Cálculo da matriz de projeção perspectiva
        aspect_ratio = GL.width / GL.height
        z_near = GL.near
        z_far = GL.far


        f = 1.0 / np.tan(fieldOfView / 2)
        perspective_matrix = np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (z_far + z_near) / (z_near - z_far), (2 * z_far * z_near) / (z_near - z_far)],
            [0, 0, -1, 0]
        ])
        

        GL.projection_matrix = perspective_matrix

        # Step 2: Create the view matrix using position and orientation
        # Conversão de rotação (eixo + ângulo) para quaternion
        axis = np.array(orientation[:3])
        angle = orientation[3]
        print(angle)
        axis = axis / np.linalg.norm(axis)  # Normaliza o eixo de rotação
        sin_half_angle = np.sin(angle / 2)
        cos_half_angle = np.cos(angle / 2)
        
        quaternion = np.array([
            cos_half_angle,
            axis[0] * sin_half_angle,
            axis[1] * sin_half_angle,
            axis[2] * sin_half_angle
        ])

        # Convert orientation (quaternion) into a rotation matrix
        w, x, y, z = quaternion
        rotation_matrix = np.array([
            [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w, 0],
            [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w, 0],
            [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y, 0],
            [0, 0, 0, 1]
        ]).T

        # Create the translation matrix to move the scene by the negative camera position
        translation_matrix = np.array([
            [1, 0, 0, -position[0]],
            [0, 1, 0, -position[1]],
            [0, 0, 1, -position[2]],
            [0, 0, 0, 1]
        ])

        # Combine rotation and translation to form the view matrix
        view_matrix = rotation_matrix @ translation_matrix
        GL.view_matrix = view_matrix




    @staticmethod
    def transform_in(translation, scale, rotation):
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo para depois potencialmente usar em outras chamadas. 
        # Quando começar a usar Transforms dentre de outros Transforms, mais a frente no curso
        # Você precisará usar alguma estrutura de dados pilha para organizar as matrizes.
        
        # Conversão de rotação (eixo + ângulo) para quaternion
        axis = np.array(rotation[:3])
        angle = rotation[3]
        axis = axis / np.linalg.norm(axis)  # Normaliza o eixo de rotação
        sin_half_angle = np.sin(angle / 2)
        cos_half_angle = np.cos(angle / 2)
        
        quaternion = np.array([
            cos_half_angle,
            axis[0] * sin_half_angle,
            axis[1] * sin_half_angle,
            axis[2] * sin_half_angle
        ])
        
        # Matriz de rotação a partir do quaternion
        w, x, y, z = quaternion
        rotation_matrix = np.array([
            [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w, 0],
            [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w, 0],
            [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y, 0],
            [0, 0, 0, 1]
        ])
        
        # Matriz de escala
        scale_matrix = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ])
        
        # Matriz de translação
        translation_matrix = np.array([
            [1, 0, 0, translation[0]],
            [0, 1, 0, translation[1]],
            [0, 0, 1, translation[2]],
            [0, 0, 0, 1]
        ])
        
        # Combinando as matrizes na ordem: Translação * Rotação * Escala
        transformation_matrix = translation_matrix @ rotation_matrix @ scale_matrix

        # Obtém a matriz de transformação atual no topo da pilha
        current_transformation = GL.transformation_stack[-1]

        # Calcula a nova transformação combinando a transformação atual com a nova
        new_transformation = current_transformation @ transformation_matrix

        # Adiciona a nova matriz de transformação à pilha
        GL.transformation_stack.append(new_transformation)

    def transform_out():
        """Função usada para finalizar a aplicação de um Transform no grafo de cena."""
        if len(GL.transformation_stack) > 1:
            # Remove a matriz do topo da pilha, retornando ao contexto de transformação anterior
            GL.transformation_stack.pop()

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        """Função usada para renderizar TriangleStripSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#TriangleStripSet
        # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
        # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
        # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
        # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
        # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
        # em uma lista chamada stripCount (perceba que é uma lista). Ligue os vértices na ordem,
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.


                # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
# imprime no terminal as cores


        i = 0
        for n_vertex in stripCount:
            for j in range(0, n_vertex):
                if i > len(point)-9:
                    break
                if j % 2 == 0:
                    triangle = point[i:i+9]
                else:
                    triangle = point[i:i+3] + point[i+6:i+9] + point[i+3:i+6]
                GL.triangleSet(triangle, colors)

                i += 3
                
            
                

            


    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Função usada para renderizar IndexedTriangleStripSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#IndexedTriangleStripSet
        # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
        # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
        # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
        # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
        # como conectar os vértices é informada em index, o valor -1 indica que a lista
        # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # Implementação do IndexedTriangleStripSet

        i = 0
        flag = False
        for j in range(len(index)):
            if index[i+2] == -1:
                if i+3 == len(index):
                    break
                i += 3
                

            vertex1 = point[index[i]*3:index[i]*3+3]
            vertex2 = point[index[i+1]*3:index[i+1]*3+3]
            vertex3 = point[index[i+2]*3:index[i+2]*3+3]

            if i % 2 == 0:
                triangle = vertex1 + vertex2 + vertex3
                flag = False
            else:
                triangle = vertex1 + vertex3 + vertex2
                flag = True         
            GL.triangleSet(triangle, colors)
            
            frame = ['-']*len(point)

            frame[index[i]*3:index[i]*3+3] = vertex1
            frame[index[i+1]*3:index[i+1]*3+3] = vertex2
            frame[index[i+2]*3:index[i+2]*3+3] = vertex3
            i += 1
            
            


        # # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        colorPerVertex = colorPerVertex and colorIndex
        textureFlag = False
        if texCoord and texCoordIndex:
            if len(texCoord) > 0 and len(texCoordIndex) > 0:
                textureFlag = True
        

        # print(f'coord: {coord}')
        # print(f'coordIndex: {coordIndex}')
        # print(f'colorPerVertex: {colorPerVertex}')
        # print(f'color: {color}')
        # print(f'colorIndex: {colorIndex}')
        print(f'texCoord: {texCoord}')
        print(f'texCoordIndex: {texCoordIndex}')
        print(f'textureFlag: {textureFlag}')
        # print(f'colors: {colors}')
        # print(f'current_texture: {current_texture}')

        # Add check if colorIndex list is empty
        
        i = 0
        call_count = 0
        pivot_point = coord[coordIndex[i]*3:coordIndex[i]*3+3]
        pivot_index = coordIndex[i]
        image_texture = None
        # print(f"colorPerVertex: {colorPerVertex}")
        if colorPerVertex:
            pivot_color = color[colorIndex[i]*3:colorIndex[i]*3+3]
        if textureFlag:
            pivot_texture = texCoord[texCoordIndex[i]*2:texCoordIndex[i]*2+2]
            image_texture = gpu.GPU.load_texture(current_texture[0])

        i +=1 
        while i < len(coordIndex)-2:
            # Connect last vertex with the first one to close the triangle strip
            
            if coordIndex[i+1] == -1:
                if i+2 == len(coordIndex):
                    break
                i += 2
                pivot_point = coord[coordIndex[i]*3:coordIndex[i]*3+3]
                pivot_index = coordIndex[i]
                if colorPerVertex:
                    pivot_color = color[colorIndex[i]*3:colorIndex[i]*3+3]
                elif textureFlag:
                    pivot_texture = texCoord[texCoordIndex[i]*2:texCoordIndex[i]*2+2]
                i += 1
                continue

            

            triangle = pivot_point + coord[coordIndex[i]*3:coordIndex[i]*3+3] + coord[coordIndex[i+1]*3:coordIndex[i+1]*3+3]
            triangle_texture = None
            if colorPerVertex:
                colors['polarColor'] = pivot_color + color[colorIndex[i]*3:colorIndex[i]*3+3] + color[colorIndex[i+1]*3:colorIndex[i+1]*3+3]
            elif textureFlag:
                triangle_texture = pivot_texture + texCoord[texCoordIndex[i]*2:texCoordIndex[i]*2+2] + texCoord[texCoordIndex[i+1]*2:texCoordIndex[i+1]*2+2]
            
                
            call_count += 1
            GL.triangleSet(triangle, colors, triangle_texture, image_texture, colorPerVertex, textureFlag)
            i += 1



    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # Box is centered at (0, 0, 0) and extends along the X, Y, and Z axes based on 'size'.
        
        # Extracting size values for clarity
        sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2  # Divide by 2 since the box is centered at the origin
        
        # Define the 8 vertices of the box
        coord = [
            [-sx, sy, -sz],  
            [-sx, sy, sz],  
            [sx,  sy, sz],
            [sx,  sy, -sz],  
            [-sx, -sy,  -sz],  
            [-sx, -sy,  sz],  
            [sx,  -sy,  sz],  
            [sx,  -sy,  -sz]   
        ]

        # Define the faces of the box using indices
        # Each face is represented by two triangles (triangle strips or indexed faces)
        points = [
            coord[0], coord[1], coord[3],
            coord[1], coord[2], coord[3],
            coord[0], coord[4], coord[1],
            coord[4], coord[5], coord[1],
            coord[1], coord[5], coord[2],
            coord[5], coord[6], coord[2],
            coord[2], coord[6], coord[3],
            coord[6], coord[7], coord[3],
            coord[3], coord[7], coord[0],
            coord[7], coord[4], coord[0],
            coord[4], coord[7], coord[5],
            coord[7], coord[6], coord[5]
        ]

        points = np.array(points).flatten()

        # If no specific colors are provided, we can assume a default color (e.g., white)
        if colors is None:
            colors = {'polarColor': [1.0, 1.0, 1.0] * 4}
        print(points)
        GL.triangleSet(points, colors)



    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        
        # Configurações para tesselar a esfera
        lat_steps = 20  # Número de divisões ao longo da latitude
        lon_steps = 20  # Número de divisões ao longo da longitude

        # Arrays para armazenar os vértices e os índices
        coord = []
        coordIndex = []

        # Gerar vértices da esfera
        for i in range(lat_steps + 1):
            theta = i * math.pi / lat_steps  # De 0 a pi (de polo a polo)
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)

            for j in range(lon_steps):
                phi = j * 2 * math.pi / lon_steps  # De 0 a 2*pi (em torno da esfera)
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)

                # Coordenadas do vértice na esfera
                x = radius * sin_theta * cos_phi
                y = radius * cos_theta
                z = radius * sin_theta * sin_phi

                coord.extend([x, y, z])

        # Gerar os índices para criar os triângulos (faces)
        for i in range(lat_steps):
            for j in range(lon_steps):
                first = i * lon_steps + j
                second = first + lon_steps

                # Criar dois triângulos para cada quadrado da malha
                coordIndex.extend([first, second, (first + 1) % lon_steps + i * lon_steps, -1])
                coordIndex.extend([(first + 1) % lon_steps + i * lon_steps, second, (second + 1) % lon_steps + (i + 1) * lon_steps, -1])

        # Se as cores não forem fornecidas, usa uma cor padrão (branco)
        if colors is None:
            colors = {'polarColor': [1.0, 1.0, 1.0] * 4}

        # Nenhuma textura está sendo usada aqui
        texCoord = None
        texCoordIndex = None
        current_texture = None

        # Chamar a função indexedFaceSet para desenhar a esfera
        GL.indexedFaceSet(coord, coordIndex, False, None, None, texCoord, texCoordIndex, colors, current_texture)



    @staticmethod
    def cone(bottomRadius, height, colors, sides=20):
        """Função usada para renderizar Cones."""

        # Listas para armazenar os vértices e os índices
        coord = []
        coordIndex = []

        # Adicionar o vértice da ponta do cone (o vértice superior)
        apex = [0, height / 2, 0]  # Vértice superior centrado no eixo Y
        coord.extend(apex)

        # Gerar os vértices da base do cone (distribuídos ao longo de um círculo)
        for i in range(sides):
            angle = i * 2 * math.pi / sides
            x = bottomRadius * math.cos(angle)
            z = bottomRadius * math.sin(angle)
            coord.extend([x, -height / 2, z])  # Adicionar vértice da base no eixo Y negativo

        # Adicionar os índices para os triângulos laterais (da ponta à base)
        for i in range(sides):
            next_index = (i + 1) % sides + 1
            coordIndex.extend([0, i + 1, next_index, -1])

        # Adicionar os índices para a base (usando triângulos em "leque")
        base_center_index = len(coord) // 3  # Índice para o centro da base
        coord.extend([0, -height / 2, 0])  # Adicionar o centro da base

        for i in range(sides):
            next_index = (i + 1) % sides + 1
            coordIndex.extend([base_center_index, next_index, i + 1, -1])

        # Se as cores não forem fornecidas, usar uma cor padrão (branco)
        if colors is None:
            colors = {'polarColor': [1.0, 1.0, 1.0] * 3}

        # Nenhuma textura está sendo usada aqui
        texCoord = None
        texCoordIndex = None
        current_texture = None

        # Chamar a função indexedFaceSet para desenhar o cone
        GL.indexedFaceSet(coord, coordIndex, False, None, None, texCoord, texCoordIndex, colors, current_texture)


    @staticmethod
    def cylinder(radius, height, colors, sides=20):
        """Função usada para renderizar Cilindros."""

        # Listas para armazenar os vértices e os índices
        coord = []
        coordIndex = []

        # Gerar os vértices das bases do cilindro (superior e inferior)
        for i in range(sides):
            angle = i * 2 * math.pi / sides
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

            # Vértice superior (no eixo Y positivo)
            coord.extend([x, height / 2, z])
            # Vértice inferior (no eixo Y negativo)
            coord.extend([x, -height / 2, z])

        # Adicionar os índices para os triângulos das laterais do cilindro
        for i in range(sides):
            next_index = (i + 1) % sides
            top1 = i * 2
            bottom1 = i * 2 + 1
            top2 = next_index * 2
            bottom2 = next_index * 2 + 1
            # Triângulo 1 da lateral
            coordIndex.extend([top1, bottom1, top2, -1])
            # Triângulo 2 da lateral
            coordIndex.extend([bottom1, bottom2, top2, -1])

        # Adicionar os vértices centrais das bases
        top_center_index = len(coord) // 3
        coord.extend([0, height / 2, 0])  # Centro da base superior
        bottom_center_index = top_center_index + 1
        coord.extend([0, -height / 2, 0])  # Centro da base inferior

        # Adicionar os índices para fechar as bases (triângulos em leque)
        for i in range(sides):
            next_index = (i + 1) % sides
            top1 = i * 2
            bottom1 = i * 2 + 1

            # Fechar a base superior
            coordIndex.extend([top_center_index, top1, next_index * 2, -1])
            # Fechar a base inferior
            coordIndex.extend([bottom_center_index, next_index * 2 + 1, bottom1, -1])

        # Se as cores não forem fornecidas, usar uma cor padrão (branco)
        if colors is None:
            colors = {'polarColor': [1.0, 1.0, 1.0] * 3}

        # Nenhuma textura está sendo usada aqui
        texCoord = None
        texCoordIndex = None
        current_texture = None

        # Chamar a função indexedFaceSet para desenhar o cilindro
        GL.indexedFaceSet(coord, coordIndex, False, None, None, texCoord, texCoordIndex, colors, current_texture)


    @staticmethod
    def navigationInfo(headlight):
        """Características físicas do avatar do visualizador e do modelo de visualização."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/navigation.html#NavigationInfo
        # O campo do headlight especifica se um navegador deve acender um luz direcional que
        # sempre aponta na direção que o usuário está olhando. Definir este campo como TRUE
        # faz com que o visualizador forneça sempre uma luz do ponto de vista do usuário.
        # A luz headlight deve ser direcional, ter intensidade = 1, cor = (1 1 1),
        # ambientIntensity = 0,0 e direção = (0 0 −1).

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("NavigationInfo : headlight = {0}".format(headlight)) # imprime no terminal

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#DirectionalLight
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("DirectionalLight : ambientIntensity = {0}".format(ambientIntensity))
        print("DirectionalLight : color = {0}".format(color)) # imprime no terminal
        print("DirectionalLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("DirectionalLight : direction = {0}".format(direction)) # imprime no terminal

    @staticmethod
    def pointLight(ambientIntensity, color, intensity, location):
        """Luz pontual."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#PointLight
        # Fonte de luz pontual em um local 3D no sistema de coordenadas local. Uma fonte
        # de luz pontual emite luz igualmente em todas as direções; ou seja, é omnidirecional.
        # Possui os campos básicos ambientIntensity, cor, intensidade. Um nó PointLight ilumina
        # a geometria em um raio de sua localização. O campo do raio deve ser maior ou igual a
        # zero. A iluminação do nó PointLight diminui com a distância especificada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("PointLight : ambientIntensity = {0}".format(ambientIntensity))
        print("PointLight : color = {0}".format(color)) # imprime no terminal
        print("PointLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("PointLight : location = {0}".format(location)) # imprime no terminal

    @staticmethod
    def fog(visibilityRange, color):
        """Névoa."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/environmentalEffects.html#Fog
        # O nó Fog fornece uma maneira de simular efeitos atmosféricos combinando objetos
        # com a cor especificada pelo campo de cores com base nas distâncias dos
        # vários objetos ao visualizador. A visibilidadeRange especifica a distância no
        # sistema de coordenadas local na qual os objetos são totalmente obscurecidos
        # pela névoa. Os objetos localizados fora de visibilityRange do visualizador são
        # desenhados com uma cor de cor constante. Objetos muito próximos do visualizador
        # são muito pouco misturados com a cor do nevoeiro.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Fog : color = {0}".format(color)) # imprime no terminal
        print("Fog : visibilityRange = {0}".format(visibilityRange))

    @staticmethod
    def timeSensor(cycleInterval, loop):
        """Gera eventos conforme o tempo passa."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/time.html#TimeSensor
        # Os nós TimeSensor podem ser usados para muitas finalidades, incluindo:
        # Condução de simulações e animações contínuas; Controlar atividades periódicas;
        # iniciar eventos de ocorrência única, como um despertador;
        # Se, no final de um ciclo, o valor do loop for FALSE, a execução é encerrada.
        # Por outro lado, se o loop for TRUE no final de um ciclo, um nó dependente do
        # tempo continua a execução no próximo ciclo. O ciclo de um nó TimeSensor dura
        # cycleInterval segundos. O valor de cycleInterval deve ser maior que zero.

        # Deve retornar a fração de tempo passada em fraction_changed

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TimeSensor : cycleInterval = {0}".format(cycleInterval)) # imprime no terminal
        print("TimeSensor : loop = {0}".format(loop))

        # Esse método já está implementado para os alunos como exemplo
        epoch = time.time()  # time in seconds since the epoch as a floating point number.
        fraction_changed = (epoch % cycleInterval) / cycleInterval

        return fraction_changed

    @staticmethod
    def splinePositionInterpolator(set_fraction, key, keyValue, closed):
        """Interpola não linearmente entre uma lista de vetores 3D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/interpolators.html#SplinePositionInterpolator
        # Interpola não linearmente entre uma lista de vetores 3D. O campo keyValue possui
        # uma lista com os valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantos vetores 3D quanto os
        # quadros-chave no key. O campo closed especifica se o interpolador deve tratar a malha
        # como fechada, com uma transições da última chave para a primeira chave. Se os keyValues
        # na primeira e na última chave não forem idênticos, o campo closed será ignorado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("SplinePositionInterpolator : set_fraction = {0}".format(set_fraction))
        print("SplinePositionInterpolator : key = {0}".format(key)) # imprime no terminal
        print("SplinePositionInterpolator : keyValue = {0}".format(keyValue))
        print("SplinePositionInterpolator : closed = {0}".format(closed))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0.0, 0.0, 0.0]
        
        return value_changed

    @staticmethod
    def orientationInterpolator(set_fraction, key, keyValue):
        """Interpola entre uma lista de valores de rotação especificos."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/interpolators.html#OrientationInterpolator
        # Interpola rotações são absolutas no espaço do objeto e, portanto, não são cumulativas.
        # Uma orientação representa a posição final de um objeto após a aplicação de uma rotação.
        # Um OrientationInterpolator interpola entre duas orientações calculando o caminho mais
        # curto na esfera unitária entre as duas orientações. A interpolação é linear em
        # comprimento de arco ao longo deste caminho. Os resultados são indefinidos se as duas
        # orientações forem diagonalmente opostas. O campo keyValue possui uma lista com os
        # valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantas rotações 3D quanto os
        # quadros-chave no key.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("OrientationInterpolator : set_fraction = {0}".format(set_fraction))
        print("OrientationInterpolator : key = {0}".format(key)) # imprime no terminal
        print("OrientationInterpolator : keyValue = {0}".format(keyValue))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0, 0, 1, 0]

        return value_changed

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""

