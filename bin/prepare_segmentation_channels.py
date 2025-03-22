import argparse
from pathlib import Path
from pprint import pprint

import dask
import tifffile as tif

from utils import read_pipeline_config


def create_dirs_per_region(listing: dict[int, dict[str, str]], out_dir: Path) -> dict[int, Path]:
    dirs_per_region = {}
    dir_name_template = "region_{region:03d}"
    for region in listing:
        dir_path = out_dir / dir_name_template.format(region=region)
        dir_path.mkdir(exist_ok=True, parents=True)
        dirs_per_region[region] = dir_path
    return dirs_per_region


def change_vals_to_keys(input_dict: dict) -> dict:
    vals_to_keys = {}
    for key, val in input_dict.items():
        vals_to_keys[val] = key
    return vals_to_keys


def extract_segm_channels(path: Path, segm_ch_ids: dict[str, list[int]]):
    stack = tif.imread(path)
    if len(stack.shape) < 3:
        raise ValueError("Input image is not multichannel")
    segm_channels = {}
    for ch_name, ids in segm_ch_ids.items():
        segm_channels[ch_name] = stack[ids, ...].sum(axis=0)
    return segm_channels


def copy_channels(
    out_dir: Path,
    img_path: Path,
    img_slice_name: str,
    segmentation_channel_ids: dict[str, list[int]],
):
    new_name_template = "{slice_name}_{segm_ch_name}.tif"
    segm_channels = extract_segm_channels(img_path, segmentation_channel_ids)
    print("segm_channels:")
    pprint(segm_channels)
    for ch_name, img in segm_channels.items():
        new_name = new_name_template.format(
            slice_name=img_slice_name,
            segm_ch_name=ch_name,
        )
        dst = out_dir / new_name
        tif.imwrite(dst, img)
        print("channel:", ch_name, "| new_location:", dst)


def copy_segm_channels_to_out_dirs(
    img_path: Path,
    listing: dict[int, dict[str, str]],
    segmentation_channel_ids: dict[str, list[int]],
    out_dir: Path,
):
    tasks = []
    for img_slice_name, path in listing.items():
        # img_path = data_dir / "converted.ome.tiff"
        task = dask.delayed(copy_channels)(
            out_dir,
            img_path,
            img_slice_name,
            segmentation_channel_ids,
        )
        tasks.append(task)
    dask.compute(*tasks)


def main(data_dir: Path, pipeline_config_path: Path, ome_tiff: Path, output_dir: Path):
    print("data_dir contents:")
    from pprint import pprint

    pprint(list(data_dir.iterdir()))

    pipeline_config = read_pipeline_config(pipeline_config_path)
    segm_ch_out_dir = output_dir / "segmentation_channels"
    segm_ch_out_dir.mkdir(exist_ok=True, parents=True)

    listing = pipeline_config["dataset_map_all_slices"]

    segm_ch_ids = pipeline_config["segmentation_channel_ids"]
    for segm_type, channel_indexes in segm_ch_ids.items():
        print(segm_type, "segmentation channels:")
        for channel_index in channel_indexes:
            print("\t", pipeline_config["channel_names"][channel_index], sep="")

    dask.config.set({"num_workers": 5, "scheduler": "processes"})

    copy_segm_channels_to_out_dirs(ome_tiff, listing, segm_ch_ids, segm_ch_out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="path to the dataset directory",
    )
    parser.add_argument(
        "--pipeline_config",
        type=Path,
        required=True,
        help="path to dataset metadata yaml",
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
        pipeline_config_path=args.pipeline_config,
        ome_tiff=args.ome_tiff,
        output_dir=args.output_dir,
    )
