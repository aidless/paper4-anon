# -*- coding: utf-8 -*-
"""P4 fourth case: CLEVR-CoGenT method-ranking N-sensitivity (independent vision domain).
Data: 5 seeds paired VQA accuracy (baseline vs object_centric) from enwi_p1_formal
(p1-final-analysis-20260807.json). Q = argmax method; R1=2 seeds, R2=5 seeds."""
import os, json, itertools, statistics as st, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SRC = os.path.join(BASE, "clevr_cogent_p1_final.json")
# data embedded here (from enwi_p1_formal p1-final-analysis-20260807.json, seeds 13/29/47/71/101)
DATA = {
  "baseline": [0.5006767072691028, 0.49984999099946, 0.5018834463401137, 0.5032168596782474, 0.501176737270903],
  "object_centric": [0.5007900474028442, 0.5024768152755832, 0.5025501530091806, 0.5034168716789674, 0.5017967744731351],
  "seeds": [13, 29, 47, 71, 101],
}
b, oc = DATA["baseline"], DATA["object_centric"]
q5 = "object_centric" if st.mean(oc) > st.mean(b) else "baseline"
print("full (5-seed) order:", q5, f"({st.mean(oc):.4f} vs {st.mean(b):.4f})")
# R1=2 seeds: flip rate over all C(5,2) subsets
tot = 0; flip = 0
for combo in itertools.combinations(range(5), 2):
    mb = st.mean([b[i] for i in combo]); mo = st.mean([oc[i] for i in combo])
    tot += 1
    if (mo > mb) != (q5 == "object_centric"):
        flip += 1
rho2 = flip / tot
# R1=3 seeds
tot3 = 0; flip3 = 0
for combo in itertools.combinations(range(5), 3):
    mb = st.mean([b[i] for i in combo]); mo = st.mean([oc[i] for i in combo])
    tot3 += 1
    if (mo > mb) != (q5 == "object_centric"):
        flip3 += 1
rho3 = flip3 / tot3
verdict2 = "N-SENSITIVE" if rho2 >= 0.8 else ("BORDERLINE" if rho2 > 0 else "NOT-SENSITIVE")
print(f"R1=2 seeds: flip_rate={rho2:.4f} ({flip}/{tot}) -> {verdict2}")
print(f"R1=3 seeds: flip_rate={rho3:.4f} ({flip3}/{tot3})")
os.makedirs(os.path.join(BASE, "analyses"), exist_ok=True)
json.dump({"case": "CLEVR-CoGenT method-ranking N-sensitivity (independent vision domain)",
           "full_order": q5, "R2": 5, "R1": 2, "flip_rate_R1_2": round(rho2, 4),
           "flip_rate_R1_3": round(rho3, 4), "verdict_R1_2": verdict2,
           "source": "enwi_p1_formal p1-final-analysis-20260807.json"},
          open(os.path.join(BASE, "analyses", "p4_clevr_case_20260809.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved analyses/p4_clevr_case_20260809.json")
