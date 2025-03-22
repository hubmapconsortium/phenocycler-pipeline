from collections import defaultdict
from pathlib import Path

import yaml


def read_pipeline_config(config_path: Path):
    with open(config_path, "r") as s:
        config = yaml.safe_load(s)
    return config


def save_pipeline_config(config: dict, out_path: Path):
    with open(out_path, "w") as s:
        yaml.safe_dump(config, s)


def get_channel_name_id_index_mapping(xml) -> dict[str, list[int]]:
    pixels = xml.find("Image").find("Pixels")
    channels = pixels.findall("Channel")
    mapping = defaultdict(list)
    for i, ch in enumerate(channels):
        mapping[ch.get("Name")].append(i)
        mapping[ch.get("ID")].append(i)
    return dict(mapping)
