from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
import yaml


@contextmanager
def new_plot():
    """
    When used in a `with` block, clears matplotlib internal state
    after plotting and saving things. Probably not necessary to be this
    thorough in clearing everything, but extra calls to `plt.clf()` and
    `plf.close()` don't *hurt*

    Intended usage:
        ```
        with new_plot():
            do_matplotlib_things()

            plt.savefig(path)
            # or
            fig.savefig(path)
        ```
    """
    plt.clf()
    try:
        yield
    finally:
        plt.clf()
        plt.close()


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
