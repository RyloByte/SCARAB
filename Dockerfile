# Supply a pinned base digest for release reproducibility when available.
ARG BASE_IMAGE=mambaorg/micromamba:latest
FROM ${BASE_IMAGE}
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install --yes --name base --file /tmp/environment.yml && micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1
COPY --chown=$MAMBA_USER:$MAMBA_USER pyproject.toml setup.py requirements.txt README.md LICENSE /opt/scarab/
COPY --chown=$MAMBA_USER:$MAMBA_USER src /opt/scarab/src
RUN python -m pip install --no-deps --no-build-isolation /opt/scarab && scarab recruit --help
ENV PATH=/opt/conda/bin:$PATH
WORKDIR /work
CMD ["scarab", "recruit", "--help"]
