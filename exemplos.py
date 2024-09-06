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
import signal
import time

DIR = "docs/exemplos/"

# List para controlar subprocesses
subprocesses = []

def signal_handler(sig, frame):
    print("Terminating subprocesses...")
    for proc in subprocesses:
        proc.terminate()
    sys.exit(0)

# Registrando sinal para SIGINT
signal.signal(signal.SIGINT, signal_handler)

TESTE = []

# Rasterização 2D
TESTE.append(["aleatorios", "-i", DIR+"2D/pontos/aleatorios/aleatorios.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["linhas_cores", "-i", DIR+"2D/linhas/linhas_cores/linhas_cores.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["octogono", "-i", DIR+"2D/linhas/octogono/octogono.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["linhas_cruzes", "-i", DIR+"2D/linhas/linhas_cruzes/linhas_cruzes.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["varias_linhas", "-i", DIR+"2D/linhas/varias_linhas/varias_linhas.x3d", "-w", "600", "-h", "400", "-p"])
TESTE.append(["circulo", "-i", DIR+"2D/linhas/circulo/circulo.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["triangulos", "-i", DIR+"2D/triangulos/triangulos/triangulos.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["helice", "-i", DIR+"2D/triangulos/helice/helice.x3d", "-w", "30", "-h", "20", "-p"])
TESTE.append(["pontas", "-i", DIR+"2D/triangulos/pontas/pontas.x3d", "-w", "600", "-h", "400", "-p"])

# Triângulos em 3D
TESTE.append(["um_triangulo", "-i", DIR+"3D/malhas/um_triangulo/um_triangulo.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["varios_triangs", "-i", DIR+"3D/malhas/varios_triangs/varios_triangs.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["zoom", "-i", DIR+"3D/malhas/zoom/zoom.x3d", "-w", "300", "-h", "200", "-p"])

# Malhas 3D
TESTE.append(["tiras", "-i", DIR+"3D/malhas/tiras/tiras.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["letras", "-i", DIR+"3D/malhas/letras/letras.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["avatar", "-i", DIR+"3D/grafo_de_cena/avatar/avatar.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["leques", "-i", DIR+"3D/malhas/leques/leques.x3d", "-w", "480", "-h", "320", "-p"])

# Primitivas
TESTE.append(["duas", "-i", DIR+"3D/primitivas/duas/duas.x3d", "-w", "300", "-h", "200", "-p"])

# Z-buffer e Transparência
TESTE.append(["retangulos", "-i", DIR+"3D/malhas/retangulos/retangulos.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["transparente", "-i", DIR+"3D/transparencia/transparente/transparente.x3d", "-w", "300", "-h", "200", "-p"])

# Interpolações de Cores
TESTE.append(["quadrado", "-i", DIR+"3D/cores/quadrado/quadrado.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["flechas", "-i", DIR+"3D/cores/flechas/flechas.x3d", "-w", "480", "-h", "320", "-p"])

# Texturas
TESTE.append(["textura", "-i", DIR+"3D/texturas/textura/textura.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["texturas", "-i", DIR+"3D/texturas/texturas/texturas.x3d", "-w", "300", "-h", "200", "-p"])

# Iluminação
TESTE.append(["difusos", "-i", DIR+"3D/malhas/difusos/difusos.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["caixas", "-i", DIR+"3D/primitivas/caixas/caixas.x3d", "-w", "300", "-h", "200", "-p"])
TESTE.append(["esferas", "-i", DIR+"3D/iluminacao/esferas/esferas.x3d", "-w", "180", "-h", "120", "-p"])

# Animações
TESTE.append(["onda", "-i", DIR+"3D/animacoes/onda/onda.x3d", "-w", "300", "-h", "200"])
TESTE.append(["piramide", "-i", DIR+"3D/animacoes/piramide/piramide.x3d", "-w", "300", "-h", "200"])

# Lista os exemplos registrados (em 3 colunas)
colunas = 4
t = -(len(TESTE)//-colunas)
for i in range(t):
    for j in range(colunas):
        d = i+j*t
        if d < len(TESTE):
            print("{0:2} : {1:15}".format(d, TESTE[d][0]), end="")
    print()

# Se um parâmetro fornecido, usar ele como escolha do exemplo
outra_opcoes = []  # caso usuario passe opções que deverão ser repassadas, por exemplo: --quiet
if len(sys.argv) > 1:
    escolhas = sys.argv[1:]
else:
    escolhas = [input("Escolha o exemplo: ")]

# Verifica se a escolha do exemplo foi por faixa, índice ou argumento da lista
opcoes = []
for escolha in escolhas:
    if ".." in escolha:
        try:
            faixa = escolha.split("..")
            for i in range(int(faixa[0]), int(faixa[1])+1):
                opcoes.append(TESTE[i])
        except:
            sys.exit("Opção inválida!")
    elif escolha.isnumeric():
        numero = int(escolha)
        if 0 <= numero < len(TESTE):
            opcoes.append(TESTE[int(escolha)])
        else:
            sys.exit("Opção inválida!")
    else:
        texto = [element for element in TESTE if element[0] == escolha]
        if len(texto) > 0:
            opcoes.append(texto[0])
        else:
            sys.exit("Opção inválida!")

# Roda renderizador com os parâmetros necessário para o exemplo escolhido
interpreter = sys.executable
for opcao in opcoes:
    print('Abrindo arquivo: "{0}"'.format(opcao[2]))
    print("> ", interpreter, "renderizador/renderizador.py", " ".join(opcao[1:]), "\n")

    proc = subprocess.Popen([interpreter, "renderizador/renderizador.py"] + opcao[1:])
    subprocesses.append(proc)

# Mantem código rodando até que o usuário pressione Ctrl+C
try:
    while True:
        # Verifica se algum subprocesso ainda rodando
        running = any(proc.poll() is None for proc in subprocesses)
        if not running:
            break
        time.sleep(1)
except KeyboardInterrupt:
    signal_handler(signal.SIGINT, None)