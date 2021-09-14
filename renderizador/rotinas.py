#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotinas de operação de nós X3D.

Desenvolvido por:
Disciplina: Computação Gráfica
Data:
"""

import gpu          # Simula os recursos de uma GPU

#################################################################################
# NÃO USAR MAIS ESSE ARQUIVO. AS ROTINAS DEVEM SER IMPLEMENTADAS AGORA NO gl.GL #
#################################################################################

# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#Polypoint2D
def polypoint2D(point, colors):
    """Função usada para renderizar Polypoint2D."""
    for i in range(0, int(len(point)), 2):
        gpu.GPU.set_pixel(int(point[i]), int(point[i + 1]), 255 * colors['emissiveColor'][0],
                          255 * colors['emissiveColor'][1], 255 * colors['emissiveColor'][2])

    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
    # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
    # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
    # você pode assumir o desenho dos pontos com a cor emissiva (emissiveColor).

    # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)


# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#Polyline2D
def polyline2D(lineSegments, colors):
    # """Função usada para renderizar Polyline2D."""
    for i in range(0, int(len(lineSegments)), 4):
        x_1 = lineSegments[i]
        y_1 = lineSegments[i + 1]
        x_2 = lineSegments[i + 2]
        y_2 = lineSegments[i + 3]
        u = x_1
        v = y_1
        s = ((y_2 - y_1) / (x_2 - x_1))
        p = 0
        if s > 1:
            p = 1/s
        elif s < -1:
            p = -1/s
        else:
            p = 1
        if x_2 > x_1:
            while x_2 + p > u:
                gpu.GPU.set_pixel(int(u), int(v), 255/2 * colors['emissiveColor'][0],
                          255/2 * colors['emissiveColor'][1], 255/2 * colors['emissiveColor'][2])
                if s > 1:
                    u = u + 1 / s
                    v = v + 1
                elif s < -1:
                    u = u - 1 / s
                    v = v - 1
                else:
                    u = u + 1
                    v = v + s
        else:
            while x_2 - p < u:
                gpu.GPU.set_pixel(int(u), int(v), 255/2 * colors['emissiveColor'][0],
                          255/2 * colors['emissiveColor'][1], 255/2 * colors['emissiveColor'][2])
                if s > 1:
                    u = u - 1 / s
                    v = v - 1
                elif s < -1:
                    u = u + 1 / s
                    v = v + 1
                else:
                    u = u - 1
                    v = v - s

    # Nessa função você receberá os pontos de uma linha no parâmetro lineSegments, esses
    # pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o valor da
    # coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é
    # a coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
    # pelo tamanho da lista. A quantidade mínima de pontos são 2 (4 valores), porém a
    # função pode receber mais pontos para desenhar vários segmentos. Assuma que sempre
    # vira uma quantidade par de valores.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polyline2D
    # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).


def dot(x_A, y_A, x_B, y_B, x_ponto, y_ponto):
    return (y_B - y_A)*x_ponto - (x_B - x_A)*y_ponto + (x_B - x_A)*y_A - (y_B - y_A)*x_A


def inside(x_A, y_A, x_B, y_B, x_C, y_C, x_ponto, y_ponto):
    d1 = dot(x_A, y_A, x_B, y_B, x_ponto, y_ponto)
    d2 = dot(x_B, y_B, x_C, y_C, x_ponto, y_ponto)
    d3 = dot(x_C, y_C, x_A, y_A, x_ponto, y_ponto)
    if dot(x_A, y_A, x_B, y_B, x_ponto, y_ponto) >= 0 and dot(x_B, y_B, x_C, y_C, x_ponto, y_ponto) >= 0 and dot(x_C, y_C, x_A, y_A, x_ponto, y_ponto) >= 0:
        return 1
    else:
        return 0


# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#TriangleSet2D
def triangleSet2D(vertices, colors):
    """Função usada para renderizar TriangleSet2D."""
    for i in range(0, len(vertices), 6):
        x_1 = vertices[i]
        y_1 = vertices[i + 1]
        x_2 = vertices[i + 2]
        y_2 = vertices[i + 3]
        x_3 = vertices[i + 4]
        y_3 = vertices[i + 5]
        minX = x_1
        maxX = x_1
        minY = y_1
        maxY = y_1
        if x_2 > maxX:
            maxX = x_2
        if x_3 > maxX:
            maxX = x_3
        if y_2 > maxY:
            maxY = y_2
        if y_3 > maxY:
            maxY = y_3
        if x_2 < minX:
            minX = x_2
        if x_3 < minX:
            minX = x_3
        if y_2 < minY:
            minY = y_2
        if y_3 < minY:
            minY = y_3

        aliasing = 4

        for x in range(int(minX)*aliasing, int(maxX)*aliasing, aliasing):
            for y in range(int(minY)*aliasing, int(maxY)*aliasing, aliasing):
                sumk = 0
                for kx in range(aliasing):
                    for ky in range(aliasing):
                        sumk += inside(x_1, y_1, x_2, y_2, x_3, y_3, (x + kx) / aliasing, (y + ky) / aliasing)
                sumk = sumk*255/aliasing
                if sumk > 0:
                    gpu.GPU.set_pixel(int(x/aliasing), int(y/aliasing), sumk * colors['emissiveColor'][0],
                                      sumk * colors['emissiveColor'][1], sumk * colors['emissiveColor'][2])



    # Nessa função você receberá os vertices de um triângulo no parâmetro vertices,
    # esses pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o
    # valor da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto.
    # Já point[2] é a coordenada x do segundo ponto e assim por diante. Assuma que a
    # quantidade de pontos é sempre multiplo de 3, ou seja, 6 valores ou 12 valores, etc.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet2D
    # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

