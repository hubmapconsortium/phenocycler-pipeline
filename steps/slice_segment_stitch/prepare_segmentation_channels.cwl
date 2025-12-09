cwlVersion: v1.1
class: CommandLineTool
label: Prepare images for segmentation

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.4
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/prepare_segmentation_channels.py"]

inputs:
  data_dir:
    type: Directory
    inputBinding:
      prefix: "--data_dir"

  pipeline_config:
    type: File
    inputBinding:
      prefix: "--pipeline_config"

  ome_tiff:
    type: File
    inputBinding:
      prefix: "--ome_tiff"


outputs:
  segmentation_channels:
    type: Directory
    outputBinding:
      glob: "/output/segmentation_channels/"
