# -*- coding: utf-8 -*-
"""P4 prospective validation on Round-4 coupling data (preregistered 2026-08-08).
Reads P5 evidence round4_live.zip (36 cells x 30 seeds), applies the four-criterion
N-sensitivity decision rule with Q = argmin-Gamma, R1=3, R2=30, rho=0.8.
Output: analyses/p4_prospective_round4_20260808.json"""
import os, json, zipfile, itertools, statistics as st, math, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ZIP = os.path.join(BASE, "..", "..", "PAPER5", "evidence", "round4_live.zip")  # fallback: also try local
if not os.path.exists(ZIP):
    ZIP = os.path.join(BASE, "round4_live.zip")
OUT = os.path.join(BASE, "analyses", "p4_prospective_round4_20260808.json")

def gamma_from_rows(rows):
    clean = [r for r in rows if r.get("arm") == "clean"]
    biased = [r for r in rows if r.get("arm") == "biased"]
    if not clean or not biased:
        return None
    def lens(rs):
        return [len((r.get("response_text") or "").split()) for r in rs]
    cl, bl = lens(clean), lens(biased)
    if len(cl) < 2 or len(bl) < 1:
        return None
    mu = st.mean(cl); sd = st.stdev(cl) if len(cl) > 1 else 0.0
    if sd == 0:
        return 0.0
    a = sorted((v - mu) / sd for v in cl); b = sorted((v - mu) / sd for v in bl)
    return sum(abs(x - y) for x, y in zip(a, b)) / len(bl)

z = zipfile.ZipFile(ZIP)
import re
PAT = re.compile(r"^(deepseek-v4-pro|deepseek-v4-flash)__(Append-Only|RAG\+Filter|Summarization)__(length|authority)__p(0\.\d+)__s(\d+)\.jsonl$")
cells = {}
for n in z.namelist():
    m = PAT.match(n)
    if not m:
        continue
    rows = [json.loads(l) for l in z.read(n).decode("utf-8").splitlines()]
    g = gamma_from_rows(rows)
    key = (m.group(1), m.group(2), m.group(3), m.group(4))
    cells.setdefault(key, {})[int(m.group(5))] = g

ARCHS = ["Append-Only", "RAG+Filter", "Summarization"]
bycell = {}
for (model, arch, bias, rate), seeds in cells.items():
    bycell.setdefault((model, bias, rate), {})[arch] = [seeds[s] for s in sorted(seeds) if seeds[s] is not None]

def order(vals):
    return tuple(a for a in sorted(ARCHS, key=lambda a: -st.mean(vals[a])))

def order(vals):
    return tuple(a for a in sorted(ARCHS, key=lambda a: -st.mean(vals[a])))

verdicts = {}
for (model, bias, rate), av in bycell.items():
    q30 = order(av)
    r1 = {a: av[a][:3] for a in ARCHS}
    q3 = order(r1)
    flip = q3 != q30
    total = 0; repro = 0
    for combo in itertools.combinations(range(min(len(av[ARCHS[0]]), 30)), 3):
        sub = {a: [av[a][i] for i in combo] for a in ARCHS}
        if order(sub) == q3:
            repro += 1
        total += 1
    rho = repro / total if total else None
    c_ii = "n/a"
    if flip:
        d = st.mean(av[q3[0]]) - st.mean(av[q30[0]])
        c_ii = "|d| < delta" if abs(d) < 0.05 else "|d| >= delta"
    verdict = "N-SENSITIVE" if (flip and (rho or 0) >= 0.8) else ("BORDERLINE" if flip else "NOT-SENSITIVE")
    verdicts[f"{model}|{bias}|p{rate}"] = {"q3": list(q3), "q30": list(q30), "flip": flip,
        "rho": round(rho, 4) if rho else None, "criterion_ii": c_ii, "verdict": verdict}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"prereg": "prereg_p4_prospective_20260808.json", "cells": len(bycell), "verdicts": verdicts},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_sens = sum(1 for v in verdicts.values() if v["verdict"] == "N-SENSITIVE")
border = sum(1 for v in verdicts.values() if v["verdict"] == "BORDERLINE")
print(f"cells={len(bycell)} N-SENSITIVE={n_sens} BORDERLINE={border} NOT={len(verdicts)-n_sens-border}")
for k, v in list(verdicts.items())[:8]:
    print(k, v["q3"], "->", v["q30"], "flip", v["flip"], "rho", v["rho"], v["verdict"])
print("saved", OUT)
