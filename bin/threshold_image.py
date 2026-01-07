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
channel_id_columns = ["channel_id", "channel id"]


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


def get_channel_id_column_name(r: csv.DictReader) -> str:
    field_name_set = set(r.fieldnames)
    for column_possibility in channel_id_columns:
        if column_possibility in field_name_set:
            return column_possibility
    message_pieces = ["Couldn't find channel ID column in CSV metadata. Tried:"]
    message_pieces.extend(f"\t{c}" for c in channel_id_columns)
    raise KeyError("")


def parse_channel_thresholds(channels_csv: Path) -> ClipData:
    thresholds_low = {}
    thresholds_high = {}
    with open(channels_csv, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        channel_id_column = get_channel_id_column_name(r)
        for line in r:
            print(line)
            channel = line[channel_id_column]
            print(channel)
            if not isnan(threshold_low := float(line.get(threshold_low_col_name, "nan") or "nan")):
                thresholds_low[channel] = threshold_low
            if not isnan(
                threshold_high := float(line.get(threshold_high_col_name, "nan") or "nan")
            ):
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
        if min_value is not None:
            channel_data[channel_data < min_value] = 0
        if max_value is not None:
            channel_data[channel_data > max_value] = max_value
        image.data[:, i, :, :, :] = channel_data
    image_new = aicsimageio.AICSImage(
        image.data.squeeze(),
        channel_names=image.channel_names,
        dim_order="CYX",
        physical_pixel_sizes=image.physical_pixel_sizes,
    )
    image_new.save(ome_tiff_file.name)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("ome_tiff_file", type=Path)
    p.add_argument("dataset_dir", type=Path)
    args = p.parse_args()

    main(args.ome_tiff_file, args.dataset_dir)
