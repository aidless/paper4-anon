# PAPER4 evidence package (Revision12)

Archived per the manuscript's "accompanying evidence package" statements:
- within_condition_results.json: 200-seed simulation (9 alpha levels; CV_N5/N8/N15/N30) used for Figure 3 and the CV-ranking check.
- p4_reversal_probability.json: Case-2-style sign-reversal and decision-rule analyses.
- heldout_validations_20260806.json: P4 decision-rule application (Qwen length p=0.8, n=3 vs n=10; 65.8% reversal fraction) plus other in-archive cross-validations.
- input_manifest_20260806.json: SHA-256 of all key inputs across the acceptance-baseline package.
- recomputed_cell_means_FIXED.json: 12 p=0.8 cells x 10 seeds (per-seed Gamma) referenced by the rule-application paragraph.

Not archived (declared in the manuscript): Case-1 raw per-round traces come from the companion source study (not persisted locally); Case-2 raw API logs are the source study's (the 36,000/48,000-call logs are referenced in the companion repository statement).
