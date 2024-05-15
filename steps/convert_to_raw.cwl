cwlVersion: v1.1
class: CommandLineTool
label: Convert a QPTiff file to a raw file

requirements:
  DockerRequirement:
    dockerPull: hubmap/ome-tiff-pyramid:latest
    dockerOutputDirectory: "/output"
  InitialWorkDirRequirement:
    listing:
      - entryname: script.sh
        entry: |-
          file=($1/*.qptiff)
          echo Running on \${file[0]}
          /opt/bioformats2raw/bin/bioformats2raw \${file[0]} /output/pipeline_output/converted.raw
          /opt/raw2ometiff/bin/raw2ometiff /output/pipeline_output/converted.raw /output/pipeline_output/converted.ome.tiff

arguments:
 - '$(inputs.data_dir)'
baseCommand: ["bash", "script.sh"]

inputs:
  data_dir:
    type: Directory


outputs:
  pipeline_output:
    type: File
    outputBinding:
      glob: "/output/pipeline_output/converted.ome.tiff"