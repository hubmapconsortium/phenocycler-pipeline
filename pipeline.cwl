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
  data_dir:
    type: Directory
  meta_path:
    type: File?
  channels_path:
    type: File?
  invert_geojson_mask:
    type: boolean?

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
  convert_to_bioformats:
    in:
      data_dir:
        source: data_dir
    out:
      - ome_tiff
    run: steps/convert_to_bioformats.cwl

  crop_image:
    in:
      ome_tiff:
        source: convert_to_bioformats/ome_tiff
      dataset_dir:
        source: data_dir
      invert_geojson_mask:
        source: invert_geojson_mask
    out:
     - crop_ome_tiff
     - crop_debug_data
    run: steps/crop_input_image.cwl

  collect_dataset_info:
    in:
      data_dir:
        source: data_dir
      meta_path:
        source: meta_path
      channels_path:
        source: channels_path
      ome_tiff:
        source: crop_image/crop_ome_tiff

    out:
      - pipeline_config
    run: steps/collect_dataset_info.cwl

  prepare_segmentation_channels:
    in:
      data_dir:
        source: data_dir
      pipeline_config:
        source: collect_dataset_info/pipeline_config
      ome_tiff:
        source: crop_image/crop_ome_tiff
    out:
      - segmentation_channels
    run: steps/prepare_segmentation_channels.cwl

  run_slicing:
    in:
      segmentation_channels_dir:
        source: prepare_segmentation_channels/segmentation_channels
      pipeline_config:
        source: collect_dataset_info/pipeline_config
    out:
      - sliced_tiles
      - modified_pipeline_config
    run: steps/slicing.cwl

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
    run: steps/run_segmentation.cwl

  stitch_output:
    in:
      ometiff_dir:
        source: run_segmentation/mask_dir
      pipeline_config:
        source: run_slicing/modified_pipeline_config
    out:
      - stitched_images
    run: steps/second_stitching.cwl

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
    run: steps/collect_output.cwl
