cwlVersion: v1.1
class: CommandLineTool
label: Threshold image using channels CSV data

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.4.4
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/threshold_image.py"]

inputs:
  ome_tiff:
    type: File
    inputBinding:
      position: 0
  dataset_dir:
    type: Directory
    inputBinding:
      position: 1

outputs:
  thresholded_ome_tiff:
    type: File
    outputBinding:
      glob: "*.ome.tiff"
