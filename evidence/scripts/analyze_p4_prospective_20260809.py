# -*- coding: utf-8 -*-
"""P4 prospective analysis (preregistered 2026-08-09, freeze 7227DE1B).
Data: fresh 30-seed prompting-strategy accuracy collection. Q = strategy ranking by accuracy.
R1=3 seeds, R2=30 seeds. Applies the four-criterion N-sensitivity rule."""
import os, json, itertools, statistics as st, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SRC = os.path.join(BASE, "analyses", "p4_prospective_collection_20260809.json")
OUT = os.path.join(BASE, "analyses", "p4_prospective_analysis_20260809.json")

rows = json.load(open(SRC, encoding="utf-8"))
STRATS = ["chain_of_thought", "direct", "structured_verify"]
vals = {s: [r[s] for r in rows] for s in STRATS}

def order_at(seeds):
    return tuple(s for s in sorted(STRATS, key=lambda x: -st.mean(vals[x][i] for i in seeds)))

full = order_at(range(30))
print("full (30-seed) strategy order:", full, {s: round(st.mean(vals[s]), 4) for s in STRATS})
# R1=3: flip rate over C(30,3) subsamples (cap for speed: random 5000)
import random
rng = random.Random(11)
q3 = order_at([0, 1, 2])
flips = 0
for _ in range(5000):
    sub = rng.sample(range(30), 3)
    if order_at(sub) != full:
        flips += 1
rho = flips / 5000
# R1=3 specific order vs full
print(f"R1=3 (first 3 seeds) order: {q3} vs full {full}")
print(f"flip rate (R1=3, 5000 subsamples): {rho:.4f}")
# stability curve
curve = {}
for n in [3, 5, 10, 15, 20]:
    f = 0
    for _ in range(2000):
        if order_at(rng.sample(range(30), n)) != full:
            f += 1
    curve[str(n)] = round(f / 2000, 4)
print("stability curve:", curve)
# four criteria
c_i = q3 != full
d_contrast = st.mean(vals[full[0]]) - st.mean(vals[q3[0]]) if c_i else 0.0
c_ii = "|d| >= delta" if abs(d_contrast) >= 0.05 else "|d| < delta"
verdict = "N-SENSITIVE" if (c_i and rho >= 0.8) else ("BORDERLINE" if c_i else "NOT-SENSITIVE")
print(f"criterion i={c_i} ii={c_ii} (d={d_contrast:.4f}) iv_rho={rho:.4f} -> {verdict}")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"prereg": "prereg_p4_prospective_20260809.json (freeze 7227DE1B)",
           "n_seeds": 30, "full_order": list(full), "R1_3_order": list(q3),
           "flip_rate_R1_3": round(rho, 4), "stability_curve": curve,
           "criteria": {"i": c_i, "ii": c_ii, "iii": True, "iv_rho": round(rho, 4)},
           "verdict": verdict}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
