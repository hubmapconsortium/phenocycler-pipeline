import html
import unicodedata
from io import BytesIO, StringIO
from typing import Dict, Literal, Optional

import lxml.etree as ET
from pint import Quantity, UnitRegistry

target_physical_size = "nm"
reg = UnitRegistry()


def strip_namespace(xmlstr: str):
    it = ET.iterparse(BytesIO(xmlstr.encode("utf-8")))
    for _, el in it:
        _, _, el.tag = el.tag.rpartition("}")
    root = it.root
    return root


def add_sa_segmentation_channels_info(
    omexml: ET.Element, nucleus_channels: list[str], cell_channels: list[str]
):
    """
    Will add this, to the root, after Image node
    <StructuredAnnotations>
    <XMLAnnotation ID="Annotation:0">
        <Value>
            <OriginalMetadata>
                <Key>SegmentationChannels</Key>
                <Value>
                    <Nucleus>DAPI-02</Nucleus>
                    <Cell>CD45</Cell>
                </Value>
            </OriginalMetadata>
        </Value>
    </XMLAnnotation>
    </StructuredAnnotations>
    """
    structured_annotation = omexml.find("StructuredAnnotations")
    if structured_annotation is None:
        structured_annotation = ET.Element("StructuredAnnotations")
        omexml.append(structured_annotation)
    annotation = ET.SubElement(structured_annotation, "XMLAnnotation", {"ID": "Annotation:0"})
    annotation_value = ET.SubElement(annotation, "Value")
    original_metadata = ET.SubElement(annotation_value, "OriginalMetadata")
    ET.SubElement(original_metadata, "Key").text = "SegmentationChannels"
    segmentation_channels_value = ET.SubElement(original_metadata, "Value")
    for nucleus_channel in nucleus_channels:
        ET.SubElement(segmentation_channels_value, "Nucleus").text = nucleus_channel
    for cell_channel in cell_channels:
        ET.SubElement(segmentation_channels_value, "Cell").text = cell_channel


def physical_size_to_quantity(
    px_node: ET.Element,
    dimension: Literal["X", "Y"],
) -> Optional[Quantity]:
    unit_str = px_node.get(f"PhysicalSize{dimension}Unit", None)
    if unit_str is None:
        print("Could not find physical unit in OMEXML for dimension", dimension)
        return None

    size_str = px_node.get(f"PhysicalSize{dimension}", None)
    if size_str is None:
        print("Could not find physical unit in OMEXML for dimension", dimension)
        return None

    unit_normalized = unicodedata.normalize("NFKC", html.unescape(unit_str))
    size = float(size_str) * reg[unit_normalized]
    return size


def convert_size_to_nm(px_node: ET.Element):
    for dimension in "XY":
        size = physical_size_to_quantity(px_node, dimension)
        if size is not None:
            size_converted = size.to(target_physical_size)
            px_node.set(f"PhysicalSize{dimension}Unit", target_physical_size)
            px_node.set(f"PhysicalSize{dimension}", str(size_converted.magnitude))


def blank_tiffdata(px_node: ET.Element):
    tiffdata_list = []
    for td in px_node.findall("TiffData"):
        count = int(td.get("PlaneCount"))
        td.clear()
        tiffdata_list.append(td)
        if count > 1:
            for x in range(1, count):
                child_td = ET.Element("TiffData")
                px_node.insert(px_node.index(td) + x, child_td)
                tiffdata_list.append(child_td)
    return tiffdata_list


def generate_and_add_new_tiffdata(px_node: ET.Element, tiffdata_list):
    num_channels = int(px_node.get("SizeC"))
    num_z = int(px_node.get("SizeZ"))
    ifd = 0
    tiffdata_elements = iter(tiffdata_list)
    for c in range(0, num_channels):
        for z in range(0, num_z):
            td = None
            try:
                td = next(tiffdata_elements)
            except StopIteration as e:
                print("Error: not enough TiffData Elements in ", ET.tostring(px_node))
            td.set("FirstT", "0")
            td.set("FirstC", str(c))
            td.set("FirstZ", str(z))
            td.set("IFD", str(ifd))
            td.set("PlaneCount", "1")
            ifd += 1


def modify_initial_ome_meta(
    xml_str: str,
    segmentation_channel_ids: dict[str, list[int]],
    channel_names: list[str],
    pixel_size_x: float,
    pixel_size_y: float,
    pixel_unit_x: str,
    pixel_unit_y: str,
) -> bytes:
    new_dim_order = "XYZCT"
    ome_xml: ET.Element = strip_namespace(xml_str)
    # ome_xml.set("xmlns", "http://www.openmicroscopy.org/Schemas/OME/2016-06")
    px_node = ome_xml.find("Image").find("Pixels")
    px_node.set("DimensionOrder", new_dim_order)
    px_node.set("PhysicalSizeX", str(pixel_size_x))
    px_node.set("PhysicalSizeY", str(pixel_size_y))
    px_node.set("PhysicalSizeXUnit", pixel_unit_x)
    px_node.set("PhysicalSizeYUnit", pixel_unit_y)
    convert_size_to_nm(px_node)
    tiffdata_list = blank_tiffdata(px_node)
    generate_and_add_new_tiffdata(px_node, tiffdata_list)

    nucleus_channels = [channel_names[i] for i in segmentation_channel_ids["nucleus"]]
    cell_channels = [channel_names[i] for i in segmentation_channel_ids["cell"]]

    add_sa_segmentation_channels_info(ome_xml, nucleus_channels, cell_channels)
    res = ET.tostring(ome_xml, encoding="UTF-8", xml_declaration=True)
    return res
