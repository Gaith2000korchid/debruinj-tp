# De Bruijn Genome Assembler

An educational Python implementation of a short-read genome assembler based on a weighted De Bruijn graph.

> **Project status:** university course project maintained as a portfolio example. It is intended for learning and demonstration, not for production-scale genome assembly.

## Overview

The program reads single-end FASTQ sequences, extracts k-mers, builds a directed weighted graph, removes simple bubbles and tips, and writes the resulting contigs in FASTA format.

The implementation demonstrates:

- FASTQ parsing with Python generators;
- k-mer extraction and occurrence counting;
- weighted directed graphs with NetworkX;
- basic bubble and tip removal;
- contig reconstruction and FASTA export;
- command-line interfaces and automated tests.

## My contribution

This repository is based on the GPL-licensed teaching scaffold created by [Amine Ghozlane](https://github.com/aghozlane) for Université Paris Diderot.

Starting from the provided function signatures, docstrings, tests, and example data, **Gaith Korchid implemented the core assembly workflow**, including:

- FASTQ read iteration;
- k-mer generation and counting;
- De Bruijn graph construction;
- path selection by coverage and length;
- bubble and entry/out-tip simplification;
- source and sink detection;
- contig reconstruction;
- FASTA output and command-line orchestration.

The detailed provenance is recorded in [ATTRIBUTION.md](ATTRIBUTION.md).

## Workflow

1. Read single-end sequences from a FASTQ file.
2. Split every read into overlapping k-mers.
3. Count k-mer occurrences.
4. Create a directed graph whose nodes are `(k-1)`-mers.
5. Simplify bubbles and low-support tips.
6. Enumerate paths between source and sink nodes.
7. Convert paths into contig sequences.
8. Save contigs in FASTA format.

## Repository structure

```text
.
├── data/                    # Reference sequence and simulated reads
├── debruijn/
│   └── debruijn.py          # Assembler and command-line interface
├── tests/                   # Course tests and small fixtures
├── ATTRIBUTION.md           # Origin and contribution statement
├── LICENSE                  # GNU GPL v3 or later
├── requirements.txt         # Runtime dependencies
└── requirements-dev.txt     # Test and lint dependencies
```

## Data provenance

The example is based on the Enterovirus A71 BrCr reference sequence, GenBank accession [U22521](https://www.ncbi.nlm.nih.gov/nuccore/U22521).

The original course reads were simulated with [ART](https://doi.org/10.1093/bioinformatics/btr708) using the command documented in the upstream course material:

```bash
art_illumina -i eva71.fna -ef -l 100 -f 20 -o eva71 \
  -ir 0 -dr 0 -ir2 0 -dr2 0 -na -qL 41 -rs 1539952693
```

The repository contains viral reference and simulated sequencing data only. It contains no patient-level or confidential health data.

## Installation

Python 3.9 or later is recommended.

```bash
git clone https://github.com/Gaith2000korchid/debruijn-genome-assembler.git
cd debruijn-genome-assembler

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Usage

Run the assembler on the included 100-read example:

```bash
python -m debruijn.debruijn \
  -i data/eva71_hundred_reads.fq \
  -k 22 \
  -o contigs.fasta
```

For a small graph visualization:

```bash
python -m debruijn.debruijn \
  -i data/eva71_two_reads.fq \
  -k 22 \
  -o contigs.fasta \
  -f graph.png
```

Display all command-line options:

```bash
python -m debruijn.debruijn --help
```

## Tests and code checks

### Docker

Build the container once:

```bash
docker build -t debruijn-assembler:local .
```

Run the included two-read example. Input is mounted read-only and output is written to a separate directory on the host:

```bash
mkdir -p results
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd)/data,dst=/input,readonly" \
  --mount "type=bind,src=$(pwd)/results,dst=/output" \
  debruijn-assembler:local -i /input/eva71_two_reads.fq -k 22 -o /output/contigs.fasta
```

The image runs as an unprivileged user by default. The `--user` option maps it to your host user so it can write to `results` without changing directory permissions. The image intentionally excludes the example data: mount your own FASTQ file under `/input`.

### Automated CI and image delivery

GitHub Actions runs the Python test suite, builds the Docker image, and executes a FASTQ-to-FASTA smoke test on pull requests and pushes to `master`. A version tag such as `v1.1.0` runs those checks and, if they pass, publishes `ghcr.io/gaith2000korchid/debruijn-genome-assembler:v1.1.0` to GitHub Container Registry. Publication is the delivery step; this CLI has no running server to deploy. The first package may require changing its visibility in GitHub Packages if you want anonymous pulls.

This extension applies the container and GitHub Actions ideas from Coursera to this existing bioinformatics program; the Dockerfile, pipeline, and smoke test are tailored to its CLI and example FASTQ data. See [ATTRIBUTION.md](ATTRIBUTION.md) for the original course scaffold and data provenance.

Run the test suite with coverage:

```bash
pytest --cov=debruijn --cov-report=term-missing
```

Run the linter:

```bash
pylint debruijn/debruijn.py
```

The tests and grading fixture originate from the teaching repository and are retained with explicit attribution.

## Limitations

- This is a teaching implementation, not a replacement for established assemblers.
- The FASTQ reader assumes valid four-line records.
- The graph simplification rules are deliberately basic.
- Exhaustive path enumeration does not scale to large sequencing datasets.
- Only single-end reads are handled.

## License

The Python implementation is distributed under the [GNU General Public License v3.0 or later](LICENSE), matching the license notice in the original teaching scaffold.

The reference sequence and simulated data retain their respective source terms. See [ATTRIBUTION.md](ATTRIBUTION.md).
