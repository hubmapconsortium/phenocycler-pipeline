cwlVersion: v1.1
class: CommandLineTool
label: Convert a QPTiff file to a raw file

requirements:
  DockerRequirement:
    dockerPull: hubmap/ome-tiff-pyramid:1.6
    dockerOutputDirectory: "/output"
  InitialWorkDirRequirement:
    listing:
      - entryname: script.sh
        entry: |-
          file=($1/*.qptiff)
          echo Running on \${file[0]}
          /opt/bioformats2raw/bin/bioformats2raw \${file[0]} /output/converted.raw
          /opt/raw2ometiff/bin/raw2ometiff /output/converted.raw /output/converted.ome.tiff

arguments:
 - '$(inputs.data_dir)'
baseCommand: ["bash", "script.sh"]

inputs:
  data_dir:
    type: Directory


outputs:
  ome_tiff:
    type: File
    outputBinding:
      glob: "/output/converted.ome.tiff"
