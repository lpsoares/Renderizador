#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Parser X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# XML
import xml.etree.ElementTree as ET

# Outras
import re
import math

def clean(child):
    """Recebe um nó XML e remove dele o namespace do atributo tag se houver."""
    _, _, child.tag = child.tag.rpartition('}') # remove os namespaces

class X3D:
    """
    Classe responsável por fazer o parsing do arquivo X3D.

    ...

    Atributos
    ----------
    root : Element
        raiz do grafo de cena X3D em XMl
    width : int
        largura tela que será renderizada (deprecated)
    height : int
        altura tela que será renderizada (deprecated)

    current_color : {list[3]} (static)
        dicionário com as cores no formato RGB usadas no momento ["diffuseColor", "emissiveColor"]
    preview : interface (static)
         sistema de preview para geometrias 2D simples
    render : {} (static)
        dicionario dos métodos de renderização

    Métodos
    -------
    parse():
        Realiza o parse e já realiza as rotinas de renderização.
    """

    current_color = {  # controle de cor instantânea
        "diffuseColor": [0.8, 0.8, 0.8],
        "emissiveColor": [0.0, 0.0, 0.0]
    }
    current_texture = []  # controle de texturas instantâneas
    preview = None  # atributo que aponta para o sistema de preview
    render = {}  # dicionario dos métodos de renderização

    def __init__(self, filename):
        """Constroi o atributo para a raiz do grafo X3D."""
        self.root = ET.parse(filename).getroot()
        self.width = 640  # Valor padrão de largura da tela
        self.height = 480  # Valor padrão de altura da tela
        self.scene = None  # Referência para o objeto da cena

    def set_preview(self, preview):
        """Armazena as rotinas para fazer o render da cena."""
        X3D.preview = preview

    def set_resolution(self, width, height):
        """Armazena a largura e altura de janela de renderização."""
        self.width = width
        self.height = height

    def parse(self):
        """Leitura e render da cena começando da raiz do X3D."""
        for child in self.root:
            clean(child) # remove namespace
            if child.tag == "Scene":
                self.scene = Scene(child)

class Scene:
    """O nó Scene acomoda a cena X3D."""

    def __init__(self, node):
        self.children = []
        for child in node: # garante pegar o Viewpoint primeiro que tudo
            clean(child) # remove namespace
            if child.tag == "Viewpoint":
                self.children.append(Viewpoint(child))
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Transform":
                self.children.append(Transform(child))

# Core component

class X3DNode:
    """Nó abstrato que é o tipo base para todos os nós no sistema X3D."""

class X3DChildNode(X3DNode):
    """Nó abstrato como base para campos children, addChildren, and removeChildren."""

class X3DBindableNode(X3DChildNode):
    """X3DBindableNode é o tipo base abstrato para certos tipos de objetos."""


# Grouping component

class X3DGroupingNode(X3DChildNode):
    """Nó abstrato indica que os tipos de nós concretos derivados dele contêm nós filhos."""

    def __init__(self):
        super().__init__() # Chama construtor da classe pai
        self.children = []

