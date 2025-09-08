cwlVersion: v1.1
class: CommandLineTool
label: Convert a QPTiff file to a raw file

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-ometiff-convert
    dockerOutputDirectory: "/output"

baseCommand: ["/opt/convert_to_bioformats.py"]

inputs:
  data_dir:
    type: Directory
    inputBinding:
      position: 0

outputs:
  ome_tiff:
    type: File
    outputBinding:
      glob: "/output/converted.ome.tiff"
