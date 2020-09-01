# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 31 de Agosto de 2020

# Numpy
import numpy as np

# Pillow
from PIL import Image

class GPU:

    def __init__(self, width, height, image_file):

        # Mantem largura e altura
        GPU.width = width
        GPU.height = height
        GPU.image_file = image_file

        # Cria imagem
        GPU._frame_buffer = np.zeros((height, width, 3), dtype=np.uint8) # cria imagem c/fundo preto

    def set_pixel(u, v, r, g, b):
        GPU._frame_buffer[v][u] = [r, g, b] # altera um pixel da imagem
        # Perceba que a matriz é organizada em linhas e colunas, ou seja, y e x

    def save_image():
        img = Image.fromarray(GPU._frame_buffer, 'RGB')
        img.save(GPU.image_file)
