# Maintenance and reproducibility

## Corrections on 9 October 2026

- Discard deleted source/sink nodes during recursive tip removal, then recompute extremities before contig export.
- Resolve the first complete bubble candidate before continuing graph traversal. Previously later nodes could overwrite the candidate and trigger a one-path standard-deviation failure; this occurred on the README's 100-read example.
- Compute path weight from its consecutive edges, excluding shortcut edges in the induced subgraph.
- Accept plain/gzip four-line FASTQ, validate record completeness, header/separator and sequence/quality lengths, and reject k-mer sizes below two.
- Remove the two empty FASTQ placeholders at the repository root. The non-empty teaching examples remain in `data/`; no source sequencing data is removed.
- Add independent regression tests, separate from the attributed teaching tests.

## Frozen dependencies

`requirements.lock` contains the Python 3.12 runtime resolution with package hashes. `requirements-dev.lock` adds the test/lint dependencies. The Dockerfile and CI consume these locks. `requirements.txt` and `requirements-dev.txt` retain human-readable dependency ranges; changing those ranges requires regenerating and testing both locks.

```bash
uv pip compile requirements.txt --python-version 3.12 --generate-hashes -o requirements.lock
uv pip compile requirements-dev.txt --python-version 3.12 --generate-hashes -o requirements-dev.lock
python -m pip install --require-hashes -r requirements-dev.lock
pytest -q
python -m debruijn.debruijn -i data/eva71_hundred_reads.fq -k 22 -o contigs.fasta
```

The image base tag remains `python:3.12-slim`; it is not a frozen OS-image digest. Package locks improve Python dependency reproducibility without claiming bit-identical container images.

## Scientific boundary

This is an educational single-end assembler. Exhaustive path enumeration limits scale. Bubble detection assumes a directed acyclic graph; circular genomes/components and realistic sequencing-error models are outside this implementation. Tests and a FASTA-producing smoke run are execution evidence, not assembly-accuracy validation against established assemblers.
