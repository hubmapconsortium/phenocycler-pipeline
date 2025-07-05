cwlVersion: v1.1
class: CommandLineTool
label: Collect segmentation masks and images for the final output

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.2.0-post4
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/collect_output.py"]

inputs:
  mask_dir:
    type: Directory
    inputBinding:
      prefix: "--mask_dir"
  pipeline_config:
    type: File
    inputBinding:
      prefix: "--pipeline_config"
  ome_tiff:
    type: File
    inputBinding:
      prefix: "--ome_tiff"

outputs:
  pipeline_output:
    type: Directory
    outputBinding:
      glob: "/output/pipeline_output"
