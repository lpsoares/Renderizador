#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Parser X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# XML
import xml.etree.ElementTree

# Outras
import re
import math

# Métodos de Apoio

def clean(child):
    """Recebe um nó XML e remove dele o namespace do atributo tag se houver."""
    _, _, child.tag = child.tag.rpartition('}') # remove os namespaces

def get_colors(appearance):
    """Método de apoio para recuperar cores de um nó Appearance."""
    colors = {
        "diffuseColor": [0.8, 0.8, 0.8],  # Valor padrão
        "emissiveColor": [0.0, 0.0, 0.0],  # Valor padrão
        "specularColor": [0.0, 0.0, 0.0],  # Valor padrão
        "shininess": 0.2,  # Valor padrão
        "transparency": 0.0  # Valor padrão
    }
    if appearance and appearance.material:
        colors["diffuseColor"] = appearance.material.diffuseColor
        colors["emissiveColor"] = appearance.material.emissiveColor
        colors["specularColor"] = appearance.material.specularColor
        colors["shininess"] = appearance.material.shininess
        colors["transparency"] = appearance.material.transparency

    return colors


# Leitores de Campos X3D

def SFTime(node, field, default):
    """Especifica um único valor de tempo."""
    if node is not None and field in node.attrib:
        return float(node.attrib[field].strip())
    return default

def SFFloat(node, field, default):
    """Especifica um único valor em ponto flutuante."""
    if node is not None and field in node.attrib:
        return float(node.attrib[field].strip())
    return default

def MFFloat(node, field, default):
    """Especifica uma cor."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def MFInt32(node, field, default):
    """Especifica zero ou mais valores inteiros."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [int(value) for value in val_str]
        return []
    return default

def SFBool(node, field, default):
    """Especifica um único valor booleano."""
    if node is not None and field in node.attrib:
        val_str = node.attrib[field].strip().lower()
        return val_str == "true"
    return default

