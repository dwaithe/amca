from aicsimageio.vendor import omexml #https://github.com/AllenCellModeling/aicsimageio
import xml.etree.ElementTree as ElementTree
import numpy as np 
class ROI(object):
    def __init__(self,node):
        self.node = node
        self.ns = omexml.get_namespaces(self.node)
class ROIRef(object):
    def __init__(self,node):
        self.node = node
        self.ns = omexml.get_namespaces(self.node)
class Rectangle(object):
    def __init__(self,node):
        self.node = node
        self.ns = omexml.get_namespaces(self.node)
class UNION(object):
    def __init__(self,node):
        self.node = node
        self.ns = omexml.get_namespaces(self.node)
class LABEL(object):
    def __init__(self,node):
        self.node = node
        self.ns = omexml.get_namespaces(self.node)

def create_roi(_roi,o):
    for _r in _roi:
        ID,X,Y,Height,Width,StrokeColor,Text,TheZ,TheT,TheC = _r
        roi = ROI(ElementTree.SubElement(o.root_node, omexml.qn(o.ns['ome'], "ROI")))
        roi.node.set("ID", "ROI:"+str(o.ct)+":0")
        union = UNION(ElementTree.SubElement(roi.node, omexml.qn(o.ns['ome'], "Union")))
        rectangle = Rectangle(ElementTree.SubElement(union.node, omexml.qn(o.ns['ome'], "Rectangle")))
        rectangle.node.set("ID",ID)
        rectangle.node.set("StrokeColor",str(StrokeColor))
        rectangle.node.set("TheC",str(TheC))
        rectangle.node.set("TheT",str(TheT))
        rectangle.node.set("TheZ",str(TheZ))
        rectangle.node.set("Text",Text)
        rectangle.node.set("X",str(X))
        rectangle.node.set("Y",str(Y))
        rectangle.node.set("Width",str(Width))
        rectangle.node.set("Height",str(Height))
        o.ct += 1
def create_roi_txt(_roi_txt,o):     
    for _r_txt in _roi_txt:
        ID,X,Y,FontSize,FontSizeUnit,StrokeColor,Text, TheZ,TheT,TheC = _r_txt
        roi = ROI(ElementTree.SubElement(o.root_node, omexml.qn(o.ns['ome'], "ROI")))
        roi.node.set("ID", "ROI:"+str(o.ct)+":0")
        union = UNION(ElementTree.SubElement(roi.node, omexml.qn(o.ns['ome'], "Union")))
        label = LABEL(ElementTree.SubElement(union.node, omexml.qn(o.ns['ome'], "Label")))

        label.node.set("FontSize",str(FontSize))
        label.node.set("FontSizeUnit",FontSizeUnit)
        label.node.set("ID",ID)
        label.node.set("StrokeColor",StrokeColor)
        label.node.set("Text",Text)
        label.node.set("TheC",str(TheC))
        label.node.set("TheT",str(TheT))
        label.node.set("TheZ",str(TheZ))
        label.node.set("X",str(X))
        label.node.set("Y",str(Y))
        o.ct += 1

def create_ROI_ref(o):
    for i in range(0, o.ct):
        roi_ref = ROIRef(ElementTree.SubElement(o.image().node, omexml.qn(o.ns['ome'], "ROIRef")))
        roi_ref.node.set("ID", "ROI:"+str(i)+":0")