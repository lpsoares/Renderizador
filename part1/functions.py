def eqDaReta(x, y, x0, y0, x1, y1):
    """ Função usada para calcular a Equação da Reta"""
    dx = x1 - x0
    dy = y1 - y0

    if (x - x0)*dy - (y - y0)*dx >= 0:
        return True
    
    return False

def inside(x, y, vertices):
    "Função usada para verificar se um píxel esta dentro do triangulo"
    x0, y0 = vertices[0], vertices[1]
    x1, y1 = vertices[2], vertices[3]
    x2, y2 = vertices[4], vertices[5]

    if eqDaReta(x, y, x0, y0, x1, y1) and eqDaReta(x, y, x1, y1, x2, y2) and eqDaReta(x, y, x2, y2, x0, y0):
        return True
    
    return False
