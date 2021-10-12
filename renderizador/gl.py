#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: Gustavo Braga
Disciplina: Computação Gráfica
Data: 13 de setembro de 2021
"""

import gpu
import utils
import numpy as np

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante
    sampling_X_ = 2
    
    eye = None
    mvp = None
    orientation = None
    view_to_point = None
    world_to_view = None
    point_to_screen = None
    transformation_matrix_stack = None
    model_to_world = []

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Define parametros para câmera de razão de aspecto, plano próximo e distante."""
        print("\n=== Rasterizer Setup ===")
        
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far

        try:
            s = int(input("\nSampling nXn: (ex: 2 is 2x2, 3 is 3x3, ...)\nDefault is 2x2, press enter to use default.\n"))
            GL.sampling_X_ = s

        except: 
            print("Using default 2x2 sampling")

        print("Sampling: " + str(GL.sampling_X_) + "X" + str(GL.sampling_X_))

        utils.Rasterizer.setup(gpu.GPU, GL.width, GL.height, GL.sampling_X_, True)
        GL.point_to_screen = utils.point_screen(width, height)
        print("\n======================================================================")

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        print("\n=== Viewpoint ===")
        GL.view_to_point = utils.view_point(fieldOfView, GL.near, GL.far, GL.width, GL.height)
        GL.world_to_view = utils.world_view_lookat_simple(position, orientation)

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

        print("\n=== Transform in ===")
        GL.transformation_matrix_stack = utils.model_world(translation, rotation, scale)
        if len(GL.model_to_world) > 0: GL.transformation_matrix_stack = np.dot(GL.model_to_world[len(GL.model_to_world) - 1], GL.transformation_matrix_stack)

        GL.model_to_world += [GL.transformation_matrix_stack]
        GL.mvp = utils.mvp(GL)

    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        print("=== Transform out ===")
        if len(GL.model_to_world) > 0: GL.model_to_world.pop()
    
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

        # print("TriangleSet")
        
        ## Transformations
        screen_points = utils.transform_points(point, GL)
        
        ## Raster
        triangles = []

        for p in range(0, len(screen_points) - 2, 3):
            triangles += [[screen_points[p][0:3, 0:1], screen_points[p + 1][0:3, 0:1], screen_points[p + 2][0:3, 0:1]]]
        
        utils.Rasterizer.render(triangles=triangles, colors=colors["diffuseColor"])

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

        # print("TriangleStripSet")

        ## Transformations
        screen_points = utils.transform_points(point, GL)
        
        ## Raster
        triangles = []

        for i in range(stripCount[0] - 2):
            triangles += [[screen_points[i + 2][0:3, 0:1], screen_points[i + 1][0:3, 0:1], screen_points[i][0:3, 0:1]]]
            if i % 2 == 0: triangles += [[screen_points[i][0:3, 0:1], screen_points[i + 1][0:3, 0:1], screen_points[i + 2][0:3, 0:1]]]
        
        utils.Rasterizer.render(triangles=triangles, colors=colors["diffuseColor"])

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

        # print("IndexedTriangleStripSet")

        ## Transformations
        screen_points = utils.transform_points(point, GL)
        
        ## Raster
        triangles = []

        for i in range(len(index) - 3):
            triangles += [[screen_points[index[i + 2]][0:3, 0:1], screen_points[index[i + 1]][0:3, 0:1], screen_points[index[i]][0:3, 0:1]]]
            if i % 2 == 0: triangles += [[screen_points[index[i]][0:3, 0:1], screen_points[index[i + 1]][0:3, 0:1], screen_points[index[i + 2]][0:3, 0:1]]]
        
        utils.Rasterizer.render(triangles=triangles, colors=colors["diffuseColor"])

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # print("Box")

        x = size[0]
        y = size[1]
        z = size[2]
        
        ## !! Cube Order, counter clock-wise
        # front, left, back, right, up, down
        square_p1 = (-x, -y, z)
        square_p2 = (x, -y, z)
        square_p3 = (x, y, z)
        square_p4 = (-x, y, z)
        square_p5 = (-x, y, -z)
        square_p6 = (x, y, -z)
        square_p7 = (-x, -y, -z)
        square_p8 = (x, -y, -z)

        point = [
            square_p1, square_p2, square_p3,
            square_p3, square_p4, square_p1,

            square_p7, square_p1, square_p4,
            square_p4, square_p5, square_p7,
            
            square_p8, square_p7, square_p5,
            square_p5, square_p6, square_p8,
            
            square_p8, square_p6, square_p2,
            square_p2, square_p6, square_p3,
            
            square_p6, square_p5, square_p4,
            square_p4, square_p3, square_p6,
            
            square_p8, square_p7, square_p1,
            square_p1, square_p2, square_p8
        ]

        point = list(sum(point, ()))
        
        ## Raster
        GL.triangleSet(point, colors)

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim coord[0] é o valor
        # da coordenada x do primeiro ponto, coord[1] o valor y do primeiro ponto, coord[2]
        # o valor z da coordenada z do primeiro ponto. Já coord[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista de vértices é informada
        # em coordIndex, o valor -1 indica que a lista acabou.
        # A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante.
        # Adicionalmente essa implementação do IndexedFace aceita cores por vértices, assim
        # se a flag colorPerVertex estiver habilitada, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.

        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("IndexedFaceSet : ")

        ## Transformations
        screen_points = utils.transform_points(coord, GL)
        
        ## Raster
        vertex_color = colorPerVertex and color and colorIndex
        has_texture = texCoord and texCoordIndex and current_texture
        input_color = [] if vertex_color else colors["diffuseColor"]
        triangles = []
        uvs = []

        for i in range(0, len(coordIndex) - 3, 4):
            triangles += [[screen_points[coordIndex[i]][0:3, 0:1], screen_points[coordIndex[i + 1]][0:3, 0:1], screen_points[coordIndex[i + 2]][0:3, 0:1]]]

            if has_texture:
                offset_1 = (texCoordIndex[i]) * 2
                offset_2 = (texCoordIndex[i + 1]) * 2
                offset_3 = (texCoordIndex[i + 2]) * 2

                uvs += [[
                    [texCoord[offset_1], texCoord[offset_1 + 1]],
                    [texCoord[offset_2], texCoord[offset_2 + 1]],
                    [texCoord[offset_3], texCoord[offset_3 + 1]]
                ]]

            elif vertex_color:
                offset_1 = (colorIndex[i]) * 3
                offset_2 = (colorIndex[i + 1]) * 3
                offset_3 = (colorIndex[i + 2]) * 3

                input_color += [[
                    [color[offset_1], color[offset_1 + 1], color[offset_1 + 2]], 
                    [color[offset_2], color[offset_2 + 1], color[offset_2 + 2]], 
                    [color[offset_3], color[offset_3 + 1], color[offset_3 + 2]]
                ]]

        utils.Rasterizer.render(triangles=triangles, colors=input_color, vertex_color=vertex_color, texture=current_texture, uv=uvs, has_texture=has_texture)

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
