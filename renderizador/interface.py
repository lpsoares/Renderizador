#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Interface Gráfica para Desenvolver e Usuários.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

import time         # Para operações com tempo, como a duração de renderização
import numpy as np  # Para operações matemáticas

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Button, TextBox, CheckButtons
import matplotlib.animation as animation
import matplotlib.patheffects as path_effects


class Interface:
    """Interface para usuário/desenvolvedor verificar resultados da renderização."""

    pontos = []        # pontos a serem desenhados
    linhas = []        # linhas a serem desenhadas
    circulos = []      # circulos a serem desenhados
    poligonos = []     # poligonos a serem desenhados

    last_time = 0      # para calculo de FPS

    def __init__(self, width, height, filename):
        """Inicializa Interface Gráfica."""
        self.width = width
        self.height = height

        self.geometrias = []    # lista de geometrias para controlar exibição
        self.grid = False       # usado para controlar se grid exibido ou não

        self.image_saver = None # recebe função para salvar imagens

        self.fig, self.axes = plt.subplots(num="Renderizador - "+filename)
        self.fig.tight_layout(rect=(0, 0.05, 1, 0.98))

        self.axes.axis([0, width, height, 0])  # [xmin, xmax, ymin, ymax]

        self.axes.xaxis.tick_top()

        # Adaptando número de divisões (ticks) conforme resolução informada
        if max(self.width, self.height) > 400:
            divisions = 100
        elif max(self.width, self.height) > 200:
            divisions = 50
        elif max(self.width, self.height) > 100:
            divisions = 20
        else:
            divisions = 10

        self.axes.xaxis.set_major_locator(MultipleLocator(divisions))
        self.axes.yaxis.set_major_locator(MultipleLocator(divisions))
        self.axes.xaxis.set_minor_locator(MultipleLocator(divisions//10))
        self.axes.yaxis.set_minor_locator(MultipleLocator(divisions//10))

    def annotation(self, points):
        """Desenha texto ao lado dos pontos identificando eles."""
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

    def draw_circles(self, circles, text=False):
        """Exibe contornos de círculos na tela da interface gráfica."""
        radius = circles["radius"]
        color = circles["appearance"].material.emissiveColor

        # desenha o contorno de um círculo
        x_values = [radius * np.sin(np.radians(i)) for i in range(0, 360, 2)]
        y_values = [radius * np.cos(np.radians(i)) for i in range(0, 360, 2)]
        circle, = self.axes.plot(x_values, y_values, marker='', color=color, linestyle="-")
        circle.set_path_effects([path_effects.withStroke(linewidth=3, foreground='black')])
        self.geometrias.append(circle)

        # desenha texto se requisitado
        if text:
            self.annotation([[0,0]]) # Centro sempre no (0,0)

    def draw_triangle(self, triangles, text=False):
        """Exibe triângulos na tela da interface gráfica."""
        points = triangles["vertices"]
        color = triangles["appearance"].material.emissiveColor

        if points:
            # converte pontos
            x_values = [pt[0] for pt in points] + [points[0][0]]
            y_values = [pt[1] for pt in points] + [points[0][1]]

            # desenha as linhas com os pontos  op:"ro-"
            line, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="-")
            self.geometrias.append(line)

            poly, = self.axes.fill(x_values, y_values, color=color+[0.4])
            self.geometrias.append(poly)

            # desenha texto se requisitado
            if text:
                self.annotation(points)

    def exibe_geometrias_grid(self, label):
        """Exibe e esconde as geometrias/grid sobre a tela da interface gráfica."""
        if label == 'Geometria':
            for geometria in self.geometrias:
                geometria.set_visible(not geometria.get_visible())
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        elif label == 'Grid':
            self.grid = not self.grid
            self.axes.grid(self.grid, which='both')
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

    def preview(self, pause, func):
        """Realização a visualização na tela da interface gráfica."""
        extent = (0, self.width, self.height, 0)

        # Coleta o tempo antes da renderização
        start = time.process_time()

        data = func()

        # Calcula o tempo ao concluir a renderização
        elapsed_time = time.process_time() - start

        image = self.axes.imshow(data, interpolation='nearest', extent=extent)

        for pontos in Interface.pontos:
            self.draw_points(pontos, text=True)

        for linha in Interface.linhas:
            self.draw_lines(linha, text=True)

        for circulo in Interface.circulos:
            self.draw_circles(circulo, text=True)

        for poligono in Interface.poligonos:
            self.draw_triangle(poligono, text=True)

        # Inicialmente deixa todas as geometrias escondidas
        for geometria in self.geometrias:
            geometria.set_visible(False)

        # Configura todos os botões da interface
        bgeogrid = CheckButtons(plt.axes([0.78, 0.02, 0.18, 0.10]), ['Grid', 'Geometria'])
        bgeogrid.on_clicked(self.exibe_geometrias_grid)

        bsave = Button(plt.axes([0.4, 0.02, 0.15, 0.06]), 'Salvar')
        bsave.on_clicked(self.save_image)

        # Animação de quadros
        def animate(_frame_number):

            # Executa a função recebida como parâmetro no método principal
            data = func()

            # Atualiza a imagem renderizada
            image.set_array(data)

            # Calcula e atualiza a quantidade de Quadros Por Segundo
            fps = "{:.1f}".format(1/(time.process_time() - Interface.last_time))
            time_box.set_val(fps)
            time_box.cursor_index = len(fps)
            Interface.last_time = time.process_time()

            return image, time_box

        # Para cálculo de FPS
        Interface.last_time = time.process_time()

        # Configura texto da interface
        time_box_pos = plt.axes([0.18, 0.02, 0.15, 0.06])
        if pause:
            time_box = TextBox(time_box_pos, 'Tempo (s) ', initial="{:.4f}".format(elapsed_time))
        else:
            time_box = TextBox(time_box_pos, 'FPS ', initial="0.0")
            _ = animation.FuncAnimation(self.fig, animate, interval=1, blit=False)

        plt.show()
