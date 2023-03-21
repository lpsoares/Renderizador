#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Simulador de GPU.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

import os           # Para rotinas do sistema operacional

# Numpy
import numpy as np

# Pillow
from PIL import Image

class FrameBuffer:
    """Organiza objetos FrameBuffer (FrameBuffer Objects)."""

    def __init__(self):
        """Iniciando propriedades do FramBuffer."""
        self.color = np.empty(0)
        self.depth = np.empty(0)


class GPU:
    """Classe que representa o funcionamento de uma GPU."""

    # Constantes a serem usadas com Enum para definir estados
    DRAW_FRAMEBUFFER = 0b01
    READ_FRAMEBUFFER = 0b10
    FRAMEBUFFER = 0b11

    RGB8 = 0b001  # Valores para Vermelho, Verde, Azul de 8bits cada (0-255)
    RGBA8 = 0b010  # Valores para Vermelho, Verde, Azul e Transpareência de 8bits cada (0-255)
    DEPTH_COMPONENT16 = 0b101  # Valores para Profundidade de 16bits cada (0-65535)
    DEPTH_COMPONENT32F = 0b110  # Valores para Profundidade de 32bits em float

    COLOR_ATTACHMENT = 0  # Para FrameBuffer Object identificar memória de imagem de cores
    DEPTH_ATTACHMENT = 1  # Para FrameBuffer Object identificar memória de imagem de profundidade

    # Atributos estáticos
    image_file = None
    frame_buffer = None
    path = "."

    def __init__(self, image_file, path):
        """Define o nome do arquivo para caso se salvar o framebuffer."""
        GPU.image_file = image_file

        # Inicia lista para objetos Frame Buffer
        GPU.frame_buffer = []

        # Define buffers de leitura e escrita
        GPU.draw_framebuffer = 0
        GPU.read_framebuffer = 0

        # Cor e profundidade padrão para apagar o FrameBuffer
        GPU.clear_color_val = [0, 0, 0]
        GPU.clear_depth_val = 1.0

        # Caminho para arquivos adicionais, como texturas
        GPU.path = path

    @staticmethod
    def gen_framebuffers(size):
        """Gera posições para FrameBuffers."""
        allocated = []
        for _ in range(size):
            fbo = FrameBuffer()
            GPU.frame_buffer.append(fbo)
            allocated += [len(GPU.frame_buffer)-1]  # informado a posição recem alocada
        return allocated

    @staticmethod
    def bind_framebuffer(buffer, position):
        """Define o framebuffer a ser usado e como."""
        if buffer == GPU.DRAW_FRAMEBUFFER:
            GPU.draw_framebuffer = position
        elif buffer == GPU.READ_FRAMEBUFFER:
            GPU.read_framebuffer = position
        elif buffer == GPU.FRAMEBUFFER:
            GPU.draw_framebuffer = position
            GPU.read_framebuffer = position

    @staticmethod
    def framebuffer_storage(position, attachment, mode, width, height):
        """Aloca o FrameBuffer especificado."""
        if attachment == GPU.COLOR_ATTACHMENT:
            if mode == GPU.RGB8:
                dtype = np.uint8
                depth = 3
            else:  # mode == GPU.RGBA8:
                dtype = np.uint8
                depth = 4
            # Aloca espaço definindo todos os valores como 0 (imagem preta)
            GPU.frame_buffer[position].color = np.zeros((height, width, depth), dtype=dtype)
        elif attachment == GPU.DEPTH_ATTACHMENT:
            if mode == GPU.DEPTH_COMPONENT16:
                dtype = np.uint16
                depth = 1
            else:  # mode == GPU.DEPTH_COMPONENT32F:
                dtype = np.float32
                depth = 1
            # Aloca espaço definindo todos os valores como 1 (profundidade máxima)
            GPU.frame_buffer[position].depth = np.ones((height, width, depth), dtype=dtype)

    @staticmethod
    def clear_color(color):
        """Definindo cor para apagar o FrameBuffer."""
        GPU.clear_color_val = color

    @staticmethod
    def clear_depth(depth):
        """Definindo profundidade para apagar o FrameBuffer."""
        GPU.clear_depth_val = depth

    @staticmethod
    def clear_buffer():
        """Usa o mesmo valor em todo o FrameBuffer, na prática apagando ele."""
        if GPU.frame_buffer[GPU.draw_framebuffer].color.size != 0:
            GPU.frame_buffer[GPU.draw_framebuffer].color[:] = GPU.clear_color_val
        if GPU.frame_buffer[GPU.draw_framebuffer].depth.size != 0:
            GPU.frame_buffer[GPU.draw_framebuffer].depth[:] = GPU.clear_depth_val

    @staticmethod
    def draw_pixel(coord, mode, data):
        """Define o valor do pixel no framebuffer."""
        if coord and data:
            fb_dim = GPU.frame_buffer[GPU.draw_framebuffer].color.shape
            if coord[0] < 0 or coord[0] >= fb_dim[1] or coord[1] < 0 or coord[1] >= fb_dim[0]:
                raise Exception(f"Acesso irregular a posição [{coord[0]}, {coord[1]}] do Framebuffer {fb_dim[1], fb_dim[0]}")
            if mode in (GPU.RGB8, GPU.RGBA8):  # cores
                if GPU.frame_buffer[GPU.draw_framebuffer].color.size != 0:
                    GPU.frame_buffer[GPU.draw_framebuffer].color[coord[1]][coord[0]] = data
                else:
                    raise Exception(f"Frame buffer {GPU.draw_framebuffer} não alocado para o canal de cor")
            elif mode in (GPU.DEPTH_COMPONENT16, GPU.DEPTH_COMPONENT32F):  # profundidade
                if GPU.frame_buffer[GPU.draw_framebuffer].depth.size != 0:
                    GPU.frame_buffer[GPU.draw_framebuffer].depth[coord[1]][coord[0]] = data
                else:
                    raise Exception(f"Frame buffer {GPU.draw_framebuffer} não alocado para o canal de profundidade")

    @staticmethod
    def read_pixel(coord, mode):
        """Retorna o valor do pixel no framebuffer."""
        if coord:
            fb_dim = GPU.frame_buffer[GPU.read_framebuffer].color.shape
            if coord[0] < 0 or coord[0] >= fb_dim[1] or coord[1] < 0 or coord[1] >= fb_dim[0]:
                raise Exception(f"Acesso irregular de leitura na posição [{coord[0]}, {coord[1]}] do Framebuffer {fb_dim[1], fb_dim[0]}")
            if mode in (GPU.RGB8, GPU.RGBA8):  # cores
                if GPU.frame_buffer[GPU.draw_framebuffer].color.size != 0:
                    data = GPU.frame_buffer[GPU.read_framebuffer].color[coord[1]][coord[0]]
                else:
                    raise Exception(f"Frame buffer {GPU.draw_framebuffer} não alocado para o canal de cor")
            elif mode in (GPU.DEPTH_COMPONENT16, GPU.DEPTH_COMPONENT32F):  # profundidade
                if GPU.frame_buffer[GPU.draw_framebuffer].depth.size != 0:
                    data = GPU.frame_buffer[GPU.read_framebuffer].depth[coord[1]][coord[0]]
                else:
                    raise Exception(f"Frame buffer {GPU.draw_framebuffer} não alocado para o canal de profundidade")
            return data

    @staticmethod
    def save_image():
        """Método para salvar a imagem do framebuffer em um arquivo."""
        if GPU.frame_buffer[GPU.read_framebuffer].color.shape[2] == 3:
            img = Image.fromarray(GPU.frame_buffer[GPU.read_framebuffer].color, 'RGB')
        else:
            img = Image.fromarray(GPU.frame_buffer[GPU.read_framebuffer].color, 'RGBA')
        counter = 0
        filename = GPU.image_file.split('.')
        while os.path.exists(filename[0]+str(counter).zfill(3)+'.'+filename[1]):
            counter += 1
        img.save(filename[0]+str(counter).zfill(3)+'.'+filename[1])

    @staticmethod
    def load_texture(textura):
        """Método para ler textura."""
        file = os.path.join(GPU.path, textura)
        imagem = Image.open(file)
        matriz = np.array(imagem)
        return matriz

    @staticmethod
    def get_frame_buffer():
        """Retorna o Framebuffer atual para leitura."""
        return GPU.frame_buffer[GPU.read_framebuffer].color

    @staticmethod
    def swap_buffers():
        """Método para a troca dos buffers (NÃO IMPLEMENTADA)."""
