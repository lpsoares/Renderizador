#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: <SEU NOME AQUI>
Disciplina: Computação Gráfica
Data:
"""

import gpu          # Simula os recursos de uma GPU
import numpy as np
import math

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
        GL.screen = np.matrix([
            [width / 2, 0, 0, width / 2], 
            [0, - height / 2, 0, height / 2],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def inside(tri, x, y):
        # print(f'X:{x}, Y:{y}, TRI:{tri}')
        x+=0.5
        y+=0.5
        # x0, y0, z0 = tri[0], tri[1], tri[2]
        # x1, y1, z1 = tri[3], tri[4], tri[5]
        # x2, y2, z2 = tri[6], tri[7], tri[8]

        x0 = tri[0][0]
        y0 = tri[0][1]
        
        x1 = tri[1][0]
        y1 = tri[1][1]

        x2 = tri[2][0]
        y2 = tri[2][1]

        L1 = (y1-y0)*x - (x1-x0)*y + y0*(x1-x0) - x0*(y1-y0)
        L2 = (y2-y1)*x - (x2-x1)*y + y1*(x2-x1) - x1*(y2-y1)
        L3 = (y0-y2)*x - (x0-x2)*y + y2*(x0-x2) - x2*(y0-y2)

        # print(L1, L2, L3)

        return L1 >= 0 and L2 >= 0 and L3 >= 0 

    @staticmethod
    def transform_point(points):
        screen_points = []
        for i in range(0, len(points) - 2, 3):
            p = np.matrix([[points[i]], [points[i+1]], [points[i+2]], [1]])
            norm = GL.matrix_mvp.dot(p)
            norm = np.divide(norm, norm[3][0])
            screen_points += [GL.screen.dot(norm)]
        return screen_points

    @staticmethod
    def triangleSet(point, colors):
        print("roda triangleSet")
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

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos
        print("TriangleSet : colors = {0}".format(colors)) # imprime no terminal as cores
        # print(len(point))
        
        point = GL.transform_point(point)
        # print(point)

        for p in range(0, len(point)-2, 3):
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)
            
            tri = [
                [point[p][0],point[p][1]],
                [point[p+1][0],point[p+1][1]],
                [point[p+2][0],point[p+2][1]],
            ]

            for x in range(GL.width):
                for y in range(GL.height):
                    if GL.inside(tri, x ,y):
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

        # # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        print("roda view Point")

        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Viewpoint : ", end='')
        print("position = {0} ".format(position), end='')
        print("orientation = {0} ".format(orientation), end='')
        print("fieldOfView = {0} ".format(fieldOfView))

        fovy = 2 * math.atan(math.tan(fieldOfView / 2) * GL.height / math.sqrt(GL.height ** 2 + GL.width ** 2))
        top = GL.near * math.tan(fovy)
        right = top * GL.width / GL.height

        GL.perspectiva = np.matrix([
            [GL.near / right, 0, 0, 0], 
            [0, GL.near / top, 0, 0],
            [0, 0, -((GL.far + GL.near) / (GL.far - GL.near)), ((- 2 * GL.far * GL.near)/(GL.far - GL.near))],
            [0, 0, -1, 0]])

        translation_matrix = np.matrix([
            [1, 0, 0, position[0]], 
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ])

        translation_matrix_inv = np.linalg.inv(translation_matrix)

        if orientation:
            if (orientation[1] > 0):
                rotation_matrix = np.array([[np.cos(orientation[3]),0,np.sin(orientation[3]),0],
                                            [0,1,0,0],
                                            [-np.sin(orientation[3]),0,np.cos(orientation[3]),0],
                                            [0,0,0,1]])
            elif (orientation[0] > 0):
                rotation_matrix = np.array([[ 1,0,0,0],
                                            [ 0, np.cos(orientation[3]),-np.sin(orientation[3]),0],
                                            [ 0, np.sin(orientation[3]),np.cos(orientation[3]),0],
                                            [ 0,0,0,1]])
            else:     
                rotation_matrix = np.array([[np.cos(orientation[3]),-np.sin(orientation[3]),0,0],
                                            [np.sin(orientation[3]),np.cos(orientation[3]),0,0],
                                            [0,0,1,0],
                                            [0,0,0,1]])

            rotation_matrix_inv = np.linalg.inv(rotation_matrix)
        
        GL.lookat = rotation_matrix_inv.dot(translation_matrix_inv)



    @staticmethod
    def transform_in(translation, scale, rotation):
        print("roda transform in")

        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo em alguma estrutura de pilha.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Transform : ", end='')
        if translation:
            print("translation = {0} ".format(translation), end='') # imprime no terminal
        if scale:
            print("scale = {0} ".format(scale), end='') # imprime no terminal
        if rotation:
            print("rotation = {0} ".format(rotation), end='') # imprime no terminal
        print("")

        scale_matrix = np.matrix([
            [scale[0], 0, 0, 0], 
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]])

        translation_matrix = np.matrix([
            [1, 0, 0, translation[0]], 
            [0, 1, 0, translation[1]],
            [0, 0, 1, translation[2]],
            [0, 0, 0, 1]])


        if rotation:
            if (rotation[1] > 0):
                rotation_matrix = np.array([[  np.cos(rotation[3]), 0, np.sin(rotation[3]), 0],
                                            [0, 1,0, 0],
                                            [ -np.sin(rotation[3]), 0, np.cos(rotation[3]), 0],
                                            [0, 0,                      0, 1]])
            elif (rotation[0] > 0):
                rotation_matrix = np.array([[ 1,                      0,                       0, 0],
                                            [ 0, np.cos(rotation[3]), -np.sin(rotation[3]), 0],
                                            [ 0, np.sin(rotation[3]),  np.cos(rotation[3]), 0],
                                            [ 0,                      0,                       0, 1]])
            
            else:     
                rotation_matrix = np.array([[ np.cos(rotation[3]), -np.sin(rotation[3]), 0, 0],
                                            [ np.sin(rotation[3]),  np.cos(rotation[3]), 0, 0],
                                            [                      0,                       0, 1, 0],
                                            [0,0,0,1]])

        GL.model_world = translation_matrix.dot(rotation_matrix).dot(scale_matrix)
        GL.matrix_mvp = GL.perspectiva.dot(GL.lookat).dot(GL.model_world)


    @staticmethod
    def transform_out():
        print("roda tranform out")

        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Saindo de Transform")

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        print("roda triangleStripSet")

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

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("TriangleStripSet : pontos = {0} ".format(point), end='')
        # for i, strip in enumerate(stripCount):
        #     print("strip[{0}] = {1} ".format(i, strip), end='')
        # print("")
        # print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        point = GL.transform_point(point)
        tri = []
        for i in range(stripCount[0] - 2):
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)

            tri = [
                [point[i + 2][0], point[i + 2][1]],
                [point[i + 1][0], point[i + 1][1]], 
                [point[i][0], point[i][1]], 
            ]
            if i % 2 == 0: 
                tri = [
                    [point[i][0], point[i][1]], 
                    [point[i + 1][0], point[i + 1][1]], 
                    [point[i + 2][0], point[i + 2][1]], 
                    ]
            for x in range(GL.width):
                for y in range(GL.height):
                    if GL.inside(tri, x ,y):
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        print("roda indexedTriangleStripSet")

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

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        point = GL.transform_point(point)
        tri = []
        for i in range(len(index) - 3):
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)

            tri = [
                [point[index[i + 2]][0], point[index[i + 2]][1]], 
                [point[index[i + 1]][0], point[index[i + 1]][1]], 
                [point[index[i]][0], point[index[i]][1]], 
            ]
            if i % 2 == 0: 
                tri = [
                    [point[index[i]][0], point[index[i]][1]], 
                    [point[index[i + 1]][0], point[index[i + 1]][1]], 
                    [point[index[i + 2]][0], point[index[i + 2]][1]], 
                    ]
            for x in range(GL.width):
                for y in range(GL.height):
                    if GL.inside(tri, x ,y):
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

    @staticmethod
    def box(size, colors):
        print("roda box")

        """Função usada para renderizar Boxes."""
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
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        points = [-size[0], -size[1],  size[2], 
                   size[0], -size[1],  size[2], 
                   size[0],  size[1],  size[2], 
                  -size[0],  size[1],  size[2],
                  -size[0],  size[1], -size[2],
                   size[0],  size[1], -size[2],
                  -size[0], -size[1], -size[2],
                   size[0], -size[1], -size[2]]

        pontos = GL.transform_point(points)

        tri = [
                [pontos[1], pontos[7], pontos[5]], 
                [pontos[5], pontos[2], pontos[1]],
                [pontos[2], pontos[3], pontos[0]], 
                [pontos[0], pontos[1], pontos[2]],
                [pontos[3], pontos[2], pontos[5]], 
                [pontos[4], pontos[3], pontos[0]], 
                [pontos[5], pontos[4], pontos[3]], 
                [pontos[4], pontos[5], pontos[6]], 
                [pontos[6], pontos[4], pontos[0]], 
                [pontos[5], pontos[6], pontos[7]],
                [pontos[7], pontos[6], pontos[0]],
                [pontos[7], pontos[1], pontos[0]] 
                ]
        
        for t in tri:
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)
            for x in range(GL.width):
                for y in range(GL.height):
                    if GL.inside(t, x ,y):
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

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
