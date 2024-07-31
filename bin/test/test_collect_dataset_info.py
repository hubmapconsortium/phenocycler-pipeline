import pytest
from collect_dataset_info import get_segm_channel_ids_from_ome, get_channel_metadata, get_segm_channel_names_from_ome, \
    get_pixel_size_from_img
from pathlib import Path
from utils_ome import strip_namespace
from ome_utils import get_physical_size_quantities
import tifffile as tif


# https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit?pli=1#gid=0
# Spec for the metadata is in this spreadsheet
#
def test_get_segm_channel_ids_from_ome():
    result, result2 = get_segm_channel_ids_from_ome(Path("test_files/16-11_Scan1.compressed.ome.tiff"),
                                                    {"nucleus": ["DAPI"], "cell": ["E-cadherin"]})
    print(result)
    assert result == {'DAPI': 0, 'E-cadherin': 4}
    assert result2 == {'cell': 'E-cadherin', 'nucleus': 'DAPI'}


def test_get_channel_metadata():
    result = get_channel_metadata(Path("test_files"), None)
    print(result)
    assert result == {'nucleus': 0, 'cell': 4}


def test_get_channel_metadata_file_misssing():
    result = get_channel_metadata(Path("test_files/empty"), None)
    print(result)
    assert result is None


def test_get_segm_channel_names_from_ome():
    result, result2 = get_segm_channel_names_from_ome(
        Path("test_files/16-11_Scan1.compressed.ome.tiff"),
        {'nucleus': 0, 'cell': 4}
    )
    assert result == {'DAPI': 0, 'E-cadherin': 4}
    assert result2 == {'cell': 'E-cadherin', 'nucleus': 'DAPI'}


def test_get_pixel_size_from_img():
    with tif.TiffFile("test_files/16-11_Scan1.compressed.ome.tiff") as TF:
        dimensions = get_physical_size_quantities(TF)
        print(dimensions)
        print(dimensions["X"].magnitude)
        print(format(dimensions["X"].units, '~'))
        results = get_pixel_size_from_img(TF)
        assert results == (0.5082855933597976, 0.5082855933597976, "µm", "µm")
