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


class Renderizador:
    """Realiza a renderização da cena informada."""

    def __init__(self):
        """Definindo valores padrão."""
        self.width = LARGURA
        self.height = ALTURA
        self.x3d_file = ""
        self.image_file = "tela.png"
        self.scene = None
        self.fbo = None

    def setup(self):
        """Configura o sistema para a renderização."""
        # Configurando color buffers para exibição na tela

        # Cria uma (1) posição de FrameBuffer na GPU
        self.fbo = gpu.GPU.gen_framebuffers(1)

        # Define que a posição criada será usada para desenho e leitura
        gpu.GPU.bind_framebuffer(gpu.GPU.FRAMEBUFFER, self.fbo[0])

        # Define o tipo e tamanho do buffer
        gpu.GPU.framebuffer_storage(
            self.fbo[0],
            gpu.GPU.RGB8,
            self.width,
            self.height
        )

        # Define cor que ira apagar o FrameBuffer quando clear_buffer() invocado
        gpu.GPU.clear_color([0, 0, 0])

        # Define a profundidade que ira apagar o FrameBuffer quando clear_buffer() invocado
        gpu.GPU.clear_depth(1.0)

        # Definindo tamanho do Viewport para renderização
        self.scene.viewport(width=self.width, height=self.height)

    def pre(self):
        """Rotinas pré renderização."""
        # Função invocada antes do processo de renderização iniciar.

        # Limpa a lista de buffers selecionados
        gpu.GPU.clear_buffer(self.fbo)

        # Recursos que podem ser úteis:
        # Define o valor do pixel no framebuffer: draw_pixels(coord_u, coord_v, data)
        # Retorna o valor do pixel no framebuffer: read_pixels(coord_u, coord_v)

    def pos(self):
        """Rotinas pós renderização."""
        # Função invocada após o processo de renderização terminar.

        # Método para a troca dos buffers (NÃO IMPLEMENTADO)
        gpu.GPU.swap_buffers()

    def main(self):
        """Executa a renderização."""
        # Tratando entrada de parâmetro
        parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
        parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
        parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
        parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
        parser.add_argument("-h", "--height", help="resolução vertical", type=int)
        parser.add_argument("-q", "--quiet", help="não exibe janela", action='store_true')
        args = parser.parse_args() # parse the arguments
        if args.input:
            self.x3d_file = args.input
        if args.output:
            self.image_file = args.output
        if args.width:
            self.width = args.width
        if args.height:
            self.height = args.height

        # Iniciando simulação de GPU
        gpu.GPU(self.image_file)

        # Abre arquivo X3D
        self.scene = x3d.X3D(self.x3d_file)

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
            window = interface.Interface(self.width, self.height)
            self.scene.set_preview(window)

        # carrega os dados do grafo de cena
        if self.scene:
            self.scene.parse()

        # Configura o sistema para a renderização.
        self.setup()

        # Coleta o tempo antes da renderização
        start = time.process_time()

        # Laço principal de renderização
        self.pre()  # executa rotina pré renderização
        self.scene.render()  # faz o traversal no grafo de cena
        self.pos()  # executa rotina pós renderização

        # Calcula o tempo ao concluir a renderização
        elapsed_time = time.process_time() - start

        # Se no modo silencioso salvar imagem e não mostrar janela de visualização
        if args.quiet:
            gpu.GPU.save_image()  # Salva imagem em arquivo
        else:
            window.set_saver(gpu.GPU.save_image)  # pasa a função para salvar imagens
            window.preview(gpu.GPU.get_frame_buffer(), elapsed_time)  # mostra visualização


if __name__ == '__main__':
    renderizador = Renderizador()
    renderizador.main()
