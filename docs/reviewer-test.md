# Reviewer/demo test

The historical demo is an external archive, not data bundled in the package or checkout. Download [demo.zip](https://drive.google.com/file/d/1yUoPpoNRl6-CZHkRoUYDbikBJk4yC-3V/view?usp=sharing), then extract it:

```bash
unzip demo.zip
cd demo
```

Check that `k12.gold_assembly.fasta`, `read_list.txt`, and `SAG/` exist. Inspect the read list and make its paths valid on your machine. Do not assume paths recorded by the original archive author exist on your system.

## Mamba package or GitHub installation

```bash
scarab info
scarab recruit -m k12.gold_assembly.fasta -l read_list.txt   -s SAG -o SCARAB_out -t 4
```

## Docker

From the extracted demo directory, replace `VERSION` with your installed image tag:

```bash
docker run --rm -u "$(id -u):$(id -g)"   -v "$PWD:$PWD" -w "$PWD" quay.io/hallamlab/scarab:VERSION   scarab recruit -m k12.gold_assembly.fasta -l read_list.txt   -s SAG -o SCARAB_out_docker -t 4
```

## Apptainer

```bash
apptainer exec --bind "$PWD:$PWD" --pwd "$PWD" scarab.sif   scarab recruit -m k12.gold_assembly.fasta -l read_list.txt   -s SAG -o SCARAB_out_apptainer -t 4
```

All three routes execute the same CLI. Input paths outside the mounted directory require additional binds. Keep separate output directories when comparing installation routes so file-existence reuse cannot hide differences.

## What to check

Confirm the command completes, inspect `SCARAB_log.txt` for mapping/feature/clustering progress and effective AutoOpt parameters, then inspect the assignment tables and nonempty FASTA products described in [outputs](outputs.md). Anchored output depends on trusted-reference matches. There is no published numeric expected-results contract in this repository for the external demo; a future reviewer bundle should add provenance, checksums, and expected outputs before being presented as a reproducibility benchmark.
