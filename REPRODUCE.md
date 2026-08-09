# Reproduction

1. **Manuscript**: `cd source && latexmk -pdf main.tex` (TeX Live 2026; bundled `tmlr.sty`/`tmlr.bst`).
2. **Analysis scripts**: under `source/` and `evidence/` (Python 3.12); each script reads paths relative to the bundle and prints its headline result.
3. **Data**: `evidence/` contains all recorded responses, per-seed archives, preregistrations, and freeze hashes; see `evidence/README.md` and `evidence_manifest.json`.
