#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from math import isnan
from pathlib import Path
from pprint import pprint

import aicsimageio


def find_channels_csv(dataset_dir: Path) -> Path:
    channels_csvs = list(dataset_dir.glob("**/*channels.csv"))
    if len(channels_csvs) == 1:
        print("Found channels CSV:", channels_csvs[0].relative_to(dataset_dir))
        return channels_csvs[0]
    elif len(channels_csvs) > 1:
        message_pieces = ["Found multiple channels CSV files:"]
        for channels_csv in channels_csvs:
            message_pieces.append(f"\t{channels_csv.relative_to(dataset_dir)}")
        raise ValueError("\n".join(message_pieces))
    else:
        raise ValueError("No channels CSV present")


def parse_channel_thresholds(channels_csv: Path) -> dict[str, float]:
    thresholds = {}
    with open(channels_csv, newline="") as f:
        r = csv.DictReader(f)
        if "threshold" not in r:
            return thresholds
        for line in r:
            threshold = float(line["threshold"])
            if not isnan(threshold):
                thresholds[line["channel_id"]] = threshold
    return thresholds


def main(ome_tiff_file: Path, dataset_dir: Path):
    channels_csv = find_channels_csv(dataset_dir)
    thresholds = parse_channel_thresholds(channels_csv)
    print("Channels thresholds:")
    pprint(thresholds)
    image = aicsimageio.AICSImage(ome_tiff_file)
    for i, channel_id in enumerate(image.channel_names):
        if channel_id in thresholds:
            threshold = thresholds[channel_id]
            print("Setting", channel_id, "pixels below", threshold, "to 0")
            channel_data = image.data[:, i, :, :, :].copy()
            channel_data[channel_data < threshold] = 0
            image.data[:, i, :, :, :] = channel_data
    image.save("image.ome.tiff")


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("ome_tiff_file", type=Path)
    p.add_argument("dataset_dir", type=Path)
    args = p.parse_args()

    main(args.ome_tiff_file, args.dataset_dir)
