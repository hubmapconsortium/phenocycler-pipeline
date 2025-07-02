cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.2.0-post1
    dockerOutputDirectory: /output

baseCommand: ["python", "/opt/secondary_stitcher/secondary_stitcher_runner.py"]


inputs:
  pipeline_config:
    type: File
    inputBinding:
      prefix: "--pipeline_config_path"

  ometiff_dir:
    type:
      - type: array
        items: Directory
        inputBinding:
          prefix: "--ometiff_dir"

outputs:
  stitched_images:
    type: Directory
    outputBinding:
      glob: output/pipeline_output
