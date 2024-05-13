from pathlib import Path
from lxml import etree as ET
from utils_ome import modify_initial_ome_meta

def test_modify_initial_ome_meta():
    xml_str = open(Path('test_files/metadata.xml')).read()
    new_meta = modify_initial_ome_meta(xml_str, {'nucleus':'', 'cell':''}, 1,1,'nm','nm')
    element = ET.fromstring(new_meta.encode('utf-8'))
    px_node = element.find('ome:Image', {'ome':'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    px_node = px_node.find("ome:Pixels", {'ome':'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    px_node = px_node.findall("ome:TiffData", {'ome':'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    assert len(px_node) == 17

def test_modify_new_ome_meta():
    xml_str = open(Path('test_files/new_meta.xml')).read()
    new_meta = modify_initial_ome_meta(xml_str, {'nucleus': '', 'cell': ''}, 1, 1, 'nm', 'nm')
    element = ET.fromstring(new_meta.encode('utf-8'))
    px_node = element.find('ome:Image', {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    px_node = px_node.find("ome:Pixels", {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    px_node = px_node.findall("ome:TiffData", {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'})
    assert len(px_node) == 17
    for node in px_node:
        print(ET.tostring(node))