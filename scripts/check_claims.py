"""Run from the project root:  python scripts/check_claims.py
Prints the real result for every claim, so nobody has to guess what the game will say."""
import sys
sys.path.insert(0, ".")
from analysis import analyze, load_df
from claims import CLAIMS

for c in CLAIMS:
    r = analyze(load_df(c), c)
    print(f"{c['category']:14} {c['id']:17} supported={str(r['supported']):5} "
          f"{r['headline_value']:>12} {r['strength']:10} n={r['n']} p={r['p_text']}")
