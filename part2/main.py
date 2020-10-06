import gpu
import numpy as np
import math

from part1.main import triangleSet2D

from parameters import viewpoint_matrixes, transform_matrix, stack

from .functions import *

def triangleSet(point, color):
    """ Função usada para renderizar TriangleSet. """
    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da 
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
    # assim por diante.
    # No TriangleSet os triângulos são informados individualmente, assim os três
    # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
    # triângulo, e assim por diante.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos

    # Número de triangulos sendo passado no point
    num_triangles = int(len(point)/9)

    # Pega as coordenadas dos pontos na lista 'point', utiliza a função create_triangle_matrix
    # para criar a matriz das coordenadas do triângulo e salva na lista 'objects_coordinates'
    objects_coordinates = []
    for e in range(num_triangles):
        triangle = create_triangle_matrix(point, e)
        objects_coordinates.append(triangle)


    # Seta as matrizes que serão usadas no for:
    # As matrizes da visão da câmera, projeção perspectiva e de coordenadas na tela
    lookAt = viewpoint_matrixes[0]
    perspective_projection_matrix = viewpoint_matrixes[1]
    screen_coord_matrix = get_screen_coord_matrix()

    # Realiza as trasnformações para cada triângulo/objeto na lista 'objects_coordinates'
    for triangle in objects_coordinates:

        # Realiza a primeira transformação -> 
        # objeto nas coordenas do mundo = matriz de transformaçao * coordenadas do objeto
        world_coord = np.matmul(transform_matrix, triangle)
        
        # Realiza a segunda transformação -> 
        # objeto nas coordenas da câmera = visão da câmera * objeto nas coordenas do mundo
        cam_coord = np.matmul(lookAt, world_coord)
        
        # Realiza a terceira transformação -> 
        # coordenadas em perspectiva = projeção perspectiva * objeto nas coordenas da câmera
        perspective_coord = np.matmul(perspective_projection_matrix, cam_coord)
        
        # Divide cada coluna da matriz das coordenadas em perspectiva pelo últivo valor 
        # da mesma coluna a fim de normaliza-las
        norm_coord = np.asmatrix(np.zeros((4,3)))
        for e in range(3):
            norm_coord[:,e] = perspective_coord[:,e]/perspective_coord[-1,e]

        # A última transformação ->
        # tela = coordenadas na tela * coordenadas normalizadas
        screen = np.matmul(screen_coord_matrix, norm_coord)

        # lista de vertices para função de printar o triangulo na tela
        vertices = get_vertice_list(screen)

        # printa o triangulo na tela
        triangleSet2D(vertices, color)

