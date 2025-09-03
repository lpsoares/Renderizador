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
    def polypoint2D(point, colors):
        """Função usada para renderizar Polypoint2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polypoint2D
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
        # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
        # você pode assumir inicialmente o desenho dos pontos com a cor emissiva (emissiveColor)
        emissive_color = colors.get("emissiveColor", [1.0, 1.0, 1.0])
        # Converte cor de (0,1) para (0,255)
        rgb = [int(c * 255) for c in emissive_color]
        for i in range(0, len(point), 2):
            x = int(point[i])
            y = int(point[i + 1])
            gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, rgb)
       
       
    @staticmethod
    def polyline2D(lineSegments, colors):
        """Função usada para renderizar Polyline2D."""
        emissive_color = colors.get("emissiveColor", [1.0, 1.0, 1.0])
        rgb = [int(c * 255) for c in emissive_color]

        def safe_draw_pixel(x, y, color):
            if 0 <= x < GL.width and 0 <= y < GL.height:
                gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

        def draw_line(x0, y0, x1, y1, color):
            # Bresenham com guarda de limites
            x0 = int(x0); y0 = int(y0); x1 = int(x1); y1 = int(y1)

            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            x, y = x0, y0
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1

            # caso degenerado: ponto único
            if dx == 0 and dy == 0:
                safe_draw_pixel(x, y, color)
                return

            if dx >= dy:
                err = dx // 2
                while x != x1:
                    safe_draw_pixel(x, y, color)
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
                safe_draw_pixel(x, y, color)  # último ponto
            else:
                err = dy // 2
                while y != y1:
                    safe_draw_pixel(x, y, color)
                    err -= dx
                    if err < 0:
                        x += sx
                        err += dy
                    y += sy
                safe_draw_pixel(x, y, color)  # último ponto

        for i in range(0, len(lineSegments) - 2, 2):
            x0 = lineSegments[i]
            y0 = lineSegments[i + 1]
            x1 = lineSegments[i + 2]
            y1 = lineSegments[i + 3]
            draw_line(x0, y0, x1, y1, rgb)

        

    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Circle2D
        # Nessa função você receberá um valor de raio e deverá desenhar o contorno de
        # um círculo.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Circle2D
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        emissive_color = colors.get("emissiveColor", [1.0, 1.0, 1.0])
        rgb = [int(c * 255) for c in emissive_color]
        cx = GL.width // 2
        cy = GL.height // 2
        num_segments = max(24, int(2 * math.pi * radius))  # ajusta para suavidade

        def draw_line(x0, y0, x1, y1, color):
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            x, y = x0, y0
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1

            if dx > dy:
                err = dx // 2
                while x != x1:
                    if 0 <= x < GL.width and 0 <= y < GL.height:
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
                if 0 <= x < GL.width and 0 <= y < GL.height:
                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)
            else:
                err = dy // 2
                while y != y1:
                    if 0 <= x < GL.width and 0 <= y < GL.height:
                        gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)
                    err -= dx
                    if err < 0:
                        x += sx
                        err += dy
                    y += sy
                if 0 <= x < GL.width and 0 <= y < GL.height:
                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

        # Desenha o círculo ponto a ponto
        for i in range(num_segments):
            theta1 = 2 * math.pi * i / num_segments
            theta2 = 2 * math.pi * (i + 1) / num_segments
            x0 = int(cx + radius * math.cos(theta1))
            y0 = int(cy + radius * math.sin(theta1))
            x1 = int(cx + radius * math.cos(theta2))
            y1 = int(cy + radius * math.sin(theta2))
            draw_line(x0, y0, x1, y1, rgb)

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
        fb_dim = (400, 600)  # ajuste conforme seu framebuffer
        emissive_color = colors.get("emissiveColor", [1.0, 1.0, 1.0])
        rgb = [int(c * 255) for c in emissive_color]

        h, w = fb_dim  # altura, largura

        def draw_pixel_safe(x, y, color):
            if 0 <= x < w and 0 <= y < h:
                gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

        def draw_line(x0, y0, x1, y1, color):
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            x, y = x0, y0
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            if dx > dy:
                err = dx // 2
                while x != x1:
                    draw_pixel_safe(x, y, color)
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
                draw_pixel_safe(x, y, color)
            else:
                err = dy // 2
                while y != y1:
                    draw_pixel_safe(x, y, color)
                    err -= dx
                    if err < 0:
                        x += sx
                        err += dy
                    y += sy
                draw_pixel_safe(x, y, color)

        def fill_triangle(v0, v1, v2, color):
            # Ordena vértices por y
            vertices_sorted = sorted([v0, v1, v2], key=lambda v: v[1])
            x0, y0 = vertices_sorted[0]
            x1, y1 = vertices_sorted[1]
            x2, y2 = vertices_sorted[2]

            def edge_interp(y, y0, x0, y1, x1):
                if y1 == y0:
                    return x0
                return int(x0 + (x1 - x0) * (y - y0) / (y1 - y0))

            for y in range(y0, y2 + 1):
                if y < y1:
                    xa = edge_interp(y, y0, x0, y1, x1)
                    xb = edge_interp(y, y0, x0, y2, x2)
                else:
                    xa = edge_interp(y, y1, x1, y2, x2)
                    xb = edge_interp(y, y0, x0, y2, x2)

                if xa > xb:
                    xa, xb = xb, xa
                for x in range(xa, xb + 1):
                    draw_pixel_safe(x, y, color)

        for i in range(0, len(vertices), 6):
            v0 = (int(vertices[i]), int(vertices[i+1]))
            v1 = (int(vertices[i+2]), int(vertices[i+3]))
            v2 = (int(vertices[i+4]), int(vertices[i+5]))

            # Preenche triângulo
            fill_triangle(v0, v1, v2, rgb)

            # Desenha bordas
            draw_line(*v0, *v1, rgb)
            draw_line(*v1, *v2, rgb)
            draw_line(*v2, *v0, rgb)



    @staticmethod
    def triangleSet(point, colors):
        """Desenha triângulos aplicando transformações acumuladas e z-buffer global."""
        rgb = [int(c*255) for c in colors.get("emissiveColor", [1.0, 1.0, 1.0])]
        w, h = GL.width, GL.height

        if not hasattr(GL, 'z_buffer'):
            GL.z_buffer = np.full((h, w), GL.far, dtype=float)

        def project_vertex(v):
            vec = np.array([v[0], v[1], v[2], 1.0])
            if hasattr(GL, 'transform_stack') and GL.transform_stack:
                vec = GL.transform_stack[-1] @ vec
            vec = GL.view_matrix @ vec
            vec = GL.projection_matrix @ vec
            if vec[3] != 0:
                vec /= vec[3]
            sx = int((vec[0]+1)*w/2)
            sy = int((1-vec[1])*h/2)
            sz = (vec[2]+1)/2
            return [sx, sy, sz]

        def safe_draw_pixel(x, y, z):
            if 0 <= x < w and 0 <= y < h:
                if z < GL.z_buffer[y, x]:
                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, rgb)
                    GL.z_buffer[y, x] = z

        def fill_triangle(v0, v1, v2):
            verts = sorted([v0, v1, v2], key=lambda v: v[1])
            x0, y0, z0 = verts[0]
            x1, y1, z1 = verts[1]
            x2, y2, z2 = verts[2]

            def edge_interp(y, y0, x0, y1, x1):
                if y1==y0: return x0
                return x0 + (x1-x0)*(y-y0)/(y1-y0)
            def z_interp(y, y0, z0, y1, z1):
                if y1==y0: return z0
                return z0 + (z1-z0)*(y-y0)/(y1-y0)

            for y in range(y0, y2+1):
                if y < y1:
                    xa = edge_interp(y, y0, x0, y1, x1)
                    xb = edge_interp(y, y0, x0, y2, x2)
                    za = z_interp(y, y0, z0, y1, z1)
                    zb = z_interp(y, y0, z0, y2, z2)
                else:
                    xa = edge_interp(y, y1, x1, y2, x2)
                    xb = edge_interp(y, y0, x0, y2, x2)
                    za = z_interp(y, y1, z1, y2, z2)
                    zb = z_interp(y, y0, z0, y2, z2)
                if xa > xb:
                    xa, xb = xb, xa
                    za, zb = zb, za
                for x in range(int(xa), int(xb)+1):
                    z = za + (zb-za)*(x-xa)/(xb-xa) if xb!=xa else za
                    safe_draw_pixel(x, y, z)

        # Cada 9 pontos forma um triângulo
        for i in range(0, len(point), 9):
            v0 = project_vertex(point[i:i+3])
            v1 = project_vertex(point[i+3:i+6])
            v2 = project_vertex(point[i+6:i+9])
            fill_triangle(v0, v1, v2)


    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """
        Define os parâmetros da câmera (viewpoint) e cria a matriz de projeção perspectiva.

        position: [x, y, z] posição da câmera no mundo
        orientation: [ax, ay, az, angle] rotação da câmera em torno do eixo (ax, ay, az) por 'angle' radianos
        fieldOfView: ângulo vertical em radianos
        """
        # Salva posição e orientação da câmera
        GL.camera_position = np.array(position, dtype=float)
        GL.camera_orientation = np.array(orientation, dtype=float)
        GL.fov = fieldOfView

        # Razão de aspecto da tela
        aspect = GL.width / GL.height
        near = GL.near
        far = GL.far
        f = 1 / math.tan(fieldOfView / 2)  # fator focal

        # Matriz de projeção perspectiva 4x4
        GL.projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ], dtype=float)

        # Matriz de visão (view matrix)
        # Convertendo orientação de eixo + ângulo para matriz de rotação
        ax, ay, az, angle = orientation
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1 - c
        R = np.array([
            [t*ax*ax + c,     t*ax*ay - s*az, t*ax*az + s*ay],
            [t*ax*ay + s*az, t*ay*ay + c,     t*ay*az - s*ax],
            [t*ax*az - s*ay, t*ay*az + s*ax, t*az*az + c]
        ], dtype=float)

        # Translacao inversa da camera
        T = np.eye(4)
        T[0:3, 3] = -GL.camera_position

        # View matrix 4x4
        GL.view_matrix = np.eye(4)
        GL.view_matrix[0:3, 0:3] = R.T  # transposta da rotação
        GL.view_matrix = GL.view_matrix @ T


    @staticmethod
    def transform_in(translation=None, scale=None, rotation=None):
        """
        Aplica uma transformação de modelo 3D (Transform node do X3D) usando matriz 4x4.

        translation: [x, y, z] deslocamento do objeto
        scale: [sx, sy, sz] escala do objeto
        rotation: [ax, ay, az, angle] rotação ao redor do eixo (ax, ay, az) por 'angle' radianos
        """
        # Matriz identidade 4x4
        M = np.eye(4, dtype=float)

        # Escala
        if scale:
            S = np.eye(4, dtype=float)
            S[0, 0] = scale[0]
            S[1, 1] = scale[1]
            S[2, 2] = scale[2]
            M = S @ M

        # Rotação
        if rotation:
            ax, ay, az, angle = rotation
            c = math.cos(angle)
            s = math.sin(angle)
            t = 1 - c
            R = np.array([
                [t*ax*ax + c,     t*ax*ay - s*az, t*ax*az + s*ay, 0],
                [t*ax*ay + s*az, t*ay*ay + c,     t*ay*az - s*ax, 0],
                [t*ax*az - s*ay, t*ay*az + s*ax, t*az*az + c,     0],
                [0, 0, 0, 1]
            ], dtype=float)
            M = R @ M

        # Translação
        if translation:
            T = np.eye(4, dtype=float)
            T[0, 3] = translation[0]
            T[1, 3] = translation[1]
            T[2, 3] = translation[2]
            M = T @ M

        # Se a pilha de transformações não existir, inicializa
        if not hasattr(GL, "transform_stack"):
            GL.transform_stack = []

        # Salva a transformação atual na pilha
        GL.transform_stack.append(M)

        # Matriz de modelagem atual
        GL.model_matrix = M



    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Saindo de Transform")

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
        print("TriangleStripSet : pontos = {0} ".format(point), end='')
        for i, strip in enumerate(stripCount):
            print("strip[{0}] = {1} ".format(i, strip), end='')
        print("")
        print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

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

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

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

        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedFaceSet : ")
        if coord:
            print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex))
        print("colorPerVertex = {0}".format(colorPerVertex))
        if colorPerVertex and color and colorIndex:
            print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex))
        if texCoord and texCoordIndex:
            print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex))
        if current_texture:
            image = gpu.GPU.load_texture(current_texture[0])
            print("\t Matriz com image = {0}".format(image))
            print("\t Dimensões da image = {0}".format(image.shape))
        print("IndexedFaceSet : colors = {0}".format(colors))  # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

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
