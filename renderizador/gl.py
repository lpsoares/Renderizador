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
        # Estados que pertencem a um quadro/cena nova não devem vazar de uma
        # execução anterior do renderizador.
        GL.lights = []
        GL.headlight = True
        GL.time_sensor_states = {}
        GL.transform_matrix = np.identity(4)
        GL.transform_stack = []

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

        # Exemplo:
        pos_x = GL.width//2
        pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 0])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

        cores = []
        for c in colors["emissiveColor"]:
            cores.append(int(c*255))

        for i in range(0, len(point) // 2):
            i = i * 2
            px = int(point[i])
            py = int(point[i+1])
            gpu.GPU.draw_pixel([px, py], gpu.GPU.RGB8, cores)            
            

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

        print("Polyline2D : lineSegments = {0}".format(lineSegments)) # imprime no terminal
        print("Polyline2D : colors = {0}".format(colors)) # imprime no terminal as cores
        
        # Exemplo:
        # pos_x = GL.width//2
        # pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 255])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

        cores = []
        for c in colors['emissiveColor']:
            cores.append(int(c*255))

        for i in range(0, len(lineSegments) - 2, 2):
            x0, y0 = lineSegments[i], lineSegments[i + 1]
            x1, y1 = lineSegments[i + 2], lineSegments[i + 3]

            dx = x1 - x0
            dy = y1 - y0

            if abs(dx) >= abs(dy):
                if x0 > x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0

                s = (y1 - y0) / (x1 - x0)
                for u in range(int(x0), int(x1) + 1):
                    v = y0 + s * (u - x0)
                    try:
                        gpu.GPU.draw_pixel([u, int(v)], gpu.GPU.RGB8, cores)
                    except Exception:
                        pass

            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0

                s = (x1 - x0) / (y1 - y0)
                for u in range(int(y0), int(y1) + 1):
                    v = x0 + s * (u - y0)
                    try:
                        gpu.GPU.draw_pixel([int(v), u], gpu.GPU.RGB8, cores)
                    except Exception:
                        pass
                


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
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#TriangleSet2D
        # Nessa função você receberá os vertices de um triângulo no parâmetro vertices,
        # esses pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o
        # valor da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto.
        # Já point[2] é a coordenada x do segundo ponto e assim por diante. Assuma que a
        # quantidade de pontos é sempre multiplo de 3, ou seja, 6 valores ou 12 valores, etc.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet2D
        # você pode assumir inicialmente o desenho das linhas com a cor emissiva (emissiveColor).
        print("TriangleSet2D : vertices = {0}".format(vertices)) # imprime no terminal
        print("TriangleSet2D : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo:
        # gpu.GPU.draw_pixel([6, 8], gpu.GPU.RGB8, [255, 255, 0])  # altera pixel (u, v, tipo, r, g, b)

        cores = []
        for c in colors["emissiveColor"]:
            cores.append(int(c*255))

        def L(ax, ay, bx, by, x, y):
            return ((by - ay) * x
                    - (bx - ax) * y
                    + ay * (bx - ax)
                    - ax * (by - ay))
        
        for i in range(0, len(vertices), 6):

            x0 = vertices[i]
            y0 = vertices[i + 1]

            x1 = vertices[i + 2]
            y1 = vertices[i + 3]

            x2 = vertices[i + 4]
            y2 = vertices[i + 5]

            xmin = max(0, int(min(x0, x1, x2)))
            xmax = min(GL.width - 1, int(max(x0, x1, x2)))

            ymin = max(0, int(min(y0, y1, y2)))
            ymax = min(GL.height - 1, int(max(y0, y1, y2)))


            for px in range(xmin, xmax + 1):
                for py in range(ymin, ymax + 1):

                    sx = px + 0.5
                    sy = py + 0.5

                    l0 = L(x0, y0, x1, y1, sx, sy)
                    l1 = L(x1, y1, x2, y2, sx, sy)
                    l2 = L(x2, y2, x0, y0, sx, sy)

                    if ((l0 >= 0 and l1 >= 0 and l2 >= 0) or
                        (l0 <= 0 and l1 <= 0 and l2 <= 0)):

                        gpu.GPU.draw_pixel([px, py], gpu.GPU.RGB8, cores)

        


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

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        # O mesmo rasterizador é utilizado pelas geometrias indexadas. Assim
        # TriangleSet recebe também profundidade, materiais e iluminação.
        coord_index = []
        for first in range(0, len(point) // 3 - 2, 3):
            coord_index.extend((first, first + 1, first + 2, -1))

        if coord_index:
            GL.indexedFaceSet(point, coord_index, False, None, None,
                              None, None, colors, None)



    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        def rotation_matrix(x, y, z, angle):
            axis = np.array([x, y, z], dtype=float)
            norm = np.linalg.norm(axis)
            if norm > 1e-8:
                axis = axis / norm
            x, y, z = axis
            c, s, t = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
            R = np.identity(4)
            R[0, 0] = t*x*x + c
            R[0, 1] = t*x*y - s*z
            R[0, 2] = t*x*z + s*y
            R[1, 0] = t*x*y + s*z
            R[1, 1] = t*y*y + c
            R[1, 2] = t*y*z - s*x
            R[2, 0] = t*x*z - s*y
            R[2, 1] = t*y*z + s*x
            R[2, 2] = t*z*z + c
            return R

        T = np.identity(4)
        T[0, 3], T[1, 3], T[2, 3] = position[0], position[1], position[2]

        R = rotation_matrix(orientation[0], orientation[1], orientation[2], orientation[3])

        camera_matrix = T @ R

        # Guarda o estado como atributo dinâmico da classe GL
        setattr(GL, "view_matrix", np.linalg.inv(camera_matrix))
        setattr(GL, "camera_position", np.asarray(position, dtype=float))
        setattr(GL, "camera_direction", R[:3, :3] @ np.array([0.0, 0.0, -1.0]))

        aspect = GL.width / GL.height
        f = 1.0 / math.tan(fieldOfView / 2)
        near, far = GL.near, GL.far

        P = np.zeros((4, 4))
        P[0, 0] = f / aspect
        P[1, 1] = f
        P[2, 2] = (far + near) / (near - far)
        P[2, 3] = (2 * far * near) / (near - far)
        P[3, 2] = -1

        setattr(GL, "perspective_matrix", P)

    @staticmethod
    def transform_in(translation, scale, rotation):
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # ESSES NÃO SÃO OS VALORES DE QUATÉRNIOS AS CONTAS AINDA PRECISAM SER FEITAS.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo para depois potencialmente usar em outras chamadas. 
        # Quando começar a usar Transforms dentre de outros Transforms, mais a frente no curso
        # Você precisará usar alguma estrutura de dados pilha para organizar as matrizes.

        def rotation_matrix(x, y, z, angle):
            axis = np.array([x, y, z], dtype=float)
            norm = np.linalg.norm(axis)
            if norm > 1e-8:
                axis = axis / norm
            x, y, z = axis
            c, s, t = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
            R = np.identity(4)
            R[0, 0] = t*x*x + c
            R[0, 1] = t*x*y - s*z
            R[0, 2] = t*x*z + s*y
            R[1, 0] = t*x*y + s*z
            R[1, 1] = t*y*y + c
            R[1, 2] = t*y*z - s*x
            R[2, 0] = t*x*z - s*y
            R[2, 1] = t*y*z + s*x
            R[2, 2] = t*z*z + c
            return R

        T = np.identity(4)
        S = np.identity(4)
        R = np.identity(4)

        if translation is not None:
            T[0, 3], T[1, 3], T[2, 3] = translation[0], translation[1], translation[2]
        if scale is not None:
            S[0, 0], S[1, 1], S[2, 2] = scale[0], scale[1], scale[2]
        if rotation is not None:
            R = rotation_matrix(rotation[0], rotation[1], rotation[2], rotation[3])

        local = T @ R @ S

        current = np.asarray(getattr(GL, "transform_matrix", np.identity(4)), dtype=float)
        stack = getattr(GL, "transform_stack", None)
        if stack is None:
            stack = []
        stack.append(current.copy())
        setattr(GL, "transform_stack", stack)

        model = current @ local
        setattr(GL, "transform_matrix", model)

    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        stack = getattr(GL, "transform_stack", [])
        if stack:
            setattr(GL, "transform_matrix", stack.pop())
            setattr(GL, "transform_stack", stack)
        else:
            setattr(GL, "transform_matrix", np.identity(4))

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

        vertices = len(point) // 3
        coord_index = []
        first = 0
        for count in stripCount:
            count = int(count)
            last = min(first + max(count, 0), vertices)
            if last - first >= 3:
                faixa = list(range(first, last))
                for i in range(len(faixa) - 2):
                    # A orientação do winding alterna em uma triangle strip.
                    # Corrigi-la aqui mantém o mesmo lado da face iluminado.
                    if i % 2:
                        triangle = (faixa[i + 1], faixa[i], faixa[i + 2])
                    else:
                        triangle = (faixa[i], faixa[i + 1], faixa[i + 2])
                    coord_index.extend((*triangle, -1))
            first += max(count, 0)
            if first >= vertices:
                break

        if coord_index:
            GL.indexedFaceSet(point, coord_index, False, None, None,
                              None, None, colors, None)

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

        faixa = []
        coord_index = []
        for value in index:
            value = int(value)
            if value == -1:
                for i in range(len(faixa) - 2):
                    if i % 2:
                        triangle = (faixa[i + 1], faixa[i], faixa[i + 2])
                    else:
                        triangle = (faixa[i], faixa[i + 1], faixa[i + 2])
                    coord_index.extend((*triangle, -1))
                faixa = []
            else:
                faixa.append(value)
        for i in range(len(faixa) - 2):
            if i % 2:
                triangle = (faixa[i + 1], faixa[i], faixa[i + 2])
            else:
                triangle = (faixa[i], faixa[i + 1], faixa[i + 2])
            coord_index.extend((*triangle, -1))

        if coord_index:
            GL.indexedFaceSet(point, coord_index, False, None, None,
                              None, None, colors, None)

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

        if coord is None or coordIndex is None:
            return

        try:
            vertices = np.asarray(coord, dtype=float).reshape(-1, 3)
        except (TypeError, ValueError):
            return

        def split_indices(values):
            """Divide uma MFInt32 nos grupos separados por -1."""
            groups = []
            group = []
            if values is None:
                return groups
            for value in values:
                value = int(value)
                if value == -1:
                    if group:
                        groups.append(group)
                        group = []
                else:
                    group.append(value)
            if group:
                groups.append(group)
            return groups

        faces = split_indices(coordIndex)
        if not faces:
            return

        view = np.asarray(getattr(GL, "view_matrix", np.identity(4)), dtype=float)
        projection = np.asarray(getattr(GL, "perspective_matrix", np.identity(4)), dtype=float)
        model = np.asarray(getattr(GL, "transform_matrix", np.identity(4)), dtype=float)
        mvp = projection @ view @ model

        def normalize(vector, fallback=None):
            vector = np.asarray(vector, dtype=float)
            length = np.linalg.norm(vector)
            if length > 1e-12:
                return vector / length
            if fallback is None:
                return np.zeros_like(vector)
            return np.asarray(fallback, dtype=float)

        def project(vertex_index):
            if vertex_index < 0 or vertex_index >= len(vertices):
                return None
            local = np.array([*vertices[vertex_index], 1.0], dtype=float)
            world_h = model @ local
            if abs(world_h[3]) < 1e-12:
                return None
            world = world_h[:3] / world_h[3]
            clip = mvp @ local
            if not np.all(np.isfinite(clip)) or abs(clip[3]) < 1e-12:
                return None
            ndc = clip[:3] / clip[3]
            if not np.all(np.isfinite(ndc)) or ndc[2] < -1.0 or ndc[2] > 1.0:
                return None
            return {
                "screen": np.array([
                    (ndc[0] + 1.0) * 0.5 * GL.width,
                    (1.0 - ndc[1]) * 0.5 * GL.height,
                ]),
                "depth": float(ndc[2]),
                "world": world,
            }

        def edge(a, b, x, y):
            return (b[1] - a[1]) * x - (b[0] - a[0]) * y \
                   + a[1] * (b[0] - a[0]) - a[0] * (b[1] - a[1])

        def rgb(name, default):
            value = colors.get(name, default) if isinstance(colors, dict) else default
            try:
                value = np.asarray(value, dtype=float).reshape(-1)[:3]
            except (TypeError, ValueError):
                value = np.asarray(default, dtype=float)
            if len(value) != 3:
                value = np.asarray(default, dtype=float)
            return np.clip(value, 0.0, 1.0)

        material_diffuse = rgb("diffuseColor", [0.8, 0.8, 0.8])
        material_emissive = rgb("emissiveColor", [0.0, 0.0, 0.0])
        material_specular = rgb("specularColor", [0.0, 0.0, 0.0])
        try:
            material_ambient = float(colors.get("ambientIntensity", 0.2))
            material_shininess = float(colors.get("shininess", 0.2))
            transparency = float(colors.get("transparency", 0.0))
        except (AttributeError, TypeError, ValueError):
            material_ambient, material_shininess, transparency = 0.2, 0.2, 0.0
        material_ambient = min(max(material_ambient, 0.0), 1.0)
        material_shininess = min(max(material_shininess, 0.0), 1.0)
        opacity = 1.0 - min(max(transparency, 0.0), 1.0)

        try:
            color_values = np.asarray(color, dtype=float).reshape(-1, 3) if color is not None else None
        except (TypeError, ValueError):
            color_values = None

        try:
            tex_values = np.asarray(texCoord, dtype=float).reshape(-1, 2) if texCoord is not None else None
        except (TypeError, ValueError):
            tex_values = None

        color_groups = split_indices(colorIndex)
        tex_groups = split_indices(texCoordIndex)
        color_has_separators = colorIndex is not None and any(int(v) == -1 for v in colorIndex)
        tex_has_separators = texCoordIndex is not None and any(int(v) == -1 for v in texCoordIndex)
        color_stream = 0
        tex_stream = 0

        texture = None
        if current_texture:
            try:
                texture = gpu.GPU.load_texture(current_texture[0])
            except (OSError, IOError, IndexError, TypeError):
                texture = None

        def get_color(index):
            if color_values is None or index is None:
                return material_diffuse.copy()
            if 0 <= int(index) < len(color_values):
                return np.clip(color_values[int(index)], 0.0, 1.0)
            return material_diffuse.copy()

        def get_texcoord(index):
            if tex_values is None or index is None:
                return None
            if 0 <= int(index) < len(tex_values):
                return tex_values[int(index)]
            return None

        camera_position = np.asarray(
            getattr(GL, "camera_position", [0.0, 0.0, 0.0]), dtype=float
        )
        # O rasterizador já garante os limites dos pixels. Acesso direto aos
        # arrays evita a validação Python da GPU simulada para cada fragmento.
        framebuffer = gpu.GPU.frame_buffer[gpu.GPU.draw_framebuffer]
        color_buffer = framebuffer.color
        depth_buffer = framebuffer.depth
        lights = list(getattr(GL, "lights", []))
        if getattr(GL, "headlight", True):
            head_direction = getattr(GL, "camera_direction", [0.0, 0.0, -1.0])
            lights.insert(0, {
                "ambientIntensity": 0.0,
                "color": np.ones(3, dtype=float),
                "intensity": 1.0,
                "direction": normalize(head_direction, [0.0, 0.0, -1.0]),
            })

        def shade(base_color, normal, position):
            """Calcula emissiva + ambiente + difusa + especular por fragmento."""
            base_color = np.clip(np.asarray(base_color, dtype=float), 0.0, 1.0)
            normal = normalize(normal, [0.0, 0.0, 1.0])
            to_camera = normalize(camera_position - position, [0.0, 0.0, 1.0])

            # Como o rasterizador não faz descarte de back-face, usa a normal
            # do lado visível para obter o comportamento de uma superfície 2D.
            if np.dot(normal, to_camera) < 0.0:
                normal = -normal

            result = material_emissive.copy()
            exponent = max(1.0, material_shininess * 128.0)
            for light in lights:
                light_color = np.clip(np.asarray(light["color"], dtype=float), 0.0, 1.0)
                light_intensity = max(float(light["intensity"]), 0.0)
                light_direction = normalize(light["direction"], [0.0, 0.0, -1.0])
                to_light = -light_direction
                diffuse_factor = max(float(np.dot(normal, to_light)), 0.0)

                result += (base_color * light_color * light_intensity
                           * diffuse_factor)
                result += (base_color * light_color * light_intensity
                           * material_ambient
                           * min(max(float(light["ambientIntensity"]), 0.0), 1.0))

                if diffuse_factor > 0.0 and np.any(material_specular):
                    reflected = normalize(
                        2.0 * diffuse_factor * normal - to_light,
                        [0.0, 0.0, 1.0],
                    )
                    specular_factor = max(float(np.dot(reflected, to_camera)), 0.0)
                    result += (material_specular * light_color * light_intensity
                               * (specular_factor ** exponent))
            return np.clip(result, 0.0, 1.0)

        for face_number, face in enumerate(faces):
            if len(face) < 3:
                continue

            if colorPerVertex:
                if color_values is None:
                    face_color_indices = [None] * len(face)
                elif colorIndex is None:
                    face_color_indices = face[:]
                elif color_has_separators:
                    face_color_indices = (color_groups[face_number]
                                          if face_number < len(color_groups) else [])
                    if len(face_color_indices) < len(face):
                        face_color_indices += face[len(face_color_indices):]
                else:
                    face_color_indices = list(np.asarray(colorIndex, dtype=int)
                                              [color_stream:color_stream + len(face)])
                    color_stream += len(face)
                    if len(face_color_indices) < len(face):
                        face_color_indices += face[len(face_color_indices):]
            else:
                if color_values is None:
                    face_color_indices = [None] * len(face)
                elif colorIndex is None:
                    face_color_indices = [0] * len(face)
                elif color_has_separators:
                    selected = color_groups[face_number] if face_number < len(color_groups) else []
                    selected = selected[0] if selected else face_number
                    face_color_indices = [selected] * len(face)
                else:
                    selected = int(colorIndex[face_number]) if face_number < len(colorIndex) else face_number
                    face_color_indices = [selected] * len(face)

            if tex_values is None:
                face_tex_indices = [None] * len(face)
            elif texCoordIndex is None:
                face_tex_indices = face[:]
            elif tex_has_separators:
                face_tex_indices = (tex_groups[face_number]
                                    if face_number < len(tex_groups) else [])
                if len(face_tex_indices) < len(face):
                    face_tex_indices += face[len(face_tex_indices):]
            else:
                face_tex_indices = list(np.asarray(texCoordIndex, dtype=int)
                                        [tex_stream:tex_stream + len(face)])
                tex_stream += len(face)
                if len(face_tex_indices) < len(face):
                    face_tex_indices += face[len(face_tex_indices):]

            for corner in range(1, len(face) - 1):
                triangle = [0, corner, corner + 1]
                vertex_indices = [face[i] for i in triangle]
                projected = [project(index) for index in vertex_indices]
                if any(value is None for value in projected):
                    continue

                a, b, c = [vertex["screen"] for vertex in projected]
                area = edge(a, b, c[0], c[1])
                if abs(area) < 1e-12:
                    continue

                positions = np.asarray([vertex["world"] for vertex in projected])
                normal = np.cross(positions[1] - positions[0], positions[2] - positions[0])
                if np.linalg.norm(normal) < 1e-12:
                    continue
                vertex_colors = [get_color(face_color_indices[i]) for i in triangle]
                vertex_tex = [get_texcoord(face_tex_indices[i]) for i in triangle]
                has_texture_coords = texture is not None and all(value is not None for value in vertex_tex)

                xmin = max(0, int(math.floor(min(a[0], b[0], c[0]))))
                xmax = min(GL.width - 1, int(math.ceil(max(a[0], b[0], c[0]))))
                ymin = max(0, int(math.floor(min(a[1], b[1], c[1]))))
                ymax = min(GL.height - 1, int(math.ceil(max(a[1], b[1], c[1]))))

                for py in range(ymin, ymax + 1):
                    for px in range(xmin, xmax + 1):
                        sx, sy = px + 0.5, py + 0.5
                        weights = np.array([
                            edge(b, c, sx, sy),
                            edge(c, a, sx, sy),
                            edge(a, b, sx, sy),
                        ]) / area
                        if np.any(weights < -1e-9):
                            continue

                        fragment_depth = float(np.dot(
                            weights, [vertex["depth"] for vertex in projected]
                        ))
                        if fragment_depth < -1.0 or fragment_depth > 1.0:
                            continue
                        stored_depth = (float(depth_buffer[py, px, 0])
                                        if depth_buffer.size else 1.0)
                        if fragment_depth >= stored_depth - 1e-7:
                            continue

                        position = (weights[0] * positions[0]
                                    + weights[1] * positions[1]
                                    + weights[2] * positions[2])
                        base_color = (weights[0] * vertex_colors[0]
                                      + weights[1] * vertex_colors[1]
                                      + weights[2] * vertex_colors[2])
                        if has_texture_coords:
                            uv = (weights[0] * vertex_tex[0]
                                  + weights[1] * vertex_tex[1]
                                  + weights[2] * vertex_tex[2])
                            image_height, image_width = texture.shape[:2]
                            tx = min(image_width - 1, max(0, int(uv[0] * (image_width - 1))))
                            ty = min(image_height - 1, max(0, int((1.0 - uv[1]) * (image_height - 1))))
                            texel = np.asarray(texture[ty, tx], dtype=float).reshape(-1)[:3]
                            if len(texel) == 3:
                                if np.max(texel) > 1.0:
                                    texel /= 255.0
                                base_color *= texel

                        pixel_color = shade(base_color, normal, position)
                        destination = np.asarray(color_buffer[py, px], dtype=float)
                        blended = pixel_color * 255.0 * opacity \
                            + destination * (1.0 - opacity)
                        pixel = np.clip(np.rint(blended), 0, 255).astype(int).tolist()
                        color_buffer[py, px] = pixel
                        if opacity >= 0.999:
                            depth_buffer[py, px, 0] = fragment_depth

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

        # NavigationInfo é o primeiro nó renderizado em cada quadro. Portanto,
        # ele também delimita o estado das luzes do quadro anterior.
        setattr(GL, "headlight", bool(headlight))
        setattr(GL, "lights", [])

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#DirectionalLight
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.

        direction = np.asarray(direction, dtype=float).reshape(-1)[:3]
        if len(direction) != 3 or np.linalg.norm(direction) <= 1e-12:
            return

        # A direção pertence ao espaço local da luz. A transformação linear
        # atual permite que a rotina continue correta caso a luz esteja dentro
        # de um Transform.
        model = np.asarray(getattr(GL, "transform_matrix", np.identity(4)), dtype=float)
        direction = model[:3, :3] @ direction
        direction /= np.linalg.norm(direction)
        light_color = np.asarray(color, dtype=float).reshape(-1)[:3]
        if len(light_color) != 3:
            light_color = np.ones(3, dtype=float)

        lights = getattr(GL, "lights", None)
        if lights is None:
            lights = []
            setattr(GL, "lights", lights)
        lights.append({
            "ambientIntensity": float(ambientIntensity),
            "color": np.clip(light_color, 0.0, 1.0),
            "intensity": float(intensity),
            "direction": direction,
        })

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

        try:
            cycle_interval = float(cycleInterval)
        except (TypeError, ValueError):
            return 0.0
        if cycle_interval <= 0.0:
            return 0.0

        # O instante inicial fica associado aos parâmetros do sensor. Isso
        # evita que a fração dependa do horário do sistema e permite tratar
        # corretamente loop=false ao final do ciclo.
        states = getattr(GL, "time_sensor_states", {})
        key = (cycle_interval, bool(loop))
        if key not in states:
            states[key] = time.monotonic()
            setattr(GL, "time_sensor_states", states)

        elapsed = max(0.0, time.monotonic() - states[key])
        if loop:
            return (elapsed % cycle_interval) / cycle_interval
        return min(elapsed / cycle_interval, 1.0)

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

        try:
            keys = np.asarray(key, dtype=float).reshape(-1)
            values = np.asarray(keyValue, dtype=float).reshape(-1, 3)
            fraction = float(set_fraction)
        except (TypeError, ValueError):
            return [0.0, 0.0, 0.0]

        count = min(len(keys), len(values))
        if count == 0:
            return [0.0, 0.0, 0.0]
        if count == 1:
            return values[0].tolist()
        keys = keys[:count]
        values = values[:count]

        fraction = min(max(fraction, float(keys[0])), float(keys[-1]))
        segment = int(np.searchsorted(keys, fraction, side="right") - 1)
        segment = min(max(segment, 0), count - 2)
        left, right = float(keys[segment]), float(keys[segment + 1])
        parameter = 0.0 if right <= left else (fraction - left) / (right - left)

        is_closed = bool(closed) and np.allclose(values[0], values[-1])

        def control(index):
            if is_closed:
                return values[index % (count - 1)]
            return values[min(max(index, 0), count - 1)]

        p0 = control(segment - 1)
        p1 = control(segment)
        p2 = control(segment + 1)
        p3 = control(segment + 2)

        # Hermite/Catmull-Rom com tangentes centradas produz a transição
        # suave exigida pelo SplinePositionInterpolator.
        t = parameter
        t2, t3 = t * t, t * t * t
        tangent1 = 0.5 * (p2 - p0)
        tangent2 = 0.5 * (p3 - p1)
        result = ((2.0 * t3 - 3.0 * t2 + 1.0) * p1
                  + (t3 - 2.0 * t2 + t) * tangent1
                  + (-2.0 * t3 + 3.0 * t2) * p2
                  + (t3 - t2) * tangent2)
        return result.tolist()

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

        try:
            keys = np.asarray(key, dtype=float).reshape(-1)
            rotations = np.asarray(keyValue, dtype=float).reshape(-1, 4)
            fraction = float(set_fraction)
        except (TypeError, ValueError):
            return [0.0, 0.0, 1.0, 0.0]

        count = min(len(keys), len(rotations))
        if count == 0:
            return [0.0, 0.0, 1.0, 0.0]
        if count == 1:
            return rotations[0].tolist()
        keys = keys[:count]
        rotations = rotations[:count]
        fraction = min(max(fraction, float(keys[0])), float(keys[-1]))
        segment = int(np.searchsorted(keys, fraction, side="right") - 1)
        segment = min(max(segment, 0), count - 2)
        left, right = float(keys[segment]), float(keys[segment + 1])
        parameter = 0.0 if right <= left else (fraction - left) / (right - left)

        def normalize(vector, fallback=None):
            vector = np.asarray(vector, dtype=float)
            length = np.linalg.norm(vector)
            if length > 1e-12:
                return vector / length
            if fallback is None:
                return np.zeros_like(vector)
            return np.asarray(fallback, dtype=float)

        def quaternion(rotation):
            axis = normalize(rotation[:3], [0.0, 0.0, 1.0])
            half = float(rotation[3]) * 0.5
            return np.array([
                math.cos(half),
                axis[0] * math.sin(half),
                axis[1] * math.sin(half),
                axis[2] * math.sin(half),
            ])

        def axis_angle(quat):
            quat = quat / max(np.linalg.norm(quat), 1e-12)
            scalar = min(max(float(quat[0]), -1.0), 1.0)
            angle = 2.0 * math.acos(scalar)
            sine = math.sin(angle * 0.5)
            if abs(sine) <= 1e-8:
                return np.array([0.0, 0.0, 1.0, 0.0])
            return np.array([quat[1] / sine, quat[2] / sine,
                             quat[3] / sine, angle])

        first = quaternion(rotations[segment])
        second = quaternion(rotations[segment + 1])
        dot = float(np.dot(first, second))
        if dot < 0.0:
            second = -second
            dot = -dot

        if dot > 0.9995:
            interpolated = first + parameter * (second - first)
        else:
            angle = math.acos(min(max(dot, -1.0), 1.0))
            sine = math.sin(angle)
            interpolated = ((math.sin((1.0 - parameter) * angle) * first
                             + math.sin(parameter * angle) * second) / sine)
        return axis_angle(interpolated).tolist()

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
