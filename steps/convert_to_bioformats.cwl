cwlVersion: v1.1
class: CommandLineTool
label: Convert a QPTiff file to a raw file

requirements:
  DockerRequirement:
    dockerPull: hubmap/phenocycler-ometiff-convert:1.3.1
    dockerOutputDirectory: "/output"
  InlineJavascriptRequirement: {}

baseCommand: ["/opt/convert_to_bioformats.py"]

inputs:
  data_dir:
    type: Directory
    inputBinding:
      position: 0

outputs:
  ome_tiff:
    type: File[]
    outputBinding:
      glob: manifest.json
      loadContents: True
      outputEval: $(eval(self[0].contents))
