#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from math import isnan
from pathlib import Path
from pprint import pprint
from typing import NamedTuple

import aicsimageio

threshold_low_col_name = "threshold low"
threshold_high_col_name = "threshold"


class ClipData(NamedTuple):
    low: dict[str, float]
    high: dict[str, float]


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


def parse_channel_thresholds(channels_csv: Path) -> ClipData:
    thresholds_low = {}
    thresholds_high = {}
    with open(channels_csv, newline="") as f:
        r = csv.DictReader(f)
        for line in r:
            channel = line["channel_id"]
            if not isnan(threshold_low := float(line.get(threshold_low_col_name, "nan"))):
                thresholds_low[channel] = threshold_low
            if not isnan(threshold_high := float(line.get(threshold_high_col_name, "nan"))):
                thresholds_high[channel] = threshold_high
    print("Thresholds, low:")
    pprint(thresholds_low)
    print("Thresholds, high:")
    pprint(thresholds_high)
    return ClipData(low=thresholds_low, high=thresholds_high)


def main(ome_tiff_file: Path, dataset_dir: Path):
    image = aicsimageio.AICSImage(ome_tiff_file)
    channels_csv = find_channels_csv(dataset_dir)
    clip_data = parse_channel_thresholds(channels_csv)
    for i, channel_id in enumerate(image.channel_names):
        min_value = clip_data.low.get(channel_id)
        max_value = clip_data.high.get(channel_id)
        print("Thresholding channel", channel_id, "with min", min_value, "and max", max_value)
        channel_data = image.data[:, i, :, :, :].copy()
        # Different semantics for lower and upper thresholds, so no usage
        # of something like `np.clip` with both values
        channel_data[channel_data < min_value] = 0
        channel_data[channel_data > max_value] = max_value
        image.data[:, i, :, :, :] = channel_data
    image.save("image.ome.tiff")


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("ome_tiff_file", type=Path)
    p.add_argument("dataset_dir", type=Path)
    args = p.parse_args()

    main(args.ome_tiff_file, args.dataset_dir)
