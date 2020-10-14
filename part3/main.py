
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
        #print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex)) # imprime no terminal

        pontos = []
        qtd_pontos = len(coord)/3

        for p in range(int(qtd_pontos)):
            pontos.append(coord[p*3:p*3+3])

        
        triangulos = []

        vertices = []
        for v in coordIndex:

            if v != -1:
                vertices.append(v)
            
                if len(vertices) == 3:
                    v0 = vertices[0] - 1
                    v1 = vertices[1] - 1
                    v2 = vertices[2] - 1 

                    triangulos.append(
                        np.matrix([
                            [pontos[v0][0], pontos[v1][0], pontos[v2][0]],
                            [pontos[v0][1], pontos[v1][1], pontos[v2][1]],
                            [pontos[v0][2], pontos[v1][2], pontos[v2][2]],
                            [1,1,1]
                        ])
                    )

            else:
                vertices = []
            
    if colorPerVertex:
        print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex)) # imprime no terminal
    
        pontos = []
        qtd_pontos = len(coord)/3
        for p in range(int(qtd_pontos)):
            pontos.append(coord[p*3:p*3+3])

        cores = []
        qtd_cores = len(color)/3
        for c in range(int(qtd_cores)):
            cores.append(color[c*3:c*3+3])

        triangulos = []
        triangulos_color = []
        qtd_triangulos = len(coordIndex)/2 - 1 
        for e in range(int(qtd_triangulos)):
            
            vf1 = e*2
            vf2 = vf1+3

            vertices = coordIndex[vf1:vf2]
            v0 = vertices[0]
            v1 = vertices[1]
            v2 = vertices[2] 

            triangulos.append(
                np.matrix([
                    [pontos[v0][0], pontos[v1][0], pontos[v2][0]],
                    [pontos[v0][1], pontos[v1][1], pontos[v2][1]],
                    [pontos[v0][2], pontos[v1][2], pontos[v2][2]],
                    [1,1,1]
                ])
            )

            vertices_color = colorIndex[vf1:vf2]
            
            c0 = vertices_color[0]  
            c1 = vertices_color[1]
            c2 = vertices_color[2]

            triangulos_color.append([cores[c0], cores[c1], cores[c2]])
      
    if texCoord:
        print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex)) # imprime no terminal

        image = gpu.GPU.load_texture(current_texture[0])

        pontos = []
        qtd_pontos = len(coord)/3
        for c in range(int(qtd_pontos)):
            pontos.append(coord[c*3:c*3+3])

        tex_pontos = []
        qtd_tex_pontos = len(texCoord)/2
        for tp in range(int(qtd_tex_pontos)):
            tex_pontos.append(texCoord[tp*2:tp*2+2])

        triangulos = []
        triangulos_tex = []
        qtd_triangulos = len(coordIndex)/2 - 1
        for e in range(int(qtd_triangulos)):
            
            vf1 = e*2
            vf2 = vf1+3

            vertices = coordIndex[vf1:vf2]
            v0 = vertices[0]
            v1 = vertices[1]
            v2 = vertices[2] 

            triangulos.append(
                np.matrix([
                    [pontos[v0][0], pontos[v1][0], pontos[v2][0]],
                    [pontos[v0][1], pontos[v1][1], pontos[v2][1]],
                    [pontos[v0][2], pontos[v1][2], pontos[v2][2]],
                    [1,1,1]
                ])
            )

            vertices_tex = texCoordIndex[vf1:vf2]
            vt0 = vertices_tex[0]
            vt1 = vertices_tex[1]
            vt2 = vertices_tex[2]

            triangulos_tex.append([tex_pontos[vt0], tex_pontos[vt1], tex_pontos[vt2]])

    if(current_texture):
        image = gpu.GPU.load_texture(current_texture[0])
        #print("\t Matriz com image = {0}".format(image))

    lookAt = viewpoint_matrixes[0]
    perspective_projection_matrix = viewpoint_matrixes[1]
    screen_coord_matrix = get_screen_coord_matrix()

    for idx in range(len(triangulos)):

        t = triangulos[idx]
    
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

                if inside(x,y,vertices):
                    
                    if coord:
                        gpu.GPU.set_pixel(x, y, 255, 255, 255)

                    if colorPerVertex:
                        
                        t_cores = triangulos_color[idx]

                        alpha = (-(x-xb)*(yc-yb) + (y-yb)*(xc-xb)) / (-(xa-xb)*(yc-yb) + (ya-yb)*(xc-xb))
                        beta = (-(x-xc)*(ya-yc) + (y-yc)*(xa-xc)) / (-(xb-xc)*(ya-yc) + (yb-yc)*(xa-xc))
                        gama = 1 - alpha - beta
            
                        red = alpha*t_cores[0][0] + beta*t_cores[1][0] + gama*t_cores[2][0]
                        green = alpha*t_cores[0][1] + beta*t_cores[1][1] + gama*t_cores[2][1]
                        blue = alpha*t_cores[0][2] + beta*t_cores[1][2] + gama*t_cores[2][2]

                        gpu.GPU.set_pixel(x, y, red*255, green*255, blue*255)
                        
                    if texCoord:

                        t_tex = triangulos_tex[idx]

                        v0 = t_tex[0]
                        v1 = t_tex[1]
                        v2 = t_tex[2]

                        alpha = (-(x-xb)*(yc-yb) + (y-yb)*(xc-xb)) / (-(xa-xb)*(yc-yb) + (ya-yb)*(xc-xb))
                        beta = (-(x-xc)*(ya-yc) + (y-yc)*(xa-xc)) / (-(xb-xc)*(ya-yc) + (yb-yc)*(xa-xc))
                        gama = 1 - alpha - beta

                        u = int(alpha*v0[0]*199 + beta*v1[0]*199 + gama*v2[0]*199)
                        v = int(alpha*v0[1]*199 + beta*v1[1]*199 + gama*v2[1]*199)

                        gpu.GPU.set_pixel(x, y, image[-v][u][0], image[-v][u][1], image[-v][u][2])