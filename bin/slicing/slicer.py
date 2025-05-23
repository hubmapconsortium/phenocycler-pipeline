import os
import os.path as osp
from pathlib import Path

import dask
import numpy as np
import tifffile as tif
from tiling import GridTiling, SnakeTiling


def get_tile(arr, hor_f: int, hor_t: int, ver_f: int, ver_t: int, overlap=0):
    hor_f -= overlap
    hor_t += overlap
    ver_f -= overlap
    ver_t += overlap

    left_check = hor_f
    top_check = ver_f
    right_check = hor_t - arr.shape[1]
    bot_check = ver_t - arr.shape[0]

    left_pad_size = 0
    top_pad_size = 0
    right_pad_size = 0
    bot_pad_size = 0

    if left_check < 0:
        left_pad_size = abs(left_check)
        hor_f = 0
    if top_check < 0:
        top_pad_size = abs(top_check)
        ver_f = 0
    if right_check > 0:
        right_pad_size = right_check
        hor_t = arr.shape[1]
    if bot_check > 0:
        bot_pad_size = bot_check
        ver_t = arr.shape[0]

    tile_slice = (slice(ver_f, ver_t), slice(hor_f, hor_t))
    tile = arr[tile_slice]
    padding = ((top_pad_size, bot_pad_size), (left_pad_size, right_pad_size))
    if max(padding) > (0, 0):
        tile = np.pad(tile, padding, mode="constant")
    return tile


def split_by_size(
    arr: np.ndarray,
    channel_name: str,
    tile_w: int,
    tile_h: int,
    overlap: int,
) -> tuple[list[np.ndarray], list[Path]]:
    """Splits image into tiles by size of tile.
    tile_w - tile width
    tile_h - tile height
    """
    region = 1
    x_axis = -1
    y_axis = -2
    arr_width, arr_height = arr.shape[x_axis], arr.shape[y_axis]

    x_ntiles = arr_width // tile_w if arr_width % tile_w == 0 else (arr_width // tile_w) + 1
    y_ntiles = arr_height // tile_h if arr_height % tile_h == 0 else (arr_height // tile_h) + 1

    tiles = []
    img_names = []

    # row
    for i in range(0, y_ntiles):
        # height of this tile
        ver_f = tile_h * i
        ver_t = ver_f + tile_h

        # col
        for j in range(0, x_ntiles):
            # width of this tile
            hor_f = tile_w * j
            hor_t = hor_f + tile_w

            tile = get_tile(arr, hor_f, hor_t, ver_f, ver_t, overlap)

            # Need names like R0_X1_Y1_cell.tif R0_X1_Y1_nucleus.tif instead of the current names

            tiles.append(tile)
            tiling = GridTiling()
            tile_num = (i * x_ntiles) + j
            co_ords = tiling.coordinates_from_index(tile_num, x_ntiles, y_ntiles)
            print(co_ords, x_ntiles, y_ntiles, tile_num)
            folder = Path(f"R{region:d}_X{co_ords[0] + 1:d}_Y{co_ords[1] + 1:d}")
            name = (
                folder / f"R{region:d}_X{co_ords[0] + 1:d}_Y{co_ords[1] + 1:d}_{channel_name}.tif"
            )

            # name = "{region:d}_{tile:05d}_Z{zplane:03d}_CH{channel:d}.tif".format(
            #     region=region, tile=tile_num, zplane=zplane, channel=channel
            # )
            img_names.append(name)

    return tiles, img_names


def slice_img(
    in_path: Path,
    out_dir: Path,
    tile_size: int,
    overlap: int,
    zplane: int,
    channel_name: str,
):
    this_plane_tiles, this_plane_img_names = split_by_size(
        tif.imread(in_path),
        channel_name=channel_name,
        tile_w=tile_size,
        tile_h=tile_size,
        overlap=overlap,
    )

    task = []
    for i, img in enumerate(this_plane_tiles):
        base = out_dir / this_plane_img_names[i]
        base.parent.mkdir(exist_ok=True, parents=True)
        task.append(
            dask.delayed(tif.imwrite)(
                osp.join(out_dir, this_plane_img_names[i]), img, photometric="minisblack"
            )
        )

    dask.compute(*task, scheduler="threads")
