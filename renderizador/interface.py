#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Interface Gráfica para Desenvolver e Usuários.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Button, TextBox

class Interface:
    """Interface para usuário/desenvolvedor verificar resultados da renderização."""

    pontos = []        # pontos a serem desenhados
    linhas = []        # linhas a serem desenhadas
    poligonos = []     # poligonos a serem desenhados

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.geometrias = []    # lista de geometrias para controlar exibição
        self.grid = False       # usado para controlar se grid exibido ou não

        self.image_saver = None # recebe função para salvar imagens

        self.fig, self.axes = plt.subplots(num="Renderizador")
        #self.axes.set_title('Renderizador')

        self.axes.axis([0, width, height, 0])  # [xmin, xmax, ymin, ymax]
        #self.axes.set_xlabel('x')
        #self.axes.set_ylabel('y')
        #self.axes.xaxis.set_label_position('top')

        self.axes.xaxis.tick_top()

        # o tamanho do gris é 1x1 para ser do tamanho do pixel
        # mostrando de 10 em 10 o posicionamento dos pixels
        self.axes.xaxis.set_major_locator(MultipleLocator(10))
        self.axes.yaxis.set_major_locator(MultipleLocator(10))
        self.axes.xaxis.set_minor_locator(MultipleLocator(1))
        self.axes.yaxis.set_minor_locator(MultipleLocator(1))

    def annotation(self, points):
        """Desenha texto ao lando dos pontos identificando eles."""
        dist_label = 5 # distância do label para o ponto
        for i, pos in enumerate(points):
            text = self.axes.annotate("P{0}".format(i), xy=pos, xytext=(dist_label, dist_label),
                                      textcoords='offset points', color='lightgray')
            self.geometrias.append(text)

    def draw_points(self, point, text=False):
        """Exibe pontos na tela da interface gráfica."""
        points = point["points"]
        color = point["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points]
        y_values = [pt[1] for pt in points]

        # desenha as linhas com os pontos
        dots, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="")  # "ro"
        self.geometrias.append(dots)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_lines(self, lines, text=False):
        """Exibe linhas na tela da interface gráfica."""
        points = lines["lines"]
        color = lines["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points]
        y_values = [pt[1] for pt in points]

        # desenha as linhas com os pontos
        line, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="-")
        self.geometrias.append(line)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_triangle(self, triangles, text=False):
        """Exibe triângulos na tela da interface gráfica."""
        points = triangles["vertices"]
        color = triangles["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points] + [points[0][0]]
        y_values = [pt[1] for pt in points] + [points[0][1]]

        # desenha as linhas com os pontos
        line, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="-")  # "ro-"
        self.geometrias.append(line)

        poly, = self.axes.fill(x_values, y_values, color=color+[0.4])
        self.geometrias.append(poly)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def exibe_geometrias(self, _event):
        """Exibe e esconde as geometrias sobre a tela da interface gráfica."""
        for geometria in self.geometrias:
            geometria.set_visible(not geometria.get_visible())
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def exibe_grid(self, _event):
        """Exibe e esconde o grid de pixels sobre a tela da interface gráfica."""
        self.grid = not self.grid
        self.axes.grid(b=self.grid, which='both')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_saver(self, image_saver):
        """Define função para salvar imagens."""
        self.image_saver = image_saver

    def save_image(self, _event):
        """Salva imagens."""
        if self.image_saver:
            print("Salvando imagem")
            self.image_saver()

    def preview(self, data, time):
        """Realização a visualização na tela da interface gráfica."""
        extent = (0, self.width, self.height, 0)
        self.axes.imshow(data, interpolation='nearest', extent=extent)

        for pontos in Interface.pontos:
            self.draw_points(pontos, text=True)

        for linha in Interface.linhas:
            self.draw_lines(linha, text=True)

        for poligono in Interface.poligonos:
            self.draw_triangle(poligono, text=True)

        # Configura texto da interface

        axbox = plt.axes([0.18, 0.02, 0.15, 0.06])
        TextBox(axbox, 'Tempo (s) ', initial="{:.4f}".format(time))

        # Configura todos os botões da interface

        bgeo = Button(plt.axes([0.8, 0.02, 0.15, 0.06]), 'Geometria')
        bgeo.on_clicked(self.exibe_geometrias)

        bgrid = Button(plt.axes([0.6, 0.02, 0.15, 0.06]), 'Grid')
        bgrid.on_clicked(self.exibe_grid)

        bsave = Button(plt.axes([0.4, 0.02, 0.15, 0.06]), 'Salvar')
        bsave.on_clicked(self.save_image)

        plt.show()
