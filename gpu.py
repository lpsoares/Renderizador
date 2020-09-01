# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 31 de Agosto de 2020

# Numpy
import numpy as np

class GPU:

    def __init__(self, width, height):
        
        # Mantem largura e altura
        GPU.width = width
        GPU.height = height

        # Cria imagem
        GPU._frame_buffer = np.zeros((height, width, 3), dtype=np.uint8) # cria imagem com fundo preto
    
    def set_pixel(u, v, r, g, b):
        GPU._frame_buffer[v][u] = [r, g, b] # altera um pixel da imagem
        # Perceba que a matriz é organizada em linhas e colunas, ou seja, y e x
