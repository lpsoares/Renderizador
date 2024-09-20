#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Carregador de exemplos X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 17 de Agosto de 2021
"""

import subprocess
import time
import json
import os
import signal
import sys

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

# Load the JSON data
with open('docs/exemplos.json', 'r') as f:
    data = json.load(f)

# Populate the TESTE list based on the JSON data
for section in data['examples']:
    for example in section['examples']:
        path = example['path']
        x3d = example['x3d']
        w = str(example.get('width', 640))
        h = str(example.get('height', 480))
        p = example.get('pause', False)
        TESTE.append([x3d, "-i", os.path.join(DIR, path, f"{x3d}/{x3d}.x3d"), "-w", w, "-h", h]  + (["-p"] if p else []))


# Lista os exemplos registrados (em 3 colunas)
colunas = 4
t = -(len(TESTE)//-colunas)
for i in range(t):
    for j in range(colunas):
        d = i+j*t
        if d < len(TESTE):
            print("{0:2}: {1:15}".format(d, TESTE[d][0]), end="")
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