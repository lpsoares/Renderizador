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

DIR = "docs/exemplos/"

TESTE = []

# Exemplos 2D
TESTE.append(["pontos", "-i", DIR+"2D/pontos/pontos.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["linhas", "-i", DIR+"2D/linhas/linhas.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["octogono", "-i", DIR+"2D/linhas/octogono.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["var_lin", "-i", DIR+"2D/linhas/varias_linhas.x3d", "-w", "600", "-h", "400", "-p"])
TESTE.append(["tri_2D", "-i", DIR+"2D/triangulos/triangulos.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["helice", "-i", DIR+"2D/triangulos/helice.x3d", "-w", "30", "-h", "20", "-p"])

# Exemplos 3D
TESTE.append(["tri_3D", "-i", DIR+"3D/triangulos/triang3d.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["tira_tri", "-i", DIR+"3D/triangulos/tiratrig.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["box", "-i", DIR+"3D/box/box.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["cores", "-i", DIR+"3D/cores/cores.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["letras", "-i", DIR+"3D/cores/letras.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["textura", "-i", DIR+"3D/texturas/textura.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["retang", "-i", DIR+"3D/retangulos/retangulos.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["avatar", "-i", DIR+"3D/avatar/avatar.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["texturas", "-i", DIR+"3D/texturas/texturas.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["esferas", "-i", DIR+"3D/iluminacao/esferas.x3d", "-w", "180", "-h", "120", "-p"])
TESTE.append(["onda", "-i", DIR+"3D/animacoes/onda.x3d", "-w", "300", "-h", "200"])
TESTE.append(["piramide", "-i", DIR+"3D/animacoes/piramide.x3d", "-w", "300", "-h", "200"])

# Lista os exemplos registrados
for i, titulo in enumerate(TESTE):
    print("{0} : {1}".format(i, titulo[0]))

# Se um parâmetro fornecido, usar ele como escolha do exemplo
outra_opcoes = []  # caso usuario passe opções que deverão ser repassadas, por exemplo: --quiet
if len(sys.argv) > 1:
    escolha = sys.argv[1]
    if len(sys.argv) > 1:
        outra_opcoes = sys.argv[2:]
else:
    escolha = input("Escolha o exemplo: ")

# Verifica se a escolha do exemplo foi pelo índice ou primeiro argumento da lista
if escolha.isnumeric():
    opcoes = TESTE[int(escolha)]
else:
    opcoes = [element for element in TESTE if element[0] == escolha][0]

# Roda renderizador com os parâmetros necessário para o exemplo escolhido
print("Abrindo arquivo: {0}".format(opcoes[2]))
subprocess.call(["python3", "renderizador/renderizador.py"] + opcoes[1:])
