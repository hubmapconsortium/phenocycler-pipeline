FROM ubuntu:focal

RUN apt-get -qq update \
    && apt-get -qq install --no-install-recommends --yes \
    wget \
    bzip2 \
    tar \
    ca-certificates \
    curl \
    libxau-dev \
    unzip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && /bin/bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh
ENV PATH /opt/conda/bin:$PATH
ENV PYTHONBUFFERED=true

RUN mkdir /output && chmod -R a+rwx /output

# Set python version explicitly to avoid error from Ubuntu updating to 3.12
# update base environment from yaml file
RUN conda install -n base conda-libmamba-solver \
  && conda config --set solver libmamba
COPY environment.yml /tmp/
RUN conda install -y python=3.12 \
    && conda env update -f /tmp/environment.yml \
    && echo "source activate base" > ~/.bashrc \
    && conda clean --index-cache --tarballs --yes \
    && rm /tmp/environment.yml
COPY SectionAligner/main.py /opt/section_aligner.py

COPY bin /opt

CMD ["/bin/bash"]
