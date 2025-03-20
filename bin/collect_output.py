import argparse
import logging
import shutil
from pathlib import Path
from typing import Optional

import numpy as np
import tifffile as tif
from aicsimageio import AICSImage
from ome_types import from_tiff
from ome_types.model import StructuredAnnotationList

from utils import read_pipeline_config
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
    segmentation_channel_ids: dict[str, list[int]],
    channel_names: list[str],
    pixel_size_x: float,
    pixel_size_y: float,
    pixel_unit_x: str,
    pixel_unit_y: str,
    new_xml: Optional[str] = None,
):
    with tif.TiffFile(img_path) as TF:
        if new_xml is None:
            ome_meta = TF.ome_metadata
        else:
            ome_meta = new_xml
        img_stack = TF.series[0].asarray()
    new_img_stack = add_z_axis(img_stack)
    new_ome_meta = modify_initial_ome_meta(
        xml_str=ome_meta,
        segmentation_channel_ids=segmentation_channel_ids,
        channel_names=channel_names,
        pixel_size_x=pixel_size_x,
        pixel_size_y=pixel_size_y,
        pixel_unit_x=pixel_unit_x,
        pixel_unit_y=pixel_unit_y,
    )

    with tif.TiffWriter(out_path, bigtiff=True, shaped=False) as TW:
        TW.write(
            new_img_stack,
            contiguous=True,
            photometric="minisblack",
            description=new_ome_meta,
            metadata=None,
        )


def collect_segm_masks(data_dir: Path, out_dir: Path):
    filenames_copied = []
    for image_file in data_dir.glob("**/*.ome.tiff"):
        output_file = out_dir / image_file.name
        shutil.copy(image_file, output_file)
        filenames_copied.append(image_file.name)
    return filenames_copied


def collect_expr(
    mask_filenames: list[str],
    out_dir: Path,
    segmentation_channel_ids: dict[str, list[int]],
    channel_names: list[str],
    pixel_size_x: float,
    pixel_size_y: float,
    pixel_unit_x: str,
    pixel_unit_y: str,
    ome_tiff: Path,
):
    if len(mask_filenames) == 1:
        new_filename = mask_filenames[0].replace("mask", "expr")
    else:
        filename_base = ome_tiff.name.split(".")[0]
        new_filename = f"{filename_base}_expr.ome.tiff"
    output_file = out_dir / new_filename

    modify_and_save_img(
        img_path=ome_tiff,
        out_path=output_file,
        segmentation_channel_ids=segmentation_channel_ids,
        channel_names=channel_names,
        pixel_size_x=pixel_size_x,
        pixel_size_y=pixel_size_y,
        pixel_unit_x=pixel_unit_x,
        pixel_unit_y=pixel_unit_y,
    )


def collect_ome_tiff(ome_tiff: Path, out_dir: Path):
    output_file = out_dir / ome_tiff.name
    shutil.copy(ome_tiff, output_file)


def main(mask_dir: Path, pipeline_config_path: Path, ome_tiff: Path):
    pipeline_config = read_pipeline_config(pipeline_config_path)
    out_dir = Path("/output/pipeline_output")
    mask_out_dir = out_dir / "mask"
    expr_out_dir = out_dir / "expr"
    mask_out_dir.mkdir(exist_ok=True, parents=True)
    expr_out_dir.mkdir(exist_ok=True, parents=True)

    print("\nCollecting segmentation masks")
    mask_filenames = collect_segm_masks(mask_dir, mask_out_dir)
    print("\nCollecting expressions")
    collect_expr(
        mask_filenames=mask_filenames,
        out_dir=expr_out_dir,
        segmentation_channel_ids=pipeline_config["segmentation_channel_ids"],
        channel_names=pipeline_config["channel_names"],
        pixel_size_x=pipeline_config["pixel_size_x"],
        pixel_size_y=pipeline_config["pixel_size_y"],
        pixel_unit_x=pipeline_config["pixel_unit_x"],
        pixel_unit_y=pipeline_config["pixel_unit_y"],
        ome_tiff=ome_tiff,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask_dir", type=Path, help="path to directory with segmentation masks")
    parser.add_argument("--pipeline_config", type=Path, help="path to region map file YAML")
    parser.add_argument("--ome_tiff", type=Path, help="path to the converted ome.tiff file")
    args = parser.parse_args()

    main(
        mask_dir=args.mask_dir,
        pipeline_config_path=args.pipeline_config,
        ome_tiff=args.ome_tiff,
    )
