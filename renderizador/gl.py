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

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far


    @staticmethod
    def _transform_vertex(vertex):
        """Transforms a 3D vertex to 2D screen coordinates."""
        vec = np.array([vertex[0], vertex[1], vertex[2], 1.0])

        # Apply model, view, and projection matrices
        if hasattr(GL, "model_matrix"):
            vec = GL.model_matrix @ vec
        if hasattr(GL, "view_matrix"):
            vec = GL.view_matrix @ vec
        if hasattr(GL, "projection_matrix"):
            vec = GL.projection_matrix @ vec

        # Perspective divide
        if vec[3] != 0:
            vec = vec / vec[3]

        # NDC → screen coordinates
        x = int((vec[0] * 0.5 + 0.5) * (GL.width - 1))
        y = int((vec[1] * 0.5 + 0.5) * (GL.height - 1)) # Assuming your Y-inversion is intended

        return (x, y)


    @staticmethod
    def _draw_inside_triangle(p0, p1, p2, emissive_color):
        """Draws a filled triangle using scanline rasterization with edge functions."""
        v0_x, v0_y = p0
        v1_x, v1_y = p1
        v2_x, v2_y = p2

        # Bounding box
        min_x, max_x = min(v0_x, v1_x, v2_x), max(v0_x, v1_x, v2_x)
        min_y, max_y = min(v0_y, v1_y, v2_y), max(v0_y, v1_y, v2_y)

        def edge_func(ax, ay, bx, by, px, py):
            return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                w0 = edge_func(v1_x, v1_y, v2_x, v2_y, x, y)
                w1 = edge_func(v2_x, v2_y, v0_x, v0_y, x, y)
                w2 = edge_func(v0_x, v0_y, v1_x, v1_y, x, y)

                # Check if pixel is inside the triangle
                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    if 0 <= x < GL.width and 0 <= y < GL.height:
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8,
                                [emissive_color[0] * 255,
                                emissive_color[1] * 255,
                                emissive_color[2] * 255])


    @staticmethod
    def _draw_inside_triangle_color_and_tex(p0, p1, p2, c0, c1, c2, uv0, uv1, uv2, texture_img, default_color_tuple):
        """Draws a filled triangle, interpolating vertex colors and texture coordinates."""
        (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2

        # Bounding box
        min_x = max(0, int(min(x0, x1, x2)))
        max_x = min(GL.width -1, int(max(x0, x1, x2)))
        min_y = max(0, int(min(y0, y1, y2)))
        max_y = min(GL.height -1, int(max(y0, y1, y2)))

        def edge_func(ax, ay, bx, by, px, py):
            return (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        
        # Calculate total area (denominator for barycentric coords)
        # We use edge_func on the third vertex to get the area * 2
        area = edge_func(x0, y0, x1, y1, x2, y2)
        if area == 0:
            return # Avoid division by zero for degenerate triangles

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                # These are our barycentric coordinates times the total area
                w0 = edge_func(x1, y1, x2, y2, x, y)
                w1 = edge_func(x2, y2, x0, y0, x, y)
                w2 = edge_func(x0, y0, x1, y1, x, y)

                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    # Normalize to get barycentric coordinates
                    b0 = w0 / area
                    b1 = w1 / area
                    b2 = w2 / area

                    final_color_tuple = default_color_tuple
                    
                    # Priority: Texture > Per-vertex color > Default color
                    if texture_img is not None and all(uv is not None for uv in [uv0, uv1, uv2]):
                        # Interpolate texture coordinates
                        u = b0*uv0[0] + b1*uv1[0] + b2*uv2[0]
                        v = b0*uv0[1] + b1*uv1[1] + b2*uv2[1]

                        # Sample the texture
                        h, w, _ = texture_img.shape
                        tex_x = int(u * (w - 1))
                        tex_y = int((1 - v) * (h - 1)) # Invert V for standard UV mapping
                        
                        px = texture_img[max(0, min(tex_y, h-1)), max(0, min(tex_x, w-1))]
                        final_color_tuple = [int(px[0]), int(px[1]), int(px[2])]

                    elif all(c is not None for c in [c0, c1, c2]):
                        # Interpolate vertex colors
                        r = b0*c0[0] + b1*c1[0] + b2*c2[0]
                        g = b0*c0[1] + b1*c1[1] + b2*c2[1]
                        b = b0*c0[2] + b1*c1[2] + b2*c2[2]
                        final_color_tuple = [int(r*255), int(g*255), int(b*255)]

                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, final_color_tuple)


    @staticmethod
    def _draw_line(p0, p1, emissive_color):
        """Draws a line between two points using Bresenham's algorithm."""
        x0, y0 = p0
        x1, y1 = p1

        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if 0 <= x0 < GL.width and 0 <= y0 < GL.height:
                gpu.GPU.draw_pixel([x0, y0], gpu.GPU.RGB8, [emissive_color[0] * 255, emissive_color[1] * 255, emissive_color[2] * 255])
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy


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

        num_points = len(point) // 2

        for i in range(num_points):
            x, y = int(point[i * 2]), int(point[i * 2 + 1])

            emissive_color = colors['emissiveColor']
            gpu.GPU.draw_pixel([int(x), int(y)], gpu.GPU.RGB8, [int(emissive_color[0] * 255), int(emissive_color[1] * 255), int(emissive_color[2] * 255)])


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
        
        emissive_color = colors['emissiveColor']

        for i in range(0, len(lineSegments) - 2, 2):
            x0, y0 = int(lineSegments[i]), int(lineSegments[i + 1])
            x1, y1 = int(lineSegments[i + 2]), int(lineSegments[i + 3])

            dx, dy = abs(x1 - x0), abs(y1 - y0)
            
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy

            # Algoritmo de Bresenham para desenhar a linha
            while True:
                if 0 <= x0 < GL.width and 0 <= y0 < GL.height:
                    gpu.GPU.draw_pixel([x0, y0], gpu.GPU.RGB8, [emissive_color[0] * 255, emissive_color[1] * 255, emissive_color[2] * 255])

                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy
 
    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Circle2D
        # Nessa função você receberá um valor de raio e deverá desenhar o contorno de
        # um círculo.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Circle2D
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        emissive_color = colors['emissiveColor']

        # Assumindo que o centro esta no (0,0)
        center_x, center_y = 0, 0

        top_left = [int(center_x - radius), int(center_y - radius)]
        bottom_right = [int(center_x + radius), int(center_y + radius)]

        # Iterando na bounding box do círculo
        for x in range(top_left[0], bottom_right[0] + 1):
            for y in range(top_left[1], bottom_right[1] + 1):
                dx2 = (x - center_x) ** 2
                dy2 = (y - center_y) ** 2
                
                # Testando se o ponto esta na circunferencia
                if dx2 + dy2 <= radius ** 2 and dx2 + dy2 >= (radius - 1) ** 2:
                    if 0 <= x < GL.width and 0 <= y < GL.height:
                        gpu.GPU.draw_pixel([int(x), int(y)], gpu.GPU.RGB8, [emissive_color[0] * 255, emissive_color[1] * 255, emissive_color[2] * 255])


    @staticmethod
    def triangleSet2D(vertices, colors):
        """Função usada para renderizar TriangleSet2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#TriangleSet2D
        # Nessa função você receberá os vertices de um triângulo no parâmetro vertices,
        # esses pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o
        # valor da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto.
        # Já point[2] é a coordenada x do segundo ponto e assim por diante. Assuma que a
        # quantidade de pontos é sempre multiplo de 3, ou seja, 6 valores ou 12 valores, etc.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet2D
        # você pode assumir inicialmente o desenho das linhas com a cor emissiva (emissiveColor).
        
        emissive_color = colors["emissiveColor"]
        
        for i in range(0, len(vertices), 6):
            v0_x, v0_y = int(vertices[i]), int(vertices[i + 1])
            v1_x, v1_y = int(vertices[i + 2]), int(vertices[i + 3])
            v2_x, v2_y = int(vertices[i + 4]), int(vertices[i + 5])

            top_left = [min(v0_x, v1_x, v2_x), min(v0_y, v1_y, v2_y)]
            bottom_right = [max(v0_x, v1_x, v2_x), max(v0_y, v1_y, v2_y)]

            # Iterando na bounding box do triangulo
            for x in range(top_left[0], bottom_right[0] + 1):
                for y in range(top_left[1], bottom_right[1] + 1):
                    L0 = np.matrix([[x - v0_x, y - v0_y],
                                    [v1_x - v0_x, v1_y - v0_y]])
                    
                    L1 = np.matrix([[x - v1_x, y - v1_y],
                                    [v2_x - v1_x, v2_y - v1_y]])
                    
                    L2 = np.matrix([[x - v2_x, y - v2_y],
                                    [v0_x - v2_x, v0_y - v2_y]])

                    # Se todos sao verdade, o ponto esta dentro do triangulo
                    if np.linalg.det(L0) >= 0 and np.linalg.det(L1) >= 0 and np.linalg.det(L2) >= 0:
                        if 0 <= x < GL.width and 0 <= y < GL.height:
                            gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, [emissive_color[0] * 255, emissive_color[1] * 255, emissive_color[2] * 255])   


    @staticmethod
    def triangleSet(point, colors):
        """Função usada para renderizar TriangleSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#TriangleSet
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
        # assim por diante.
        # No TriangleSet os triângulos são informados individualmente, assim os três
        # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
        # triângulo, e assim por diante.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, você pode assumir
        # inicialmente, para o TriangleSet, o desenho das linhas com a cor emissiva
        # (emissiveColor), conforme implementar novos materias você deverá suportar outros
        # tipos de cores.

        if not point or len(point) < 9:
            return

        emissive_color = colors["emissiveColor"]
                        
        for i in range(0, len(point), 9):
            triangle = point[i:i + 9]
            v0, v1, v2 = triangle[0:3], triangle[3:6], triangle[6:9]
            p0, p1, p2 = GL._transform_vertex(v0), GL._transform_vertex(v1), GL._transform_vertex(v2)

            GL._draw_inside_triangle(p0, p1, p2, emissive_color)
            GL._draw_line(p0, p1, emissive_color)
            GL._draw_line(p1, p2, emissive_color)
            GL._draw_line(p2, p0, emissive_color)


    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        GL.camera_position = position
        GL.camera_orientation = orientation
        GL.camera_fov = fieldOfView

        def build_rotation_matrix(axis_angle):
            if not axis_angle or len(axis_angle) < 4:
                return
            ax, ay, az, theta = axis_angle
            c, s = math.cos(theta), math.sin(theta)
            n = math.sqrt(ax*ax + ay*ay + az*az) or 1.0
            ax, ay, az = ax/n, ay/n, az/n
            return np.array([
                [c + ax*ax*(1-c),   ax*ay*(1-c) - az*s, ax*az*(1-c) + ay*s, 0],
                [ay*ax*(1-c) + az*s, c + ay*ay*(1-c),   ay*az*(1-c) - ax*s, 0],
                [az*ax*(1-c) - ay*s, az*ay*(1-c) + ax*s, c + az*az*(1-c),   0],
                [0,                  0,                  0,                 1]
            ])
        
        def look_at(eye, target, up):
            f = np.array(target) - np.array(eye)
            f = f / (np.linalg.norm(f) or 1.0)
            right = np.cross(f, up)
            right = right / (np.linalg.norm(right) or 1.0)
            new_up = np.cross(f, right)

            view = np.identity(4)
            view[0, :3] = right
            view[1, :3] = new_up
            view[2, :3] = -f
            view[:3, 3] = -np.dot(view[:3, :3], np.array(eye))
            return view
        
        rot_matrix = build_rotation_matrix(orientation)
        forward_vec = (rot_matrix @ np.array([0, 0, -1, 0]))[:3]
        up_vec      = (rot_matrix @ np.array([0, 1,  0, 0]))[:3]

        eye = np.array(position)
        target = (eye + forward_vec).tolist()
        up_vec = up_vec.tolist()

        GL.view_matrix = look_at(eye, target, up_vec)

        # Projeção perspectiva
        aspect_ratio = GL.width / GL.height
        near_clip, far_clip = GL.near, GL.far
        fov_radians = fieldOfView if fieldOfView and fieldOfView <= math.pi else math.radians(fieldOfView or 60)
        scale = 1.0 / math.tan(fov_radians / 2)

        proj = np.zeros((4, 4))
        proj[0, 0] = scale / aspect_ratio
        proj[1, 1] = scale
        proj[2, 2] = (far_clip + near_clip) / (near_clip - far_clip)
        proj[2, 3] = (2 * far_clip * near_clip) / (near_clip - far_clip)
        proj[3, 2] = -1.0

        GL.projection_matrix = proj


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

        if not hasattr(GL, "model_matrix"):
            GL.model_matrix = np.identity(4)
        if not hasattr(GL, "matrix_stack"):
            GL.matrix_stack = []

        # Push current matrix
        GL.matrix_stack.append(GL.model_matrix.copy())

        T = np.identity(4)
        if translation:
            T[:3, 3] = translation[:3]

        S = np.identity(4)
        if scale:
            S[0,0], S[1,1], S[2,2] = scale

        def build_rotation_matrix(axis_angle):
            if not axis_angle or len(axis_angle) < 4:
                return np.identity(4)
            x, y, z, theta = axis_angle
            c, s = math.cos(theta), math.sin(theta)
            n = math.sqrt(x*x + y*y + z*z) or 1.0
            x, y, z = x/n, y/n, z/n
            return np.array([
                [c + x*x*(1-c),   x*y*(1-c) - z*s, x*z*(1-c) + y*s, 0],
                [y*x*(1-c) + z*s, c + y*y*(1-c),   y*z*(1-c) - x*s, 0],
                [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c),   0],
                [0,               0,               0,               1]
            ])

        R = build_rotation_matrix(rotation)

        # Compose new model matrix: parent * T * R * S
        GL.model_matrix = GL.model_matrix @ (T @ R @ S)

    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        if hasattr(GL, "matrix_stack") and GL.matrix_stack:
            GL.model_matrix = GL.matrix_stack.pop()
        else:
            GL.model_matrix = np.identity(4)

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

        if not point or len(point) < 9 or not stripCount or len(stripCount) < 1:
            return
        
        emissive_color = colors["emissiveColor"]

        index = 0
        for count in stripCount:
            if count < 3:
                index += count
                continue
            
            vertices = [GL._transform_vertex(point[i:i + 3]) for i in range(index * 3, (index + count) * 3, 3)]
            screen_coords = vertices

            for i in range(count - 2):
                if i % 2 == 0:
                    p0, p1, p2 = screen_coords[i], screen_coords[i+1], screen_coords[i+2]
                else:
                    p0, p1, p2 = screen_coords[i], screen_coords[i+2], screen_coords[i+1]
                
                GL._draw_inside_triangle(p0, p1, p2, emissive_color)
                GL._draw_line(p0, p1, emissive_color)
                GL._draw_line(p1, p2, emissive_color)
                GL._draw_line(p2, p0, emissive_color)

            index += count


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

        if not point or len(point) < 9 or not index or len(index) < 3:
            return
        
        emissive_color = colors["emissiveColor"]

        current_strip = []
        for idx in index:
            if idx == -1:
                if len(current_strip) >= 3:
                    vertices = [GL._transform_vertex(point[i:i + 3]) for i in current_strip]
                    screen_coords = vertices

                    for i in range(len(current_strip) - 2):
                        if i % 2 == 0:
                            p0, p1, p2 = screen_coords[i], screen_coords[i+1], screen_coords[i+2]
                        else:
                            p0, p1, p2 = screen_coords[i], screen_coords[i+2], screen_coords[i+1]
                        
                        GL._draw_inside_triangle(p0, p1, p2, emissive_color)
                        GL._draw_line(p0, p1, emissive_color)
                        GL._draw_line(p1, p2, emissive_color)
                        GL._draw_line(p2, p0, emissive_color)

                current_strip = []
            else:
                if 0 <= idx * 3 + 2 < len(point):
                    current_strip.append(idx * 3)

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#IndexedFaceSet
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim coord[0] é o valor
        # da coordenada x do primeiro ponto, coord[1] o valor y do primeiro ponto, coord[2]
        # o valor z da coordenada z do primeiro ponto. Já coord[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista de vértices é informada
        # em coordIndex, o valor -1 indica que a lista acabou.
        # A ordem de conexão não possui uma ordem oficial, mas em geral se o primeiro ponto com os dois
        # seguintes e depois este mesmo primeiro ponto com o terçeiro e quarto ponto. Por exemplo: numa
        # sequencia 0, 1, 2, 3, 4, -1 o primeiro triângulo será com os vértices 0, 1 e 2, depois serão
        # os vértices 0, 2 e 3, e depois 0, 3 e 4, e assim por diante, até chegar no final da lista.
        # Adicionalmente essa implementação do IndexedFace aceita cores por vértices, assim
        # se a flag colorPerVertex estiver habilitada, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.

        if not coord or not coordIndex:
            return
        
        # Load texture image once
        texture_img = None
        if current_texture and current_texture[0]:
            try:
                texture_img = gpu.GPU.load_texture(current_texture[0])
            except:
                texture_img = None

        # Unpack 3D coordinates into a list of vertices
        verts = [coord[i:i+3] for i in range(0, len(coord), 3)]
        
        # Unpack per-vertex colors if available
        vert_colors = None
        if colorPerVertex and color:
            vert_colors = [color[i:i+3] for i in range(0, len(color), 3)]

        # Unpack texture coordinates if available
        vert_tex_coords = None
        if texture_img and texCoord:
            vert_tex_coords = [texCoord[i:i+2] for i in range(0, len(texCoord), 2)]

        emissive_color = colors["emissiveColor"]
        default_color_tuple = [c * 255 for c in emissive_color]

        current_face_indices = []
        for idx in coordIndex:
            if idx == -1:
                if len(current_face_indices) >= 3:
                    # Triangulate the face using a "fan" pattern
                    p0_idx = current_face_indices[0]
                    for i in range(1, len(current_face_indices) - 1):
                        p1_idx = current_face_indices[i]
                        p2_idx = current_face_indices[i+1]

                        # Get screen positions
                        p0_screen = GL._transform_vertex(verts[p0_idx])
                        p1_screen = GL._transform_vertex(verts[p1_idx])
                        p2_screen = GL._transform_vertex(verts[p2_idx])
                        
                        # Get vertex colors for this triangle
                        c0, c1, c2 = None, None, None
                        if vert_colors and colorIndex:
                            # Using colorIndex to find the right color for each vertex
                            c0 = vert_colors[colorIndex[current_face_indices.index(p0_idx)]]
                            c1 = vert_colors[colorIndex[current_face_indices.index(p1_idx)]]
                            c2 = vert_colors[colorIndex[current_face_indices.index(p2_idx)]]
                        elif vert_colors: # If no colorIndex, assume 1-to-1 mapping
                             c0, c1, c2 = vert_colors[p0_idx], vert_colors[p1_idx], vert_colors[p2_idx]

                        # Get texture coordinates for this triangle
                        uv0, uv1, uv2 = None, None, None
                        if vert_tex_coords and texCoordIndex:
                            uv0 = vert_tex_coords[texCoordIndex[current_face_indices.index(p0_idx)]]
                            uv1 = vert_tex_coords[texCoordIndex[current_face_indices.index(p1_idx)]]
                            uv2 = vert_tex_coords[texCoordIndex[current_face_indices.index(p2_idx)]]
                        elif vert_tex_coords: # If no texCoordIndex, assume 1-to-1 mapping
                            uv0, uv1, uv2 = vert_tex_coords[p0_idx], vert_tex_coords[p1_idx], vert_tex_coords[p2_idx]

                        # Draw the triangle with all its data
                        GL._draw_inside_triangle_color_and_tex( p0_screen, p1_screen, p2_screen,
                                                                c0, c1, c2,
                                                                uv0, uv1, uv2,
                                                                texture_img, default_color_tuple)
                        
                        # Draw wireframe outline
                        GL._draw_line(p0_screen, p1_screen, emissive_color)
                        GL._draw_line(p1_screen, p2_screen, emissive_color)
                        GL._draw_line(p2_screen, p0_screen, emissive_color)

                current_face_indices = []
            else:
                current_face_indices.append(idx)

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Box
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Box : size = {0}".format(size)) # imprime no terminal pontos
        print("Box : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Sphere
        # A função sphere é usada para desenhar esferas na cena. O esfera é centrada no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da esfera que está sendo criada. Para desenha essa esfera você vai
        # precisar tesselar ela em triângulos, para isso encontre os vértices e defina
        # os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Sphere : radius = {0}".format(radius)) # imprime no terminal o raio da esfera
        print("Sphere : colors = {0}".format(colors)) # imprime no terminal as cores

    @staticmethod
    def cone(bottomRadius, height, colors):
        """Função usada para renderizar Cones."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Cone
        # A função cone é usada para desenhar cones na cena. O cone é centrado no
        # (0, 0, 0) no sistema de coordenadas local. O argumento bottomRadius especifica o
        # raio da base do cone e o argumento height especifica a altura do cone.
        # O cone é alinhado com o eixo Y local. O cone é fechado por padrão na base.
        # Para desenha esse cone você vai precisar tesselar ele em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Cone : bottomRadius = {0}".format(bottomRadius)) # imprime no terminal o raio da base do cone
        print("Cone : height = {0}".format(height)) # imprime no terminal a altura do cone
        print("Cone : colors = {0}".format(colors)) # imprime no terminal as cores

    @staticmethod
    def cylinder(radius, height, colors):
        """Função usada para renderizar Cilindros."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Cylinder
        # A função cylinder é usada para desenhar cilindros na cena. O cilindro é centrado no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da base do cilindro e o argumento height especifica a altura do cilindro.
        # O cilindro é alinhado com o eixo Y local. O cilindro é fechado por padrão em ambas as extremidades.
        # Para desenha esse cilindro você vai precisar tesselar ele em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Cylinder : radius = {0}".format(radius)) # imprime no terminal o raio do cilindro
        print("Cylinder : height = {0}".format(height)) # imprime no terminal a altura do cilindro
        print("Cylinder : colors = {0}".format(colors)) # imprime no terminal as cores

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
