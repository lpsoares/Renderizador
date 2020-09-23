# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU
import numpy as np
import math

def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """
    # gpu.GPU.set_pixel(3, 1, 255, 0, 0) # altera um pixel da imagem
    # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

    # O laço passa por todos elementos da lista point
    # pega a posição de cada ponto e pinta o píxel correspondente 
    i = 0
    while (i < len(point)):
        gpu.GPU.set_pixel(int(point[i]), int(point[i+1]), color[0]*255, color[1]*255, color[2]*255)
        i+=2

def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """
    #x = gpu.GPU.width//2
    #y = gpu.GPU.height//2
    #gpu.GPU.set_pixel(x, y, 255, 0, 0) # altera um pixel da imagem

    if lineSegments[0] <= lineSegments[2]:
        x0 = lineSegments[0] 
        y0 = lineSegments[1]
        x1 = lineSegments[2] 
        y1 = lineSegments[3] 
    else:
        x1 = lineSegments[0] 
        y1 = lineSegments[1]
        x0 = lineSegments[2] 
        y0 = lineSegments[3] 

    s = (y1-y0)/(x1-x0) # Inclinação da reta
    
    x, y = x0, y0
    while x <= x1:
        if s > 1:
            k = y
            for i in range(int(y+s) - int(y)):
                gpu.GPU.set_pixel(int(x), int(k+i), color[0]*255, color[1]*255, color[2]*255) # altera um pixel da imagem
        elif s < -1:
            k = y
            for i in range(abs(int(y) - int(y+s))):
                gpu.GPU.set_pixel(int(x), int(k-i), color[0]*255, color[1]*255, color[2]*255) # altera um pixel da imagem
        else:
            gpu.GPU.set_pixel(int(x), int(y), color[0]*255, color[1]*255, color[2]*255) # altera um pixel da imagem
      
        y += s
        x += 1

def eqDaReta(x, y, x0, y0, x1, y1):
    """ Função usada para calcular a Equação da Reta"""
    dx = x1 - x0
    dy = y1 - y0

    if (x - x0)*dy - (y - y0)*dx >= 0:
        return True
    
    return False

def inside(x, y, vertices):
    "Função usada para verificar se um píxel esta dentro do triangulo"
    x0, y0 = vertices[0], vertices[1]
    x1, y1 = vertices[2], vertices[3]
    x2, y2 = vertices[4], vertices[5]

    if eqDaReta(x, y, x0, y0, x1, y1) and eqDaReta(x, y, x1, y1, x2, y2) and eqDaReta(x, y, x2, y2, x0, y0):
        return True
    
    return False

def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    #gpu.GPU.set_pixel(24, 8, 255, 255, 0) # altera um pixel da imagem

    xmax, ymax = 30, 20

    for x in range(xmax):
        for y in range(ymax):
            supersampling = 4
            mean = 0
            
            if inside(x+0.25, y+0.25, vertices):
                mean += 1/supersampling
            if inside(x+0.25, y+0.75, vertices):
                mean += 1/supersampling
            if inside(x+0.75, y+0.25, vertices):
                mean += 1/supersampling
            if inside(x+0.75, y+0.75, vertices):
                mean += 1/supersampling

            if mean > 0:
                gpu.GPU.set_pixel(x, y, color[0]*255*mean, color[1]*255*mean, color[2]*255*mean)

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
    print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos
    
    numTriangles = int(len(point)/9)
    triangles = []
    for e in range(numTriangles):
        k = e*9
        triangle = np.matrix([
                [point[0+k], point[3+k], point[6+k]],
                [point[1+k], point[4+k], point[7+k]],
                [point[2+k], point[5+k], point[8+k]],
                [1,1,1]
            ])
        triangles.append(triangle)

    global lista_de_matrizes
    #LA, MPP, MCT

    for triangle in triangles:
        triangle_transformado = np.matmul(matriz, triangle)
        triangle_lookat = np.matmul(lista_de_matrizes[0], triangle_transformado)
        perspectiva = np.matmul(lista_de_matrizes[1], triangle_lookat)
        
        for e in range(3):
            perspectiva[:,e] = perspectiva[:,e]/perspectiva[-1,e]

        tela = np.matmul(lista_de_matrizes[2], perspectiva)
        
        vertices = []
        vertices.append(tela[0,0])
        vertices.append(tela[1,0])
        vertices.append(tela[0,1])
        vertices.append(tela[1,1])
        vertices.append(tela[0,2])
        vertices.append(tela[1,2])

        triangleSet2D(vertices, color)

