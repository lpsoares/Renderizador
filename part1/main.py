import gpu

from parameters import ALTURA, LARGURA

from .functions import inside

def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """

    # O laço passa por todos elementos da lista point
    # pega a posição de cada ponto e pinta o píxel correspondente 
    i = 0
    while (i < len(point)):
        gpu.GPU.set_pixel(int(point[i]), int(point[i+1]), color[0]*255, color[1]*255, color[2]*255)
        i+=2

def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """

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

def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    #gpu.GPU.set_pixel(24, 8, 255, 255, 0) # altera um pixel da imagem

    xmax, ymax = LARGURA, ALTURA

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
