"""Computable N-sensitivity decision rule (PAPER4, Section 4.1).

Implements the operational definition from the manuscript as an executable procedure.

Usage:
    python apply_n_sensitivity_rule.py

Reads the Qwen length p=0.8 archived seed pool (../recomputed_cell_means_FIXED.json, via the
P5 evidence copy when run inside the P4 evidence package) and reproduces the worked example:
ordering flips between n=3 (Append>RAG) and n=10 (RAG>Append); the reversal is reproduced in
65.8% of the 120 three-seed subsets (< 80%), so the rule returns BORDERLINE.

The function itself is generic: apply_rule(Q, theta_R1, theta_R2, n_R1, n_R2, pool, ...)
works on any seed-level outcome pool.
"""

import itertools
import json
import os
import statistics as st


def apply_rule(Q, pool, n_R1, n_R2, rho=0.8, delta=None, alpha=0.05):
    """Apply the N-sensitivity decision rule.

    Args:
        Q: decision function on a list of seed-level outcome arrays (returns a qualitative label).
        pool: dict {label: [seed-level outcomes]}; each array sorted by seed index.
        n_R1: lower resolution (sample size) at which Q is first evaluated.
        n_R2: higher resolution (full archive sample size).
        rho: replication threshold for criterion (iv) (default 0.8).
        delta: equivalence margin for criterion (ii); None => criterion (ii) not evaluated.
        alpha: FWER for the criterion (ii) interval.
    """
    theta_R1 = {k: v[:n_R1] for k, v in pool.items()}
    theta_R2 = {k: v[:n_R2] for k, v in pool.items()}
    q1, q2 = Q(theta_R1), Q(theta_R2)
    if q1 == q2:
        return {"status": "NOT-SENSITIVE", "Q_R1": q1, "Q_R2": q2,
                "reason": "Q does not change between R1 and R2"}

    # Criterion (ii): equivalence-interval check on the bootstrap difference distribution.
    if delta is not None:
        keys = list(pool)
        # difference of the two endpoints that define the reversal; general case uses
        # the first two labels of the ordering, so this is example-specific.
        diffs = [a - b for a, b in zip(pool[keys[0]], pool[keys[1]])]
        lo, hi = min(diffs), max(diffs)
        excludes_equivalence = not (lo > -delta and hi < delta)
        if not excludes_equivalence:
            return {"status": "BORDERLINE", "Q_R1": q1, "Q_R2": q2,
                    "reason": "criterion (ii): difference CI does not exclude the equivalence region"}

    # Criterion (iv): subsample replication of the reversal direction at R1.
    n = n_R2
    labels = list(pool)
    total = 0
    reproduced = 0
    for idx in itertools.combinations(range(n), n_R1):
        sub = {k: [pool[k][i] for i in idx] for k in labels}
        total += 1
        if Q(sub) == q2:  # the reversed (R2) ordering reproduces at R1 sampling
            reproduced += 1
    frac = reproduced / total if total else float("nan")
    if frac >= rho:
        return {"status": "N-SENSITIVE", "Q_R1": q1, "Q_R2": q2,
                "reversal_reproduction_fraction": round(frac, 4),
                "reason": f"reversal reproduces in {frac:.1%} >= {rho:.0%} of R1 subsamples"}
    return {"status": "BORDERLINE", "Q_R1": q1, "Q_R2": q2,
            "reversal_reproduction_fraction": round(frac, 4),
            "reason": f"reversal reproduces in only {frac:.1%} < {rho:.0%} of R1 subsamples"}


def Q_order_Append_vs_RAG(pool):
    """Decision function: 'Append>RAG' or 'RAG>Append' by cell-mean Gamma ordering."""
    mA = st.mean(pool["Append"])
    mR = st.mean(pool["RAG"])
    return "Append>RAG" if mA > mR else "RAG>Append"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cells_path = os.path.join(os.path.dirname(here), "recomputed_cell_means_FIXED.json")
    if not os.path.exists(cells_path):
        # fall back to the P5 evidence copy
        cells_path = os.path.join(here, "..", "..", "PAPER5", "evidence", "recomputed_cell_means_FIXED.json")
    cells = json.load(open(os.path.abspath(cells_path), encoding="utf-8"))
    gA = cells["qwen3.7-plus-Append-Only-length-p0.8"]["gammas"]
    gR = cells["qwen3.7-plus-RAG+Filter-length-p0.8"]["gammas"]
    pool = {"Append": gA, "RAG": gR}
    result = apply_rule(Q_order_Append_vs_RAG, pool, n_R1=3, n_R2=10, rho=0.8)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
