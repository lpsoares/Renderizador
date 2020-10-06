import numpy as np

from parameters import LARGURA, ALTURA

def create_triangle_matrix(point, e):
    """ 
        Função usada para criar a matriz das coordenadas dos pontos do triangulo 
        utilizando o método matrix da biblioteca numpy
    """
    k = e*9

    triangle = np.matrix([
                [point[0+k], point[3+k], point[6+k]],
                [point[1+k], point[4+k], point[7+k]],
                [point[2+k], point[5+k], point[8+k]],
                [1,1,1]
            ])
    return triangle

def get_screen_coord_matrix():
    """
        Essa função retorna a matriz de coordenadas na tela
    """

    # Chama a altura e largura da imagem criada
    global ALTURA, LARGURA

    # Matriz de escala
    mS = np.matrix([
            [LARGURA/2,0,0,0],
            [0,ALTURA/2,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    # Matriz de translação
    mT = np.matrix([
            [1,0,0,1],
            [0,1,0,1],
            [0,0,1,0],
            [0,0,0,1]
        ])

    # Matriz de espelhamento
    mE = np.matrix([
            [1,0,0,0],
            [0,-1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])

    # Retorna a multiplicação de mS * mT * mE
    return np.matmul(np.matmul(mS, mT), mE)

def get_vertice_list(screen):
    """
        Essa função retorna a lista de vertices que são as coordenadas x e y 
        dos 3 pontos do triângulo na tela, ou seja, valores em pixel
    """

    vertices = []
    vertices.append(screen[0,0])
    vertices.append(screen[1,0])
    vertices.append(screen[0,1])
    vertices.append(screen[1,1])
    vertices.append(screen[0,2])
    vertices.append(screen[1,2])

    return vertices

def get_box_vertices(size, centro):
    vertices = [
        [centro[0] - size[0]/2, centro[1] - size[1]/2, centro[2] - size[2]/2],
        [centro[0] - size[0]/2, centro[1] - size[1]/2, centro[2] + size[2]/2],
        [centro[0] - size[0]/2, centro[1] + size[1]/2, centro[2] - size[2]/2],
        [centro[0] - size[0]/2, centro[1] + size[1]/2, centro[2] + size[2]/2],
        [centro[0] + size[0]/2, centro[1] - size[1]/2, centro[2] - size[2]/2],
        [centro[0] + size[0]/2, centro[1] - size[1]/2, centro[2] + size[2]/2],
        [centro[0] + size[0]/2, centro[1] + size[1]/2, centro[2] - size[2]/2],
        [centro[0] + size[0]/2, centro[1] + size[1]/2, centro[2] + size[2]/2],
    ]
    return vertices

def get_box_faces(vertices):
    faces = [
        [vertices[4], vertices[6], vertices[0], vertices[2]],
        [vertices[2], vertices[3], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[4], vertices[5]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[5], vertices[7], vertices[1], vertices[3]],
    ]

    return faces

def create_triangle_strip_matrix(point, e):
    """ 
        Função usada para criar a matriz das coordenadas dos pontos do triangulo 
        utilizando o método matrix da biblioteca numpy
    """
    k = e*3

    print(e)

    if e % 2 == 0:
        triangle = np.matrix([
                    [point[0+k], point[3+k], point[6+k]],
                    [point[1+k], point[4+k], point[7+k]],
                    [point[2+k], point[5+k], point[8+k]],
                    [1,1,1]
                ])
    else:
        triangle = np.matrix([
                    [point[3+k], point[0+k], point[6+k]],
                    [point[4+k], point[1+k], point[7+k]],
                    [point[5+k], point[2+k], point[8+k]],
                    [1,1,1]
                ])
    return triangle

