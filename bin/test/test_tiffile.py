from pathlib import Path

import tifffile

def test_load_file():

    t = tifffile.TiffFile(Path('test_files/16-11_Scan1.compressed.ome.tiff'))
    print(t.series[0].axes)
    assert t.series[0].axes == 'CYX'
    t = tifffile.TiffFile('test_files/empty/test.ome.tiff')
    print(t.series[0].axes)
    assert t.series[0].axes == 'CYX'