def SFRotation(node, field, default):
    """Especifica uma rotação única."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def SFColor(node, field, default):
    """Especifica uma cor."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def MFColor(node, field, default):
    """Especifica uma cor."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def SFVec3f(node, field, default):
    """Especifica um vetor tridimensional (3D)."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def MFVec3f(node, field, default):
    """Especifica zero ou mais vetores tridimensionais (3D)."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def MFVec2f(node, field, default):
    """Especifica zero ou mais vetores bidimensionais (2D)."""
    if node is not None and field in node.attrib:
        val = node.attrib[field].strip()
        if val:
            val_str = re.split(r'[,\s]\s*', val)
            return [float(value) for value in val_str]
        return []
    return default

def SFString(node, field, default):
    """Especifica uma strings."""
    if node is not None and field in node.attrib:
        return node.attrib[field].strip()
    return default

def MFString(node, field, default):
    """Especifica zero ou mais strings."""
    if node is not None and field in node.attrib:
        val_str = re.split(r'[,\s]\s*', node.attrib[field].strip())
        return [addr.replace('"', '').replace("'", '') for addr in val_str if addr != '']
    return default

def MFNode(node, name, default):
    """Especifica zero ou mais nós X3D."""
    children = default

    for child in node:
        clean(child) # remove namespace
        if name == "X3DChildNode":
            if child.tag == "Shape":
                children.append(Shape(child))
            elif child.tag == "Transform":
                children.append(Transform(child))

    return children

def SFNode(node, name, default):
    """Especifica um nó X3D."""
    for child in node:
        clean(child) # remove namespace
        if name == "X3DAppearanceNode":
            if child.tag == "Appearance":
                appearance = Appearance(child)
                X3D.current_appearance = appearance
                return appearance
        elif name == "X3DGeometryNode":
            if child.tag == "Polypoint2D":
                return Polypoint2D(child)
            if child.tag == "Polyline2D":
                return Polyline2D(child)
            if child.tag == "Circle2D":
                return Circle2D(child)
            if child.tag == "TriangleSet2D":
                return TriangleSet2D(child)
            if child.tag == "TriangleSet":
                return TriangleSet(child)
            if child.tag == "TriangleStripSet":
                return TriangleStripSet(child)
            if child.tag == "IndexedTriangleStripSet":
                return IndexedTriangleStripSet(child)
            if child.tag == "Box":
                return Box(child)
            if child.tag == "Sphere":
                return Sphere(child)
            if child.tag == "Cone":
                return Cone(child)
            if child.tag == "Cylinder":
                return Cylinder(child)
            if child.tag == "IndexedFaceSet":
                return IndexedFaceSet(child)
        elif name == "X3DMaterialNode":
            if child.tag == "Material":
                return Material(child)
        elif name == "X3DTextureNode":
            if child.tag == "ImageTexture":
                return ImageTexture(child)
        elif name == "X3DCoordinateNode":
            if child.tag == "Coordinate":
                return Coordinate(child)
        elif name == "X3DColorNode":
            if child.tag == "Color":
                return Color(child)
        elif name == "X3DTextureCoordinateNode":
            if child.tag == "TextureCoordinate":
                return TextureCoordinate(child)

    return default


# Estrutura do X3D

class X3D:
    """
    Classe responsável por fazer o Parse do arquivo X3D.

    ...

    Atributos
    ----------
    root : Element
        raiz do grafo de cena X3D em XMl

    current_color : {list[3]} (static)
        dicionário com as cores no formato RGB usadas no momento ["diffuseColor", "emissiveColor"]
        além dos valores de transparencia ["transparency"]
    current_appearance : X3DAppearanceNode (static)
        objeto de aparencia em X3D
    current_texture = String (static)
        URL das texturas

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
        "emissiveColor": [0.0, 0.0, 0.0],
        "transparency": 0.0,
    }
    current_appearance = None  # objeto de aparencia atual
    current_texture = []  # controle de texturas instantâneas
    preview = None  # atributo que aponta para o sistema de preview
    renderer = {}  # dicionario dos métodos de renderização

    def __init__(self, filename):
        """Constroi o atributo para a raiz do grafo X3D."""
        self.root = xml.etree.ElementTree.parse(filename).getroot()
        self.scene = None  # Referência para o objeto da cena

    def set_preview(self, preview):
        """Armazena as rotinas para fazer o render da cena."""
        X3D.preview = preview

    def viewport(self, width, height):
        """Armazena a largura e altura de janela de renderização."""
        self.width = width
        self.height = height

    def parse(self):
        """Leitura da cena começando da raiz do X3D."""
        for child in self.root:
            clean(child) # remove namespace
            if child.tag == "Scene":
                self.scene = Scene(child)

    def render(self):
        """Renderização da cena começando da raiz do X3D."""
        self.scene.render()

class Scene:
    """O nó Scene acomoda a cena X3D."""

    def __init__(self, node):
        """Parse do nó X3D."""
        self.children = []
        lights = []
        viewpoint = None
        navigation_info = None
        fog = None

        for child in node:
            clean(child)  # remove namespace
            if child.tag == "Transform":
                self.children.append(Transform(child))
            elif child.tag == "TimeSensor":
                self.children.append(TimeSensor(child))
            elif child.tag == "SplinePositionInterpolator":
                self.children.append(SplinePositionInterpolator(child))
            elif child.tag == "OrientationInterpolator":
                self.children.append(OrientationInterpolator(child))
            elif child.tag == "ROUTE":
                self.children.append(ROUTE(child))
            elif child.tag == "DirectionalLight":
                lights.append(DirectionalLight(child))
            elif child.tag == "PointLight":
                lights.append(PointLight(child))
            elif child.tag == "Viewpoint":
                viewpoint = Viewpoint(child)
            elif child.tag == "NavigationInfo":
                navigation_info = NavigationInfo(child)
            elif child.tag == "Fog":
                fog = Fog(child)

        self.children = lights + self.children  # deixa luzes primeiro

        if navigation_info:  # garante tratar o Viewpoint antes dos outros nós
            self.children.insert(0, navigation_info)
        else:  # cria um navigation_info se não definido
            self.children.insert(0, NavigationInfo())

        if viewpoint:  # garante tratar o Viewpoint primeiro que tudo
            self.children.insert(0, viewpoint)
        else:  # cria um viewpoint se não definido
            self.children.insert(0, Viewpoint())

        if fog:  # garante que fog seja o último nó
            self.children.append(fog)

    def render(self):
        """Rotina de renderização."""
        for child in self.children:
            child.render()

