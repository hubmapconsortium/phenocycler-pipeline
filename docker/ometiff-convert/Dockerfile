FROM hubmap/ome-tiff-pyramid:1.6

RUN apt-get update \
 && apt-get -y install python3-pip \
 && pip3 install hubmap-ome-utils==0.3.4

COPY bin/convert_to_bioformats.py /opt
