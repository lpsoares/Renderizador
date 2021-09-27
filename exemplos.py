#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Carregador de exemplos X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 17 de Agosto de 2021
"""

import sys
import subprocess

DIR_EXP = "docs/exemplos/"

EXEMPLOS = []

# Exemplos 2D
EXEMPLOS.append(["pontos", "-i", DIR_EXP+"2D/pontos/pontos.x3d", "-w", "30", "-h", "20"])
EXEMPLOS.append(["linhas", "-i", DIR_EXP+"2D/linhas/linhas.x3d", "-w", "30", "-h", "20"])
EXEMPLOS.append(["octogono", "-i", DIR_EXP+"2D/linhas/octogono.x3d", "-w", "30", "-h", "20"])
EXEMPLOS.append(["var_lin", "-i", DIR_EXP+"2D/linhas/varias_linhas.x3d", "-w", "600", "-h", "400"])
EXEMPLOS.append(["tri_2D", "-i", DIR_EXP+"2D/triangulos/triangulos.x3d", "-w", "30", "-h", "20"])
EXEMPLOS.append(["helice", "-i", DIR_EXP+"2D/triangulos/helice.x3d", "-w", "30", "-h", "20"])

# Exemplos 3D
EXEMPLOS.append(["tri_3D", "-i", DIR_EXP+"3D/triangulos/triang3d.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["tira_tri", "-i", DIR_EXP+"3D/triangulos/tiratrig.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["box", "-i", DIR_EXP+"3D/box/box.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["cores", "-i", DIR_EXP+"3D/cores/cores.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["letras", "-i", DIR_EXP+"3D/cores/letras.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["textura", "-i", DIR_EXP+"3D/texturas/textura.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["retang", "-i", DIR_EXP+"3D/retangulos/retangulos.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["avatar", "-i", DIR_EXP+"3D/avatar/avatar.x3d", "-w", "300", "-h", "200"])
EXEMPLOS.append(["texturas", "-i", DIR_EXP+"3D/texturas/texturas.x3d", "-w", "300", "-h", "200"])

# Lista os exemplos registrados
for i, titulo in enumerate(EXEMPLOS):
    print("{0} : {1}".format(i, titulo[0]))

# Se um parâmetro fornecido, usar ele como escolha do exemplo
if len(sys.argv) > 1:
    escolha = sys.argv[1]
else:
    escolha = input("Escolha o exemplo: ")

# Verifica se a escolha do exemplo foi pelo índice ou primeiro argumento da lista
if escolha.isnumeric():
    opcoes = EXEMPLOS[int(escolha)]
else:
    opcoes = [element for element in EXEMPLOS if element[0] == escolha][0]

# Roda renderizador com os parâmetros necessário para o exemplo escolhido
subprocess.call(["python3", "renderizador/renderizador.py"] + opcoes[1:])
    
