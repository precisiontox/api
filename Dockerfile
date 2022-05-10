FROM mambaorg/micromamba:0.14.0

RUN apt-get update

COPY environment.yml /tmp/environment.yaml

RUN micromamba env create -f /tmp/environment.yaml && \
   micromamba clean --all --yes

COPY ./ /home/docker/api
COPY .env /home/docker/api/.env

RUN useradd -ms /bin/bash docker
WORKDIR /home/docker
USER docker

ENV PATH="/opt/conda/envs/ptox/bin:$PATH"

#CMD ["bash"]

RUN /bin/bash -c "micromamba activate ptox"

CMD [ "flask", "run" ]




