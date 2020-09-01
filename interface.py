# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 31 de Agosto de 2020

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoLocator
from matplotlib.widgets import Button

# Pillow
from PIL import Image

# GPU
import gpu


class Interface:

    _pontos = []        # pontos a serem desenhados
    _linhas = []        # linhas a serem desenhadas
    _poligonos = []     # poligonos a serem desenhados

    def __init__(self, width, height, file):

        self.width = width
        self.height = height

        self.image_file = file  # nome do arquivo usado para salvar imagem

        self.geometrias = []    # lista de geometrias para controlar exibição
        self.grid = False       # usado para controlar se grid exibido ou não

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

    def draw_points(self, point, text=False):

        points = point["points"]
        color = point["color"]

        # converte pontos
        x_values = [ pt[0] for pt in points ]
        y_values = [ pt[1] for pt in points ]

        # desenha as linhas com os pontos
        dots, = self.ax.plot(x_values, y_values,  marker='o', color=color, linestyle="")  # "ro"
        self.geometrias.append(dots)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_lines(self, lines, text=False):

        points = lines["lines"]
        color = lines["color"]

        # converte pontos
        x_values = [ pt[0] for pt in points ]
        y_values = [ pt[1] for pt in points ]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color=color, linestyle="-")
        self.geometrias.append(line)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_triangle(self, triangles, text=False):
        
        points = triangles["vertices"]
        color = triangles["color"]

        # converte pontos
        x_values = [ pt[0] for pt in points ] + [points[0][0]]
        y_values = [ pt[1] for pt in points ] + [points[0][1]]

        # desenha as linhas com os pontos
        line, = self.ax.plot(x_values, y_values,  marker='o', color=color, linestyle="-")  # "ro-"
        self.geometrias.append(line)

        poly, = self.ax.fill(x_values, y_values, color=color+[0.4]) 
        self.geometrias.append(poly)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

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

    def save_image(self, event): 
        img = Image.fromarray(self.data, 'RGB')
        img.save(self.image_file)


    def preview(self, data):
        
        self.data = data # armazena Frame Buffer

        extent = (0, self.width, self.height, 0)
        imgplot = self.ax.imshow(data, interpolation='nearest', extent=extent)

        for pontos in Interface._pontos:
            self.draw_points(pontos, text=True)

        for linha in Interface._linhas:
            self.draw_lines(linha, text=True)

        for poligono in Interface._poligonos:
            self.draw_triangle(poligono, text=True)

        bgeo = Button(plt.axes([0.8, 0.01, 0.15, 0.06]), 'Geometria')
        bgeo.on_clicked(self.exibe_geometrias)

        bgrid = Button(plt.axes([0.6, 0.01, 0.15, 0.06]), 'Grid')
        bgrid.on_clicked(self.exibe_grid)

        bsave = Button(plt.axes([0.4, 0.01, 0.15, 0.06]), 'Salvar')
        bsave.on_clicked(self.save_image)

        plt.show()