# Core component

class X3DNode:
    """Nó abstrato que é o tipo base para todos os nós no sistema X3D."""

    named_nodes = {}  # Dicionário com todos os nós X3D nomeados

    def __init__(self, node=None):
        """Parse do nó X3D."""
        if node is not None and "DEF" in node.attrib:
            self.name = node.attrib["DEF"].strip()
            X3DNode.named_nodes[self.name] = self

class X3DChildNode(X3DNode):
    """Nó abstrato como base para campos children, addChildren, and removeChildren."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DBindableNode(X3DChildNode):
    """X3DBindableNode é o tipo base abstrato para certos tipos de objetos."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DSensorNode(X3DChildNode):
    """X3DSensorNode é o tipo base abstrato para todos tipos de sensores."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


# Time component

class X3DTimeDependentNode(X3DChildNode):
    """Nó abstrato que todos os tipos que dependem de tempo derivam."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class TimeSensor(X3DTimeDependentNode, X3DSensorNode):
    """Gera eventos conforme o tempo passa."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai
        self.cycleInterval = SFTime(node, "cycleInterval", 1)
        self.loop = SFBool(node, "loop", False)
        self.fraction_changed = 0

    def render(self):
        """Rotina de renderização."""
        if "TimeSensor" not in X3D.renderer:
            raise Exception("TimeSensor não foi implementado.")

        # NO FUTURO MANDAR O OBJETO INTEIRO COM SEUS PARAMETROS ENCAPSULADOS
        self.fraction_changed = X3D.renderer["TimeSensor"](cycleInterval=self.cycleInterval,
                                                           loop=self.loop)


# Grouping component

class X3DGroupingNode(X3DChildNode):
    """Nó abstrato indica que os tipos de nós concretos derivados dele contêm nós filhos."""

    def __init__(self, node=None):
        """Parse do nó X3d."""
        super().__init__(node)  # Chama construtor da classe pai
        self.children = MFNode(node, "X3DChildNode", [])
        self.bboxCenter = SFVec3f(node, "bboxCenter", [0, 0, 0])
        self.bboxSize = SFVec3f(node, "bboxSize", [-1, -1, -1])
        #   MFNode     [in]     addChildren               [X3DChildNode]
        #   MFNode     [in]     removeChildren            [X3DChildNode]


class Transform(X3DGroupingNode):
    """Nó de agrupamento que define um sistema de coordenadas para seus nós filhos."""

    def __init__(self, node):
        """Parse do nó X3d."""
        super().__init__(node) # Chama construtor da classe pai
        self.rotation = SFRotation(node, "rotation", [0, 0, 1, 0])
        self.scale = SFVec3f(node, "scale", [1, 1, 1])
        self.translation = SFVec3f(node, "translation", [0, 0, 0])
        self.center = SFVec3f(node, "center", [0, 0, 0])
        self.scaleOrientation = SFRotation(node, "scaleOrientation", [0, 0, 1, 0])

    def render(self):
        """Rotina de renderização."""
        if not all(func in X3D.renderer for func in ("Transform_in", "Transform_out")):
            raise Exception("Transform(s) não foram implementados.")

        # NO FUTURO MANDAR O OBJETO INTEIRO COM SEUS PARAMETROS ENCAPSULADOS
        X3D.renderer["Transform_in"](translation=self.translation,
                                     scale=self.scale,
                                     rotation=self.rotation)

        for child in self.children:
            child.render()

        X3D.renderer["Transform_out"]()  # Tira a transformação da pilha


# Shape component

class X3DShapeNode(X3DChildNode):
    """Este é o tipo de nó base para todos os nós do tipo Shape."""

    def __init__(self, node=None):
        """Parse do nó X3d."""
        super().__init__(node) # Chama construtor da classe pai
        self.appearance = SFNode(node, "X3DAppearanceNode", None)
        self.geometry = SFNode(node, "X3DGeometryNode", None)

class X3DAppearanceNode(X3DNode):
    """Este é o tipo de nó básico para todos os nós do tipo Appearance."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DAppearanceChildNode(X3DNode):
    """Este é o tipo de nó básico para todos os nós do tipo X3DAppearanceNode."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DMaterialNode(X3DAppearanceChildNode):
    """Este é o tipo de nó básico para todos os nós do tipo Material."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class Material(X3DMaterialNode):
    """Especifica propriedades do material de superfícies para nós de geometria associados."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai
        self.ambientIntensity = SFFloat(node, "ambientIntensity", 0.2)
        self.diffuseColor = SFColor(node, "diffuseColor", [0.8, 0.8, 0.8])
        self.emissiveColor = SFColor(node, "emissiveColor", [0.0, 0.0, 0.0])
        self.specularColor = SFColor(node, "specularColor", [0.0, 0.0, 0.0])
        self.shininess = SFFloat(node, "shininess", 0.2)
        self.transparency = SFFloat(node, "transparency", 0.0)

    def render(self):
        """Rotina de renderização."""
        X3D.current_color["ambientIntensity"] = self.ambientIntensity
        X3D.current_color["diffuseColor"] = self.diffuseColor
        X3D.current_color["emissiveColor"] = self.emissiveColor
        X3D.current_color["specularColor"] = self.specularColor
        X3D.current_color["shininess"] = self.shininess
        X3D.current_color["transparency"] = self.transparency


class X3DTextureNode(X3DAppearanceChildNode):
    """Nó abstrato base para todos os tipos de nó que especificam imagens de textura."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DTexture2DNode(X3DTextureNode):
    """Nó abstrato base para todos os tipos de nó que especificam imagens 2D de textura."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class ImageTexture(X3DTexture2DNode):
    """Define mapa de textura para um arquivo de imagem e parâmetros gerais de mapeamento."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.url = MFString(node, "url", [])
        self.repeatS = SFBool(node, "repeatS", True)
        self.repeatT = SFBool(node, "repeatT", True)

    def render(self):
        """Rotina de renderização."""
        X3D.current_texture = self.url