class Transform(X3DGroupingNode):
    """Nó de agrupamento que define um sistema de coordenadas para seus nós filhos."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.rotation = [0, 0, 1, 0]
        self.scale = [1, 1, 1]
        self.translation = [0, 0, 0]

        if 'rotation' in node.attrib:
            rotation_str = re.split(r'[,\s]\s*', node.attrib['rotation'])
            self.rotation = [float(value) for value in rotation_str]

        if 'scale' in node.attrib:
            scale_str = re.split(r'[,\s]\s*', node.attrib['scale'])
            self.scale = [float(value) for value in scale_str]

        if 'translation' in node.attrib:
            translation_str = re.split(r'[,\s]\s*', node.attrib['translation'])
            self.translation = [float(value) for value in translation_str]

        # Render
        if "Transform" in X3D.render:
            X3D.render["Transform"](translation=self.translation,
                                    scale=self.scale,
                                    rotation=self.rotation)

        for child in node:
            clean(child) # remove namespace
            if child.tag == "Shape":
                self.children.append(Shape(child))
            elif child.tag == "Transform":
                self.children.append(Transform(child))

        if "_Transform" in X3D.render:
            X3D.render["_Transform"]()


# Shape component

class X3DShapeNode(X3DChildNode):
    """Este é o tipo de nó base para todos os nós do tipo Shape."""

    def __init__(self):
        super().__init__() # Chama construtor da classe pai
        self.geometry = None
        self.appearance = None

class X3DAppearanceNode(X3DNode):
    """Este é o tipo de nó básico para todos os nós do tipo Appearance."""

class X3DMaterialNode():
    """Este é o tipo de nó básico para todos os nós do tipo Material."""

class Material(X3DMaterialNode):
    """Especifica propriedades do material de superfícies para nós de geometria associados."""

    def __init__(self, node):
        super().__init__()  # Chama construtor da classe pai
        self.diffuseColor = [0.8, 0.8, 0.8]  # Valor padrão
        self.emissiveColor = [0.0, 0.0, 0.0]  # Valor padrão
        if 'diffuseColor' in node.attrib:
            diffuseColor_str = re.split(r'[,\s]\s*', node.attrib['diffuseColor'])
            self.diffuseColor = [float(color) for color in diffuseColor_str]
        if 'emissiveColor' in node.attrib:
            emissiveColor_str = re.split(r'[,\s]\s*', node.attrib['emissiveColor'])
            self.emissiveColor = [float(color) for color in emissiveColor_str]
        X3D.current_color["diffuseColor"] = self.diffuseColor
        X3D.current_color["emissiveColor"] = self.emissiveColor

class X3DAppearanceChildNode(X3DNode):
    """Este é o tipo de nó básico para todos os nós do tipo X3DAppearanceNode."""

class X3DTextureNode(X3DAppearanceChildNode):
    """Nó abstrato base para todos os tipos de nó que especificam imagens de textura."""

class X3DTexture2DNode(X3DTextureNode):
    """Nó abstrato base para todos os tipos de nó que especificam imagens 2D de textura."""

class ImageTexture(X3DTexture2DNode):
    """Define mapa de textura para um arquivo de imagem e parâmetros gerais de mapeamento."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.url = []
        if 'url' in node.attrib:
            url_list = re.split(r'[,\s]\s*', node.attrib['url'])
            self.url = [addr.replace('"', '').replace("'", '') for addr in url_list if addr != '']
        X3D.current_texture = self.url

class Appearance(X3DAppearanceNode):
    """Especifica as propriedades visuais da geometria."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.material = None
        self.imageTexture = None
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Material":
                self.material = Material(child)
            if child.tag == "ImageTexture":
                self.imageTexture = ImageTexture(child)

class Shape(X3DShapeNode):
    """Define aparência e geometria, que são usados para criar objetos renderizados."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Appearance":
                self.appearance = Appearance(child)
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Polypoint2D":
                self.geometry = Polypoint2D(child)
            elif child.tag == "Polyline2D":
                self.geometry = Polyline2D(child)
            elif child.tag == "TriangleSet2D":
                self.geometry = TriangleSet2D(child)
            elif child.tag == "TriangleSet":
                self.geometry = TriangleSet(child)
            elif child.tag == "TriangleStripSet":
                self.geometry = TriangleStripSet(child)
            elif child.tag == "IndexedTriangleStripSet":
                self.geometry = IndexedTriangleStripSet(child)
            elif child.tag == "Box":
                self.geometry = Box(child)
            elif child.tag == "IndexedFaceSet":
                self.geometry = IndexedFaceSet(child)


# Rendering component

class X3DGeometryNode(X3DNode):
    """Este é o tipo de nó base para todas as geometrias em X3D."""

class X3DComposedGeometryNode(X3DGeometryNode):
    """Este é o tipo de nó base para toda a geometria 3D composta em X3D."""

class X3DGeometricPropertyNode(X3DNode):
    """Nó base para todos os tipos de nós de propriedades geométricas definidos no X3D."""

class X3DCoordinateNode(X3DGeometricPropertyNode):
    """Nó base para todos os tipos de nós de coordenadas em X3D."""

class X3DColorNode(X3DGeometricPropertyNode):
    """Nó básico para especificações de cores no X3D."""

class Coordinate(X3DCoordinateNode):
    """Define um conjunto de coordenadas 3D para nós de geometria baseada em vértices."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        point_str = re.split(r'[,\s]\s*', node.attrib['point'].strip())
        self.point = [float(p) for p in point_str]

class Color(X3DColorNode):
    """Define um conjunto de cores RGB a serem usadas nos campos de outro nó."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        color_str = re.split(r'[,\s]\s*', node.attrib['color'].strip())
        self.color = [float(p) for p in color_str]

