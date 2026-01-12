cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.4.4
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/slicing/run_slicing.py"]


inputs:
  segmentation_channels_dir:
    type: Directory
    inputBinding:
      prefix: "--segmentation_channels_dir"

  pipeline_config:
    type: File
    inputBinding:
      prefix: "--pipeline_config_path"

  tile_size:
    type: int?
    inputBinding:
      prefix: "--tile_size"

  tile_overlap:
    type: int?
    inputBinding:
      prefix: "--tile_overlap"

outputs:
  sliced_tiles:
    type: Directory[]
    outputBinding:
      glob: "output/new_tiles/R*"

  modified_pipeline_config:
    type: File
    outputBinding:
      glob: "pipelineConfig.json"
