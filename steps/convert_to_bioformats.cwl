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
          file=($1/raw/images/*.qptiff)
          if [ -f \${file[0]} ]; then
            echo "Running on \${file[0]}"
          else
           file=\$(find $1 -name "*.qptiff")
           if [ -f \${file[0]} ] ; then
             echo "Running on \${file[0]} as no qptiff in /raw/images/"
           else
            file=\$(find $1 -name "*.ome.tif" -or -name "*.ome.tiff")
            echo "Skipping conversion as no qptiff found, using \${file[0]}"
            cp "\${file[0]}" /output/converted.ome.tiff
            exit 0
          fi
          /opt/bioformats2raw/bin/bioformats2raw --resolutions 1 --series 0 "\${file[0]}" /output/converted.raw
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
