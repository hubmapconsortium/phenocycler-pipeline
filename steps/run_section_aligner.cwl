cwlVersion: v1.1
class: CommandLineTool
label: Run Section Aligner to take out a single section of tissue and crop

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-scripts:1.1
    dockerOutputDirectory: "/output"

arguments:
 - '--crop_only'
 - '--output_dir=/output'
 - '--num_tissue=1'
baseCommand: ["python", "/opt/section_aligner.py"]

inputs:
  ome_tiff:
    type: File
    inputBinding:
      prefix: --input_path=
      separate: false
      position: 2


outputs:
  crop_ome_tiff:
    type: File
    outputBinding:
      glob: "/output/aligned_tissue_0.ome.tif"