class Appearance(X3DAppearanceNode):
    """Especifica as propriedades visuais da geometria."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai

        self.fillProperties = SFNode(node, "FillProperties", None)
        self.lineProperties = SFNode(node, "LineProperties", None)
        self.material = SFNode(node, "X3DMaterialNode", None)
        self.shaders = MFNode(node, "X3DShaderNode", [])
        self.texture = SFNode(node, "X3DTextureNode", None)
        self.textureTransform = SFNode(node, "X3DTextureTransformNode", None)

    def render(self):
        """Rotina de renderização."""
        if self.material:
            self.material.render()
        if self.texture:
            self.texture.render()

class Shape(X3DShapeNode):
    """Define aparência e geometria, que são usados para criar objetos renderizados."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai

    def render(self):
        """Rotina de renderização."""
        if self.appearance:
            self.appearance.render()
        if self.geometry:
            self.geometry.render(self.appearance)

# Rendering component

class X3DGeometryNode(X3DNode):
    """Este é o tipo de nó base para todas as geometrias em X3D."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DComposedGeometryNode(X3DGeometryNode):
    """Este é o tipo de nó base para toda a geometria 3D composta em X3D."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai
        self.coord = SFNode(node, "X3DCoordinateNode", [])
        self.attrib = MFNode(node, "X3DVertexAttributeNode", [])
        self.fogCoord = SFNode(node, "FogCoordinate", [])
        self.normal = SFNode(node, "X3DNormalNode", [])
        self.texCoord = SFNode(node, "X3DTextureCoordinateNode", [])
        self.ccw = SFBool(node, "ccw", True)
        self.colorPerVertex = SFBool(node, "colorPerVertex", True)
        self.normalPerVertex = SFBool(node, "normalPerVertex", True)
        self.solid = SFBool(node, "solid", True)


