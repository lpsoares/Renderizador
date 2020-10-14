import numpy as np

# Defina o tamanhã da tela que melhor sirva para perceber a renderização
LARGURA, ALTURA = 400, 200

viewpoint_matrixes = []

# 'transform_matrix' inicia com o valor da matriz identidade pois os valores das coordenadas do objeto
# não devem ser alterados caso não haja transformações
transform_matrix = np.matrix([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ])

# 'stack' é a pilha que armazena os resultados de 'transform_matrix'
stack = []

"""
matrix = np.matrix([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ])
"""