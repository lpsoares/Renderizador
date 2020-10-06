
import numpy as np

from part1.main import *
from part2.main import *

def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex, texCoord, texCoordIndex, current_color, current_texture):
    """ Função usada para renderizar IndexedFaceSet. """
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
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("IndexedFaceSet : ")
    if coord:
        print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex)) # imprime no terminal
    if colorPerVertex:
        print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex)) # imprime no terminal
    if texCoord:
        print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex)) # imprime no terminal
    if(current_texture):
        image = gpu.GPU.load_texture(current_texture[0])
        print("\t Matriz com image = {0}".format(image))

    if texCoord:
        pontos = []

        for c in range(int(len(coord)/3)):
            pontos.append(coord[c*3:c*3+3])

        num_triangulos = len(pontos) - 2

        triangulos = []

        for e in range(num_triangulos):

            idx1 = 0+e*2
            idx2 = 1+e*2
            
            if 2+e*2 > len(pontos) - 1 : 
                idx3 = 0
            else:
                idx3 = 2+e*2

            triangulos.append(
                np.matrix([
                    [pontos[idx1][0], pontos[idx2][0], pontos[idx3][0]],
                    [pontos[idx1][1], pontos[idx2][1], pontos[idx3][1]],
                    [pontos[idx1][2], pontos[idx2][2], pontos[idx3][2]],
                    [1,1,1]
                ])
            )

        lookAt = viewpoint_matrixes[0]
        perspective_projection_matrix = viewpoint_matrixes[1]
        screen_coord_matrix = get_screen_coord_matrix()


        image = gpu.GPU.load_texture(current_texture[0])

        color_list = []
        
        for e in texCoordIndex:
            u = int(texCoord[e*2])
            v = int(texCoord[e*2 + 1])

            color_list.append(image[u][v][0:3])

        contador = 0

        for t in triangulos:

            if contador == 0:
                pts = [0,1,2]
                contador += 1
            else:
                pts = [2,3,0]

            w_c = np.matmul(transform_matrix, t)
            c_c = np.matmul(lookAt, w_c)
            p_c = np.matmul(perspective_projection_matrix, c_c)

            n_c = np.asmatrix(np.zeros((4,3)))

            for e in range(3):
                n_c[:,e] = p_c[:,e]/p_c[-1,e]

            screen = np.matmul(screen_coord_matrix, n_c)

            xa, xb, xc = screen[0,0], screen[0,1], screen[0,2]
            ya, yb, yc = screen[1,0], screen[1,1], screen[1,2]
            
            vertices = [xa, ya, xb, yb, xc, yc]

            for x in range(LARGURA):
                for y in range(ALTURA):

                    if inside(x+0.5,y+0.5,vertices):

                        alpha = (-(x-xb)*(yc-yb) + (y-yb)*(xc-xb)) / (-(xa-xb)*(yc-yb) + (ya-yb)*(xc-xb))
                        beta = (-(x-xc)*(ya-yc) + (y-yc)*(xa-xc)) / (-(xb-xc)*(ya-yc) + (yb-yc)*(xa-xc))
                        gama = 1 - alpha - beta

                        red = alpha*color_list[pts[0]][0] + beta*color_list[pts[1]][0] + gama*color_list[pts[2]][0]
                        green = alpha*color_list[pts[0]][1] + beta*color_list[pts[1]][1] + gama*color_list[pts[2]][1]
                        blue = alpha*color_list[pts[0]][2] + beta*color_list[pts[1]][2] + gama*color_list[pts[2]][2]
                        
                        gpu.GPU.set_pixel(x, y, red, green, blue)
