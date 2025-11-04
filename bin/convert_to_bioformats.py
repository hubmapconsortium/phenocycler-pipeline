#!/usr/bin/env python3
import json
import shlex
from argparse import ArgumentParser
from os import fspath
from pathlib import Path
from pprint import pprint
from shutil import copy
from subprocess import check_call
from typing import Iterable

from ome_utils import find_ome_tiffs

output_dir = Path("/output")
output_path_single = output_dir / "converted.ome.tiff"
bioformats2raw_command_template = [
    "/opt/bioformats2raw/bin/bioformats2raw",
    "--resolutions",
    "1",
    "--series",
    "0",
    "{input_qptiff}",
    "/output/converted.raw",
]
raw2ometiff_command = [
    "/opt/raw2ometiff/bin/raw2ometiff",
    "/output/converted.raw",
    fspath(output_path_single),
]


def get_directory_manifest(paths: Iterable[Path]):
    manifest = []
    for path in paths:
        manifest.append(
            {
                "class": "File",
                "path": fspath(path),
                "basename": fspath(path),
            }
        )

    return manifest


def find_qptiffs(input_directory: Path) -> list[Path]:
    qptiffs = list(input_directory.glob("raw/images/*.qptiff"))
    if not qptiffs:
        qptiffs = list(input_directory.glob("**/*.qptiff"))
    return qptiffs


def main(input_directory: Path):
    files = []
    qptiffs = find_qptiffs(input_directory)
    ometiffs = list(find_ome_tiffs(input_directory, recurse=True))
    if ometiffs:
        print("Found OME-TIFF(s):")
        pprint(ometiffs)
        for ometiff in ometiffs:
            relative_path = ometiff.relative_to(input_directory)
            ometiff_output_file = output_dir / relative_path
            ometiff_output_file.parent.mkdir(exist_ok=True, parents=True)
            print("Copying", ometiff, "to", ometiff_output_file)
            copy(ometiff, ometiff_output_file)
            files.append(relative_path)
    elif qptiffs:
        if len(qptiffs) > 1:
            raise NotImplementedError("Multiple QPTIFFs are not supported")
        bioformats2raw_command = [
            piece.format(input_qptiff=qptiffs[0]) for piece in bioformats2raw_command_template
        ]
        print("Running", shlex.join(bioformats2raw_command))
        check_call(bioformats2raw_command)
        print("Running", raw2ometiff_command)
        check_call(raw2ometiff_command)
        files.append(output_path_single)
    else:
        raise ValueError("No OME-TIFF or QPTIFF images found")
    with open("manifest.json", "w") as f:
        manifest = get_directory_manifest(files)
        pprint(manifest)
        json.dump(manifest, f)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_directory", type=Path)
    args = p.parse_args()

    main(args.input_directory)
