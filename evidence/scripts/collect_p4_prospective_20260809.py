# -*- coding: utf-8 -*-
"""P4 prospective collection: prompting-strategy ranking, 30 seeds x 3 strategies x 5 problems.
Preregistered 2026-08-09 (freeze 7227DE1B). Executor deepseek-v4-flash. Gold answers from
trap problems (deterministic). Output per seed: accuracy per strategy."""
import os, json, random, re, time, urllib.request, urllib.error, sys, io

DS_KEY = os.environ.get("DS_ANTHROPIC_KEY", "")
URL = "https://api.deepseek.com/anthropic/v1/messages"
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(os.path.dirname(HERE), "analyses")
BACKOFF = [5, 15, 45, 90, 180, 300]

def ds_call(prompt):
    data = json.dumps({"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 512, "temperature": 0.0}).encode()
    req = urllib.request.Request(URL, data=data, headers={"x-api-key": DS_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read().decode())
                c = body.get("content")
                if isinstance(c, list):
                    for b in c:
                        if b.get("type") == "text" and b.get("text"):
                            return b["text"]
                    return str(c)
                return str(c)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(BACKOFF[min(attempt, 5)]); continue
            if attempt == 5: raise RuntimeError(f"DS: {e}")
            time.sleep(3)
        except Exception as e:
            if attempt == 5: raise RuntimeError(f"DS: {e}")
            time.sleep(3)
    raise RuntimeError("DS exhausted")

def trap_problems(seed, n=60):
    rng = random.Random(seed)
    probs = []
    for _ in range(n):
        t = rng.randrange(5)
        if t == 0:
            a = rng.randint(20, 90); b = rng.randint(3, 9)
            q = f"A train has {a} cars, each holding {b} passengers, except the last which is empty. How many passengers? (ignore the empty car)"
            ans = str(a * b)
        elif t == 1:
            d = rng.randint(3, 10); per = rng.randint(2, 6)
            q = f"A shop sells eggs in cartons of {per} dozen. A customer buys {d} cartons. How many individual eggs?"
            ans = str(d * per * 12)
        elif t == 2:
            a = rng.randint(30, 80); b = rng.randint(50, 120); c2 = rng.randint(10, 40)
            q = f"A store has {a} items, sells {b}, then receives {c2} back. How many items in the store?"
            ans = str(a - b + c2)
        elif t == 3:
            a = rng.randint(5, 20); b = rng.randint(4, 15); d2 = rng.randint(10, 60)
            q = f"A farm has {a} fields with {b} sheep each, plus lambs not counted. A truck takes {d2} sheep. How many sheep remain?"
            ans = str(a * b - d2)
        else:
            a = rng.randint(40, 120); f = rng.choice([2, 3, 4]); addv = rng.randint(5, 20)
            q = f"A tank holds {a} liters, is {f} percent full, then {addv} liters are added. How many liters in the tank now?"
            ans = str(a * f // 100 + addv)
        probs.append((q, ans))
    return probs

STRATS = {
    "chain_of_thought": "Think step by step, then give the final numeric answer only.",
    "direct": "Give the final numeric answer only.",
    "structured_verify": "Solve step by step, then verify your answer with a quick sanity check before giving the final number.",
}
def parse_answer(text):
    nums = re.findall(r"-?\d+", text)
    return nums[-1] if nums else None

def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    probs = trap_problems(999)
    os.makedirs(OUTDIR, exist_ok=True)
    out_p = os.path.join(OUTDIR, "p4_prospective_collection_20260809.json")
    results = json.load(open(out_p, encoding="utf-8")) if os.path.exists(out_p) else []
    done = {r["seed"] for r in results}
    for seed in range(n_seeds):
        if seed in done:
            continue
        row = {"seed": seed}
        for strat, instr in STRATS.items():
            ok = 0
            for i in range(5):
                q, gold = probs[(seed * 15 + i * 3 + list(STRATS).index(strat)) % len(probs)]
                prompt = f"{instr}\nProblem: {q}\nAnswer with ONLY the final number."
                try:
                    text = ds_call(prompt)
                except Exception:
                    text = ""
                ans = parse_answer(text)
                if ans == gold:
                    ok += 1
            row[strat] = round(ok / 5.0, 4)
        results.append(row)
        json.dump(results, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"seed {seed}: {row}", flush=True)
    print("collection complete:", len(results), "seeds")

if __name__ == "__main__":
    main()