def viewpoint(position, orientation, fieldOfView):
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    # Na função de viewpoint você receberá a posição, orientação e campo de visão da
    # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
    # perspectiva para poder aplicar nos pontos dos objetos geométricos.    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Viewpoint : position = {0}, orientation = {1}, fieldOfView = {2}".format(position, orientation, fieldOfView)) # imprime no terminal

    # Chama 'viewpoint_matrixes' para conseguirmos utilizar as matrizes geradas 
    # em outras funções
    global viewpoint_matrixes

    # Matriz de orientação da câmera
    mOrientation = np.matrix([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    # Matriz de tranlação da câmera. A traslação que a câmera fará para ficar na origem.
    mTraslation = np.matrix([
            [1,0,0,-position[0]],
            [0,1,0,-position[1]],
            [0,0,1,-position[2]],
            [0,0,0,1]
        ])
    
    # Matriz da visão da câmera. 
    # A visão da câmera é a orientação que queremos pra ela (vRight = x, vUp = y, vView = -z)
    # e a posição dela (mTranslação transloca a câmera para origem).
    lookAt = np.matmul(mOrientation, mTraslation)

    # Matriz de Projeção Perspectiva
    perspective_projection_matrix = np.matrix([
            [0.5, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, -1.01, -1.005],
            [0, 0, -1, 0]
        ])
    
    # Adiciona as matrizes 'lookAt' e 'perspective_projection_matrix' na lista viewpoint_matrixes
    viewpoint_matrixes.append(lookAt)
    viewpoint_matrixes.append(perspective_projection_matrix)

def transform(translation, scale, rotation):
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função transform será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Transform : ", end = '')

    # Chama as variáveis globais 'stack' e 'transform_matrix' 
    global stack
    global transform_matrix

    if translation:
        # print("translation = {0} ".format(translation), end = '') # imprime no terminal
        
        # Adicionamos o valor atual de 'transform_matrix' na 'stack' 
        # pois ele será alterado após a transformação
        stack.append(transform_matrix)

        # matriz traslação
        mTranslation = np.matrix([
            [1,0,0, translation[0]],
            [0,1,0, translation[1]],
            [0,0,1, translation[2]],
            [0,0,0,1]
        ])

        # Atualizamos o valor de 'transform_matrix' realizando a multiplicação da 
        # matriz translação * valor atual de transform_matrix
        transform_matrix = np.matmul(mTranslation, transform_matrix)

    if scale:
        #print("scale = {0} ".format(scale), end = '') # imprime no terminal
        
        # Adicionamos o valor atual de 'transform_matrix' na 'stack' 
        # pois ele será alterado após a transformação
        stack.append(transform_matrix)

        # matriz escala
        mScale = np.matrix([
            [scale[0],0,0,0],
            [0,scale[1],0,0],
            [0,0,scale[2],0],
            [0,0,0,1]
        ])
        
        # Atualizamos o valor de 'transform_matrix' realizando a multiplicação da 
        # matriz escala * valor atual de transform_matrix
        transform_matrix = np.matmul(mScale, transform_matrix)        

    if rotation:
        #print("rotation = {0} ".format(rotation), end = '') # imprime no terminal

        #Existem 3 possíveis matrizes de rotação para um sistema 3D, variando de acordo com o eixo
        #de rotação, dado isso cada if abaixo corresponde à uma possível matriz
        if rotation[0]: 
            # Adicionamos o valor atual de 'transform_matrix' na 'stack' 
            # pois ele será alterado após a transformação
            stack.append(transform_matrix)

            # matriz rotação (no eixo x)
            # rotation[3] é o valor de rotação em radianos
            mRotation = np.matrix([
                [1, 0, 0, 0],
                [0, math.cos(rotation[3]), -math.sin(rotation[3]), 0],
                [0, math.sin(rotation[3]),  math.cos(rotation[3]), 0],
                [0, 0, 0, 1]
            ])

            # Atualizamos o valor de 'transform_matrix' realizando a multiplicação da 
            # matriz rotação * valor atual de transform_matrix
            transform_matrix = np.matmul(mRotation, transform_matrix)

        elif rotation[1]:
            # Adicionamos o valor atual de 'transform_matrix' na 'stack' 
            # pois ele será alterado após a transformação
            stack.append(transform_matrix)

            # matriz rotação (no eixo y)
            # rotation[3] é o valor de rotação em radianos
            mRotation = np.matrix([
                [math.cos(rotation[3]), 0, math.sin(rotation[3]), 0],
                [0, 1, 0, 0],
                [-math.sin(rotation[3]), 0, math.cos(rotation[3]), 0],
                [0, 0, 0, 1]
            ])

            # Atualizamos o valor de 'transform_matrix' realizando a multiplicação da 
            # matriz rotação * valor atual de transform_matrix
            transform_matrix = np.matmul(mRotation, transform_matrix)

        elif rotation[2]:
            # Adicionamos o valor atual de 'transform_matrix' na 'stack' 
            # pois ele será alterado após a transformação
            stack.append(transform_matrix)

            # matriz rotação (no eixo z)
            # rotation[3] é o valor de rotação em radianos
            mRotation = np.matrix([
                [math.cos(rotation[3]), -math.sin(rotation[3]), 0, 0],
                [math.sin(rotation[3]),  math.cos(rotation[3]), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])

            # Atualizamos o valor de 'transform_matrix' realizando a multiplicação da 
            # matriz rotação * valor atual de matrix
            transform_matrix = np.matmul(mRotation, transform_matrix)

def _transform():
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função _transform será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Saindo de Transform")

    #Chama as variáveis globais 'stack' e 'transform_matrix' 
    global stack
    global transform_matrix

    # 'transform_matrix' recebe o valor da última matriz inserida na stack
    transform_matrix = stack[-1]

    # retira a última matriz inserida na stack
    del stack[-1]

def triangleStripSet(point, stripCount, color, text=False):
    """ Função usada para renderizar TriangleStripSet. """
    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("TriangleStripSet : pontos = {0} ".format(point), end = '') # imprime no terminal pontos
    #for i, strip in enumerate(stripCount):
    #    print("strip[{0}] = {1} ".format(i, strip), end = '') # imprime no terminal
    
    # Chama a matriz de transformação e a lista de matrizes da função 'viewpoint' 
    # que possui as matrizes: 'lookAt' e 'perspective_projection_matrix'
    global transform_matrix, viewpoint_matrixes

    num_triangles = int(stripCount[0] - 2)

    objects_coordinates = []
    for e in range(num_triangles):
        if text:
            triangle = create_triangle_strip_matrix(point, e, text)
        else:
            triangle = create_triangle_strip_matrix(point, e)
        objects_coordinates.append(triangle)
        
    # Seta as matrizes que serão usadas no for:
    # As matrizes da visão da câmera, projeção perspectiva e de coordenadas na tela
    lookAt = viewpoint_matrixes[0]
    perspective_projection_matrix = viewpoint_matrixes[1]
    screen_coord_matrix = get_screen_coord_matrix()

    for i in range(len(objects_coordinates)):

        triangle = objects_coordinates[i]

        # Realiza a primeira transformação -> 
        # objeto nas coordenas do mundo = matriz de transformaçao * coordenadas do objeto
        world_coord = np.matmul(transform_matrix, triangle)
        
        # Realiza a segunda transformação -> 
        # objeto nas coordenas da câmera = visão da câmera * objeto nas coordenas do mundo
        cam_coord = np.matmul(lookAt, world_coord)
        
        # Realiza a terceira transformação -> 
        # coordenadas em perspectiva = projeção perspectiva * objeto nas coordenas da câmera
        perspective_coord = np.matmul(perspective_projection_matrix, cam_coord)
        
        # Divide cada coluna da matriz das coordenadas em perspectiva pelo últivo valor 
        # da mesma coluna a fim de normaliza-las
        norm_coord = np.asmatrix(np.zeros((4,4)))
        for e in range(3):
            norm_coord[:,e] = perspective_coord[:,e]/perspective_coord[-1,e]

        # A última transformação ->
        # tela = coordenadas na tela * coordenadas normalizadas
        screen = np.matmul(screen_coord_matrix, norm_coord)

        # lista de vertices para função de printar o triangulo na tela
        vertices = get_vertice_list(screen)

        if text:
            triangleSet2D(vertices, color[i: i+3], text=True)

        else:    
            # printa o triangulo na tela
            triangleSet2D(vertices, color)

def indexedTriangleStripSet(point, index, color):
    """ Função usada para renderizar IndexedTriangleStripSet. """
    # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
    # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
    # como conectar os vértices é informada em index, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index)) # imprime no terminal pontos

    # Chama a matriz de transformação e a lista de matrizes da função 'viewpoint' 
    # que possui as matrizes: 'lookAt' e 'perspective_projection_matrix'
    global transform_matrix, viewpoint_matrixes

    num_triangles = int(max(index) - 1)

    objects_coordinates = []
    for e in range(num_triangles):
        triangle = create_triangle_strip_matrix(point, e)
        objects_coordinates.append(triangle)

    # Seta as matrizes que serão usadas no for:
    # As matrizes da visão da câmera, projeção perspectiva e de coordenadas na tela
    lookAt = viewpoint_matrixes[0]
    perspective_projection_matrix = viewpoint_matrixes[1]
    screen_coord_matrix = get_screen_coord_matrix()

    for triangle in objects_coordinates:
        # Realiza a primeira transformação -> 
        # objeto nas coordenas do mundo = matriz de transformaçao * coordenadas do objeto
        world_coord = np.matmul(transform_matrix, triangle)
        
        # Realiza a segunda transformação -> 
        # objeto nas coordenas da câmera = visão da câmera * objeto nas coordenas do mundo
        cam_coord = np.matmul(lookAt, world_coord)
        
        # Realiza a terceira transformação -> 
        # coordenadas em perspectiva = projeção perspectiva * objeto nas coordenas da câmera
        perspective_coord = np.matmul(perspective_projection_matrix, cam_coord)
        
        # Divide cada coluna da matriz das coordenadas em perspectiva pelo últivo valor 
        # da mesma coluna a fim de normaliza-las
        norm_coord = np.asmatrix(np.zeros((4,4)))
        for e in range(3):
            norm_coord[:,e] = perspective_coord[:,e]/perspective_coord[-1,e]

        # A última transformação ->
        # tela = coordenadas na tela * coordenadas normalizadas
        screen = np.matmul(screen_coord_matrix, norm_coord)

        # lista de vertices para função de printar o triangulo na tela
        vertices = get_vertice_list(screen)

        # printa o triangulo na tela
        triangleSet2D(vertices, color)

def box(size, color):
    """ Função usada para renderizar Boxes. """
    # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
    # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
    # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
    # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
    # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
    # encontre os vértices e defina os triângulos.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("Box : size = {0}".format(size)) # imprime no terminal pontos

    centro = [0,0,0]
    vertices = get_box_vertices(size, centro)

    faces = get_box_faces(vertices)

    for face in faces:
        points = []
        for vertices in face:
            for coord in vertices:
                points.append(coord)

        triangleStripSet(points, [4], color)
