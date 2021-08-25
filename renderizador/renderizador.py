#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Renderizador X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 28 de Agosto de 2020
"""

import time

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import rotinas      # Recupera todas as rotinas de suporte ao X3D

LARGURA = 60  # Valor padrão para largura da tela
ALTURA = 40   # Valor padrão para altura da tela

def main():
    """Executa a renderização."""
    width = LARGURA          # Valores padrão da aplicação
    height = ALTURA          # Valores padrão da aplicação
    x3d_file = ""            # Valores padrão da aplicação
    image_file = "tela.png"  # Valores padrão da aplicação

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    parser.add_argument("-q", "--quiet", help="não exibe janela", action='store_true')
    args = parser.parse_args() # parse the arguments
    if args.input:
        x3d_file = args.input
    if args.output:
        image_file = args.output
    if args.width:
        width = args.width
    if args.height:
        height = args.height

    # Iniciando simulação de GPU
    gpu.GPU(image_file)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)

    # Funções que irão fazer o rendering
    x3d.X3D.renderer["Polypoint2D"] = rotinas.polypoint2D
    x3d.X3D.renderer["Polyline2D"] = rotinas.polyline2D
    x3d.X3D.renderer["TriangleSet2D"] = rotinas.triangleSet2D
    x3d.X3D.renderer["TriangleSet"] = rotinas.triangleSet
    x3d.X3D.renderer["Viewpoint"] = rotinas.viewpoint
    x3d.X3D.renderer["Transform_in"] = rotinas.transform_in
    x3d.X3D.renderer["Transform_out"] = rotinas.transform_out
    x3d.X3D.renderer["TriangleStripSet"] = rotinas.triangleStripSet
    x3d.X3D.renderer["IndexedTriangleStripSet"] = rotinas.indexedTriangleStripSet
    x3d.X3D.renderer["Box"] = rotinas.box
    x3d.X3D.renderer["IndexedFaceSet"] = rotinas.indexedFaceSet

    # Se no modo silencioso não configurar janela de visualização
    if not args.quiet:
        window = interface.Interface(width, height)
        scene.set_preview(window)

    scene.parse()  # carrega os dados do grafo de cena

    # Configura o sistema para a renderização.
    gpu.GPU.set_framebuffer(width=width, height=height, depth=3)
    scene.set_resolution(width=width, height=height)

    # Coleta o tempo antes da renderização
    start = time.process_time()

    # Laço principal de renderização
    rotinas.pre()  # executa rotina pré renderização
    scene.render()  # faz o traversal no grafo de cena
    rotinas.pos()  # executa rotina pós renderização

    # Calcula o tempo ao concluir a renderização
    elapsed_time = time.process_time() - start

    # Se no modo silencioso salvar imagem e não mostrar janela de visualização
    if args.quiet:
        gpu.GPU.save_image()  # Salva imagem em arquivo
    else:
        window.set_saver(gpu.GPU.save_image)  # pasa a função para salvar imagens
        window.preview(gpu.GPU.frame_buffer, elapsed_time)  # mostra janela de visualização


if __name__ == '__main__':
    main()
