import argparse
import csv
from collections import defaultdict
from pathlib import Path
from pprint import pprint
from typing import Optional

import aicsimageio
import tifffile as tif
import yaml
from ome_utils import get_physical_size_quantities

from utils import (
    get_channel_name_id_index_mapping,
    make_dir_if_not_exists,
    path_to_str,
    path_to_str_local,
    save_pipeline_config,
)
from utils_ome import strip_namespace


def read_meta(meta_path: Path) -> dict:
    with open(meta_path, "r") as s:
        meta = yaml.safe_load(s)
    return meta


def convert_all_paths_to_str(listing: dict) -> dict[int, dict[str, str]]:
    all_ch_dirs = dict()
    for channel_name, ch_path in listing.items():
        all_ch_dirs[channel_name] = path_to_str_local(ch_path)
    return all_ch_dirs


def get_pixel_size_from_img(img: Path) -> tuple[float, float, str, str]:
    dimensions = get_physical_size_quantities(tif.TiffFile(img))
    pixel_size_x = dimensions["X"].magnitude
    pixel_size_y = dimensions["Y"].magnitude
    pixel_unit_x = format(dimensions["X"].units, "~")
    pixel_unit_y = format(dimensions["Y"].units, "~")
    return pixel_size_x, pixel_size_y, pixel_unit_x, pixel_unit_y


def get_pixel_size_from_tsv(tsvpath: Path) -> tuple[float, float, str, str]:
    # print(tsvpath)
    with open(path_to_str(tsvpath)) as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")
        for row in reader:
            pixel_size_x = float(row["pixel_size_x_value"])
            pixel_size_y = float(row["pixel_size_y_value"])
            pixel_unit_x = row["pixel_size_x_unit"]
            pixel_unit_y = row["pixel_size_y_unit"]

    return pixel_size_x, pixel_size_y, pixel_unit_x, pixel_unit_y
    # with tif.TiffWriter(path_to_str(tifpath), bigtiff=True) as tf:
    #    tf.write(
    #        metadata={
    #            'PhysicalSizeX' : pixel_size_x,
    #            'PhysicalSizeY' : pixel_size_y
    #        }
    #    )


def get_segm_channel_ids_from_ome(
    path: Path,
    channels_metadata: dict[str, set[str]],
) -> tuple[dict[str, list[str]], dict[str, list[int]]]:
    """
    Returns a 2-tuple:
     [0] Mapping from segmentation channel names to 0-based indexes into channel list
     [1] Adjustment of segm_ch_names listing the first segmentation channel found
    """
    with tif.TiffFile(path_to_str(path)) as TF:
        ome_meta = TF.ome_metadata
    ome_xml = strip_namespace(ome_meta)
    name_id_index_mapping: dict[str, list[int]] = get_channel_name_id_index_mapping(ome_xml)
    pprint(name_id_index_mapping)
    segm_ch_ids: dict[str, list[str]] = defaultdict(list)
    pprint(channels_metadata)

    for segm_type in ["cell", "nucleus"]:
        channel_set = channels_metadata[segm_type]
        for channel_name_or_id in channel_set:
            segm_ch_ids[segm_type].extend(name_id_index_mapping[channel_name_or_id])

    return dict(segm_ch_ids), dict(name_id_index_mapping)


def get_first_img_path(data_dir: Path, listing: dict[int, dict[str, Path]]) -> Path:
    first_region = min(list(listing.keys()))
    first_img_path = list(listing[first_region].values())[0]
    return Path(data_dir / first_img_path).absolute()


def is_selected(s: str) -> bool:
    return s.casefold() in {"yes", "true"}


def get_channel_metadata(data_dir: Path, channels_path: Path) -> Optional[dict[str, set[str]]]:
    channel_metadata = defaultdict(set)
    if channels_path is not None and not channels_path.exists():
        print("Error no " + str(channels_path))
    if channels_path is None:
        for file in data_dir.glob("**/*.channels.csv"):
            channels_path = file
        if channels_path is None:
            print("No *.channels.csv file found in " + str(data_dir))
            return None
    with open(channels_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0].casefold().strip() in {"channel_id", "channel id"}:
                print(channels_path, " has header row ", row, ". Please delete it and resubmit")
                continue
            ch_id = row[0]
            if is_selected(row[1]):
                channel_metadata["nucleus"].add(ch_id)
            if is_selected(row[2]):
                channel_metadata["cell"].add(ch_id)
    if channel_metadata:
        return channel_metadata


def main(
    data_dir: Path,
    meta_path: Optional[Path],
    channels_path: Optional[Path],
    ome_tiff: Path,
    out_dir: Path,
):
    make_dir_if_not_exists(out_dir)
    if ome_tiff is not None:
        first_img_path = ome_tiff
    else:
        first_img_path = data_dir / "converted.ome.tiff"

    x_size, y_size, x_unit, y_unit = get_pixel_size_from_img(first_img_path)

    # for image_file in data_dir.glob("*.tsv"):
    #   tsv_path = image_file
    # tsv_path = data_dir.glob("*.ome.tsv")
    # x_size, y_size, x_unit, y_unit = get_pixel_size_from_tsv(tsv_path)

    channel_names = [str(c) for c in aicsimageio.AICSImage(first_img_path).channel_names]
    channels_metadata = get_channel_metadata(data_dir, channels_path)

    if channels_metadata is None:
        meta = read_meta(meta_path)
        channels_metadata = meta["segmentation_channels"]

    segm_ch_ids, name_id_index_mapping = get_segm_channel_ids_from_ome(
        first_img_path, channels_metadata
    )

    listing = {first_img_path.name.split(".")[0]: first_img_path}

    listing_str = convert_all_paths_to_str(listing)

    pipeline_config = {
        "channel_names": channel_names,
        "segmentation_channel_ids": segm_ch_ids,
        "dataset_map_all_slices": listing_str,
        "name_id_index_mapping": name_id_index_mapping,
        "pixel_size_x": x_size,
        "pixel_size_y": y_size,
        "pixel_unit_x": x_unit,
        "pixel_unit_y": y_unit,
    }

    pipeline_config_path = out_dir / "pipeline_config.yaml"
    save_pipeline_config(pipeline_config, pipeline_config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="path to the dataset directory",
    )
    parser.add_argument(
        "--meta_path",
        type=Path,
        help="path to dataset metadata yaml",
    )
    parser.add_argument(
        "--channels_path",
        type=Path,
        help="path to the channels.csv file",
    )
    parser.add_argument(
        "--ome_tiff",
        type=Path,
        required=True,
        help="path to the converted ome.tiff file",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("/output"),
        help="path to the converted ome.tiff file",
    )
    args = parser.parse_args()

    main(
        data_dir=args.data_dir,
        meta_path=args.meta_path,
        channels_path=args.channels_path,
        ome_tiff=args.ome_tiff,
        out_dir=args.output_dir,
    )
