import argparse
import json
import re
from pathlib import Path
from typing import Tuple

import tifffile as tif
from modify_pipeline_config import modify_pipeline_config
from slicer import slice_img

filename_pattern = re.compile(r"^(?P<label>\w+)_(?P<channel>\w+).tif$")


def path_to_str(path: Path):
    return str(path.absolute().as_posix())


def path_to_dict(path: Path):
    """
    Extract region, x position, y position and put into the dictionary
    {R:region, X: position, Y: position, path: path}
    """
    value_list = re.split(r"(\d+)(?:_?)", path.name)[:-1]
    if len(value_list) != 6:
        return None
    d = dict(zip(*[iter(value_list)] * 2))
    d = {k: int(v) for k, v in d.items()}
    d.update({"path": path})
    return d


def get_image_path_in_dir(dir_path: Path) -> Path:
    allowed_extensions = (".tif", ".tiff")
    listing = list(dir_path.iterdir())
    img_listing = [f for f in listing if f.suffix in allowed_extensions]
    return img_listing[0]


def get_stitched_image_shape(directory: Path) -> Tuple[int, int]:
    stitched_img_path = get_image_path_in_dir(directory)
    with tif.TiffFile(stitched_img_path) as TF:
        stitched_image_shape = TF.series[0].shape
    return stitched_image_shape


def split_channels_into_tiles(
    input_dir: Path,
    output_dir: Path,
    tile_size=1000,
    overlap=50,
):
    for file_path in input_dir.iterdir():
        if m := filename_pattern.match(file_path.name):
            channel_name = m.group("channel")

            slice_img(
                file_path,
                output_dir,
                tile_size=tile_size,
                overlap=overlap,
                zplane=1,
                channel_name=channel_name,
            )


def main(
    segmentation_channels_dir: Path,
    pipeline_config_path: Path,
    tile_size: int,
    tile_overlap: int,
):
    out_dir = Path("output/new_tiles")
    pipeline_conf_dir = Path("output/pipeline_conf")
    out_dir.mkdir(exist_ok=True, parents=True)
    pipeline_conf_dir.mkdir(exist_ok=True, parents=True)

    stitched_img_shape = get_stitched_image_shape(segmentation_channels_dir)

    print("Splitting images into tiles")
    print("Tile size:", tile_size, "| overlap:", tile_overlap)
    split_channels_into_tiles(segmentation_channels_dir, out_dir, tile_size, tile_overlap)

    modified_experiment = modify_pipeline_config(
        pipeline_config_path, (tile_size, tile_size), tile_overlap, stitched_img_shape
    )
    with open((p := "pipelineConfig.json"), "w") as f:
        print("Saving modified pipeline config to", p)
        json.dump(modified_experiment, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--segmentation_channels_dir",
        type=Path,
        help="path to directory with one image per segmentation channel",
    )
    parser.add_argument(
        "--pipeline_config_path",
        type=Path,
        help="path to pipelineConfig.json file",
    )
    parser.add_argument(
        "--tile_size",
        type=int,
        default=10_000,
    )
    parser.add_argument(
        "--tile_overlap",
        type=int,
        default=100,
    )

    args = parser.parse_args()

    main(
        segmentation_channels_dir=args.segmentation_channels_dir,
        pipeline_config_path=args.pipeline_config_path,
        tile_size=args.tile_size,
        tile_overlap=args.tile_overlap,
    )
