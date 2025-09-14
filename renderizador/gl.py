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
    transform_stack = []  # pilha para transforms aninhados

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far

    @staticmethod
    def polypoint2D(point, colors):
        """Função usada para renderizar Polypoint2D."""
        # Conversão de cor emissiva (0..1) para (0..255)
        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        r, g, b = [max(0, min(255, int(c * 255))) for c in emissive]

        # Desenha cada ponto
        for i in range(0, len(point), 2):
            x = int(round(point[i]))
            y = int(round(point[i + 1]))
            if 0 <= x < GL.width and 0 <= y < GL.height:
                gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, [r, g, b])
        
    @staticmethod
    def polyline2D(lineSegments, colors):
        """Função usada para renderizar Polyline2D."""
        if len(lineSegments) < 4:
            return

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        col = [max(0, min(255, int(c * 255))) for c in emissive]

        # Converte lista em lista de pontos inteiros
        pts = []
        for i in range(0, len(lineSegments), 2):
            x = int(round(lineSegments[i]))
            y = int(round(lineSegments[i + 1]))
            pts.append((x, y))

        def draw_line(p0, p1):
            x0, y0 = p0
            x1, y1 = p1
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy
            while True:
                if 0 <= x0 < GL.width and 0 <= y0 < GL.height:
                    gpu.GPU.draw_pixel([x0, y0], gpu.GPU.RGB8, col)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy

        for i in range(len(pts) - 1):
            draw_line(pts[i], pts[i + 1])

    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Circle2D
        # Nessa função você receberá um valor de raio e deverá desenhar o contorno de
        # um círculo.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Circle2D
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        print("Circle2D : radius = {0}".format(radius)) # imprime no terminal
        print("Circle2D : colors = {0}".format(colors)) # imprime no terminal as cores
        
        # Exemplo:
        pos_x = GL.width//2
        pos_y = GL.height//2
        gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 255])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)


    @staticmethod
    def triangleSet2D(vertices, colors):
        """Função usada para renderizar TriangleSet2D."""
        if len(vertices) < 6:
            return

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        col = [max(0, min(255, int(c * 255))) for c in emissive]

        def draw_filled_triangle(p0, p1, p2):
            (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
            # reduzindo iterações
            min_x = max(0, min(x0, x1, x2))
            max_x = min(GL.width - 1, max(x0, x1, x2))
            min_y = max(0, min(y0, y1, y2))
            max_y = min(GL.height - 1, max(y0, y1, y2))

            # Área dupla do triângulo
            area = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
            if area == 0:
                return  # Dava errado

            # Pré-cálculo para incremento baricentrico
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    w0 = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
                    w1 = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
                    w2 = (x0 - x2) * (y - y2) - (y0 - y2) * (x - x2)
                    if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, col)

        # Percorre cada triângulo (3 vértices -> 6 valores)
        for i in range(0, len(vertices), 6):
            if i + 5 >= len(vertices):
                break
            p0 = (int(round(vertices[i])),     int(round(vertices[i + 1])))
            p1 = (int(round(vertices[i + 2])), int(round(vertices[i + 3])))
            p2 = (int(round(vertices[i + 4])), int(round(vertices[i + 5])))
            draw_filled_triangle(p0, p1, p2)
            

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

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        col = [max(0, min(255, int(c * 255))) for c in emissive]

        def transform_vertex(v):
            # v = [x, y, z]
            vec = np.array([v[0], v[1], v[2], 1.0])
            # Aplica modelo, visão e projeção
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            # Normaliza para NDC
            if vec[3] != 0:
                vec = vec / vec[3]
            # Converte para coordenadas de tela
            x = int(round((1.0 - (vec[0] * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (vec[1] * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y)

        for i in range(0, len(point), 9):
            if i + 8 >= len(point):
                break
            v0 = [point[i], point[i+1], point[i+2]]
            v1 = [point[i+3], point[i+4], point[i+5]]
            v2 = [point[i+6], point[i+7], point[i+8]]
            p0 = transform_vertex(v0)
            p1 = transform_vertex(v1)
            p2 = transform_vertex(v2)
            # Preenche o triângulo usando a regra Top-Left para evitar falhas nas bordas
            def draw_filled_triangle(p0, p1, p2):
                (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
                # Bounding box half-open [min, max)
                min_x = max(0, int(math.floor(min(x0, x1, x2))))
                max_x = min(GL.width, int(math.ceil(max(x0, x1, x2))) )
                min_y = max(0, int(math.floor(min(y0, y1, y2))))
                max_y = min(GL.height, int(math.ceil(max(y0, y1, y2))) )

                def edge(ax, ay, bx, by, px, py):
                    return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

                def is_top_left(ax, ay, bx, by):
                    dx = bx - ax
                    dy = by - ay
                    return (dy > 0) or (dy == 0 and dx < 0)

                area = edge(x0, y0, x1, y1, x2, y2)
                if area == 0:
                    return
                # Orientação consistente (CCW)
                if area < 0:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                    area = -area

                topLeft0 = is_top_left(x1, y1, x2, y2)
                topLeft1 = is_top_left(x2, y2, x0, y0)
                topLeft2 = is_top_left(x0, y0, x1, y1)

                eps = 0.0  # com amostragem no centro, não precisamos de epsilon
                for y in range(min_y, max_y):
                    for x in range(min_x, max_x):
                        px = x + 0.5
                        py = y + 0.5
                        w0 = edge(x1, y1, x2, y2, px, py)
                        w1 = edge(x2, y2, x0, y0, px, py)
                        w2 = edge(x0, y0, x1, y1, px, py)
                        if (w0 > eps or (w0 >= -eps and topLeft0)) and \
                           (w1 > eps or (w1 >= -eps and topLeft1)) and \
                           (w2 > eps or (w2 >= -eps and topLeft2)):
                            gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, col)
            draw_filled_triangle(p0, p1, p2)

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Coleta parâmetros do Viewpoint e monta as matrizes de câmera e projeção."""

        # guarda
        GL.camera_position = position
        GL.camera_orientation = orientation
        GL.camera_fov = fieldOfView

        # ----- axis-angle -> rotation matrix (reuses logic from transform_in) -----
        def axis_angle_to_matrix(ax):
            if not ax or len(ax) != 4:
                return np.identity(4)
            x, y, z, theta = ax
            c = math.cos(theta)
            s = math.sin(theta)
            n = math.sqrt(x*x + y*y + z*z) or 1.0
            x, y, z = x/n, y/n, z/n
            return np.array([
                [c + x*x*(1-c),     x*y*(1-c) - z*s, x*z*(1-c) + y*s, 0],
                [y*x*(1-c) + z*s,   c + y*y*(1-c),   y*z*(1-c) - x*s, 0],
                [z*x*(1-c) - y*s,   z*y*(1-c) + x*s, c + z*z*(1-c),   0],
                [0,                 0,               0,               1]
            ])

        # rotate default forward (-Z) and up (+Y)
        R = axis_angle_to_matrix(orientation)
        fwd = (R @ np.array([0, 0, -1, 0]))[:3]
        up  = (R @ np.array([0, 1,  0, 0]))[:3]
        eye = np.array(position)
        center = (eye + fwd).tolist()
        up = up.tolist()

        def look_at(eye, center, up):
            f = np.array(center) - np.array(eye)
            f = f / (np.linalg.norm(f) or 1.0)
            s = np.cross(up, f)
            s = s / (np.linalg.norm(s) or 1.0)
            u = np.cross(f, s)
            m = np.identity(4)
            m[0, :3] = s
            m[1, :3] = u
            m[2, :3] = -f
            m[:3, 3] = -np.dot(m[:3, :3], np.array(eye))
            return m

        GL.view_matrix = look_at(eye, center, up)

        # projeção
        aspect = GL.width / GL.height
        near, far = GL.near, GL.far
        fovy = fieldOfView if fieldOfView and fieldOfView <= math.pi else math.radians(fieldOfView or 60)
        f = 1.0 / math.tan(fovy / 2)
        proj = np.zeros((4, 4))
        proj[0, 0] = f / aspect
        proj[1, 1] = f
        proj[2, 2] = (far + near) / (near - far)
        proj[2, 3] = (2 * far * near) / (near - far)
        proj[3, 2] = -1.0
        GL.projection_matrix = proj
        
    @staticmethod
    def transform_in(translation, scale, rotation):
        """Empilha transform atual e aplica nova (suporte a transforms aninhados)."""
        # Monta T, R, S
        t = np.identity(4)
        if translation:
            t[:3, 3] = translation[:3]
        s_mat = np.identity(4)
        if scale:
            s_mat[0, 0] = scale[0]
            s_mat[1, 1] = scale[1]
            s_mat[2, 2] = scale[2]
        r_mat = np.identity(4)
        if rotation and len(rotation) == 4:
            x, y, z, theta = rotation
            c = math.cos(theta)
            s_ = math.sin(theta)
            n = math.sqrt(x*x + y*y + z*z) or 1.0
            x, y, z = x/n, y/n, z/n
            r_mat = np.array([
                [c + x*x*(1-c),     x*y*(1-c) - z*s_, x*z*(1-c) + y*s_, 0],
                [y*x*(1-c) + z*s_,  c + y*y*(1-c),    y*z*(1-c) - x*s_, 0],
                [z*x*(1-c) - y*s_,  z*y*(1-c) + x*s_, c + z*z*(1-c),    0],
                [0,                 0,               0,                1]
            ])
        local = t @ r_mat @ s_mat  # T * R * S
        prev = getattr(GL, 'model_matrix', np.identity(4))
        GL.transform_stack.append(prev)
        GL.model_matrix = prev @ local

    @staticmethod
    def transform_out():
        """Sai de um nó Transform: desempilha a matriz anterior."""
        if GL.transform_stack:
            GL.model_matrix = GL.transform_stack.pop()
        else:
            if hasattr(GL, 'model_matrix'):
                delattr(GL, 'model_matrix')

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        """Renderiza TriangleStripSet (tiras sequenciais de triângulos)."""
        if not point or not stripCount:
            return

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        col = [max(0, min(255, int(c * 255))) for c in emissive]

        # lista de vértices 3D
        verts = []
        for i in range(0, len(point), 3):
            verts.append([point[i], point[i+1], point[i+2]])

        def transform_vertex(v):
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            if vec[3] != 0:
                vec = vec / vec[3]
            x = int(round((1.0 - (vec[0] * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (vec[1] * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y)

        def fill_triangle(p0, p1, p2):
            (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
            min_x = max(0, int(math.floor(min(x0, x1, x2))))
            max_x = min(GL.width, int(math.ceil(max(x0, x1, x2))))
            min_y = max(0, int(math.floor(min(y0, y1, y2))))
            max_y = min(GL.height, int(math.ceil(max(y0, y1, y2))))

            def edge(ax, ay, bx, by, px, py):
                return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

            def is_top_left(ax, ay, bx, by):
                dx = bx - ax
                dy = by - ay
                return (dy > 0) or (dy == 0 and dx < 0)

            area = edge(x0, y0, x1, y1, x2, y2)
            if area == 0:
                return
            if area < 0:
                x1, y1, x2, y2 = x2, y2, x1, y1
                area = -area

            topLeft0 = is_top_left(x1, y1, x2, y2)
            topLeft1 = is_top_left(x2, y2, x0, y0)
            topLeft2 = is_top_left(x0, y0, x1, y1)

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    px = x + 0.5
                    py = y + 0.5
                    w0 = edge(x1, y1, x2, y2, px, py)
                    w1 = edge(x2, y2, x0, y0, px, py)
                    w2 = edge(x0, y0, x1, y1, px, py)
                    if (w0 > 0 or (w0 == 0 and topLeft0)) and \
                       (w1 > 0 or (w1 == 0 and topLeft1)) and \
                       (w2 > 0 or (w2 == 0 and topLeft2)):
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, col)

        base = 0
        for count in stripCount:
            if count < 3:
                base += count
                continue
            for i in range(count - 2):
                i0 = base + i
                i1 = base + i + 1
                i2 = base + i + 2
                if i % 2 == 0:
                    order = (i0, i1, i2)
                else:
                    order = (i1, i0, i2)
                p0 = transform_vertex(verts[order[0]])
                p1 = transform_vertex(verts[order[1]])
                p2 = transform_vertex(verts[order[2]])
                fill_triangle(p0, p1, p2)
            base += count

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Renderiza IndexedTriangleStripSet (-1 separa tiras)."""
        if not point or not index:
            return

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        col = [max(0, min(255, int(c * 255))) for c in emissive]

        verts = []
        for i in range(0, len(point), 3):
            verts.append([point[i], point[i+1], point[i+2]])

        def transform_vertex(v):
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            if vec[3] != 0:
                vec = vec / vec[3]
            x = int(round((1.0 - (vec[0] * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (vec[1] * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y)

        def fill_triangle(p0, p1, p2):
            (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
            min_x = max(0, int(math.floor(min(x0, x1, x2))))
            max_x = min(GL.width, int(math.ceil(max(x0, x1, x2))))
            min_y = max(0, int(math.floor(min(y0, y1, y2))))
            max_y = min(GL.height, int(math.ceil(max(y0, y1, y2))))

            def edge(ax, ay, bx, by, px, py):
                return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

            def is_top_left(ax, ay, bx, by):
                dx = bx - ax
                dy = by - ay
                return (dy > 0) or (dy == 0 and dx < 0)

            area = edge(x0, y0, x1, y1, x2, y2)
            if area == 0:
                return
            if area < 0:
                x1, y1, x2, y2 = x2, y2, x1, y1

            topLeft0 = is_top_left(x1, y1, x2, y2)
            topLeft1 = is_top_left(x2, y2, x0, y0)
            topLeft2 = is_top_left(x0, y0, x1, y1)

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    px = x + 0.5
                    py = y + 0.5
                    w0 = edge(x1, y1, x2, y2, px, py)
                    w1 = edge(x2, y2, x0, y0, px, py)
                    w2 = edge(x0, y0, x1, y1, px, py)
                    if (w0 > 0 or (w0 == 0 and topLeft0)) and \
                       (w1 > 0 or (w1 == 0 and topLeft1)) and \
                       (w2 > 0 or (w2 == 0 and topLeft2)):
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, col)

        current = []
        for idx in index:
            if idx == -1:
                if len(current) >= 3:
                    for i in range(len(current) - 2):
                        i0, i1, i2 = current[i], current[i+1], current[i+2]
                        order = (i0, i1, i2) if (i % 2 == 0) else (i1, i0, i2)
                        p0 = transform_vertex(verts[order[0]])
                        p1 = transform_vertex(verts[order[1]])
                        p2 = transform_vertex(verts[order[2]])
                        fill_triangle(p0, p1, p2)
                current = []
            else:
                if 0 <= idx < len(verts):
                    current.append(idx)
        if len(current) >= 3:
            for i in range(len(current) - 2):
                i0, i1, i2 = current[i], current[i+1], current[i+2]
                order = (i0, i1, i2) if (i % 2 == 0) else (i1, i0, i2)
                p0 = transform_vertex(verts[order[0]])
                p1 = transform_vertex(verts[order[1]])
                p2 = transform_vertex(verts[order[2]])
                fill_triangle(p0, p1, p2)

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Renderiza IndexedFaceSet triangulando em fan, com cores por vértice e textura simples."""
        if not coord or not coordIndex:
            return

        # vertices
        verts = []
        for i in range(0, len(coord), 3):
            verts.append([coord[i], coord[i+1], coord[i+2]])

        # faces como listas de índices, separadas por -1
        faces = []
        cur = []
        for idx in coordIndex:
            if idx == -1:
                if len(cur) >= 3:
                    faces.append(cur)
                cur = []
            else:
                if 0 <= idx < len(verts):
                    cur.append(idx)
        if len(cur) >= 3:
            faces.append(cur)

        # cores por vértice (opcional)
        face_colors = None
        if colorPerVertex and color and colorIndex:
            colors_list = []
            for i in range(0, len(color), 3):
                colors_list.append([color[i], color[i+1], color[i+2]])
            face_colors = []
            curc = []
            for ci in colorIndex:
                if ci == -1:
                    if len(curc) >= 3:
                        face_colors.append(curc)
                    curc = []
                else:
                    if 0 <= ci < len(colors_list):
                        curc.append(colors_list[ci])
            if len(curc) >= 3:
                face_colors.append(curc)
            if len(face_colors) != len(faces):
                face_colors = None

        # textura (opcional)
        tex_faces = None
        texture_img = None
        if current_texture and texCoord and texCoordIndex:
            try:
                texture_img = gpu.GPU.load_texture(current_texture[0])
            except Exception:
                texture_img = None
            if texture_img is not None:
                uv_list = []
                for i in range(0, len(texCoord), 2):
                    uv_list.append([texCoord[i], texCoord[i+1]])
                tex_faces = []
                curu = []
                for ti in texCoordIndex:
                    if ti == -1:
                        if len(curu) >= 3:
                            tex_faces.append(curu)
                        curu = []
                    else:
                        if 0 <= ti < len(uv_list):
                            curu.append(uv_list[ti])
                if len(curu) >= 3:
                    tex_faces.append(curu)
                if len(tex_faces) != len(faces):
                    tex_faces = None

        emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
        emissive_col = [max(0, min(255, int(c * 255))) for c in emissive]

        def transform_vertex(v):
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            if vec[3] != 0:
                vec = vec / vec[3]
            x = int(round((1.0 - (vec[0] * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (vec[1] * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y)

        def sample_tex(u, v):
            if texture_img is None:
                return emissive_col
            h, w = texture_img.shape[0], texture_img.shape[1]
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
            xi = int(u * (w - 1))
            yi = int((1 - v) * (h - 1))
            px = texture_img[yi, xi]
            if len(px) >= 3:
                return [int(px[0]), int(px[1]), int(px[2])]
            return emissive_col

        def draw_triangle(p0, p1, p2, c0, c1, c2, uv0, uv1, uv2):
            (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
            min_x = max(0, int(math.floor(min(x0, x1, x2))))
            max_x = min(GL.width, int(math.ceil(max(x0, x1, x2))))
            min_y = max(0, int(math.floor(min(y0, y1, y2))))
            max_y = min(GL.height, int(math.ceil(max(y0, y1, y2))))

            def edge(ax, ay, bx, by, px, py):
                return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

            def is_top_left(ax, ay, bx, by):
                dx = bx - ax
                dy = by - ay
                return (dy > 0) or (dy == 0 and dx < 0)

            den = edge(x0, y0, x1, y1, x2, y2)
            if den == 0:
                return
            if den < 0:
                x1, y1, x2, y2 = x2, y2, x1, y1
                den = -den

            topLeft0 = is_top_left(x1, y1, x2, y2)
            topLeft1 = is_top_left(x2, y2, x0, y0)
            topLeft2 = is_top_left(x0, y0, x1, y1)

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    px = x + 0.5
                    py = y + 0.5
                    w0 = edge(x1, y1, x2, y2, px, py)
                    w1 = edge(x2, y2, x0, y0, px, py)
                    w2 = edge(x0, y0, x1, y1, px, py)
                    if (w0 > 0 or (w0 == 0 and topLeft0)) and \
                       (w1 > 0 or (w1 == 0 and topLeft1)) and \
                       (w2 > 0 or (w2 == 0 and topLeft2)):
                        # baricêntricas normalizadas
                        wA = w0 / den
                        wB = w1 / den
                        wC = w2 / den
                        if uv0 is not None and uv1 is not None and uv2 is not None and texture_img is not None:
                            u = wA*uv0[0] + wB*uv1[0] + wC*uv2[0]
                            v = wA*uv0[1] + wB*uv1[1] + wC*uv2[1]
                            col_px = sample_tex(u, v)
                        elif c0 is not None and c1 is not None and c2 is not None:
                            R = wA*c0[0] + wB*c1[0] + wC*c2[0]
                            G = wA*c0[1] + wB*c1[1] + wC*c2[1]
                            B = wA*c0[2] + wB*c1[2] + wC*c2[2]
                            col_px = [int(max(0, min(255, R*255))), int(max(0, min(255, G*255))), int(max(0, min(255, B*255)))]
                        else:
                            col_px = emissive_col
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, col_px)

        for fi, face in enumerate(faces):
            base = face[0]
            for k in range(1, len(face) - 1):
                i0, i1, i2 = base, face[k], face[k+1]
                p0 = transform_vertex(verts[i0])
                p1 = transform_vertex(verts[i1])
                p2 = transform_vertex(verts[i2])
                c0 = c1 = c2 = None
                if face_colors and fi < len(face_colors):
                    fc = face_colors[fi]
                    try:
                        c0 = fc[ face.index(i0) ]
                        c1 = fc[ face.index(i1) ]
                        c2 = fc[ face.index(i2) ]
                    except Exception:
                        c0 = c1 = c2 = None
                uv0 = uv1 = uv2 = None
                if tex_faces and fi < len(tex_faces):
                    tf = tex_faces[fi]
                    try:
                        uv0 = tf[ face.index(i0) ]
                        uv1 = tf[ face.index(i1) ]
                        uv2 = tf[ face.index(i2) ]
                    except Exception:
                        uv0 = uv1 = uv2 = None
                draw_triangle(p0, p1, p2, c0, c1, c2, uv0, uv1, uv2)

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
