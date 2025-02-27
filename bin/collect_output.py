import argparse
import logging
import re
import shutil
from os import walk
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import tifffile as tif
from aicsimageio import AICSImage
from ome_types import from_tiff
from ome_types.model import AnnotationRef, Map, MapAnnotation, StructuredAnnotationList

from utils import make_dir_if_not_exists, path_to_str, read_pipeline_config
from utils_ome import modify_initial_ome_meta

Image = np.ndarray
logging.basicConfig(level=logging.INFO, format="%(levelname)-7s - %(message)s")
logger = logging.getLogger(__name__)


def get_omexml(ome_tiff: Path) -> Optional[str]:
    image = AICSImage(ome_tiff)
    original_channels = image.channel_names
    if original_channels is None:
        return None
    else:
        omexml = from_tiff(ome_tiff)
        return omexml


def add_z_axis(img_stack: Image):
    stack_shape = img_stack.shape
    new_stack_shape = [stack_shape[0], 1, stack_shape[1], stack_shape[2]]
    return img_stack.reshape(new_stack_shape)


def modify_and_save_img(
    img_path: Path,
    out_path: Path,
    segmentation_channels: Dict[str, str],
    pixel_size_x: float,
    pixel_size_y: float,
    pixel_unit_x: str,
    pixel_unit_y: str,
    new_xml: Optional[str],
):
    with tif.TiffFile(path_to_str(img_path)) as TF:
        if new_xml == None:
            ome_meta = TF.ome_metadata
        else:
            ome_meta = new_xml
        img_stack = TF.series[0].asarray()
    new_img_stack = add_z_axis(img_stack)
    new_ome_meta = modify_initial_ome_meta(
        ome_meta, segmentation_channels, pixel_size_x, pixel_size_y, pixel_unit_x, pixel_unit_y
    )

    with tif.TiffWriter(path_to_str(out_path), bigtiff=True, shaped=False) as TW:
        TW.write(
            new_img_stack,
            contiguous=True,
            photometric="minisblack",
            description=new_ome_meta,
            metadata=None,
        )


def copy_files(
    file_type: str,
    src_data_dir: Path,
    src_dir_name: str,
    img_name_template: str,
    out_dir: Path,
    out_name_template: str,
    region: int,
    slices: Dict[str, str],
    additional_info=None,
):
    for img_slice_name, slice_path in slices.items():
        img_name = img_name_template.format(slice_name="1")
        src = src_data_dir / src_dir_name / img_name
        dst = out_dir / out_name_template.format(slice_name="1")
        if file_type == "mask":
            shutil.copy(src, dst)
        elif file_type == "expr":
            segmentation_channels = additional_info
            modify_and_save_img(src, dst, segmentation_channels)
        print("src:", src, "| dst:", dst)


def collect_segm_masks(data_dir: Path, out_dir: Path):
    for image_file in data_dir.glob("**/*.ome.tiff"):
        filename_base = image_file.name.split(".")[0]
        output_file = out_dir / image_file.name
        shutil.copy(image_file, output_file)


def collect_expr(
    data_dir: Path,
    listing: dict,
    out_dir: Path,
    segmentation_channels: Dict[str, str],
    pixel_size_x: float,
    pixel_size_y: float,
    pixel_unit_x: str,
    pixel_unit_y: str,
    ome_tiff: Path,
):
    for image_file in data_dir.glob("*.qptiff"):
        filename_base = image_file.name.split(".")[0]
        new_filename = f"{filename_base}_expr.ome.tiff"
        output_file = out_dir / new_filename
        new_xml = get_omexml(ome_tiff)

        modify_and_save_img(
            ome_tiff,
            output_file,
            segmentation_channels,
            pixel_size_x,
            pixel_size_y,
            pixel_unit_x,
            pixel_unit_y,
            new_xml,
        )


def collect_ome_tiff(ome_tiff: Path, out_dir: Path):
    output_file = out_dir / ome_tiff.name
    shutil.copy(ome_tiff, output_file)


def main(data_dir: Path, mask_dir: Path, pipeline_config_path: Path, ome_tiff: Path):
    pipeline_config = read_pipeline_config(pipeline_config_path)
    listing = pipeline_config["dataset_map_all_slices"]
    segmentation_channels = pipeline_config["segmentation_channels"]
    pixel_size_x = pipeline_config["pixel_size_x"]
    pixel_size_y = pipeline_config["pixel_size_y"]
    pixel_unit_x = pipeline_config["pixel_unit_x"]
    pixel_unit_y = pipeline_config["pixel_unit_y"]
    out_dir = Path("/output/pipeline_output")
    mask_out_dir = out_dir / "mask"
    expr_out_dir = out_dir / "expr"
    make_dir_if_not_exists(mask_out_dir)
    make_dir_if_not_exists(expr_out_dir)

    print("\nCollecting segmentation masks")
    collect_segm_masks(mask_dir, mask_out_dir)
    print("\nCollecting expressions")
    collect_expr(
        data_dir,
        listing,
        expr_out_dir,
        segmentation_channels,
        pixel_size_x,
        pixel_size_y,
        pixel_unit_x,
        pixel_unit_y,
        antb_info,
        ome_tiff,
    )
    # collect_ome_tiff(ome_tiff, out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=Path, help="path to directory with images")
    parser.add_argument("--mask_dir", type=Path, help="path to directory with segmentation masks")
    parser.add_argument("--pipeline_config", type=Path, help="path to region map file YAML")
    parser.add_argument("--ome_tiff", type=Path, help="path to the converted ome.tiff file")
    args = parser.parse_args()

    main(args.data_dir, args.mask_dir, args.pipeline_config, args.ome_tiff)