# Geometry2D component

class Polypoint2D(X3DGeometryNode):
    """Pontos exibidos por um conjunto de vértices no sistema de coordenadas 2D."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        point_str = re.split(r'[,\s]\s*', node.attrib['point'].strip())
        self.point = [float(p) for p in point_str]

        # Preview
        if X3D.preview:
            polypoint2D = []
            for i in range(0, len(self.point), 2):
                polypoint2D.append([self.point[i], self.point[i+1]])
            X3D.preview._pontos.append({'color': X3D.current_color, 'points': polypoint2D})

        # Render
        if "Polypoint2D" in X3D.render:
            X3D.render["Polypoint2D"](point=self.point, color=X3D.current_color)

class Polyline2D(X3DGeometryNode):
    """Série de segmentos de linha contíguos no sistema de coordenadas 2D."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        lineSegments_str = re.split(r'[,\s]\s*', node.attrib['lineSegments'].strip())
        self.lineSegments = [float(point) for point in lineSegments_str]

        # Preview
        if X3D.preview:
            polyline2D = []
            for i in range(0, len(self.lineSegments), 2):
                polyline2D.append([self.lineSegments[i], self.lineSegments[i+1]])
            X3D.preview._linhas.append({'color': X3D.current_color, 'lines': polyline2D})

        # Render
        if "Polyline2D" in X3D.render:
            X3D.render["Polyline2D"](lineSegments=self.lineSegments, color=X3D.current_color)

class TriangleSet2D(X3DGeometryNode):
    """Especifica um conjunto de triângulos no sistema de coordenadas 2D local."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        vertices_str = re.split(r'[,\s]\s*', node.attrib['vertices'].strip())
        self.vertices = [float(point) for point in vertices_str]

        # Preview
        if X3D.preview:
            for i in range(0, len(self.vertices), 6):
                X3D.preview._poligonos.append({'color': X3D.current_color,
                                               'vertices': [[self.vertices[i], self.vertices[i+1]],
                                                            [self.vertices[i+2], self.vertices[i+3]],
                                                            [self.vertices[i+4], self.vertices[i+5]]]})

        # Render
        if "TriangleSet2D" in X3D.render:
            X3D.render["TriangleSet2D"](vertices=self.vertices, color=X3D.current_color)

class TriangleSet(X3DComposedGeometryNode):
    """Representa uma forma 3D que representa uma coleção de triângulos individuais."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.coord = None
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Coordinate":
                self.coord = Coordinate(child)

        # Preview
        # Implemente se desejar

        # Render
        if "TriangleSet" in X3D.render:
            X3D.render["TriangleSet"](point=self.coord.point, color=X3D.current_color)

class TriangleStripSet(X3DComposedGeometryNode):
    """Representa uma forma 3D composta por faixas de triângulos."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.coord = None
        self.stripCount = []

        stripCount_str = re.split(r'[,\s]\s*', node.attrib['stripCount'].strip())
        self.stripCount = [int(point) for point in stripCount_str]

        for child in node:
            clean(child) # remove namespace
            if child.tag == "Coordinate":
                self.coord = Coordinate(child)

        # Preview
        # Implemente se desejar

        # Render
        if "TriangleStripSet" in X3D.render:
            X3D.render["TriangleStripSet"](point=self.coord.point,
                                           stripCount=self.stripCount,
                                           color=X3D.current_color)


class IndexedTriangleStripSet(X3DComposedGeometryNode):
    """Representa uma forma 3D composta de tiras de triângulos."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.coord = None
        self.index = []

        index_str = re.split(r'[,\s]\s*', node.attrib['index'].strip())
        self.index = [int(point) for point in index_str]

        for child in node:
            clean(child) # remove namespace
            if child.tag == "Coordinate":
                self.coord = Coordinate(child)

        # Preview
        # Implemente se desejar

        # Render
        if "IndexedTriangleStripSet" in X3D.render:
            X3D.render["IndexedTriangleStripSet"](point=self.coord.point,
                                                  index=self.index,
                                                  color=X3D.current_color)


# Navigation component

class X3DViewpointNode(X3DBindableNode):
    """Define localização no sistema de coordenadas local para visualização."""

