# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 28 de Agosto de 2020

# Numpy
import numpy as np

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoLocator
from matplotlib.widgets import Button

# Pillow
from PIL import Image

# XML
import xml.etree.ElementTree as ET

# Outras
import re
import math

class Interface:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.geometrias = []    # lista de geometrias para controlar exibição
        self.grid = False       # usado para controlar se grid exibido ou não

        self.linhas = []        # linhas a serem desenhadas
        self.poligonos = []     # poligonos a serem desenhados

        self.fig, self.ax = plt.subplots()
        self.ax.set_title('Renderizador')

        self.ax.axis([0, width, height, 0])  # [xmin, xmax, ymin, ymax]

        #self.ax.set_xlabel('x')
        #self.ax.set_ylabel('y')
        #self.ax.xaxis.set_label_position('top')

        self.ax.xaxis.tick_top()

        # o tamanho do gris é 1x1 para ser do tamanho do pixel
        # mostrando de 10 em 10 o posicionamento dos pixels
        self.ax.xaxis.set_major_locator(MultipleLocator(10))
        self.ax.yaxis.set_major_locator(MultipleLocator(10))
        self.ax.xaxis.set_minor_locator(MultipleLocator(1))
        self.ax.yaxis.set_minor_locator(MultipleLocator(1))

    def annotation(self, points):
        """ Desenha texto ao lando dos pontos identificando eles. """

        sh = 5 # distância do label para o ponto
        for i, pos in enumerate(points):
            text = self.ax.annotate("P{0}".format(i), xy=pos,  xytext = (sh, sh),
                                textcoords = 'offset points', color='lightgray')
            self.geometrias.append(text)

    def draw_lines(self, points, text=False):
        # converte pontos
        
        x_values = [ pt[0] for pt in points ]
        y_values = [ pt[1] for pt in points ]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color='red', linestyle="-")  # "ro-"
        self.geometrias.append(line)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_triangle(self, points, text=False):
        # converte pontos
        print(points)
        x_values = [ pt[0] for pt in points ] + [points[0][0]]
        y_values = [ pt[1] for pt in points ] + [points[0][1]]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color='red', linestyle="-")  # "ro-"
        self.geometrias.append(line)

        poly, = self.ax.fill(x_values, y_values, color=(1.0, 0.0, 0.0, 0.4)) 
        self.geometrias.append(poly)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

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

    def preview(self, data):
        
        extent = (0, self.width, self.height, 0)
        imgplot = self.ax.imshow(data, interpolation='nearest', extent=extent)

        for linha in self.linhas:
            self.draw_lines(linha, text=True)

        print(self.poligonos)
        for poligono in self.poligonos:
            self.draw_triangle(poligono, text=True)

        bgeo = Button(plt.axes([0.8, 0.01, 0.15, 0.06]), 'Geometria', color='red')
        bgeo.on_clicked(self.exibe_geometrias)

        bgrid = Button(plt.axes([0.6, 0.01, 0.15, 0.06]), 'Grid', color='red')
        bgrid.on_clicked(self.exibe_grid)

        plt.show()

def clean(child):
    _, _, child.tag = child.tag.rpartition('}') # remove os namespaces

class X3D:

    def __init__(self, filename):
        
        self.x3d = ET.parse(filename)
        self.root = self.x3d.getroot()

    def set_resolution(self, width, height):
        self.width = width
        self.height = height

    def set_interface(self, interface):
        self.interface = interface
    
    def parse(self):
        """ parse começando da raiz do X3D. """
        for child in self.root:
            clean(child) # remove namespace
            if child.tag == "Scene":
                self.Scene(child)

    def Scene(self, node):
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Transform":
                self.Transform(child)

    def Transform(self, node):
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Shape":
                self.Shape(child)

    def Shape(self, node):
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Polyline2D":
                self.Polyline2D(child)
            if child.tag == "TriangleSet2D":
                self.TriangleSet2D(child)

    def Polyline2D(self, node):
        pontos = re.split(r'[,\s]\s*',node.attrib['lineSegments'])
        polylines = []
        for i in range(0, len(pontos)-2, 2):
            polylines.append([float(pontos[i]), float(pontos[i+1])])
        interface.linhas.append(polylines)            

    def TriangleSet2D(self, node):
        pontos = re.split(r'[,\s]\s*',node.attrib['vertices'])
        for i in range(0, len(pontos)-1, 6):
            interface.poligonos.append([[float(pontos[i  ]), float(pontos[i+1])],
                                        [float(pontos[i+2]), float(pontos[i+3])],
                                        [float(pontos[i+4]), float(pontos[i+5])]])

if __name__ == '__main__':

    x3d = X3D("exemplo1.x3d")
    x3d.set_resolution(30, 20)
    interface = Interface(30, 20)
    x3d.set_interface(interface)

    x3d.parse()

    # Cria imagem
    data = np.zeros((x3d.height, x3d.width, 3), dtype=np.uint8) # cria imagem com fundo preto
    data[1][3] = [255, 0, 0] # altera um pixel da imagem
    data[1][5] = [0, 200, 0] # altera um pixel da imagem
    # Perceba que a matriz é organizada em linhas e colunas, ou seja, y e x

    #renderer.salva_imagem(data, "tela.png")    
    interface.preview(data)