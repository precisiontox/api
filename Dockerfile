FROM mambaorg/micromamba:0.14.0 AS builder

# Copy yml file for the conda environment
COPY environment.yml /tmp/env.yaml

RUN apt-get update -qq && \
   micromamba install -y -c conda-forge conda-pack && \
   micromamba env create -f /tmp/env.yaml && \
   conda-pack -p /opt/conda/envs/ptox -o /tmp/env.tar && \
   micromamba remove -p /opt/conda/envs/ptox --all -y && \
   micromamba clean --all --yes

WORKDIR /ptox
RUN mkdir env && cd env && \
   tar xf /tmp/env.tar && \
   rm /tmp/env.tar && \
   /ptox/env/bin/conda-unpack

FROM python:3.6-stretch
RUN apt-get update --fix-missing && \
        apt-get install -y \
    libz-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    git \
    wget \
    unzip \
    curl \
    build-essential \
    libpq-dev \
    zlib1g-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /ptox /ptox
ENV PATH="/ptox/env/bin:$PATH"
RUN useradd -ms /bin/bash docker
WORKDIR /home/docker
USER docker

COPY ./ /home/docker/api
COPY .env /home/docker/api/.env

CMD ["flask", "run"]
#CMD ["uwsgi", "app.ini"]




