FROM hubmap/ome-tiff-pyramid:1.6

RUN apt-get update \
 && apt-get -y install python3-pip \
 && pip3 install git+https://github.com/hubmapconsortium/ome-utils@v0.3.5

COPY bin/convert_to_bioformats.py /opt
