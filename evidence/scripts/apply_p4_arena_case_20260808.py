# -*- coding: utf-8 -*-
"""P4 third-case N-sensitivity validation on Chatbot Arena (non-calibration domain).
Q = win-rate model ranking; resolution = number of battles per model.
R1=100 battles (subsample), R2=full sample. Reports P(Q flip) and the four-criterion verdict.
Input: arena_data_cache.json (per-model battle records)."""
import os, json, random, statistics as st, collections, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SRC = os.path.join(BASE, "arena_data_cache.zip")
OUT = os.path.join(BASE, "analyses", "p4_arena_case_20260808.json")

import zipfile
with zipfile.ZipFile(SRC) as z:
    cache = json.loads(z.read("arena_data_cache.json").decode("utf-8"))
model_battles = cache["model_battles"]
models = list(model_battles.keys())
# per-model win scores
scores = {}
for m in models:
    vals = []
    for b in model_battles[m]:
        r = b.get("result")
        if r == "win":
            vals.append(1.0)
        elif r == "loss":
            vals.append(0.0)
        elif r == "tie":
            vals.append(0.5)
    scores[m] = vals
print("models:", len(models), "min battles:", min(len(v) for v in scores.values()))

def order_at_n(vals_by_model, n, rng):
    wr = {}
    for m, v in vals_by_model.items():
        if len(v) >= n:
            wr[m] = st.mean(rng.sample(v, n))
    return tuple(m for m, _ in sorted(wr.items(), key=lambda x: -x[1])[:5])

rng = random.Random(42)
q_full = order_at_n(scores, min(len(v) for v in scores.values()), rng)  # full = min battles? use each model's own full sample
# full-order using each model's complete sample
q_full = tuple(m for m, _ in sorted(((m, st.mean(v)) for m, v in scores.items()), key=lambda x: -x[1])[:5])
# R1=100 battles: flip rate across 2000 subsamples
R1 = 100
flips = 0
for _ in range(2000):
    q1 = order_at_n(scores, R1, rng)
    if q1 != q_full:
        flips += 1
rho = flips / 2000
# also R1=50, R1=200 for a stability curve
curve = {}
for n in [50, 100, 200, 500]:
    f = 0
    for _ in range(1000):
        if order_at_n(scores, n, rng) != q_full:
            f += 1
    curve[str(n)] = round(f / 1000, 4)

verdict = "N-SENSITIVE" if (rho >= 0.8) else ("BORDERLINE" if 0 < rho < 0.8 else "NOT-SENSITIVE")
print("full top-5 order:", q_full)
print(f"flip rate at R1={R1}: {rho:.4f} -> verdict {verdict}")
print("stability curve:", curve)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"case": "Chatbot Arena model-ranking N-sensitivity (non-calibration third case)",
           "q_full_top5": list(q_full), "R1": R1, "flip_rate_R1": round(rho, 4),
           "stability_curve": curve, "verdict": verdict, "source": SRC},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
