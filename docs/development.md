# Development and release preparation

SCARAB 1.0.0 installation packages and runtime changes are being prepared separately from this documentation preview. Anaconda and Quay publication still require project configuration and validation; a documentation build does not publish software.

## Release checklist

1. Validate the runtime changes and run the biological demo on a fresh output directory.
2. Build and install the Python and Conda packages in fresh environments; check the CLI, native tools, and runtime parameter tables.
3. Build and test the container and its Apptainer conversion with the same demo.
4. Configure the Anaconda channel and Quay repository, publisher credentials, and release automation.
5. Review and merge the release changes, then tag the approved version and publish its tested artifacts.
6. Verify installation from the published registries and enable the matching Read the Docs version.

Registry names in the installation examples are provisional until publishing is configured. Keep credentials out of source control. Do not advertise a package tag or DOI before it exists.

Runtime reference tables under `src/scarab/configs` are part of the software. Manuscript drafts, unpublished study tables and figures, and local research outputs must not be added to release artifacts or documentation commits.

See [documentation maintenance](documentation.md) for building this guide independently of the scientific environment.
