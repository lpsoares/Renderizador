#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Renderizador X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 28 de Agosto de 2020
"""

import os           # Para rotinas do sistema operacional
import time         # Para operações com tempo, como a duração de renderização
import argparse     # Para tratar os parâmetros da linha de comando

import gl           # Recupera rotinas de suporte ao X3D

import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal

# Deprecated
import rotinas      # Desatualizado possui rotinas antigas de suporte ao X3D (legado)

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
        self.framebuffers = {}

    def setup(self):
        """Configura o sistema para a renderização."""
        # Configurando color buffers para exibição na tela

        # Cria uma (1) posição de FrameBuffer na GPU
        fbo = gpu.GPU.gen_framebuffers(1)

        # Define o atributo FRONT como o FrameBuffe principal
        self.framebuffers["FRONT"] = fbo[0]

        # Define que a posição criada será usada para desenho e leitura
        gpu.GPU.bind_framebuffer(gpu.GPU.FRAMEBUFFER, self.framebuffers["FRONT"])
        # Opções:
        # - DRAW_FRAMEBUFFER: Faz o bind só para escrever no framebuffer
        # - READ_FRAMEBUFFER: Faz o bind só para leitura no framebuffer
        # - FRAMEBUFFER: Faz o bind para leitura e escrita no framebuffer

        # Aloca memória no FrameBuffer para um tipo e tamanho especificado de buffer
        gpu.GPU.framebuffer_storage(
            self.framebuffers["FRONT"],
            gpu.GPU.COLOR_ATTACHMENT,
            gpu.GPU.RGB8,
            self.width,
            self.height
        )
        # Opções:
        # - COLOR_ATTACHMENT: alocações para as cores da imagem renderizada
        # - DEPTH_ATTACHMENT: alocações para as profundidades da imagem renderizada
        # Obs: Você pode chamar duas vezes a rotina com cada tipo de buffer.

        # Tipos de dados:
        # - RGB8: Para canais de cores (Vermelho, Verde, Azul) 8bits cada (0-255)
        # - RGBA8: Para canais de cores (Vermelho, Verde, Azul, Transparência) 8bits cada (0-255)
        # - DEPTH_COMPONENT16: Para canal de Profundidade de 16bits (half-precision) (0-65535)
        # - DEPTH_COMPONENT32F: Para canal de Profundidade de 32bits (single-precision) (float)

        # Define cor que ira apagar o FrameBuffer quando clear_buffer() invocado
        gpu.GPU.clear_color([0, 0, 0])

        # Define a profundidade que ira apagar o FrameBuffer quando clear_buffer() invocado
        # Assuma 1.0 o mais afastado e -1.0 o mais próximo da camera
        gpu.GPU.clear_depth(1.0)

        # Definindo tamanho do Viewport para renderização
        self.scene.viewport(width=self.width, height=self.height)

    def pre(self):
        """Rotinas pré renderização."""
        # Função invocada antes do processo de renderização iniciar.

        # Limpa o frame buffers atual
        gpu.GPU.clear_buffer()

        # Recursos que podem ser úteis:
        # Define o valor do pixel no framebuffer: draw_pixels(coord, mode, data)
        # Retorna o valor do pixel no framebuffer: read_pixels(coord, mode)

    def pos(self):
        """Rotinas pós renderização."""
        # Função invocada após o processo de renderização terminar.

        # Método para a troca dos buffers (NÃO IMPLEMENTADO)
        gpu.GPU.swap_buffers()

    def mapping(self):
        """Mapeamento de funções para as rotinas de renderização."""
        # Rotinas antigas ainda no arquivo rotinas.py
        x3d.X3D.renderer["Polypoint2D"] = rotinas.polypoint2D
        x3d.X3D.renderer["Polyline2D"] = rotinas.polyline2D
        x3d.X3D.renderer["TriangleSet2D"] = rotinas.triangleSet2D
        # Rotinas encapsuladas na classe GL (Graphics Library)
        x3d.X3D.renderer["TriangleSet"] = gl.GL.triangleSet
        x3d.X3D.renderer["Viewpoint"] = gl.GL.viewpoint
        x3d.X3D.renderer["Transform_in"] = gl.GL.transform_in
        x3d.X3D.renderer["Transform_out"] = gl.GL.transform_out
        x3d.X3D.renderer["TriangleStripSet"] = gl.GL.triangleStripSet
        x3d.X3D.renderer["IndexedTriangleStripSet"] = gl.GL.indexedTriangleStripSet
        x3d.X3D.renderer["Box"] = gl.GL.box
        x3d.X3D.renderer["IndexedFaceSet"] = gl.GL.indexedFaceSet

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
        
        self.width = 15
        self.height = 15

        path = os.path.dirname(os.path.abspath(self.x3d_file))

        # Iniciando simulação de GPU
        gpu.GPU(self.image_file, path)

        # Abre arquivo X3D
        self.scene = x3d.X3D(self.x3d_file)

        # Iniciando Biblioteca Gráfica
        gl.GL.setup(
            self.width,
            self.height,
            near=0.01,
            far=1000
        )

        # Funções que irão fazer o rendering
        self.mapping()

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
