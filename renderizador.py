# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 28 de Agosto de 2020

# Numpy
import numpy as np

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Button

# Pillow
from PIL import Image

# XML
import xml.etree.ElementTree as ET

# Outras
import re
import math

class Renderer:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.geometrias = []
        self.grid = False

        self.fig, self.ax = plt.subplots()
        self.ax.set_title('Renderizador')

        self.ax.axis([0, width, height, 0])  # [xmin, xmax, ymin, ymax]

        #self.ax.set_xlabel('x')
        #self.ax.set_ylabel('y')
        #self.ax.xaxis.set_label_position('top')

        self.ax.grid(b=self.grid, which='both')
        self.ax.xaxis.tick_top()

        self.ax.xaxis.set_minor_locator(MultipleLocator(1))
        self.ax.yaxis.set_minor_locator(MultipleLocator(1))


    def anotacao(self, points):
        # Desenha o texto identificando os pontos
        #sh = max(self.width/4, self.height/4) # deslocamento do texto do ponto
        sh = 5
        for i, pos in enumerate(points):
            text = self.ax.annotate("P{0}".format(i), xy=pos,  xytext = (sh, sh),
                                textcoords = 'offset points', color='lightgray')
            self.geometrias.append(text)

    def desenha_linha(self, points, text=False):
        # converte pontos
        x_values = [ pt[0] for pt in points ]
        y_values = [ pt[1] for pt in points ]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color='red', linestyle="-")  # "ro-"
        self.geometrias.append(line)

        # desenha texto se requisitado
        if text:
            self.anotacao(points)


    def desenha_triangulo(self, points, text=False):
        # converte pontos
        x_values = [ pt[0] for pt in points ] + [points[0][0]]
        y_values = [ pt[1] for pt in points ] + [points[0][1]]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color='red', linestyle="-")  # "ro-"
        self.geometrias.append(line)

        poly, = self.ax.fill(x_values, y_values, color=(1.0, 0.0, 0.0, 0.4)) 
        self.geometrias.append(poly)

        # desenha texto se requisitado
        if text:
            self.anotacao(points)

    def desenha_tela(self, data):
        extent = (0, self.width, self.height, 0)
        imgplot = self.ax.imshow(data, interpolation='nearest', extent=extent)

    def salva_imagem(self, data, filename):
        img = Image.fromarray(data, 'RGB')
        img.save(filename)

    def exibe_geometrias(self, event):
        for geometria in self.geometrias:
            geometria.set_visible(not geometria.get_visible())
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def exibe_grid(self, event):
        self.grid = not self.grid
        self.ax.grid(b=self.grid, which='both')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

if __name__ == '__main__':

    svg = ET.parse("test4.svg")

    root = svg.getroot()

    width = math.ceil(float(root.attrib["width"].split("px")[0]))
    height = math.ceil(float(root.attrib["height"].split("px")[0]))

    linhas = []
    poligonos = []
    for child in root:
        _, _, child.tag = child.tag.rpartition('}') # remove ns
        if child.tag == "line":
            linhas.append([ [float(child.attrib['x1']), float(child.attrib['y1'])], [float(child.attrib['x2']), float(child.attrib['y2'])]  ])
            color = child.attrib['fill']
        elif child.tag == "polygon":
            poligono = []
            pontos = re.split(r'[,\s]\s*',child.attrib['points'])
            for i in range(0, len(pontos)-2, 2):
                poligono.append([float(pontos[i]), float(pontos[i+1])])
            poligonos.append(poligono)
            color = child.attrib['fill']

    renderer = Renderer(width, height)

    for linha in linhas:
        renderer.desenha_linha(linha, text=True)

    for poligono in poligonos:
        renderer.desenha_triangulo(poligono, text=True)

    data = np.zeros((height, width, 3), dtype=np.uint8) # cria imagem com fundo preto
    data[1][3] = [255, 0, 0] # altera um pixel da imagem
    data[1][5] = [0, 200, 0] # altera um pixel da imagem
    # Perceba que a matriz é organizada em linhas e colunas, ou seja, y e x

    renderer.desenha_tela(data)
    #renderer.salva_imagem(data, "tela.png")
    
    bgeo = Button(plt.axes([0.8, 0.01, 0.15, 0.06]), 'Geometria', color='red')
    bgeo.on_clicked(renderer.exibe_geometrias)

    bgrid = Button(plt.axes([0.6, 0.01, 0.15, 0.06]), 'Grid', color='red')
    bgrid.on_clicked(renderer.exibe_grid)

    plt.show()