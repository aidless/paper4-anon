# N-Sensitivity in LLM Evaluation: A Diagnostic Framework Illustrated by Four Case Studies
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  [![Data](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](LICENSE)

Anonymous artifact bundle (double-blind review).

## Contents
- `source/` -- LaTeX manuscript and analysis code (compiles with the bundled `tmlr.sty`/`tmlr.bst`; `latexmk -pdf main.tex`).
- `evidence/` -- data, preregistrations, deviation records, and analysis outputs; `evidence_manifest.json` lists every file with its SHA-256.

## Verification
- Evidence hashes: recompute SHA-256 over each file in `evidence/` and compare with `evidence_manifest.json`.
- Manuscript: compile `source/main.tex` with TeX Live (the bundle includes the TMLR style files).

## CI status: the evidence-chain job is red **by design**

`.github/workflows/ci.yml` compares every file in `evidence/` against
`evidence_manifest.json` and exits non-zero on any mismatch or absence. As of
last measurement it reports **14/24 match, 8 differ, 2 absent** (the two absent
are `p4_prospective_collect.log` / `.err`, which were dropped from the bundle
as run-time byproducts).

The gate is deliberately left red rather than silenced: re-recording the
manifest would overwrite hashes that were published against this bundle, and
that is a reviewer-facing decision, not a CI one. The drift is pre-existing —
it is recorded here so a red badge is not mistaken for a broken build, and so
nobody "fixes" it by rewriting the manifest. Read the CI log for the current
per-file comparison.

_This repository is anonymized for review; author identity will be restored at camera-ready._

## License

Code is MIT-licensed ([LICENSE](LICENSE)). Paper 4 releases the analyses, arena data, and evidence files under `evidence/` under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

GitHub's license detector reports this repository as `NOASSERTION` because it reads
a single SPDX id per repository and this one carries two. The split is deliberate:
the code stays permissively licensed so it can be reused, and the research material
stays attributable so a citation is required.