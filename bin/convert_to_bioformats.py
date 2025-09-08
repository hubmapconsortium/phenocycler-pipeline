#!/usr/bin/env python3
import shlex
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy
from subprocess import check_call

from ome_utils import find_ome_tiffs

output_path = "/output/converted.ome.tiff"
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
    output_path,
]


def find_qptiffs(input_directory: Path) -> list[Path]:
    qptiffs = list(input_directory.glob("raw/images/*.qptiff"))
    if qptiffs:
        print("Found QPTIFF image(s), running conversion")
    else:
        qptiffs = list(input_directory.glob("**/*.qptiff"))
    return qptiffs


def main(input_directory: Path):
    qptiffs = find_qptiffs(input_directory)
    if qptiffs:
        bioformats2raw_command = [
            piece.format(input_qptiff=qptiffs[0]) for piece in bioformats2raw_command_template
        ]
        print("Running", shlex.join(bioformats2raw_command))
        check_call(bioformats2raw_command)
        print("Running", raw2ometiff_command)
        check_call(raw2ometiff_command)
    else:
        print("No QPTIFFs found; using OME-TIFF")
        ometiffs = list(find_ome_tiffs(input_directory))
        if not ometiffs:
            raise ValueError("No OME-TIFFs found")
        print("Copying", ometiffs[0], "to", output_path)
        copy(ometiffs[0], output_path)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_directory", type=Path)
    args = p.parse_args()

    main(args.input_directory)
