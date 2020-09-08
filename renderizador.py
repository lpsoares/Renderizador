# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU
       
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

LARGURA = 30
ALTURA = 20

if __name__ == '__main__':

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo3.x3d"
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
