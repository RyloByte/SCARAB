# Packaging, validation, and releases

## One dependency definition

`requirements.txt` defines Python runtime requirements. `packaging/runtime.json` defines the supported Python version and external bioinformatics tools. `scripts/render_packaging.py` generates `environment.yml`, its compatibility alias `scarab_env.yml`, and both Conda recipes from those sources.

```bash
python scripts/render_packaging.py
python scripts/render_packaging.py --check
```

The setuptools upper bound preserves `pkg_resources`, used by the supported UMAP version. Do not remove it without updating and validating that dependency. Scientific versions are preserved rather than silently upgrading algorithms during a packaging refresh.

## Validate this checkout

In the source installation environment:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python scripts/render_packaging.py --check
scarab info
```

The regression tests exercise input validation, effective parameter overrides, safe reruns, read-name collisions, similarity thresholds, external-tool failure propagation, and unanchored/noise behavior. They are not a replacement for a representative biological reviewer run.

## Build a local Conda package

```bash
mamba create -n scarab-build -c conda-forge python=3.11 conda-build conda-index python-build
mamba run -n scarab-build conda build conda-recipe-local \
  --override-channels -c conda-forge -c bioconda --output-folder "$PWD/dist/conda"
mamba run -n scarab-build conda index "$PWD/dist/conda"
mamba create -n scarab-package-test --strict-channel-priority \
  -c "file://$PWD/dist/conda" -c conda-forge -c bioconda scarab=1.0.0
mamba run -n scarab-package-test scarab info
mamba run -n scarab-package-test scarab recruit --help
```

The local recipe builds the working tree. The release recipe uses the matching version tag from GitHub. No package upload happens during these commands.

## Python artifacts

```bash
mamba run -n scarab-build python -m build
python scripts/check_artifacts.py dist
```

The artifact check requires the runtime parameter tables, rejects manuscript/developer directories, and verifies the wheel's version and CLI entry point. The package version comes from `src/scarab/__init__.py`. Preserve the configuration tables under `src/scarab/configs`: those are required runtime reference assets, not manuscript supplements.

## Release preparation and publication

The **Build release candidates (no publishing)** GitHub Actions workflow builds/tests a local Conda package and a Docker image, runs the reviewer demo in the container, and retains artifacts. It does not tag, merge, upload to registries, or publish a release. The ordinary test workflow exercises the source install and reviewer demo; the Python artifact workflow checks source/wheel contents.

Before publication, create the Anaconda channel and Quay repository and confirm their namespace. The documentation currently uses `hallamlab` as the intended namespace. Configure publisher credentials outside the repository. Publishing remains a separate reviewed step after the candidate artifacts and reviewer outputs pass validation.

The local Conda recipe uses this checkout; the release recipe uses the matching version tag. Do not invoke the release recipe before that tag exists. Verify the published package and image through clean installs before announcing availability. Enable the corresponding Read the Docs version and use the project's Zenodo integration only after an approved release exists; do not invent a DOI.