class X3DGeometricPropertyNode(X3DNode):
    """Nó base para todos os tipos de nós de propriedades geométricas definidos no X3D."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DCoordinateNode(X3DGeometricPropertyNode):
    """Nó base para todos os tipos de nós de coordenadas em X3D."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class X3DColorNode(X3DGeometricPropertyNode):
    """Nó básico para especificações de cores no X3D."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai


class Coordinate(X3DCoordinateNode):
    """Define um conjunto de coordenadas 3D para nós de geometria baseada em vértices."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.point = MFVec3f(node, "point", [])


class Color(X3DColorNode):
    """Define um conjunto de cores RGB a serem usadas nos campos de outro nó."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.color = MFColor(node, "color", [])


class TriangleSet(X3DComposedGeometryNode):
    """Representa uma forma 3D que representa uma coleção de triângulos individuais."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.vertices = MFVec2f(node, "vertices", [])

        # Preview
        # Implemente se desejar

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "TriangleSet" not in X3D.renderer:
            raise Exception("TriangleSet não foi implementado.")

        colors = get_colors(appearance)
        if self.coord and self.coord.point:
            # NO FUTURO MANDAR O OBJETO INTEIRO COM SEUS PARAMETROS ENCAPSULADOS
            X3D.renderer["TriangleSet"](point=self.coord.point, colors=colors)

class TriangleStripSet(X3DComposedGeometryNode):
    """Representa uma forma 3D composta por faixas de triângulos."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.stripCount = MFInt32(node, "stripCount", [])

        # Preview
        # Implemente se desejar

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "TriangleStripSet" not in X3D.renderer:
            raise Exception("TriangleStripSet não foi implementado.")

        colors = get_colors(appearance)
        if self.coord and self.coord.point and self.stripCount:
            # NO FUTURO MANDAR O OBJETO INTEIRO COM SEUS PARAMETROS ENCAPSULADOS
            X3D.renderer["TriangleStripSet"](point=self.coord.point,
                                             stripCount=self.stripCount,
                                             colors=colors)

class IndexedTriangleStripSet(X3DComposedGeometryNode):
    """Representa uma forma 3D composta de tiras de triângulos."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.index = MFInt32(node, "index", [])

        # Preview
        # Implemente se desejar

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "IndexedTriangleStripSet" not in X3D.renderer:
            raise Exception("IndexedTriangleStripSet não foi implementado.")

        colors = get_colors(appearance)
        if "IndexedTriangleStripSet" in X3D.renderer:
            if self.coord and self.coord.point and self.index:
                # NO FUTURO MANDAR O OBJETO INTEIRO COM SEUS PARAMETROS ENCAPSULADOS
                X3D.renderer["IndexedTriangleStripSet"](point=self.coord.point,
                                                        index=self.index,
                                                        colors=colors)


# Geometry2D component

