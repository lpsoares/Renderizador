# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 31 de Agosto de 2020

# XML
import xml.etree.ElementTree as ET

# Outras
import re
import math

# Interface
import interface

def clean(child):
    _, _, child.tag = child.tag.rpartition('}') # remove os namespaces

class X3D:

    def __init__(self, filename):
        self.x3d = ET.parse(filename)
        self.root = self.x3d.getroot()

        X3D.current_color = [1.0, 1.0, 1.0]

        X3D.render = {} # dicionario dos métodos de renderização

    def set_resolution(self, width, height):
        self.width = width
        self.height = height
    
    def parse(self):
        """ parse começando da raiz do X3D. """
        for child in self.root:
            clean(child) # remove namespace
            if child.tag == "Scene":
                self.scene = Scene(child)

class Scene:
    def __init__(self, node):
        self.children = []
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Transform":
                self.children.append(Transform(child))

# Core component

class X3DNode:
    pass

class X3DChildNode(X3DNode):
    def __init__(self):
        super().__init__()

# Grouping component

class X3DGroupingNode(X3DChildNode):
    def __init__(self):
        super().__init__()
        self.children = []

class Transform(X3DGroupingNode):
    def __init__(self, node):
        super().__init__()
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Shape":
                self.children.append(Shape(child))

# Shape component

class X3DShapeNode(X3DChildNode):
    def __init__(self):
        super().__init__()
        self.geometry = None
        self.appearance = None

class X3DAppearanceNode(X3DNode):
    def __init__(self):
        super().__init__()

class X3DMaterialNode():
    def __init__(self):
        super().__init__()

class Material(X3DMaterialNode):
    def __init__(self, node):
        super().__init__()
        self.diffuseColor = [0.8, 0.8, 0.8]
        if 'diffuseColor' in node.attrib:
            diffuseColor_str = re.split(r'[,\s]\s*',node.attrib['diffuseColor'])
            self.diffuseColor = [ float(color) for color in diffuseColor_str]
        X3D.current_color = self.diffuseColor

class Appearance(X3DAppearanceNode):
    def __init__(self, node):
        super().__init__()
        self.material = None
        for child in node:
            clean(child) # remove namespace
            if child.tag == "Material":
                self.material = Material(child)

class Shape(X3DShapeNode):
    def __init__(self, node):
        super().__init__()
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
            



# Rendering component

class X3DGeometryNode(X3DNode):
    def __init__(self):
        super().__init__()


# Geometry2D component

class Polypoint2D(X3DGeometryNode):
    def __init__(self, node):
        super().__init__()
        point_str = re.split(r'[,\s]\s*',node.attrib['point'].strip())
        point = [ float(p) for p in point_str]
        
        # Preview
        polypoint2D = []
        for i in range(0, len(point), 2):
            polypoint2D.append([point[i], point[i+1]])
        interface.Interface._pontos.append({'color': X3D.current_color, 'points': polypoint2D})

        # Render
        if "Polypoint2D" in X3D.render:
            X3D.render["Polypoint2D"](point=point, color=X3D.current_color)  

class Polyline2D(X3DGeometryNode):
    def __init__(self, node):
        super().__init__()
        lineSegments_str = re.split(r'[,\s]\s*',node.attrib['lineSegments'].strip())
        lineSegments = [ float(point) for point in lineSegments_str]

        # Preview
        polyline2D = []
        for i in range(0, len(lineSegments), 2):
            polyline2D.append([lineSegments[i], lineSegments[i+1]])
        interface.Interface._linhas.append({'color': X3D.current_color, 'lines': polyline2D})

        # Render
        if "Polyline2D" in X3D.render:
            X3D.render["Polyline2D"](lineSegments=lineSegments, color=X3D.current_color)  

class TriangleSet2D(X3DGeometryNode):
    def __init__(self, node):
        super().__init__()
        vertices_str = re.split(r'[,\s]\s*',node.attrib['vertices'].strip())
        vertices = [ float(point) for point in vertices_str]

        # Preview
        for i in range(0, len(vertices), 6):
            interface.Interface._poligonos.append({'color': X3D.current_color,
                                                   'vertices': [[vertices[i  ], vertices[i+1]],
                                                                [vertices[i+2], vertices[i+3]],
                                                                [vertices[i+4], vertices[i+5]]]})
        
        # Render
        if "TriangleSet2D" in X3D.render:
            X3D.render["TriangleSet2D"](vertices=vertices, color=X3D.current_color)
