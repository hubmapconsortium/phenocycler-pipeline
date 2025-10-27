#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1

requirements:
- class: ScatterFeatureRequirement
- class: SubworkflowFeatureRequirement

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
  tile_size:
    type: int?
  tile_overlap:
    type: int?

outputs:
  pipeline_output:
    outputSource: slice_segment_stitch/pipeline_output
    type: Directory[]
    label: "Expressions and segmentation masks in OME-TIFF format"
  crop_debug_data:
    outputSource: slice_segment_stitch/crop_debug_data
    type: Directory[]?
    label: "Debug data from GeoJSON image cropping"

steps:
  convert_to_bioformats:
    in:
      data_dir:
        source: data_dir
    out:
      - ome_tiff
    run: steps/convert_to_bioformats.cwl

  slice_segment_stitch:
    scatter: ome_tiff
    in:
      segmentation_method:
        source: segmentation_method
      gpus:
        source: gpus
      source_dataset_dir:
        source: data_dir
      ome_tiff:
        source: convert_to_bioformats/ome_tiff
      meta_path:
        source: meta_path
      channels_path:
        source: channels_path
      invert_geojson_mask:
        source: invert_geojson_mask
      tile_size:
        source: tile_size
      tile_overlap:
        source: tile_overlap
    out:
      - pipeline_output
      - crop_debug_data
    run: steps/slice_segment_stitch/slice_segment_stitch.cwl
