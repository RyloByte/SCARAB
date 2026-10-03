#!/usr/bin/env bash
set -euo pipefail
# Compatibility launcher; installations use the packaged console entry point.
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${HERE}/src${PYTHONPATH:+:${PYTHONPATH}}"
exec python -m scarab "$@"