class Viewpoint(X3DViewpointNode):
    """Define um ponto de vista que fornece uma vista em perspectiva da cena."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.position = [0, 0, 10]         # Valores padrão
        self.orientation = [0, 0, 1, 0]    # Valores padrão
        self.fieldOfView = math.pi/4       # Valores padrão
        if 'position' in node.attrib:
            position_str = re.split(r'[,\s]\s*', node.attrib['position'].strip())
            self.position = [float(point) for point in position_str]

        if 'orientation' in node.attrib:
            orientation_str = re.split(r'[,\s]\s*', node.attrib['orientation'].strip())
            self.orientation = [float(point) for point in orientation_str]

        if 'fieldOfView' in node.attrib:
            self.fieldOfView = float(node.attrib['fieldOfView'].strip())

        # Render
        if "Viewpoint" in X3D.render:
            X3D.render["Viewpoint"](position=self.position,
                                    orientation=self.orientation,
                                    fieldOfView=self.fieldOfView)

# Geometry3D component

class Box(X3DGeometryNode):
    """Classe responsável por geometria Box, que é um paralelepípedo centro no (0,0,0)."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        self.size = [2, 2, 2]         # Valores padrão

        if 'size' in node.attrib:
            size_str = re.split(r'[,\s]\s*', node.attrib['size'].strip())
            self.size = [float(point) for point in size_str]

        # Preview
        # Implemente se desejar

        # Render
        if "Box" in X3D.render:
            X3D.render["Box"](size=self.size, color=X3D.current_color)

class IndexedFaceSet(X3DComposedGeometryNode):
    """Classe responsável por geometria Indexed Face Set, que é uma malha de polígonos."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai

        self.coord = None
        self.color = None
        self.texCoord = None

        self.coordIndex = []
        self.colorIndex = []
        self.texCoordIndex = []

        self.colorPerVertex = True

        if "coordIndex" in node.attrib:
            coordIndex_str = re.split(r'[,\s]\s*', node.attrib['coordIndex'].strip())
            self.coordIndex = [int(point) for point in coordIndex_str]

        if 'colorPerVertex' in node.attrib:
            colorPerVertex_str = node.attrib['colorPerVertex'].strip()
            self.colorPerVertex = colorPerVertex_str == "true"

        if "colorIndex" in node.attrib:
            colorIndex_str = re.split(r'[,\s]\s*', node.attrib['colorIndex'].strip())
            self.colorIndex = [int(point) for point in colorIndex_str]

        if "texCoordIndex" in node.attrib:
            texCoordIndex_str = re.split(r'[,\s]\s*', node.attrib['texCoordIndex'].strip())
            self.texCoordIndex = [int(point) for point in texCoordIndex_str]

        for child in node:
            clean(child) # remove namespace
            if child.tag == "Coordinate":
                self.coord = Coordinate(child)
            elif child.tag == "Color":
                self.color = Color(child)
            elif child.tag == "TextureCoordinate":
                self.texCoord = TextureCoordinate(child)

        # Preview
        # Implemente se desejar

        if self.coord:
            ret_coord = self.coord.point
        else:
            ret_coord = None

        if self.color:
            ret_color = self.color.color
        else:
            ret_color = None

        if self.texCoord:
            ret_texCoord = self.texCoord.point
        else:
            ret_texCoord = None

        # Render
        if "IndexedFaceSet" in X3D.render:
            X3D.render["IndexedFaceSet"](coord=ret_coord, coordIndex=self.coordIndex,
                                         colorPerVertex=self.colorPerVertex, color=ret_color,
                                         colorIndex=self.colorIndex, texCoord=ret_texCoord,
                                         texCoordIndex=self.texCoordIndex,
                                         current_color=X3D.current_color,
                                         current_texture=X3D.current_texture)

# Texturing component

class X3DTextureCoordinateNode(X3DGeometricPropertyNode):
    """Nó abstrato base para todos os tipos de nó que especificam coordenadas de textura."""

class TextureCoordinate(X3DTextureCoordinateNode):
    """Conjunto de coordenadas de textura 2D usadas por nós de geometria baseados em vértices."""

    def __init__(self, node):
        super().__init__() # Chama construtor da classe pai
        point_str = re.split(r'[,\s]\s*', node.attrib['point'].strip())
        self.point = [float(p) for p in point_str]
