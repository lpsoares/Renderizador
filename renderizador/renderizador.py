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

    def setup(self, supersampling=2):
        """Configura os buffers de superamostragem e profundidade."""
        self.supersampling = max(1, int(supersampling))
        sample_width = self.width * self.supersampling
        sample_height = self.height * self.supersampling

        framebuffers = gpu.GPU.gen_framebuffers(2)
        self.framebuffers["FRONT"] = framebuffers[0]
        self.framebuffers["RESOLVED"] = framebuffers[1]

        gpu.GPU.bind_framebuffer(
            gpu.GPU.FRAMEBUFFER, self.framebuffers["FRONT"]
        )
        gpu.GPU.framebuffer_storage(
            self.framebuffers["FRONT"],
            gpu.GPU.COLOR_ATTACHMENT,
            gpu.GPU.RGB8,
            sample_width,
            sample_height,
        )
        gpu.GPU.framebuffer_storage(
            self.framebuffers["FRONT"],
            gpu.GPU.DEPTH_ATTACHMENT,
            gpu.GPU.DEPTH_COMPONENT32F,
            sample_width,
            sample_height,
        )
        gpu.GPU.framebuffer_storage(
            self.framebuffers["RESOLVED"],
            gpu.GPU.COLOR_ATTACHMENT,
            gpu.GPU.RGB8,
            self.width,
            self.height,
        )

        gpu.GPU.clear_color([0, 0, 0])
        gpu.GPU.clear_depth(1.0)

        gl.GL.width = sample_width
        gl.GL.height = sample_height
        gl.GL.sample_rate = self.supersampling

        # TriangleSet2D usa coordenadas absolutas. Este adaptador aplica
        # a grade 2x2 sem modificar a implementação de triangleSet2D().
        triangle_set_2d = x3d.X3D.renderer.get("TriangleSet2D")
        if triangle_set_2d:
            rate = self.supersampling

            def supersampled_triangle_set_2d(vertices, colors):
                scaled = [coordinate * rate for coordinate in vertices]
                triangle_set_2d(vertices=scaled, colors=colors)

            x3d.X3D.renderer["TriangleSet2D"] = (
                supersampled_triangle_set_2d
            )

        self.scene.viewport(width=self.width, height=self.height)

    def pre(self):
        """Limpa os buffers antes de renderizar um quadro."""
        gpu.GPU.bind_framebuffer(
            gpu.GPU.FRAMEBUFFER, self.framebuffers["FRONT"]
        )
        gpu.GPU.clear_buffer()

    def pos(self):
        """Resolve quatro amostras em cada pixel da imagem final."""
        import numpy as np

        samples = gpu.GPU.frame_buffer[
            self.framebuffers["FRONT"]
        ].color
        rate = self.supersampling
        resolved = samples.reshape(
            self.height,
            rate,
            self.width,
            rate,
            samples.shape[2],
        ).mean(axis=(1, 3))

        gpu.GPU.frame_buffer[
            self.framebuffers["RESOLVED"]
        ].color[:] = np.rint(resolved).astype(np.uint8)
        gpu.GPU.bind_framebuffer(
            gpu.GPU.FRAMEBUFFER, self.framebuffers["RESOLVED"]
        )
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
        # Para a animação, uma amostra por pixel evita quadruplicar o custo
        # do rasterizador em todos os quadros. O modo pausado mantém a
        # superamostragem para preservar a qualidade da imagem estática.
        self.setup(supersampling=1 if not args.pause else 2)

        # Se no modo silencioso salvar imagem e não mostrar janela de visualização
        if args.quiet:
            gpu.GPU.save_image()  # Salva imagem em arquivo
        else:
            window.set_saver(gpu.GPU.save_image)  # pasa a função para salvar imagens
            window.preview(args.pause, self.render)  # mostra visualização

if __name__ == '__main__':
    renderizador = Renderizador()
    renderizador.main()
