#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Simulador de GPU.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# Numpy
import numpy as np

# Pillow
from PIL import Image

class GPU:
    """
    Classe que representa o funcionamento de uma GPU.

    ...

    Atributos
    ----------
    width : int (static)
        largura tela
    height : int (static)
        altura tela
    image_file : str (static)
        nome do arquivo a ser salvo
    framebuffer : numpy.ndarray (static)
        matriz que armazena pixels no formato RGB

    Métodos
    -------
    parse():
        Realiza o parse e já realiza as rotinas de renderização.
    """

    # Constantes a serem usadas com Enum para definir estados
    DRAW_FRAMEBUFFER = 0b01
    READ_FRAMEBUFFER = 0b10
    FRAMEBUFFER = 0b11

    RGB8 = 0b001  # Valores para Vermelho, Verde, Azul de 8bits cada (0-255)
    RGBA8 = 0b010  # Valores para Vermelho, Verde, Azul e Transpareência de 8bits cada (0-255)
    DEPTH_COMPONENT16 = 0b101  # Valores para Profundidade de 16bits cada (0-65535)
    DEPTH_COMPONENT32F = 0b110  # Valores para Profundidade de 32bits em float

    # Atributos estáticos
    width = 60
    height = 40
    image_file = None
    frame_buffer = None

    # Legado, deverá ser REMOVIDO
    width = 1
    height = 1

    def __init__(self, image_file):
        """Define o nome do arquivo para caso se salvar o framebuffer."""
        GPU.image_file = image_file

        # Prepara o Frame Buffer para ser uma matriz NumPy
        GPU.frame_buffer = []

        # Define buffers de leitura e escrita
        GPU.draw_framebuffer = 0
        GPU.read_framebuffer = 0

        # Cor e profundidade padrão para apagar o FrameBuffer
        GPU.clear_color_buffer = [0, 0, 0]
        GPU.clear_depth_buffer = 1.0

    @staticmethod
    def gen_framebuffers(size):
        """Gera posições para FrameBuffers."""
        allocated = []
        for _ in range(size):
            GPU.frame_buffer.append(np.empty([]))
            allocated += [len(GPU.frame_buffer)-1]  # informado a posição recem alocada
        return allocated

    @staticmethod
    def bind_framebuffer(buffer, framebuffer_pos):
        """Define o framebuffer a ser usado e como."""
        if buffer == GPU.DRAW_FRAMEBUFFER:
            GPU.draw_framebuffer = framebuffer_pos
        elif buffer == GPU.READ_FRAMEBUFFER:
            GPU.read_framebuffer = framebuffer_pos
        elif buffer == GPU.FRAMEBUFFER:
            GPU.draw_framebuffer = framebuffer_pos
            GPU.read_framebuffer = framebuffer_pos

    @staticmethod
    def framebuffer_storage(framebuffer_pos, mode, width, height):
        """Aloca o FrameBuffer especificado."""
        # Mantem largura e altura
        if mode == GPU.RGB8:
            dtype = np.uint8
            depth = 3
        elif mode == GPU.RGBA8:
            dtype = np.uint8
            depth = 4
        elif mode == GPU.DEPTH_COMPONENT16:
            dtype = np.uint16
            depth = 1
        elif mode == GPU.DEPTH_COMPONENT32F:
            dtype = np.float32
            depth = 1

        # Aloca espaço definindo todos os valores como 0 (imagem preta)
        GPU.frame_buffer[framebuffer_pos] = np.zeros((height, width, depth), dtype=dtype)

    @staticmethod
    def clear_color(color):
        """Definindo cor para apagar o FrameBuffer."""
        GPU.clear_color_buffer = color

    @staticmethod
    def clear_depth(depth):
        """Definindo profundidade para apagar o FrameBuffer."""
        GPU.clear_depth_buffer = depth

    @staticmethod
    def clear_buffer(buffers):
        """Usa o mesmo valor em todo o FrameBuffer, na prática apagando ele."""
        for buffer in buffers:
            print(GPU.frame_buffer[buffer].dtype)
            if GPU.frame_buffer[buffer].dtype == "uint8":  # Assumindo que é um color buffer
                GPU.frame_buffer[buffer][:] = GPU.clear_color_buffer
            else:  # Assumindo que é um depth buffer (z-buffer)
                GPU.frame_buffer[buffer][:] = GPU.clear_depth_buffer

    # Obsoleto, parar de usar no futuro
    @staticmethod
    def set_pixel(coord_u, coord_v, clr_r, clr_g, clr_b, clr_a=-1):
        """Troca a cor de um pixel no framebuffer."""
        if clr_a >= 0:
            GPU.frame_buffer[GPU.draw_framebuffer][coord_v][coord_u] = [clr_r, clr_g, clr_b, clr_a]
        else:
            GPU.frame_buffer[GPU.draw_framebuffer][coord_v][coord_u] = [clr_r, clr_g, clr_b]

    # Obsoleto, parar de usar no futuro
    @staticmethod
    def set_depth(coord_u, coord_v, depth):
        """Troca a profundidade de um pixel no framebuffer."""
        GPU.frame_buffer[GPU.draw_framebuffer][coord_v][coord_u] = depth

    @staticmethod
    def draw_pixels(coord_u, coord_v, data):
        """Define o valor do pixel no framebuffer."""
        GPU.frame_buffer[GPU.draw_framebuffer][coord_v][coord_u] = data

    @staticmethod
    def read_pixels(coord_u, coord_v):
        """Retorna o valor do pixel no framebuffer."""
        return GPU.frame_buffer[GPU.read_framebuffer][coord_v][coord_u]

    @staticmethod
    def save_image():
        """Método para salvar a imagem do framebuffer em um arquivo."""
        img = Image.fromarray(GPU.frame_buffer[GPU.read_framebuffer], 'RGB')
        img.save(GPU.image_file)

    @staticmethod
    def load_texture(textura):
        """Método para ler textura."""
        imagem = Image.open(textura)
        matriz = np.array(imagem)
        return matriz

    @staticmethod
    def get_frame_buffer():
        """Retorna o Framebuffer atual para leitura."""
        return GPU.frame_buffer[GPU.read_framebuffer]

    @staticmethod
    def swap_buffers():
        """Método para a troca dos buffers (NÃO IMPLEMENTADA)."""
