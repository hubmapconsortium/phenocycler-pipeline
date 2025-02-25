cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:latest
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/slicing/run_slicing.py"]


inputs:
  segmentation_channels_dir:
    type: Directory
    inputBinding:
      prefix: "--segmentation_channels_dir"

outputs:
  sliced_tiles:
    type: Directory[]
    outputBinding:
      glob: "output/new_tiles/R*"

  modified_pipeline_config:
    type: File
    outputBinding:
      glob: "pipelineConfig.json"
