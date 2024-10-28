cwlVersion: v1.1
class: CommandLineTool
label: Collect dataset info

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:latest
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/collect_dataset_info.py"]

inputs:
  data_dir:
    type: Directory
    inputBinding:
      prefix: "--data_dir"

  meta_path:
    type: File?
    inputBinding:
      prefix: "--meta_path"

  channels_path:
    type: File?
    inputBinding:
      prefix: "--channels_path"

  ome_tiff:
    type: File
    inputBinding:
      prefix: "--ome_tiff"

outputs:
  pipeline_config:
    type: File
    outputBinding:
      glob: "/output/pipeline_config.yaml"
