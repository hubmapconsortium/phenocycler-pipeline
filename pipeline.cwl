#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1

inputs:
  segmentation_method:
    type: string
  gpus:
    type: string
  data_dir:
    type: Directory
  meta_path:
    type: File
  channels_path:
    type: File

outputs:
  pipeline_output:
    outputSource: collect_output/pipeline_output
    type: Directory
    label: "Expressions and segmentation masks in OME-TIFF format"

steps:
  collect_dataset_info:
    in:
      data_dir:
        source: data_dir
      meta_path:
        source: meta_path
      channels_path:
      source: channels_path
    out:
      - pipeline_config
    run: steps/collect_dataset_info.cwl

  prepare_segmentation_channels:
    in:
      data_dir:
        source: data_dir
      pipeline_config:
        source: collect_dataset_info/pipeline_config
    out:
      - segmentation_channels
    run: steps/prepare_segmentation_channels.cwl

  run_segmentation:
    in:
      method:
        source: segmentation_method
      dataset_dir:
        source: prepare_segmentation_channels/segmentation_channels
      gpus:
        source: gpus
    out:
      - mask_dir
    run: steps/run_segmentation.cwl

  collect_output:
    in:
      data_dir:
        source: data_dir
      mask_dir:
        source: run_segmentation/mask_dir
      pipeline_config:
        source: collect_dataset_info/pipeline_config
    out:
      - pipeline_output
    run: steps/collect_output.cwl
