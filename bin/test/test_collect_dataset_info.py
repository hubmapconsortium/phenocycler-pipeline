from pathlib import Path

import pytest
import tifffile as tif
from ome_utils import get_physical_size_quantities

from collect_dataset_info import (
    get_channel_metadata,
    get_pixel_size_from_img,
    get_segm_channel_ids_from_ome,
    get_segm_channel_names_from_ome,
)
from utils_ome import strip_namespace


# https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit?pli=1#gid=0
# Spec for the metadata is in this spreadsheet
#
def test_get_segm_channel_ids_from_ome():
    result, result2 = get_segm_channel_ids_from_ome(
        Path("test_files/16-11_Scan1.compressed.ome.tiff"),
        {"nucleus": ["DAPI"], "cell": ["E-cadherin"]},
    )
    print(result)
    assert result == {"DAPI": 0, "E-cadherin": 4}
    assert result2 == {"cell": "E-cadherin", "nucleus": "DAPI"}


def test_get_channel_metadata():
    result = get_channel_metadata(Path("test_files"), None)
    print(result)
    assert result == {"nucleus": "Channel:0:0", "cell": "Channel:0:4"}


def test_get_channel_metadata_file_misssing():
    result = get_channel_metadata(Path("test_files/empty"), None)
    print(result)
    assert result is None


def test_get_segm_channel_names_from_ome():
    result, result2 = get_segm_channel_names_from_ome(
        Path("test_files/16-11_Scan1.compressed.ome.tiff"),
        {"nucleus": "Channel:0:0", "cell": "Channel:0:4"},
    )
    assert result == {"DAPI": 0, "E-cadherin": 4}
    assert result2 == {"cell": "E-cadherin", "nucleus": "DAPI"}


def test_get_segm_channel_names_from_ome_no_id():
    result, result2 = get_segm_channel_names_from_ome(
        Path("test_files/16-11_Scan1.compressed.ome.tiff"),
        {"nucleus": "DAPI", "cell": "E-cadherin"},
    )
    assert result == {"DAPI": 0, "E-cadherin": 4}
    assert result2 == {"cell": "E-cadherin", "nucleus": "DAPI"}


def test_get_segm_channel_names_from_ome_no_id_error():
    with pytest.raises(Exception):
        result, result2 = get_segm_channel_names_from_ome(
            Path("test_files/16-11_Scan1.compressed.ome.tiff"),
            {"nucleus": "DAPI2", "cell": "foobar"},
        )


def test_get_pixel_size_from_img():
    file_path = "test_files/16-11_Scan1.compressed.ome.tiff"
    with tif.TiffFile(file_path) as TF:
        dimensions = get_physical_size_quantities(TF)
        print(dimensions)
        print(dimensions["X"].magnitude)
        print(format(dimensions["X"].units, "~"))
        results = get_pixel_size_from_img(file_path)
        assert results == (0.5082855933597976, 0.5082855933597976, "µm", "µm")
