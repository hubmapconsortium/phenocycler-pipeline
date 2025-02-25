cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: hubmap/segmentations:1.3.1
    dockerOutputDirectory: "output"

baseCommand: ["python", "/opt/slicing/run_slicing.py"]


inputs:
  base_stitched_dir:
    type: Directory
    inputBinding:
      prefix: "--base_stitched_dir"

outputs:
  sliced_tiles:
    type: Directory[]
    outputBinding:
      glob: "output/new_tiles/Cyc1_reg1/"

  modified_pipeline_config:
    type: File
    outputBinding:
      glob: "output/pipeline_conf/pipelineConfig.json"
