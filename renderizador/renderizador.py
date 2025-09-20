#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Renderizador X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 28 de Agosto de 2020
"""

import os           # Para rotinas do sistema operacional
import argparse     # Para tratar os parâmetros da linha de comando

import gl           # Recupera rotinas de suporte ao X3D

import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import scenegraph   # Imprime o grafo de cena no console

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
        # Fator de super amostragem padrão (2 = 2x2). Pode ser ajustado externamente.
        self.ssaa_factor = 2

    def setup(self):
        """Configura o sistema para a renderização."""
        # Configurando color buffers: podemos ter um framebuffer super (SSAA) e um final (FRONT)
        if self.ssaa_factor > 1:
            fbo = gpu.GPU.gen_framebuffers(2)
            self.framebuffers["SUPER"] = fbo[0]
            self.framebuffers["FRONT"] = fbo[1]
        else:
            fbo = gpu.GPU.gen_framebuffers(1)
            self.framebuffers["FRONT"] = fbo[0]

        # Define que a posição FRONT será usada para leitura final (display)
        gpu.GPU.bind_framebuffer(gpu.GPU.READ_FRAMEBUFFER, self.framebuffers["FRONT"])
        # E SUPER/FRONT para escrita conforme fator
        draw_target = self.framebuffers["SUPER"] if self.ssaa_factor > 1 else self.framebuffers["FRONT"]
        gpu.GPU.bind_framebuffer(gpu.GPU.DRAW_FRAMEBUFFER, draw_target)
        gpu.GPU.bind_framebuffer(gpu.GPU.FRAMEBUFFER, draw_target)  # conveniência para read/write iguais de início
        # Opções:
        # - DRAW_FRAMEBUFFER: Faz o bind só para escrever no framebuffer
        # - READ_FRAMEBUFFER: Faz o bind só para leitura no framebuffer
        # - FRAMEBUFFER: Faz o bind para leitura e escrita no framebuffer

        # Aloca memória no FrameBuffer para um tipo e tamanho especificado de buffer

        target_w = self.width * self.ssaa_factor
        target_h = self.height * self.ssaa_factor
        # Atualiza dimensões da GL para rasterização correta em supersampling
        gl.GL.width = target_w
        gl.GL.height = target_h

        # Se houver supersampling, SUPER é o alvo de renderização; FRONT mantém resolução nativa
        if self.ssaa_factor > 1:
            # SUPER: color + depth em resolução aumentada
            gpu.GPU.framebuffer_storage(
                self.framebuffers["SUPER"],
                gpu.GPU.COLOR_ATTACHMENT,
                gpu.GPU.RGB8,
                target_w,
                target_h
            )
            gpu.GPU.framebuffer_storage(
                self.framebuffers["SUPER"],
                gpu.GPU.DEPTH_ATTACHMENT,
                gpu.GPU.DEPTH_COMPONENT32F,
                target_w,
                target_h
            )
            # FRONT: apenas cor na resolução final
            gpu.GPU.framebuffer_storage(
                self.framebuffers["FRONT"],
                gpu.GPU.COLOR_ATTACHMENT,
                gpu.GPU.RGB8,
                self.width,
                self.height
            )
        else:
            # FRONT único: color + depth
            gpu.GPU.framebuffer_storage(
                self.framebuffers["FRONT"],
                gpu.GPU.COLOR_ATTACHMENT,
                gpu.GPU.RGB8,
                target_w,
                target_h
            )
            gpu.GPU.framebuffer_storage(
                self.framebuffers["FRONT"],
                gpu.GPU.DEPTH_ATTACHMENT,
                gpu.GPU.DEPTH_COMPONENT32F,
                target_w,
                target_h
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

        # Definindo tamanho do Viewport para renderização (usa resolução de render)
        self.scene.viewport(width=target_w, height=target_h)

    def pre(self):
        """Rotinas pré renderização."""
        # Função invocada antes do processo de renderização iniciar.
        # Define framebuffer de desenho correto
        if self.ssaa_factor > 1:
            gpu.GPU.bind_framebuffer(gpu.GPU.FRAMEBUFFER, self.framebuffers["SUPER"])
        else:
            gpu.GPU.bind_framebuffer(gpu.GPU.FRAMEBUFFER, self.framebuffers["FRONT"])
        gpu.GPU.clear_buffer()

        # Recursos que podem ser úteis:
        # Define o valor do pixel no framebuffer: draw_pixel(coord, mode, data)
        # Retorna o valor do pixel no framebuffer: read_pixel(coord, mode)

    def pos(self):
        """Rotinas pós renderização."""
        # Função invocada após o processo de renderização terminar.

        # Essa é uma chamada conveniente para manipulação de buffers
        # ao final da renderização de um frame. Como por exemplo, executar
        # downscaling da imagem.

        # Método para a troca dos buffers (NÃO IMPLEMENTADO)
        # Esse método será utilizado na fase de implementação de animações
        if self.ssaa_factor > 1:
            # Downsample simples (box filter) de SUPER -> FRONT
            super_fb = gpu.GPU.frame_buffer[self.framebuffers["SUPER"]].color
            factor = self.ssaa_factor
            h_super, w_super, _ = super_fb.shape
            # Segurança
            assert w_super == self.width * factor and h_super == self.height * factor
            # Preparar destino
            dest_fb = gpu.GPU.frame_buffer[self.framebuffers["FRONT"]].color
            for y in range(self.height):
                sy0 = y * factor
                sy1 = sy0 + factor
                for x in range(self.width):
                    sx0 = x * factor
                    sx1 = sx0 + factor
                    block = super_fb[sy0:sy1, sx0:sx1]
                    # Média simples
                    avg = block.mean(axis=(0,1))
                    dest_fb[y, x] = avg.astype(dest_fb.dtype)
            # Garantir que leitura ocorra do FRONT
            gpu.GPU.bind_framebuffer(gpu.GPU.READ_FRAMEBUFFER, self.framebuffers["FRONT"])
        else:
            gpu.GPU.bind_framebuffer(gpu.GPU.READ_FRAMEBUFFER, self.framebuffers["FRONT"])
        gpu.GPU.swap_buffers()

    def mapping(self):
        """Mapeamento de funções para as rotinas de renderização."""
        # Rotinas encapsuladas na classe GL (Graphics Library)
        x3d.X3D.renderer["Polypoint2D"] = gl.GL.polypoint2D
        x3d.X3D.renderer["Polyline2D"] = gl.GL.polyline2D
        x3d.X3D.renderer["Circle2D"] = gl.GL.circle2D
        x3d.X3D.renderer["TriangleSet2D"] = gl.GL.triangleSet2D
        x3d.X3D.renderer["TriangleSet"] = gl.GL.triangleSet
        x3d.X3D.renderer["Viewpoint"] = gl.GL.viewpoint
        x3d.X3D.renderer["Transform_in"] = gl.GL.transform_in
        x3d.X3D.renderer["Transform_out"] = gl.GL.transform_out
        x3d.X3D.renderer["TriangleStripSet"] = gl.GL.triangleStripSet
        x3d.X3D.renderer["IndexedTriangleStripSet"] = gl.GL.indexedTriangleStripSet
        x3d.X3D.renderer["IndexedFaceSet"] = gl.GL.indexedFaceSet
        x3d.X3D.renderer["Box"] = gl.GL.box
        x3d.X3D.renderer["Sphere"] = gl.GL.sphere
        x3d.X3D.renderer["Cone"] = gl.GL.cone
        x3d.X3D.renderer["Cylinder"] = gl.GL.cylinder
        x3d.X3D.renderer["NavigationInfo"] = gl.GL.navigationInfo
        x3d.X3D.renderer["DirectionalLight"] = gl.GL.directionalLight
        x3d.X3D.renderer["PointLight"] = gl.GL.pointLight
        x3d.X3D.renderer["Fog"] = gl.GL.fog
        x3d.X3D.renderer["TimeSensor"] = gl.GL.timeSensor
        x3d.X3D.renderer["SplinePositionInterpolator"] = gl.GL.splinePositionInterpolator
        x3d.X3D.renderer["OrientationInterpolator"] = gl.GL.orientationInterpolator

    def render(self):
        """Laço principal de renderização."""
        self.pre()  # executa rotina pré renderização
        self.scene.render()  # faz o traversal no grafo de cena
        self.pos()  # executa rotina pós renderização
        return gpu.GPU.get_frame_buffer()

    def main(self):
        """Executa a renderização."""
        # Tratando entrada de parâmetro
        parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
        parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
        parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
        parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
        parser.add_argument("-h", "--height", help="resolução vertical", type=int)
        parser.add_argument("-g", "--graph", help="imprime o grafo de cena", action='store_true')
        parser.add_argument("-p", "--pause", help="começa simulação em pausa", action='store_true')
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
            window = interface.Interface(self.width, self.height, self.x3d_file)
            self.scene.set_preview(window)

        # carrega os dados do grafo de cena
        if self.scene:
            self.scene.parse()
            if args.graph:
                scenegraph.Graph(self.scene.root)

        # Configura o sistema para a renderização.
        self.setup()

        # Se no modo silencioso salvar imagem e não mostrar janela de visualização
        if args.quiet:
            gpu.GPU.save_image()  # Salva imagem em arquivo
        else:
            window.set_saver(gpu.GPU.save_image)  # pasa a função para salvar imagens
            window.preview(args.pause, self.render)  # mostra visualização

if __name__ == '__main__':
    renderizador = Renderizador()
    renderizador.main()
