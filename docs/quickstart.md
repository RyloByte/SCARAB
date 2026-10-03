# Your first recruitment run

## Prepare three inputs

You need a metagenome assembly in FASTA format, raw reads in FASTQ format, and a text file listing the reads. Trusted reference genomes, such as SAGs, are optional but required for anchored recruitment and xPG construction. An assembly is not a FASTQ file, and SCARAB does not assemble your reads in this command.

For paired reads, create a tab-separated list with one pair per line and no header:

```bash
printf '%s	%s
' /absolute/path/sample_R1.fastq.gz /absolute/path/sample_R2.fastq.gz > read_list.txt
```

For interleaved reads, put one FASTQ path per line. Paths are resolved from the directory where you launch SCARAB, so absolute paths are easiest when inputs are elsewhere. Read [input requirements](inputs.md) before using several samples or references.

## Run

```bash
scarab recruit   -m /absolute/path/assembly.fasta   -l read_list.txt   -s /absolute/path/trusted_genomes   -o recruitment-results   -t 4
```

Leave advanced parameters at their defaults for the first test. `-t 4` requests four threads from supported stages; the CLI executes stages in sequence. Omitting `-s` requests the unanchored/de novo path.

## Review

Read `recruitment-results/SCARAB_log.txt` for the selected parameter method and setting. The parameter-setting subdirectory contains `denovo`, `hdbscan`, `ocsvm`, `intersect`, and `xpgs` output directories; anchored products depend on usable trusted matches. See [outputs](outputs.md) for filenames and their meaning.

Assess completeness, contamination, and reference similarity independently before treating recruited bins as validated genomes. No single recruitment threshold establishes strain identity. This command produces sequence files and intermediate tables, not a MetaPathways-style HTML explorer.