class Polypoint2D(X3DGeometryNode):
    """Pontos exibidos por um conjunto de vértices no sistema de coordenadas 2D."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.point = MFVec2f(node, "point", [])

        # Preview
        if X3D.preview:
            points = []
            for i in range(0, len(self.point), 2):
                points.append([self.point[i], self.point[i+1]])
            X3D.preview.pontos.append({'appearance': X3D.current_appearance,
                                       'points': points})

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Polypoint2D" not in X3D.renderer:
            raise Exception("Polypoint2D não foi implementado.")

        colors = get_colors(appearance)
        if self.point:
            X3D.renderer["Polypoint2D"](point=self.point, colors=colors)


class Polyline2D(X3DGeometryNode):
    """Série de segmentos de linha contíguos no sistema de coordenadas 2D."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.lineSegments = MFVec2f(node, "lineSegments", [])

        # Preview
        if X3D.preview:
            points = []
            for i in range(0, len(self.lineSegments), 2):
                points.append([self.lineSegments[i], self.lineSegments[i+1]])
            X3D.preview.linhas.append({'appearance': X3D.current_appearance,
                                       'lines': points})

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Polyline2D" not in X3D.renderer:
            raise Exception("Polyline2D não foi implementado.")

        colors = get_colors(appearance)
        if self.lineSegments:
            X3D.renderer["Polyline2D"](lineSegments=self.lineSegments, colors=colors)


class Circle2D(X3DGeometryNode):
    """Uma linha que forma um círculo no sistema de coordenadas 2D."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.radius = SFFloat(node, "radius", 1)

        # Preview
        if X3D.preview:
            radius = self.radius
            X3D.preview.circulos.append({'appearance': X3D.current_appearance,
                                         'radius': radius})

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Circle2D" not in X3D.renderer:
            raise Exception("Circle2D não foi implementado.")

        colors = get_colors(appearance)
        if self.radius:
            X3D.renderer["Circle2D"](radius=self.radius, colors=colors)


class TriangleSet2D(X3DGeometryNode):
    """Especifica um conjunto de triângulos no sistema de coordenadas 2D local."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.vertices = MFVec2f(node, "vertices", [])
        self.solid = SFBool(node, "solid", False)

        # Preview
        if X3D.preview:
            points = []
            for i in range(0, len(self.vertices), 2):
                points.append([self.vertices[i], self.vertices[i+1]])
            X3D.preview.poligonos.append({'appearance': X3D.current_appearance,
                                          'vertices': points})

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "TriangleSet2D" not in X3D.renderer:
            raise Exception("TriangleSet2D não foi implementado.")

        colors = get_colors(appearance)
        if self.vertices:
            X3D.renderer["TriangleSet2D"](vertices=self.vertices, colors=colors)


# Navigation component

class NavigationInfo(X3DBindableNode):
    """Características físicas do avatar do visualizador e do modelo de visualização."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai
        self.headlight = SFBool(node, "headlight", True)  # Valor padrão

    def render(self):
        """Rotina de renderização."""
        if "NavigationInfo" not in X3D.renderer:
            raise Exception("NavigationInfo não foi implementado.")

        X3D.renderer["NavigationInfo"](headlight=self.headlight)


class X3DViewpointNode(X3DBindableNode):
    """Define localização no sistema de coordenadas local para visualização."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node)  # Chama construtor da classe pai
        self.jump = SFBool(node, "jump", True)
        self.description = SFString(node, "description", "")
        self.retainUserOffsets = SFBool(node, "retainUserOffsets", False)
        self.centerOfRotation = SFVec3f(node, "centerOfRotation", [0.0, 0.0, 0.0])
        self.position = SFVec3f(node, "position", [0, 0, 10])
        self.orientation = SFRotation(node, "orientation", [0, 0, 1, 0])

class Viewpoint(X3DViewpointNode):
    """Define um ponto de vista que fornece uma vista em perspectiva da cena."""

    def __init__(self, node=None):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.fieldOfView = SFFloat(node, "fieldOfView", math.pi/4)
        if (self.fieldOfView < 0) or (self.fieldOfView > math.pi):
            self.fieldOfView = math.pi/4

    def render(self):
        """Rotina de renderização."""
        if "Viewpoint" not in X3D.renderer:
            raise Exception("Viewpoint não foi implementado.")

        X3D.renderer["Viewpoint"](position=self.position,
                                  orientation=self.orientation,
                                  fieldOfView=self.fieldOfView)


# Geometry3D component

