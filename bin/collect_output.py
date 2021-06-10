import argparse
import shutil
from pathlib import Path
from typing import Dict

import dask
from utils import make_dir_if_not_exists, read_pipeline_config


def copy_files(
    data_dir: Path,
    dir_name: str,
    img_name_template: str,
    out_dir: Path,
    out_name_template: str,
    region: int,
    slices: Dict[str, str],
):
    for img_slice_name, slice_path in slices.items():
        img_name = img_name_template.format(region=region, slice_name=img_slice_name)
        src = data_dir / dir_name / img_name
        dst = (
            out_dir
            / dir_name
            / out_name_template.format(region=region, slice_name=img_slice_name)
        )
        shutil.copy(src, dst)
        print("region:", region, "| src:", src, "| dst:", dst)


def collect_segm_masks(
    data_dir: Path, listing: Dict[int, Dict[str, str]], out_dir: Path
):
    out_name_template = "reg{region:03d}_{slice_name}_mask.ome.tiff"
    img_name_template = "reg{region:03d}_{slice_name}_mask.ome.tiff"
    dir_name_template = "region_{region:03d}"
    tasks = []
    for region, slices in listing.items():
        dir_name = dir_name_template.format(region=region)
        make_dir_if_not_exists(out_dir / dir_name)
        task = dask.delayed(copy_files)(
            data_dir,
            dir_name,
            img_name_template,
            out_dir,
            out_name_template,
            region,
            slices,
        )
        tasks.append(task)
    dask.compute(*tasks)


def collect_expr(data_dir: Path, listing: dict, out_dir: Path):
    out_name_template = "reg{region:03d}_{slice_name}_expr.ome.tiff"
    img_name_template = "{slice_name}.ome.tif"  # one f
    dir_name_template = "region_{region:03d}"
    tasks = []
    for region, slices in listing.items():
        dir_name = dir_name_template.format(region=region)
        make_dir_if_not_exists(out_dir / dir_name)
        task = dask.delayed(copy_files)(
            data_dir,
            dir_name,
            img_name_template,
            out_dir,
            out_name_template,
            region,
            slices,
        )
        tasks.append(task)
    dask.compute(*tasks)


def main(data_dir: Path, mask_dir: Path, pipeline_config_path: Path):
    pipeline_config = read_pipeline_config(pipeline_config_path)
    listing = pipeline_config["dataset_map_all_slices"]

    out_dir = Path("/output/pipeline_output")
    mask_out_dir = out_dir / "mask"
    expr_out_dir = out_dir / "expr"
    make_dir_if_not_exists(mask_out_dir)
    make_dir_if_not_exists(expr_out_dir)

    dask.config.set({"num_workers": 5, "scheduler": "processes"})
    print("\nCollecting segmentation masks")
    collect_segm_masks(mask_dir, listing, mask_out_dir)
    print("\nCollecting expressions")
    collect_expr(data_dir, listing, expr_out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=Path, help="path to directory with images")
    parser.add_argument(
        "--mask_dir", type=Path, help="path to directory with segmentation masks"
    )
    parser.add_argument(
        "--pipeline_config", type=Path, help="path to region map file YAML"
    )
    args = parser.parse_args()

    main(args.data_dir, args.mask_dir, args.pipeline_config)
