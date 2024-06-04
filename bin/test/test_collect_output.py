from pathlib import Path
from typing import Dict

from collect_output import modify_and_save_img
def test_modify_and_save_image():
    data_dir: Path = Path('test_files/')
    segmentation_channels: Dict[str, str] = {'nucleus': 'DAPI', 'cell':'E-cadherin'}
    pixel_size_x: float = 391.0
    pixel_size_y: float = 391.0
    pixel_unit_x: str = 'nm'
    pixel_unit_y: str = 'nm'
    ome_tiff: Path = Path('test_files/16-11_Scan1.compressed.ome.tiff')
    output_file: Path = Path('test_files/empty/test.ome.tiff')
    new_xml = None

    modify_and_save_img(
            ome_tiff,
            output_file,
            segmentation_channels,
            pixel_size_x,
            pixel_size_y,
            pixel_unit_x,
            pixel_unit_y,
            new_xml,
        )