cwlVersion: v1.1
class: CommandLineTool
label: Convert a QPTiff file to a raw file

requirements:
  DockerRequirement:
    dockerPull: hubmap/ome-tiff-pyramid:latest
    dockerOutputDirectory: "/output"

arguments:
 - '$(inputs.data_dir)'
 - '/output/pipeline_output/converted.raw'
baseCommand: /opt/bioformats2raw/bin/bioformats2raw

inputs:
  data_dir:
    type: Directory


outputs:
  pipeline_output:
    type: Directory
    outputBinding:
      glob: "/output/pipeline_output/converted.raw"