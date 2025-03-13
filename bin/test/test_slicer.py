import os
from pathlib import Path

from slicing.run_slicing import main

base_stitched_dir = Path(
    os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../../test_files/segmentation_channels/")
    )
)
pipeline_config_path = Path("test_files/slicing/slicing_config.json")


def test_slicing_main():
    main(base_stitched_dir, pipeline_config_path)
