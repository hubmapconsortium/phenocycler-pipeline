from pathlib import Path
from slicing.run_slicing import main

base_stitched_dir = Path('test_files/new_tiles')
pipeline_config_path = Path('test_files/slicing_config.json')

def test_slicing_main():
    main(base_stitched_dir, pipeline_config_path)


