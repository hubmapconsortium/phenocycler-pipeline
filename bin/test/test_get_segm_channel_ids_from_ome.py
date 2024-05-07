import pytest
from collect_dataset_info import get_segm_channel_ids_from_ome
from pathlib import Path
from utils_ome import strip_namespace

# https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit?pli=1#gid=0
# Spec for the metadata is in this spreadsheet
#
def test_get_segm_channel_ids_from_ome():
    result, _ = get_segm_channel_ids_from_ome(Path("test_files/16-11_Scan1.compressed.ome.tiff"), {"nucleus": ["DAPI"], "cells":["E-cadherin"]})
    print(result)
    assert result == {'DAPI': 0, 'E-cadherin': 4}
