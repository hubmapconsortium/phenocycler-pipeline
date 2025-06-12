#!/usr/bin/env python3
import shlex
from argparse import ArgumentParser
from pathlib import Path
from subprocess import check_call
from typing import Optional

import aicsimageio
import numpy as np
import rasterio
import rasterio.features
import shapely
from skimage.measure import regionprops

padding_default = 128


def find_geojson(directory: Path) -> Optional[Path]:
    geojson_files = list(directory.glob("**/*.geojson"))
    if len(geojson_files) > 1:
        raise ValueError(f"Found multiple GeoJSON files in {directory}")
    elif len(geojson_files) == 1:
        return geojson_files[0]
    else:
        return None


def crop_geojson(image_path: Path, geojson_path: Path, padding: int):
    print("Reading image from", image_path)
    image = aicsimageio.AICSImage(image_path)
    image_data = image.data
    print("Shape:", image_data.shape)

    print("Loading GeoJSON from", geojson_path)
    with open(geojson_path) as f:
        crop_geometry = shapely.from_geojson(f.read())

    identity_transform = rasterio.transform.Affine(1, 0, 0, 0, 1, 0)

    print("Computing mask")
    mask = rasterio.features.geometry_mask(
        [crop_geometry],
        image_data.shape[-2:],
        identity_transform,
        invert=True,
    )
    print("Proportion of image selected:", mask.mean())

    print("Calculating bounding box of selected region")
    rps = list(regionprops(mask.astype(np.uint8)))
    assert len(rps) == 1

    bbox = rps[0].bbox
    pixel_slices = (
        slice(max(0, bbox[0] - padding), min(bbox[1] + padding, image.shape[-2])),
        slice(max(0, bbox[2] - padding), min(bbox[3] + padding, image.shape[-1])),
    )
    print("Crop region (y, x):", pixel_slices)

    print("Cropping image with", padding, "pixel(s) of padding")
    image_data_cropped = image.data[:, :, :, *pixel_slices]
    print("Cropping mask with", padding, "pixel(s) of padding")
    mask_data_cropped = mask[*pixel_slices]

    print("Zeroing pixels outside of selection")
    image_data_cropped[:, :, :, ~mask_data_cropped] = 0

    print("Instantiating new AICSImage")
    image_cropped = aicsimageio.AICSImage(
        image_data_cropped,
        channel_names=image.channel_names,
        physical_pixel_sizes=image.physical_pixel_sizes,
    )

    output_path = Path("/output/aligned_tissue_0.ome.tif")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    print("Saving to", output_path)
    image_cropped.save(output_path)


def crop_image(image_path: Path, dataset_directory: Path):
    maybe_geojson_file = find_geojson(dataset_directory)
    if maybe_geojson_file is None:
        # TODO: use a better interface; the SectionAligner defaults
        #   are stored in the argparse ArgumentParser and would need
        #   to be duplicated here to call it directly
        command = [
            "python",
            "/opt/section_aligner.py",
            "--crop_only",
            "--output_dir=/output",
            "--num_tissue=1",
            f"--input_path={image_path}",
        ]
        print("Running", shlex.join(command))
        check_call(command)
    else:
        crop_geojson(image_path, maybe_geojson_file, padding_default)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("image_path", type=Path)
    p.add_argument("dataset_dir", type=Path)
    args = p.parse_args()

    crop_geojson(args.image_path, args.geojson_path, args.padding)