lista_de_matrizes = []
def viewpoint(position, orientation, fieldOfView):
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    # Na função de viewpoint você receberá a posição, orientação e campo de visão da
    # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
    # perspectiva para poder aplicar nos pontos dos objetos geométricos.

    global lista_de_matrizes

    mOrientation = np.matrix([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    mTraslation = np.matrix([
            [1,0,0,-position[0]],
            [0,1,0,-position[1]],
            [0,0,1,-position[2]],
            [0,0,0,1]
        ])

    lookAt = np.matmul(mOrientation, mTraslation)

    mPP = np.matrix([
            [0.5, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, -1.01, -1.005],
            [0, 0, -1, 0]
        ])
    
    global ALTURA
    global LARGURA

    mResolution = np.matrix([
            [LARGURA/2,0,0,0],
            [0,ALTURA/2,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    T = np.matrix([
            [1,0,0,1],
            [0,1,0,1],
            [0,0,1,0],
            [0,0,0,1]
        ])

    E = np.matrix([
            [1,0,0,0],
            [0,-1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    mCT_partial = np.matmul(mResolution, T)
    mCT = np.matmul(mCT_partial, E)

    lista_de_matrizes.append(lookAt)
    lista_de_matrizes.append(mPP)
    lista_de_matrizes.append(mCT)

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("Viewpoint : position = {0}, orientation = {1}, fieldOfView = {2}".format(position, orientation, fieldOfView)) # imprime no terminal

pilha = []
matriz = np.matrix([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ])

def transform(translation, scale, rotation):
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função transform será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.

    global pilha
    global matriz

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Transform : ", end = '')
    if translation:
        pilha.append(matriz)

        mTranslation = np.matrix([
            [1,0,0, translation[0]],
            [0,1,0, translation[1]],
            [0,0,1, translation[2]],
            [0,0,0,1]
        ])

        matriz = np.matmul(mTranslation, matriz)

        print("translation = {0} ".format(translation), end = '') # imprime no terminal
    if scale:
        pilha.append(matriz)

        mScale = np.matrix([
            [scale[0],0,0,0],
            [0,scale[1],0,0],
            [0,0,scale[2],0],
            [0,0,0,1]
        ])

        matriz = np.matmul(mScale, matriz)

        print("scale = {0} ".format(scale), end = '') # imprime no terminal

    if rotation:
        if rotation[0]: 
            pilha.append(matriz)

            mRotation = np.matrix([
                [1, 0, 0, 0],
                [0, math.cos(rotation[3]), -math.sin(rotation[3]), 0],
                [0, math.sin(rotation[3]),  math.cos(rotation[3]), 0],
                [0, 0, 0, 1]
            ])

            matriz = np.matmul(mRotation, matriz)

        elif rotation[1]:
            pilha.append(matriz)

            mRotation = np.matrix([
                [math.cos(rotation[3]), 0, math.sin(rotation[3]), 0],
                [0, 1, 0, 0],
                [-math.sin(rotation[3]), 0, math.cos(rotation[3]), 0],
                [0, 0, 0, 1]
            ])

            matriz = np.matmul(mRotation, matriz)

        elif rotation[2]:
            pilha.append(matriz)

            mRotation = np.matrix([
                [math.cos(rotation[3]), -math.sin(rotation[3]), 0, 0],
                [math.sin(rotation[3]),  math.cos(rotation[3]), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])

            matriz = np.matmul(mRotation, matriz)


        print("rotation = {0} ".format(rotation), end = '') # imprime no terminal
    #print("")

def _transform():
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função _transform será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.

    global pilha
    global matriz

    matriz = pilha[-1]

    del pilha[-1]

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("Saindo de Transform")

def triangleStripSet(point, stripCount, color):
    """ Função usada para renderizar TriangleStripSet. """
    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("TriangleStripSet : pontos = {0} ".format(point), end = '') # imprime no terminal pontos
    for i, strip in enumerate(stripCount):
        print("strip[{0}] = {1} ".format(i, strip), end = '') # imprime no terminal
    print("")

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
    print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index)) # imprime no terminal pontos

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


LARGURA = 40
ALTURA = 30

if __name__ == '__main__':

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo4.x3d"
    image_file = "tela.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    parser.add_argument("-q", "--quiet", help="não exibe janela de visualização", action='store_true')
    args = parser.parse_args() # parse the arguments
    if args.input: x3d_file = args.input
    if args.output: image_file = args.output
    if args.width: width = args.width
    if args.height: height = args.height

    # Iniciando simulação de GPU
    gpu.GPU(width, height, image_file)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D
    x3d.X3D.render["Transform"] = transform
    x3d.X3D.render["TriangleSet"] = triangleSet
    x3d.X3D.render["Viewpoint"] = viewpoint
    x3d.X3D.render["_Transform"] = _transform
    x3d.X3D.render["TriangleStripSet"] = triangleStripSet
    x3d.X3D.render["IndexedTriangleStripSet"] = indexedTriangleStripSet
    x3d.X3D.render["Box"] = box

    # Se no modo silencioso não configurar janela de visualização
    if not args.quiet:
        window = interface.Interface(width, height)
        scene.set_preview(window)

    scene.parse() # faz o traversal no grafo de cena

    # Se no modo silencioso salvar imagem e não mostrar janela de visualização
    if args.quiet:
        gpu.GPU.save_image() # Salva imagem em arquivo
    else:
        window.image_saver = gpu.GPU.save_image # pasa a função para salvar imagens
        window.preview(gpu.GPU._frame_buffer) # mostra janela de visualização
