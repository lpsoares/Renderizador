#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: Henry Rocha e Rafael dos Santos.
Disciplina: Computação Gráfica
Data:
"""

import gpu          # Simula os recursos de uma GPU
import numpy as np

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
        GL.screen_mat = np.array([[width * 2 / 2,                        0, 0,  width * 2 / 2], 
                                  [            0,         - height * 2 / 2, 0, height * 2 / 2],
                                  [            0,                        0, 1,              0],
                                  [            0,                        0, 0,              1]])
        GL.framebuffer = np.zeros([width * 2, height * 2, 3], dtype=np.uint)

    @staticmethod
    def triangleSet(point, colors):
        """Função usada para renderizar TriangleSet."""
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
        # assim por diante.
        # No TriangleSet os triângulos são informados individualmente, assim os três
        # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
        # triângulo, e assim por diante.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        triangle_points = GL.prepare_points(point * 2)

        color_r = int(colors["diffuseColor"][0] * 255)
        color_g = int(colors["diffuseColor"][1] * 255)
        color_b = int(colors["diffuseColor"][2] * 255)
        color = (color_r, color_g, color_b)

        for i in range(0, len(triangle_points), 3):
            x0, y0 = int(triangle_points[i][0]), int(triangle_points[i][1])
            x1, y1 = int(triangle_points[i + 1][0]), int(triangle_points[i + 1][1])
            x2, y2 = int(triangle_points[i + 2][0]), int(triangle_points[i + 2][1])

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P0 -> P1.
            L0 = lambda x, y: (x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P1 -> P2.
            L1 = lambda x, y: (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P2 -> P0.
            L2 = lambda x, y: (x - x2) * (y0 - y2) - (y - y2) * (x0 - x2)

            # Determina se o ponto está dentro do triângulo ou não.
            inside = lambda x, y: L0(x, y) >= 0 and L1(x, y) >= 0 and L2(x, y) >= 0

            for si in range(GL.width * 2):
                for sj in range(GL.height * 2):
                    if inside(si + 0.5, sj + 0.5):
                        GL.framebuffer[si, sj] = color
            
        GL.supersampling_2x()

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        GL.fieldOfView = fieldOfView

        # Criando as matrizes de transformação da câmera de acordo com os dados coletados nesse frame.
        GL.trans_mat_cam= np.array([[1, 0, 0, position[0]],
                                    [0, 1, 0, position[1]],
                                    [0, 0, 1, position[2]],
                                    [0, 0, 0,          1]])

        if orientation:
            if (orientation[0] > 0):
                # Rotação em x
                GL.orient_mat_cam = np.array([[ 1,                      0,                       0, 0],
                                              [ 0, np.cos(orientation[3]), -np.sin(orientation[3]), 0],
                                              [ 0, np.sin(orientation[3]),  np.cos(orientation[3]), 0],
                                              [ 0,                      0,                       0, 1]])
            elif (orientation[1] > 0):
                # Rotação em y
                GL.orient_mat_cam = np.array([[  np.cos(orientation[3]), 0, np.sin(orientation[3]), 0],
                                              [                       0, 1,                      0, 0],
                                              [ -np.sin(orientation[3]), 0, np.cos(orientation[3]), 0],
                                              [                       0, 0,                      0, 1]])
            else:
                # Rotação em z     
                GL.orient_mat_cam = np.array([[ np.cos(orientation[3]), -np.sin(orientation[3]), 0, 0],
                                              [ np.sin(orientation[3]),  np.cos(orientation[3]), 0, 0],
                                              [                      0,                       0, 1, 0],
                                              [                      0,                       0, 0, 1]])

    @staticmethod
    def transform_in(translation, scale, rotation):
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo em alguma estrutura de pilha.

        # Criando as matrizes de transformação de acordo com os dados coletados nesse frame.
        if translation:
            GL.trans_mat = np.array([[1, 0, 0, translation[0]],
                                     [0, 1, 0, translation[1]],
                                     [0, 0, 1, translation[2]],
                                     [0, 0, 0,             1]])

        if scale:
            GL.scale_mat = np.array([[scale[0],        0,        0, 0],
                                     [       0, scale[1],        0, 0],
                                     [       0,        0, scale[2], 0],
                                     [       0,        0,        0, 1]])

        if rotation:
            if (rotation[0] > 0):
                # Rotação em x
                GL.rot_mat = np.array([[1,0,0,0],
                                      [ 0, np.cos(rotation[3]), -np.sin(rotation[3]), 0],
                                      [ 0, np.sin(rotation[3]),  np.cos(rotation[3]), 0],
                                      [ 0,                   0,                    0, 1]])
            elif (rotation[1] > 0):
                # Rotação em y
                GL.rot_mat = np.array([[  np.cos(rotation[3]), 0, np.sin(rotation[3]), 0],
                                       [                    0, 1,                   0, 0],
                                       [ -np.sin(rotation[3]), 0, np.cos(rotation[3]), 0],
                                       [                    0, 0,                   0, 1]])
            else:
                # Rotação em z     
                GL.rot_mat = np.array([[np.cos(rotation[3]), -np.sin(rotation[3]), 0, 0],
                                       [np.sin(rotation[3]),  np.cos(rotation[3]), 0, 0],
                                       [                  0,                    0, 1, 0],
                                       [                  0,                    0, 0, 1]])

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

        triangle_points = GL.prepare_points(point * 2)

        # print(f"triangleStripSet: {point}")
        # print(f"triangleStripSet: {stripCount}")

        color_r = int(colors["diffuseColor"][0] * 255)
        color_g = int(colors["diffuseColor"][1] * 255)
        color_b = int(colors["diffuseColor"][2] * 255)
        color = (color_r, color_g, color_b)

        for i in range(stripCount[0] - 2):                                            
            if i % 2 == 0:
                x0, y0 = int(triangle_points[i][0]), int(triangle_points[i][1])
                x1, y1 = int(triangle_points[i + 1][0]), int(triangle_points[i + 1][1])
                x2, y2 = int(triangle_points[i + 2][0]), int(triangle_points[i + 2][1])
            else:
                x2, y2 = int(triangle_points[i][0]), int(triangle_points[i][1])
                x1, y1 = int(triangle_points[i + 1][0]), int(triangle_points[i + 1][1])
                x0, y0 = int(triangle_points[i + 2][0]), int(triangle_points[i + 2][1])
            
            print(x0, y0, x1, y1, x2, y2)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P0 -> P1.
            L0 = lambda x, y: (x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P1 -> P2.
            L1 = lambda x, y: (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P2 -> P0.
            L2 = lambda x, y: (x - x2) * (y0 - y2) - (y - y2) * (x0 - x2)

            # Determina se o ponto está dentro do triângulo ou não.
            inside = lambda x, y: L0(x, y) >= 0 and L1(x, y) >= 0 and L2(x, y) >= 0

            for si in range(GL.width * 2):
                for sj in range(GL.height * 2):
                    if inside(si + 0.5, sj + 0.5):
                        GL.framebuffer[si, sj] = color
                        # gpu.GPU.set_pixel(si, sj, color_r, color_g, color_b)
            
        GL.supersampling_2x()

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Função usada para renderizar IndexedTriangleStripSet."""
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

        # # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        # print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores

        triangle_points = GL.prepare_points(point * 2)

        color_r = int(colors["diffuseColor"][0] * 255)
        color_g = int(colors["diffuseColor"][1] * 255)
        color_b = int(colors["diffuseColor"][2] * 255)
        color = (color_r, color_g, color_b)

        for i in range(len(index) - 3):
            if i % 2 == 0:
                x0, y0 = int(triangle_points[index[i]][0]), int(triangle_points[index[i]][1])
                x1, y1 = int(triangle_points[index[i + 1]][0]), int(triangle_points[index[i + 1]][1])
                x2, y2 = int(triangle_points[index[i + 2]][0]), int(triangle_points[index[i + 2]][1])
            else:
                x2, y2 = int(triangle_points[index[i]][0]), int(triangle_points[index[i]][1])
                x1, y1 = int(triangle_points[index[i + 1]][0]), int(triangle_points[index[i + 1]][1])
                x0, y0 = int(triangle_points[index[i + 2]][0]), int(triangle_points[index[i + 2]][1])
            
            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P0 -> P1.
            L0 = lambda x, y: (x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P1 -> P2.
            L1 = lambda x, y: (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

            # Calcula se o ponto (x, y) está acima, abaixo, ou na linha descrita por P2 -> P0.
            L2 = lambda x, y: (x - x2) * (y0 - y2) - (y - y2) * (x0 - x2)

            # Determina se o ponto está dentro do triângulo ou não.
            inside = lambda x, y: L0(x, y) >= 0 and L1(x, y) >= 0 and L2(x, y) >= 0

            for si in range(GL.width * 2):
                for sj in range(GL.height * 2):
                    if inside(si + 0.5, sj + 0.5):
                        GL.framebuffer[si, sj] = color
            
        # GL.supersampling_2x()

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        x = size[0]
        y = size[1]
        z = size[2]
        
        bottom_front_left  = (-x, -y,  z)
        bottom_front_right = ( x, -y,  z)
        bottom_back_left   = ( x,  y,  z)
        bottom_back_right  = (-x,  y,  z)
        top_front_left     = (-x,  y, -z)
        top_front_right    = ( x,  y, -z)
        top_back_left      = (-x, -y, -z)
        top_back_right     = ( x, -y, -z)

        point = np.array([
                bottom_front_left, bottom_front_right, bottom_back_left,
                bottom_back_left, bottom_back_right, bottom_front_left,

                top_back_left, bottom_front_left, bottom_back_right,
                bottom_back_right, top_front_left, top_back_left,
                
                top_back_right, top_back_left, top_front_left,
                top_front_left, top_front_right, top_back_right,
                
                top_back_right, top_front_right, bottom_front_right,
                bottom_front_right, top_front_right, bottom_back_left,
                
                top_front_right, top_front_left, bottom_back_right,
                bottom_back_right, bottom_back_left, top_front_right,
                
                top_back_right, top_back_left, bottom_front_left,
                bottom_front_left, bottom_front_right, top_back_right
        ]).flatten()
        
        GL.triangleSet(point, colors)

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
        # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
        # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista informando
        # como conectar os vértices é informada em coordIndex, o valor -1 indica que a lista
        # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante.
        # Adicionalmente essa implementação do IndexedFace suport cores por vértices, assim
        # a se a flag colorPerVertex estiver habilidades, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.

        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedFaceSet : ")
        if coord:
            print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex))
        if colorPerVertex:
            print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex))
        if texCoord:
            print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex))
        if current_texture:
            image = gpu.GPU.load_texture(current_texture[0])
            print("\t Matriz com image = {0}".format(image))
        print("IndexedFaceSet : colors = {0}".format(colors))  # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def view_point(fovx, near, far, width, height):
        fovy = 2 * np.arctan(np.tan(fovx / 2) * height / (height ** 2 + width ** 2)**0.5)
        top = near * np.tan(fovy)
        right = top * width / height

        return np.array([
            [near / right,          0,                              0,                                 0], 
            [           0, near / top,                              0,                                 0],
            [           0,          0, -((far + near) / (far - near)), ((- 2 * far * near)/(far - near))],
            [           0,          0,                             -1,                                 0]])

    @staticmethod
    def prepare_points(point):
        GL.mat_mundo: np.array = GL.trans_mat.dot(GL.rot_mat).dot(GL.scale_mat)
        GL.lookAt = np.linalg.inv(GL.orient_mat_cam).dot(np.linalg.inv(GL.trans_mat_cam))

        triangle_points = []
        for i in range(0, len(point), 3):
            current_point = np.array([[point[i]],
                                      [point[i + 1]],
                                      [point[i + 2]],
                                      [1]])

            # Transformação do ponto para coordenadas de tela
            current_point = GL.mat_mundo.dot(current_point)
            current_point = GL.lookAt.dot(current_point)

            # Leva o ponto para as coordenadas de perspectiva
            current_point = GL.view_point(GL.fieldOfView, GL.near, GL.far, GL.width * 2, GL.height * 2).dot(current_point)
            current_point /= current_point[3][0]
            current_point = GL.screen_mat.dot(current_point)
            triangle_points.append(current_point)
        
        return triangle_points

    @staticmethod
    def supersampling_2x():
        """
        Supersamples the framebuffer by 2x.
        """

        for i in range(0, GL.width * 2, 2):
            for j in range(0, GL.height * 2, 2):
                pixel1 = GL.framebuffer[    i,     j]
                pixel2 = GL.framebuffer[i + 1,     j]
                pixel3 = GL.framebuffer[    i, j + 1]
                pixel4 = GL.framebuffer[i + 1, j + 1]

                new_color = (pixel1 + pixel2 + pixel3 + pixel4) // 4

                if new_color[0] > 0 or new_color[1] > 0 or new_color[2] > 0:
                    gpu.GPU.set_pixel(int(i/2), int(j/2), new_color[0], new_color[1], new_color[2])