class Box(X3DGeometryNode):
    """Classe responsável por geometria Box, que é um paralelepípedo centro no (0,0,0)."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.size = SFVec3f(node, "size", [2, 2, 2])

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Box" not in X3D.renderer:
            raise Exception("Box não foi implementado.")

        colors = get_colors(appearance)
        if self.size:
            X3D.renderer["Box"](size=self.size, colors=colors)


class Sphere(X3DGeometryNode):
    """Classe responsável por geometria Sphere, que é uma esfera com centro no (0,0,0)."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.radius = SFFloat(node, "radius", 1)

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Sphere" not in X3D.renderer:
            raise Exception("Sphere não foi implementado.")

        colors = get_colors(appearance)
        if self.radius:
            X3D.renderer["Sphere"](radius=self.radius, colors=colors)


class Cone(X3DGeometryNode):
    """Classe responsável por geometria Cone, que é um cone com centro no (0,0,0)."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.bottomRadius  = SFFloat(node, "bottomRadius", 1)
        self.height = SFFloat(node, "height", 2)

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Cone" not in X3D.renderer:
            raise Exception("Cone não foi implementado.")

        colors = get_colors(appearance)
        if self.height and self.bottomRadius:
            X3D.renderer["Cone"](bottomRadius=self.bottomRadius, height=self.height, colors=colors)

class Cylinder(X3DGeometryNode):
    """Classe responsável por geometria Cylinder, que é uma cilindro com centro no (0,0,0)."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.radius = SFFloat(node, "radius", 1)
        self.height = SFFloat(node, "height", 2)

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "Cylinder" not in X3D.renderer:
            raise Exception("Cylinder não foi implementado.")

        colors = get_colors(appearance)
        if self.radius and self.height:
            X3D.renderer["Cylinder"](radius=self.radius, height=self.height, colors=colors)

class IndexedFaceSet(X3DComposedGeometryNode):
    """Classe responsável por geometria Indexed Face Set, que é uma malha de polígonos."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.color = SFNode(node, "X3DColorNode", None)
        self.coordIndex = MFInt32(node, "coordIndex", [])
        self.colorIndex = MFInt32(node, "colorIndex", [])
        self.texCoordIndex = MFInt32(node, "texCoordIndex", [])

    def render(self, appearance=None):
        """Rotina de renderização."""
        if "IndexedFaceSet" not in X3D.renderer:
            raise Exception("IndexedFaceSet não foi implementado.")

        ret_coord = None
        ret_color = None
        ret_texCoord = None

        if self.coord:
            ret_coord = self.coord.point
        if self.color:
            ret_color = self.color.color
        if self.texCoord:
            ret_texCoord = self.texCoord.point

        colors = get_colors(appearance)

        if self.coordIndex:
            X3D.renderer["IndexedFaceSet"](coord=ret_coord, coordIndex=self.coordIndex,
                                           colorPerVertex=self.colorPerVertex, color=ret_color,
                                           colorIndex=self.colorIndex, texCoord=ret_texCoord,
                                           texCoordIndex=self.texCoordIndex,
                                           colors=colors,
                                           current_texture=X3D.current_texture)


# Lighting component

class X3DLightNode(X3DChildNode):
    """Nó abstrato base para todos os tipos de luzes."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.ambientIntensity = SFFloat(node, "ambientIntensity", 0)
        self.color = SFColor(node, "color", [1.0, 1.0, 1.0])
        self.intensity = SFFloat(node, "intensity", 1)
        self.on = SFBool(node, "on", True)


