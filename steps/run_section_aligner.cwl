cwlVersion: v1.1
class: CommandLineTool
label: Run Section Aligner to take out a single section of tissue and crop

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:latest
    dockerOutputDirectory: "/outputs"

arguments:
 - '--crop_only'
baseCommand: ["python", "/opt/section_aligner.py"]

inputs:
  ome_tiff:
    type: File
    inputBinding:
      prefix: --input_path=
      separate: false
      position: 2


outputs:
  ome_tiff:
    type: File
    outputBinding:
      glob: "/outputs/aligned_tissue_*.ome.tiff"
