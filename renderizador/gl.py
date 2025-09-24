#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: André Corrêa Santos
Disciplina: Computação Gráfica
Data: 12/08/2024
"""

import time  # Para operações com tempo
import gpu  # Simula os recursos de uma GPU
import math  # Funções matemáticas
import numpy as np  # Biblioteca do Numpy


class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    perspective_matrix = np.mat([])
    transform_stack = []
    vertex_colors = []
    vertex_tex_coord = []
    texture = []

    width = 800  # largura da tela
    height = 600  # altura da tela
    near = 0.01  # plano de corte próximo
    far = 1000  # plano de corte distante

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far

    @staticmethod
    def polypoint2D(point: list[float], colors: dict[str, list[float]]) -> None:
        """Função usada para renderizar Polypoint2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polypoint2D
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
        # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
        # você pode assumir inicialmente o desenho dos pontos com a cor emissiva (emissiveColor).

        color = np.array(colors["emissiveColor"]) * 255

        for i in range(0, len(point), 2):
            x = int(point[i])
            y = int(point[i + 1])
            if (x <=GL.width and x >= 0) and (y <=GL.width and y >= 0):
                gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

    @staticmethod
    def polyline2D(lineSegments: list[float], colors: dict[str, list[float]]) -> None:
        """Função usada para renderizar Polyline2D."""

        color = np.array(colors["emissiveColor"]) * 255

        for i in range(0, len(lineSegments) - 2, 2):
            p0 = [lineSegments[i], lineSegments[i + 1]]
            p1 = [lineSegments[i + 2], lineSegments[i + 3]]

            if p0[0] > p1[0]:
                p0, p1 = p1, p0

            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]

            if dx != 0:  # evitar divisao por zero
                slope = dy / dx
            else:
                slope = 10**5  # caso divisao por zero chutar numero grande

            if np.abs(slope) <= 1:
                y = p0[1]

                for x in range(int((p0[0])), int((p1[0]))):
                    if (x <GL.width and x >= 0) and (y <GL.height and y >= 0):
                        gpu.GPU.draw_pixel([int(x), int((y))], gpu.GPU.RGB8, color)
                    y += slope
            else:
                if p0[1] > p1[1]:

                    p0, p1 = p1, p0

                slope = 1 / slope
                x = p0[0]
                for y in range(int((p0[1])), int((p1[1]))):
                    if (x <GL.width and x >= 0) and (y <GL.height and y >= 0):
                        gpu.GPU.draw_pixel([int((x)), int(y)], gpu.GPU.RGB8, color)
                    x += slope

    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""

        color = np.array(colors["emissiveColor"]) * 255.0

        tolerance = 20.0

        for x in range(0, GL.width):
            for y in range(0, GL.height):
                inPerimeter = abs((x) ** 2 + (y) ** 2  - radius**2) <= tolerance
                inScreen = (x >= 0 and x < GL.width) and (y >= 0 and y < GL.height)
                if inPerimeter and inScreen:

                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

    @staticmethod
    def triangleSet2D(vertices, colors):
        """Função usada para renderizar TriangleSet2D."""

        def insideTri(tri: list[float], x: float, y: float) -> bool:
            def line_eq(x0, y0, x1, y1, px, py):
                return (y1 - y0) * px - (x1 - x0) * py + y0 * (x1 - x0) - x0 * (y1 - y0)

            p1 = [tri[0], tri[1]]
            p2 = [tri[2], tri[3]]
            p3 = [tri[4], tri[5]]

            L1 = line_eq(p1[0], p1[1], p2[0], p2[1], x, y)
            L2 = line_eq(p2[0], p2[1], p3[0], p3[1], x, y)
            L3 = line_eq(p3[0], p3[1], p1[0], p1[1], x, y)

            if (L1 > 0 and L2 > 0 and L3 > 0) or (L1 < 0 and L2 < 0 and L3 < 0):
                return True
            return False

        if len(vertices) < 5:
            print("ERROR NO TRIANGLES SENT")

        print("vertices")
        print(len(vertices))
        


        color = np.array(colors["emissiveColor"]) * 255

        for i in range(0, len(vertices), 6):
            tri = vertices[i : i + 6]
            xs = [tri[j] for j in range(0, len(tri), 2)]
            ys = [tri[j] for j in range(1, len(tri), 2)]

            if(len(tri) != 6):
                return
            
            # Bounding Box
            box = [int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))]
            # Iterando na bounding Box
            for x in range(box[0], box[1] + 1):
                for y in range(box[2], box[3] + 1):
                    if insideTri(tri, x+0.5, y+0.5):
                        if (x <GL.width and x >= 0) and (y <GL.height and y >= 0):
                            # if(vertex_colors):
                            #     # interpolate position with vertex_colors to get the color
                            #     color = 
                            # if(vertex_tex_coords):
                            #     # interpolate position with the texture at each vertex to get the color
                            #     color = 
                            gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, color)

    @staticmethod
    def triangleSet(point, colors):
        """Função usada para renderizar TriangleSet."""
        
        # Helper function to multiply matrices
        def multiply_mats(mat_list):
            accumulator = np.identity(mat_list[0].shape[0])
            for mat in mat_list:
                accumulator = accumulator @ mat
            return accumulator

        # Helper function to transform 3D points to 2D
        def transform_points(points, min_x, min_y, min_z, max_z):
            w = GL.width
            h = GL.height
            delta_z = max_z - min_z

            screenMatrix = np.mat([
                [w / 2, 0.0, 0.0, min_x + w / 2],
                [0.0, -h / 2, 0.0, min_y + h / 2],
                [0.0, 0.0, delta_z, min_z],
                [0.0, 0.0, 0.0, 1.0]
            ])
            transformed_points = []
            for i in range(0, len(points), 3):
                p = points[i:i + 3]
                p.append(1.0)  # homogeneous coordinate

                # Apply all transformation matrices
                transform_mat_res = multiply_mats(GL.transform_stack)
                p = GL.perspective_matrix @ transform_mat_res @ p

                # Z-Divide
                p = np.array(p).flatten()
                p = p / p[-1]
                p = screenMatrix @ p

                p = np.array(p).flatten()
                transformed_points.append(p[0])
                transformed_points.append(p[1])

            return transformed_points

        # Transform the 3D points to 2D
        xs = [point[i] for i in range(0, len(point), 3)]
        ys = [point[i] for i in range(1, len(point), 3)]
        zs = [point[i] for i in range(2, len(point), 3)]

        vertices = transform_points(point, min(xs), min(ys), min(zs), max(zs))

        # Call triangleSet2D with the transformed 2D vertices
        GL.triangleSet2D(vertices, colors)


    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.

        #LÓGICA TRANSLAÇÕES E ROTAÇÕES LOOK AT
        cam_pos = np.matrix([
            [1.0,0.0,0.0,position[0]],
            [0.0,1.0,0.0,position[1]],
            [0.0,0.0,1.0,position[2]],
            [0.0,0.0,0.0,        1.0],
        ])
        
        x = orientation[0]
        y = orientation[1]
        z = orientation[2]
        t = orientation[3]
        sin_t = np.sin(t)
        cos_t = np.cos(t)
        sin_t = np.sin(t)

        rotation_m = np.mat([
            [cos_t + x**2 * (1 - cos_t), x * y * (1 - cos_t) - z * sin_t, x * z * (1 - cos_t) + y * sin_t, 0],
            [y * x * (1 - cos_t) + z * sin_t, cos_t + y**2 * (1 - cos_t), y * z * (1 - cos_t) - x * sin_t, 0],
            [z * x * (1 - cos_t) - y * sin_t, z * y * (1 - cos_t) + x * sin_t, cos_t + z**2 * (1 - cos_t), 0],
            [0, 0, 0, 1]
        ])

        look_at_trans =  np.linalg.inv(cam_pos)
        look_at_rot = np.linalg.inv(rotation_m)

        # TRANSLADANDO E DEPOIS ROTACIONANDO
        look_at_mat = look_at_rot@look_at_trans
        # print("look_at")
        # print(look_at_mat)
        # LÓGICA MATRIZ DE PROJEÇÃO
        aspect_ratio = GL.width/GL.height
        near = GL.near
        far = GL.far
        top = near * np.tan(fieldOfView / 2)
        right = top * aspect_ratio

        perspective_m = np.matrix([
            [near / right, 0.0, 0.0, 0.0],
            [0.0, near / top, 0.0, 0.0],
            [0.0, 0.0, -(far + near) / (far - near), -2.0 * (far * near) / (far - near)],
            [0.0, 0.0, -1.0, 0.0],
        ])

        # retornando matriz que aplica LOOK_AT e projeção perspectiva
        # print("perspective")
        # print(perspective_m)

        GL.perspective_matrix = perspective_m @ look_at_mat




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

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        
        scale_m = np.mat([
            [scale[0],0.0,0.0,0.0],
            [0.0,scale[1],0.0,0.0],
            [0.0,0.0,scale[2],0.0],
            [0.0,0.0,0.0,1.0]
            ]
        )
        translation_m = np.mat([
            [1.0,0.0,0.0,translation[0]],
            [0.0,1.0,0.0,translation[1]],
            [0.0,0.0,1.0,translation[2]],
            [0.0,0.0,0.0,1.0],
            ]
        )
        x = rotation[0]
        y = rotation[1]
        z = rotation[2]
        t = rotation[3]
        sin_t = np.sin(t)
        cos_t = np.cos(t)
        sin_t = np.sin(t)

        rotation_m = np.mat([
            [cos_t + x**2 * (1 - cos_t), x * y * (1 - cos_t) - z * sin_t, x * z * (1 - cos_t) + y * sin_t, 0],
            [y * x * (1 - cos_t) + z * sin_t, cos_t + y**2 * (1 - cos_t), y * z * (1 - cos_t) - x * sin_t, 0],
            [z * x * (1 - cos_t) - y * sin_t, z * y * (1 - cos_t) + x * sin_t, cos_t + z**2 * (1 - cos_t), 0],
            [0, 0, 0, 1]
        ])
        object_to_world_m = translation_m  @ rotation_m @ scale_m
        # print("model")
        # print(object_to_world_m)
        GL.transform_stack.append(object_to_world_m)


    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO. # Referência à variável global
        if len(GL.transform_stack)>0:
            GL.transform_stack.pop()  # Modificação da lista global


    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        """Função usada para renderizar TriangleStripSet."""
        vertices = []                      
        for i in range(0,len(point)-6,3): #
            for u in range(0,9): # appending each vertex, 3 vertices
                vertices.append(point[i+u])

        GL.triangleSet(vertices,colors)

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Função usada para renderizar IndexedTriangleStripSet."""

        def appendVertices(points, vertices, idx):
            coord = idx * 3
            for u in range(3): 
                vertices.append(points[coord + u])

        vertices = []
        i = 0

        while i < len(index) - 2:
            if index[i] == -1 or index[i + 1] == -1 or index[i + 2] == -1:
                i += 1 # pulando indices -1
                continue

            
            appendVertices(point, vertices, index[i])     # Vertex 1
            appendVertices(point, vertices, index[i + 1]) # Vertex 2
            appendVertices(point, vertices, index[i + 2]) # Vertex 3

            i += 1 

        GL.triangleSet(vertices, colors)


    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Box : size = {0}".format(size))  # imprime no terminal pontos
        print("Box : colors = {0}".format(colors))  # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def indexedFaceSet(
        coord,
        coordIndex,
        colorPerVertex,
        color,
        colorIndex,
        texCoord,
        texCoordIndex,
        colors,
        current_texture,
    ):
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

        def appendVertices(points, vertices, index):
            coord_idx = index * 3
            for u in range(3):
                vertices.append(points[coord_idx + u])

        vertices = []
        vertex_colors = []
        vertex_tex_coords = []


        texture = []
        print("PASSOU")
        if current_texture:
            texture = gpu.GPU.load_texture(current_texture[0])
            GL.texture = texture

        for i in range(len(coordIndex)):
            if coordIndex[i] == -1:
                if len(vertices) >= 9:
                    GL.vertex_colors = vertex_colors
                    GL.vertex_tex_coord = vertex_tex_coords
                    GL.triangleSet(vertices, colors)
                vertices = []
                vertex_colors = []
                vertex_tex_coords = []
            else:
                appendVertices(coord, vertices, coordIndex[i])

                if colorPerVertex and color and colorIndex:
                    vertex_color_idx = colorIndex[i] * 3
                    vertex_color = color[vertex_color_idx : vertex_color_idx + 3]
                    vertex_colors.append(vertex_color)

                if texCoord and texCoordIndex:
                    tex_coord_idx = texCoordIndex[i] * 2
                    tex_u, tex_v = texCoord[tex_coord_idx], texCoord[tex_coord_idx + 1]
                    vertex_tex_coords.append([tex_u, tex_v])

        if len(vertices) >= 9:
            GL.triangleSet(vertices, colors, vertex_colors, vertex_tex_coords, texture)




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
        print(
            "Sphere : radius = {0}".format(radius)
        )  # imprime no terminal o raio da esfera
        print("Sphere : colors = {0}".format(colors))  # imprime no terminal as cores

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
        print(
            "NavigationInfo : headlight = {0}".format(headlight)
        )  # imprime no terminal

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
        print("DirectionalLight : color = {0}".format(color))  # imprime no terminal
        print(
            "DirectionalLight : intensity = {0}".format(intensity)
        )  # imprime no terminal
        print(
            "DirectionalLight : direction = {0}".format(direction)
        )  # imprime no terminal

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
        print("PointLight : color = {0}".format(color))  # imprime no terminal
        print("PointLight : intensity = {0}".format(intensity))  # imprime no terminal
        print("PointLight : location = {0}".format(location))  # imprime no terminal

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
        print("Fog : color = {0}".format(color))  # imprime no terminal
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
        print(
            "TimeSensor : cycleInterval = {0}".format(cycleInterval)
        )  # imprime no terminal
        print("TimeSensor : loop = {0}".format(loop))

        # Esse método já está implementado para os alunos como exemplo
        epoch = (
            time.time()
        )  # time in seconds since the epoch as a floating point number.
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
        print(
            "SplinePositionInterpolator : key = {0}".format(key)
        )  # imprime no terminal
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
        print("OrientationInterpolator : key = {0}".format(key))  # imprime no terminal
        print("OrientationInterpolator : keyValue = {0}".format(keyValue))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0, 0, 1, 0]

        return value_changed

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
