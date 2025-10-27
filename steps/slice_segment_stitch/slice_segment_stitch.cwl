#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1

requirements:
- class: ScatterFeatureRequirement

inputs:
  segmentation_method:
    type: string
  gpus:
    type: string
  source_dataset_dir:
    type: Directory
  ome_tiff:
    type: File
  meta_path:
    type: File?
  channels_path:
    type: File?
  invert_geojson_mask:
    type: boolean?
  tile_size:
    type: int?
  tile_overlap:
    type: int?

outputs:
  pipeline_output:
    outputSource: collect_output/pipeline_output
    type: Directory
    label: "Expressions and segmentation masks in OME-TIFF format"
  crop_debug_data:
    outputSource: crop_image/crop_debug_data
    type: Directory?
    label: "Debug data from GeoJSON image cropping"

steps:
  crop_image:
    in:
      ome_tiff:
        source: ome_tiff
      dataset_dir:
        source: source_dataset_dir
      invert_geojson_mask:
        source: invert_geojson_mask
    out:
     - crop_ome_tiff
     - crop_debug_data
    run: crop_input_image.cwl

  threshold_image:
    in:
      ome_tiff:
        source: crop_image/crop_ome_tiff
      dataset_dir:
        source: source_dataset_dir
    out:
      - thresholded_ome_tiff
    run: threshold_image.cwl

  collect_dataset_info:
    in:
      data_dir:
        source: source_dataset_dir
      meta_path:
        source: meta_path
      channels_path:
        source: channels_path
      ome_tiff:
        source: threshold_image/thresholded_ome_tiff

    out:
      - pipeline_config
    run: collect_dataset_info.cwl

  prepare_segmentation_channels:
    in:
      data_dir:
        source: source_dataset_dir
      pipeline_config:
        source: collect_dataset_info/pipeline_config
      ome_tiff:
        source: threshold_image/thresholded_ome_tiff
    out:
      - segmentation_channels
    run: prepare_segmentation_channels.cwl

  run_slicing:
    in:
      segmentation_channels_dir:
        source: prepare_segmentation_channels/segmentation_channels
      pipeline_config:
        source: collect_dataset_info/pipeline_config
      tile_size:
        source: tile_size
      tile_overlap:
        source: tile_overlap
    out:
      - sliced_tiles
      - modified_pipeline_config
    run: slicing.cwl

  run_segmentation:
    scatter: dataset_dir
    in:
      method:
        source: segmentation_method
      dataset_dir:
        source: run_slicing/sliced_tiles
      gpus:
        source: gpus
    out:
      - mask_dir
    run: run_segmentation.cwl

  stitch_output:
    in:
      ometiff_dir:
        source: run_segmentation/mask_dir
      pipeline_config:
        source: run_slicing/modified_pipeline_config
    out:
      - stitched_images
    run: second_stitching.cwl

  collect_output:
    in:
      mask_dir:
        source: stitch_output/stitched_images
      pipeline_config:
        source: collect_dataset_info/pipeline_config
      ome_tiff:
        source: crop_image/crop_ome_tiff
    out:
      - pipeline_output
    run: collect_output.cwl
