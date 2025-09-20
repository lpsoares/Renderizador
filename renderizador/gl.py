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
    
    # Lighting system variables
    lights = []  # Lista de luzes direcionais
    headlight_enabled = True  # NavigationInfo headlight
    ambient_light = [0.2, 0.2, 0.2]  # Luz ambiente global

    @staticmethod
    def calculate_lighting(world_pos, normal, material):
        """Calcula a iluminação para um ponto usando o modelo de iluminação Phong."""
        if not normal or len(normal) != 3:
            return material.get("diffuseColor", [0.8, 0.8, 0.8])
        
        # Normaliza a normal
        norm_length = math.sqrt(sum(n*n for n in normal)) or 1.0
        normal = [n / norm_length for n in normal]
        
        # Extrai propriedades do material
        diffuse = material.get("diffuseColor", [0.8, 0.8, 0.8])
        specular = material.get("specularColor", [0.0, 0.0, 0.0])
        emissive = material.get("emissiveColor", [0.0, 0.0, 0.0])
        shininess = material.get("shininess", 0.2)
        ambient_intensity = material.get("ambientIntensity", 0.2)
        
        # Cor ambiente
        ambient = [ambient_intensity * diffuse[i] for i in range(3)]
        
        # Cor final acumulada
        final_color = [emissive[i] + ambient[i] for i in range(3)]
        
        # Calcular contribuição de cada luz
        for light in GL.lights:
            if light['type'] in ['directional', 'headlight']:
                # Direção da luz (para DirectionalLight é fixa, para headlight é a direção da câmera)
                light_dir = light['direction']
                if light['type'] == 'headlight' and hasattr(GL, 'view_matrix'):
                    # Transforma direção da luz pelo espaço da câmera
                    light_dir = [0.0, 0.0, -1.0]  # Sempre para frente na câmera
                
                # Produto escalar: normal . luz (máximo 0)
                dot_nl = max(0.0, sum(normal[i] * (-light_dir[i]) for i in range(3)))
                
                if dot_nl > 0:
                    # Componente difusa
                    diffuse_contrib = [
                        light['intensity'] * light['color'][i] * diffuse[i] * dot_nl
                        for i in range(3)
                    ]
                    
                    # Componente especular (se houver)
                    if any(s > 0 for s in specular) and shininess > 0:
                        # Direção da câmera (assumindo que está na origem para simplificar)
                        view_dir = [0.0, 0.0, 1.0]  # Direção padrão da câmera
                        
                        # Direção de reflexão: R = 2(N·L)N - L
                        reflect_dir = [
                            2 * dot_nl * normal[i] - (-light_dir[i])
                            for i in range(3)
                        ]
                        
                        # Produto escalar: R . V
                        dot_rv = max(0.0, sum(reflect_dir[i] * view_dir[i] for i in range(3)))
                        spec_factor = pow(dot_rv, shininess * 128)  # Shininess normalizado
                        
                        specular_contrib = [
                            light['intensity'] * light['color'][i] * specular[i] * spec_factor
                            for i in range(3)
                        ]
                        
                        # Adiciona contribuição especular
                        for i in range(3):
                            final_color[i] += specular_contrib[i]
                    
                    # Adiciona contribuição difusa
                    for i in range(3):
                        final_color[i] += diffuse_contrib[i]
        
        # Limita valores entre 0 e 1
        final_color = [max(0.0, min(1.0, c)) for c in final_color]
        return final_color

    @staticmethod
    def clear_lights():
        """Limpa todas as luzes da cena."""
        GL.lights = []

    @staticmethod
    def calculate_triangle_normal(v0, v1, v2):
        """Calcula a normal de um triângulo usando produto vetorial."""
        # Vetores das arestas
        edge1 = [v1[i] - v0[i] for i in range(3)]
        edge2 = [v2[i] - v0[i] for i in range(3)]
        
        # Produto vetorial edge1 x edge2
        normal = [
            edge1[1] * edge2[2] - edge1[2] * edge2[1],
            edge1[2] * edge2[0] - edge1[0] * edge2[2],
            edge1[0] * edge2[1] - edge1[1] * edge2[0]
        ]
        
        # Normaliza
        length = math.sqrt(sum(n*n for n in normal)) or 1.0
        return [n / length for n in normal]

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far
        # Reset lighting system for each scene
        GL.lights = []
        GL.headlight_enabled = True

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

        transp = colors.get("transparency", 0.0) if colors else 0.0

        def transform_vertex(v):
            # Retorna (x_screen, y_screen, z_ndc, inv_w)
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            w = vec[3] if vec[3] != 0 else 1.0
            inv_w = 1.0 / w
            # NDC
            x_ndc = vec[0] * inv_w
            y_ndc = vec[1] * inv_w
            z_ndc = vec[2] * inv_w  # assumindo z em [-1,1]
            x = int(round((1.0 - (x_ndc * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (y_ndc * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y, z_ndc, inv_w)

        def depth_test_and_write(x, y, z):
            try:
                current = gpu.GPU.read_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F)[0]
            except Exception:
                # depth buffer não alocado
                return True
            # Converter z_ndc [-1,1] para [0,1] (1 longe, 0 perto) assumindo clear_depth=1
            depth = (z + 1.0) * 0.5
            if depth < current:  # mais perto
                gpu.GPU.draw_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F, [depth])
                return True
            return False

        def blend(dst, src, alpha):
            return [int(src[i] * (1-alpha) + dst[i] * alpha) for i in range(3)]

        for i in range(0, len(point), 9):
            if i + 8 >= len(point):
                break
            v0 = [point[i], point[i+1], point[i+2]]
            v1 = [point[i+3], point[i+4], point[i+5]]
            v2 = [point[i+6], point[i+7], point[i+8]]
            
            # Calcula a normal do triângulo no espaço mundial
            triangle_normal = GL.calculate_triangle_normal(v0, v1, v2)
            
            # Transforma normal para o espaço mundial
            if hasattr(GL, 'model_matrix'):
                # Para transformar normais, usamos a transposta da inversa da matriz de modelo
                # Simplificação: assumimos que a matriz não tem escala não-uniforme
                normal_vec = np.array([triangle_normal[0], triangle_normal[1], triangle_normal[2], 0.0])
                world_normal = (GL.model_matrix @ normal_vec)[:3]
                norm_length = np.linalg.norm(world_normal) or 1.0
                triangle_normal = (world_normal / norm_length).tolist()
            
            # Calcula centro do triângulo para lighting
            center_world = [(v0[i] + v1[i] + v2[i]) / 3.0 for i in range(3)]
            if hasattr(GL, 'model_matrix'):
                center_vec = np.array([center_world[0], center_world[1], center_world[2], 1.0])
                center_world = (GL.model_matrix @ center_vec)[:3].tolist()
            
            # Calcula a cor usando lighting
            if GL.lights:  # Se há luzes na cena, usa lighting
                lit_color = GL.calculate_lighting(center_world, triangle_normal, colors)
                base_col = [max(0, min(255, int(c * 255))) for c in lit_color]
            else:  # Caso contrário, usa cor emissiva apenas
                emissive = colors.get("emissiveColor", [1.0, 1.0, 1.0]) if colors else [1.0, 1.0, 1.0]
                base_col = [max(0, min(255, int(c * 255))) for c in emissive]
            
            p0 = transform_vertex(v0)
            p1 = transform_vertex(v1)
            p2 = transform_vertex(v2)
            # Preenche o triângulo usando a regra Top-Left para evitar falhas nas bordas
            def draw_filled_triangle(p0, p1, p2):
                (x0, y0, z0, w0), (x1, y1, z1, w1), (x2, y2, z2, w2) = p0, p1, p2
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
                    z1, z2 = z2, z1
                    w1, w2 = w2, w1
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
                            # baricêntricas não normalizadas -> normalizar
                            wA = w0 / area
                            wB = w1 / area
                            wC = w2 / area
                            # perspective correct via 1/w
                            z_interp = wA * z0 + wB * z1 + wC * z2
                            if depth_test_and_write(x, y, z_interp):
                                final_col = base_col
                                if transp > 0.0:
                                    dst = gpu.GPU.read_pixel([x, y], gpu.GPU.RGB8)
                                    final_col = blend(dst, base_col, transp)
                                gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, final_col)
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

        # textura (opcional) com geração de mipmaps
        tex_faces = None
        mipmaps = None  # lista de níveis [level0, level1, ...]
        if current_texture and texCoord and texCoordIndex:
            try:
                base_img = gpu.GPU.load_texture(current_texture[0])
            except Exception:
                base_img = None
            if base_img is not None:
                # gera pirâmide até 1x1
                mipmaps = [base_img]
                lvl = 0
                current = base_img
                while current.shape[0] > 1 or current.shape[1] > 1:
                    h, w = current.shape[0], current.shape[1]
                    new_h = max(1, h // 2)
                    new_w = max(1, w // 2)
                    # média 2x2 simples (se ímpar, último pixel repete)
                    new_level = np.zeros((new_h, new_w, current.shape[2]), dtype=current.dtype)
                    for y in range(new_h):
                        for x in range(new_w):
                            block = current[y*2:min(h, y*2+2), x*2:min(w, x*2+2)]
                            new_level[y, x] = block.mean(axis=(0,1))
                    mipmaps.append(new_level)
                    current = new_level
                    lvl += 1
                # montar faces de UV
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
        transp = colors.get("transparency", 0.0) if colors else 0.0

        def transform_vertex(v):
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'model_matrix'):
                vec = GL.model_matrix @ vec
            if hasattr(GL, 'view_matrix'):
                vec = GL.view_matrix @ vec
            if hasattr(GL, 'projection_matrix'):
                vec = GL.projection_matrix @ vec
            w = vec[3] if vec[3] != 0 else 1.0
            inv_w = 1.0 / w
            x_ndc = vec[0] * inv_w
            y_ndc = vec[1] * inv_w
            z_ndc = vec[2] * inv_w
            x = int(round((1.0 - (x_ndc * 0.5 + 0.5)) * (GL.width - 1)))
            y = int(round((1.0 - (y_ndc * 0.5 + 0.5)) * (GL.height - 1)))
            return (x, y, z_ndc, inv_w)

        def choose_mip_level(uv0, uv1, uv2, p0, p1, p2):
            # Aproxima dU/dx, dV/dy via diferenças de tela -> heurística simples
            try:
                (x0, y0, *_), (x1, y1, *_), (x2, y2, *_) = p0, p1, p2
                du1 = uv1[0] - uv0[0]; dv1 = uv1[1] - uv0[1]
                du2 = uv2[0] - uv0[0]; dv2 = uv2[1] - uv0[1]
                dx1 = x1 - x0; dy1 = y1 - y0
                dx2 = x2 - x0; dy2 = y2 - y0
                # área em pixels
                area = abs(dx1*dy2 - dy1*dx2) + 1e-6
                # magnitude média de variação de UV
                du_avg = (abs(du1) + abs(du2)) * 0.5
                dv_avg = (abs(dv1) + abs(dv2)) * 0.5
                # estimativa粗: densidade de texels por pixel ~ (du_avg+dv_avg)/sqrt(area)
                density = (du_avg + dv_avg) / math.sqrt(area)
                level = max(0, math.log2(density * (mipmaps[0].shape[0] + mipmaps[0].shape[1]) * 0.25)) if density>0 else 0
                return int(min(level, len(mipmaps)-1))
            except Exception:
                return 0

        def sample_tex(u, v, level):
            if mipmaps is None:
                return emissive_col
            level = int(max(0, min(level, len(mipmaps)-1)))
            tex = mipmaps[level]
            h, w = tex.shape[0], tex.shape[1]
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
            xi = int(u * (w - 1))
            yi = int((1 - v) * (h - 1))
            px = tex[yi, xi]
            if len(px) >= 3:
                return [int(px[0]), int(px[1]), int(px[2])]
            return emissive_col

        def depth_test_and_write(x, y, z_ndc):
            try:
                current = gpu.GPU.read_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F)[0]
            except Exception:
                return True
            depth = (z_ndc + 1.0) * 0.5
            if depth < current:
                gpu.GPU.draw_pixel([x, y], gpu.GPU.DEPTH_COMPONENT32F, [depth])
                return True
            return False

        def blend(dst, src, alpha):
            return [int(src[i]*(1-alpha) + dst[i]*alpha) for i in range(3)]

        def draw_triangle(p0, p1, p2, c0, c1, c2, uv0, uv1, uv2):
            (x0, y0, z0, iw0), (x1, y1, z1, iw1), (x2, y2, z2, iw2) = p0, p1, p2
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
                z1, z2 = z2, z1
                iw1, iw2 = iw2, iw1
                c1, c2 = c2, c1
                uv1, uv2 = uv2, uv1
                den = -den

            topLeft0 = is_top_left(x1, y1, x2, y2)
            topLeft1 = is_top_left(x2, y2, x0, y0)
            topLeft2 = is_top_left(x0, y0, x1, y1)

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    px = x + 0.5
                    py = y + 0.5
                    e0 = edge(x1, y1, x2, y2, px, py)
                    e1 = edge(x2, y2, x0, y0, px, py)
                    e2 = edge(x0, y0, x1, y1, px, py)
                    if (e0 > 0 or (e0 == 0 and topLeft0)) and \
                       (e1 > 0 or (e1 == 0 and topLeft1)) and \
                       (e2 > 0 or (e2 == 0 and topLeft2)):
                        wA = e0 / den
                        wB = e1 / den
                        wC = e2 / den
                        # perspective correct usando 1/w
                        inv_wA = wA * iw0
                        inv_wB = wB * iw1
                        inv_wC = wC * iw2
                        sum_inv = inv_wA + inv_wB + inv_wC
                        if sum_inv == 0:
                            continue
                        inv_norm = 1.0 / sum_inv
                        z_interp = (z0*inv_wA + z1*inv_wB + z2*inv_wC) * inv_norm
                        if not depth_test_and_write(x, y, z_interp):
                            continue
                        if uv0 is not None and uv1 is not None and uv2 is not None and mipmaps is not None:
                            u = (uv0[0]*inv_wA + uv1[0]*inv_wB + uv2[0]*inv_wC) * inv_norm
                            v = (uv0[1]*inv_wA + uv1[1]*inv_wB + uv2[1]*inv_wC) * inv_norm
                            lvl = choose_mip_level(uv0, uv1, uv2, p0, p1, p2)
                            col_px = sample_tex(u, v, lvl)
                        elif c0 is not None and c1 is not None and c2 is not None:
                            R = (c0[0]*inv_wA + c1[0]*inv_wB + c2[0]*inv_wC) * inv_norm
                            G = (c0[1]*inv_wA + c1[1]*inv_wB + c2[1]*inv_wC) * inv_norm
                            B = (c0[2]*inv_wA + c1[2]*inv_wB + c2[2]*inv_wC) * inv_norm
                            col_px = [int(max(0, min(255, R*255))), int(max(0, min(255, G*255))), int(max(0, min(255, B*255)))]
                        else:
                            col_px = emissive_col
                        if transp > 0.0:
                            dst = gpu.GPU.read_pixel([x, y], gpu.GPU.RGB8)
                            col_px = blend(dst, col_px, transp)
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

        if not size or len(size) < 3:
            return
        
        sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
        
        # Vértices do cubo (8 vértices)
        vertices = [
            [-sx, -sy, -sz],  # 0: Bottom-left-back
            [ sx, -sy, -sz],  # 1: Bottom-right-back
            [ sx,  sy, -sz],  # 2: Top-right-back
            [-sx,  sy, -sz],  # 3: Top-left-back
            [-sx, -sy,  sz],  # 4: Bottom-left-front
            [ sx, -sy,  sz],  # 5: Bottom-right-front
            [ sx,  sy,  sz],  # 6: Top-right-front
            [-sx,  sy,  sz],  # 7: Top-left-front
        ]
        
        # Faces do cubo (12 triângulos, 2 por face)
        faces = [
            # Back face (z = -sz)
            [0, 2, 1], [0, 3, 2],
            # Front face (z = sz)
            [4, 5, 6], [4, 6, 7],
            # Left face (x = -sx)
            [0, 4, 7], [0, 7, 3],
            # Right face (x = sx)
            [1, 6, 5], [1, 2, 6],
            # Bottom face (y = -sy)
            [0, 1, 5], [0, 5, 4],
            # Top face (y = sy)
            [3, 6, 2], [3, 7, 6],
        ]
        
        # Converte as faces em uma lista de pontos para o triangleSet
        points = []
        for face in faces:
            for vertex_idx in face:
                points.extend(vertices[vertex_idx])
        
        # Chama triangleSet para renderizar
        GL.triangleSet(points, colors)

    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Sphere
        # A função sphere é usada para desenhar esferas na cena. O esfera é centrada no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da esfera que está sendo criada. Para desenha essa esfera você vai
        # precisar tesselar ela em triângulos, para isso encontre os vértices e defina
        # os triângulos.

        if not radius or radius <= 0:
            return
        
        # Parâmetros de tesselação
        latitudes = 16   # Divisões horizontais
        longitudes = 32  # Divisões verticais
        
        vertices = []
        
        # Gera vértices usando coordenadas esféricas
        for i in range(latitudes + 1):
            lat = math.pi * i / latitudes - math.pi / 2  # de -π/2 a π/2
            for j in range(longitudes):
                lng = 2 * math.pi * j / longitudes  # de 0 a 2π
                
                x = radius * math.cos(lat) * math.cos(lng)
                y = radius * math.sin(lat)
                z = radius * math.cos(lat) * math.sin(lng)
                vertices.append([x, y, z])
        
        # Gera triângulos
        points = []
        for i in range(latitudes):
            for j in range(longitudes):
                # Índices dos vértices para formar dois triângulos
                i0 = i * longitudes + j
                i1 = i * longitudes + (j + 1) % longitudes
                i2 = (i + 1) * longitudes + j
                i3 = (i + 1) * longitudes + (j + 1) % longitudes
                
                # Primeiro triângulo
                if i < latitudes:
                    points.extend(vertices[i0])
                    points.extend(vertices[i2])
                    points.extend(vertices[i1])
                
                # Segundo triângulo
                if i < latitudes:
                    points.extend(vertices[i1])
                    points.extend(vertices[i2])
                    points.extend(vertices[i3])
        
        # Chama triangleSet para renderizar
        GL.triangleSet(points, colors)

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

        if not bottomRadius or not height or bottomRadius <= 0 or height <= 0:
            return
        
        # Parâmetros de tesselação
        segments = 32  # Divisões circulares
        
        vertices = []
        
        # Vértice do topo do cone
        top_vertex = [0, height / 2, 0]
        
        # Vértices da base
        base_vertices = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = bottomRadius * math.cos(angle)
            z = bottomRadius * math.sin(angle)
            y = -height / 2
            base_vertices.append([x, y, z])
        
        # Centro da base
        base_center = [0, -height / 2, 0]
        
        points = []
        
        # Triângulos da lateral do cone
        for i in range(segments):
            i_next = (i + 1) % segments
            
            # Triângulo lateral
            points.extend(top_vertex)
            points.extend(base_vertices[i_next])
            points.extend(base_vertices[i])
        
        # Triângulos da base (fan triangulation)
        for i in range(segments):
            i_next = (i + 1) % segments
            
            # Triângulo da base
            points.extend(base_center)
            points.extend(base_vertices[i])
            points.extend(base_vertices[i_next])
        
        # Chama triangleSet para renderizar
        GL.triangleSet(points, colors)

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

        if not radius or not height or radius <= 0 or height <= 0:
            return
        
        # Parâmetros de tesselação
        segments = 32  # Divisões circulares
        
        vertices = []
        
        # Vértices do topo
        top_vertices = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = height / 2
            top_vertices.append([x, y, z])
        
        # Vértices da base
        bottom_vertices = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = -height / 2
            bottom_vertices.append([x, y, z])
        
        # Centros das faces
        top_center = [0, height / 2, 0]
        bottom_center = [0, -height / 2, 0]
        
        points = []
        
        # Triângulos da lateral do cilindro
        for i in range(segments):
            i_next = (i + 1) % segments
            
            # Primeiro triângulo da lateral
            points.extend(bottom_vertices[i])
            points.extend(top_vertices[i])
            points.extend(bottom_vertices[i_next])
            
            # Segundo triângulo da lateral
            points.extend(bottom_vertices[i_next])
            points.extend(top_vertices[i])
            points.extend(top_vertices[i_next])
        
        # Triângulos do topo (fan triangulation)
        for i in range(segments):
            i_next = (i + 1) % segments
            
            # Triângulo do topo
            points.extend(top_center)
            points.extend(top_vertices[i_next])
            points.extend(top_vertices[i])
        
        # Triângulos da base (fan triangulation)
        for i in range(segments):
            i_next = (i + 1) % segments
            
            # Triângulo da base
            points.extend(bottom_center)
            points.extend(bottom_vertices[i])
            points.extend(bottom_vertices[i_next])
        
        # Chama triangleSet para renderizar
        GL.triangleSet(points, colors)

    @staticmethod
    def navigationInfo(headlight):
        """Características físicas do avatar do visualizador e do modelo de visualização."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/navigation.html#NavigationInfo
        # O campo do headlight especifica se um navegador deve acender um luz direcional que
        # sempre aponta na direção que o usuário está olhando. Definir este campo como TRUE
        # faz com que o visualizador forneça sempre uma luz do ponto de vista do usuário.
        # A luz headlight deve ser direcional, ter intensidade = 1, cor = (1 1 1),
        # ambientIntensity = 0,0 e direção = (0 0 −1).

        GL.headlight_enabled = headlight
        
        if headlight:
            # Adiciona luz headlight (direção da câmera)
            headlight_info = {
                'type': 'headlight',
                'ambientIntensity': 0.0,
                'color': [1.0, 1.0, 1.0],
                'intensity': 1.0,
                'direction': [0.0, 0.0, -1.0]  # Direção da câmera
            }
            GL.lights.append(headlight_info)

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#DirectionalLight
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.

        # Normaliza a direção da luz
        dir_norm = np.linalg.norm(direction) or 1.0
        normalized_direction = [d / dir_norm for d in direction]
        
        # Armazena informações da luz direcional
        light_info = {
            'type': 'directional',
            'ambientIntensity': ambientIntensity,
            'color': color,
            'intensity': intensity,
            'direction': normalized_direction
        }
        
        # Adiciona à lista de luzes
        GL.lights.append(light_info)

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

        if not key or not keyValue or len(key) == 0:
            return [0.0, 0.0, 0.0]
        
        # Garante que set_fraction está no intervalo [0, 1]
        set_fraction = max(0.0, min(1.0, set_fraction))
        
        # Se só há uma chave, retorna o valor correspondente
        if len(key) == 1:
            return keyValue[0:3]
        
        # Encontra os índices das chaves para interpolação
        if set_fraction <= key[0]:
            return keyValue[0:3]
        if set_fraction >= key[-1]:
            return keyValue[-3:]  # Últimos 3 valores
        
        # Encontra o intervalo para interpolação
        for i in range(len(key) - 1):
            if key[i] <= set_fraction <= key[i + 1]:
                # Interpolação linear entre os dois pontos
                t = (set_fraction - key[i]) / (key[i + 1] - key[i])
                
                # Índices dos vetores 3D
                idx0 = i * 3
                idx1 = (i + 1) * 3
                
                # Interpolação linear de cada componente
                value_changed = [
                    keyValue[idx0] + t * (keyValue[idx1] - keyValue[idx0]),      # x
                    keyValue[idx0 + 1] + t * (keyValue[idx1 + 1] - keyValue[idx0 + 1]),  # y
                    keyValue[idx0 + 2] + t * (keyValue[idx1 + 2] - keyValue[idx0 + 2])   # z
                ]
                return value_changed
        
        return [0.0, 0.0, 0.0]

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

        if not key or not keyValue or len(key) == 0:
            return [0, 0, 1, 0]
        
        # Garante que set_fraction está no intervalo [0, 1]
        set_fraction = max(0.0, min(1.0, set_fraction))
        
        # Se só há uma chave, retorna o valor correspondente
        if len(key) == 1:
            return keyValue[0:4]
        
        # Encontra os índices das chaves para interpolação
        if set_fraction <= key[0]:
            return keyValue[0:4]
        if set_fraction >= key[-1]:
            return keyValue[-4:]  # Últimos 4 valores
        
        # Encontra o intervalo para interpolação
        for i in range(len(key) - 1):
            if key[i] <= set_fraction <= key[i + 1]:
                # Interpolação linear entre os dois quaternions/axis-angle
                t = (set_fraction - key[i]) / (key[i + 1] - key[i])
                
                # Índices dos eixos-ângulo (4 valores cada)
                idx0 = i * 4
                idx1 = (i + 1) * 4
                
                # Interpolação SLERP simplificada para axis-angle
                # Para simplicidade, fazemos interpolação linear dos componentes
                value_changed = [
                    keyValue[idx0] + t * (keyValue[idx1] - keyValue[idx0]),      # axis x
                    keyValue[idx0 + 1] + t * (keyValue[idx1 + 1] - keyValue[idx0 + 1]),  # axis y
                    keyValue[idx0 + 2] + t * (keyValue[idx1 + 2] - keyValue[idx0 + 2]),  # axis z
                    keyValue[idx0 + 3] + t * (keyValue[idx1 + 3] - keyValue[idx0 + 3])   # angle
                ]
                
                # Normaliza o eixo
                axis_length = math.sqrt(value_changed[0]**2 + value_changed[1]**2 + value_changed[2]**2)
                if axis_length > 0:
                    value_changed[0] /= axis_length
                    value_changed[1] /= axis_length
                    value_changed[2] /= axis_length
                
                return value_changed
        
        return [0, 0, 1, 0]

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