class DirectionalLight(X3DLightNode):
    """Conjunto de coordenadas de textura 2D usadas por nós de geometria baseados em vértices."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.direction = SFVec3f(node, "direction", [0.0, 0.0, -1.0])

    def render(self):
        """Rotina de renderização."""
        if "DirectionalLight" not in X3D.renderer:
            raise Exception("DirectionalLight não foi implementado.")

        X3D.renderer["DirectionalLight"](ambientIntensity=self.ambientIntensity,
                                         color=self.color,
                                         intensity=self.intensity,
                                         direction=self.direction)


class PointLight(X3DLightNode):
    """Conjunto de coordenadas de textura 2D usadas por nós de geometria baseados em vértices."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.location = SFVec3f(node, "location", [0.0, 0.0, 0.0])

    def render(self):
        """Rotina de renderização."""
        if "PointLight" not in X3D.renderer:
            raise Exception("PointLight não foi implementado.")

        X3D.renderer["PointLight"](ambientIntensity=self.ambientIntensity,
                                   color=self.color,
                                   intensity=self.intensity,
                                   location=self.location)


# Texturing component

class X3DTextureCoordinateNode(X3DGeometricPropertyNode):
    """Nó abstrato base para todos os tipos de nó que especificam coordenadas de textura."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai


class TextureCoordinate(X3DTextureCoordinateNode):
    """Conjunto de coordenadas de textura 2D usadas por nós de geometria baseados em vértices."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.point = MFVec2f(node, "point", [])

    def render(self):
        """Rotina de renderização."""


# Environmental effects


class X3DFogObject():
    """Ttipo abstrato que descreve um nó que influencia a equação de iluminação de Fog."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.color = SFColor(node, "color", [1.0, 1.0, 1.0])
        self.fogType = SFString(node, "fogType", "LINEAR")
        self.visibilityRange = SFFloat(node, "visibilityRange", 0)

class Fog(X3DBindableNode, X3DFogObject):
    """Simula efeitos atmosféricos combinando objetos com a cor especificada."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai

    def render(self):
        """Rotina de renderização."""
        if "Fog" not in X3D.renderer:
            raise Exception("Fog não foi implementado.")

        X3D.renderer["Fog"](visibilityRange=self.visibilityRange,
                            color=self.color)

class X3DInterpolatorNode(X3DChildNode):
    """Base para todos os tipos de interpoladores."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.set_fraction = SFFloat(node, "set_fraction", 0)
        self.key = MFFloat(node, "key", [])  # MF<type>     [in,out] keyValue      []
        self.keyValue = MFFloat(node, "keyValue", None)
        self.value_changed = None  #   [S|M]F<type> [out]    value_changed

class SplinePositionInterpolator(X3DInterpolatorNode):
    """Interpola não linearmente entre uma lista de vetores 3D."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai
        self.closed = SFBool(node, "closed", False)

    def render(self):
        """Rotina de renderização."""
        if "SplinePositionInterpolator" not in X3D.renderer:
            raise Exception("SplinePositionInterpolator não foi implementado.")

        self.value_changed = X3D.renderer["SplinePositionInterpolator"]\
            (set_fraction=self.set_fraction,
             key=self.key,
             keyValue=self.keyValue,
             closed=self.closed)

class OrientationInterpolator(X3DInterpolatorNode):
    """Interpola entre uma lista de valores de rotação especificados no campo keyValue."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__(node) # Chama construtor da classe pai

    def render(self):
        """Rotina de renderização."""
        if "OrientationInterpolator" not in X3D.renderer:
            raise Exception("OrientationInterpolator não foi implementado.")

        self.value_changed = X3D.renderer["OrientationInterpolator"](set_fraction=self.set_fraction,
                                                                     key=self.key,
                                                                     keyValue=self.keyValue)

class ROUTE():
    """."""

    def __init__(self, node):
        """Parse do nó X3D."""
        super().__init__() # Chama construtor da classe pai
        self.fromNode = SFString(node, "fromNode", '')
        self.fromField = SFString(node, "fromField", '')
        self.toNode = SFString(node, "toNode", '')
        self.toField = SFString(node, "toField", '')

    def render(self):
        """Rotina de renderização."""
        fromNode = X3DNode.named_nodes[self.fromNode]
        value = getattr(fromNode, self.fromField)
        toNode = X3DNode.named_nodes[self.toNode]
        setattr(toNode, self.toField, value)
