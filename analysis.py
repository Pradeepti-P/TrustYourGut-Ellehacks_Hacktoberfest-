"""All the statistics. The AI never computes numbers, this file does."""
import numpy as np
import pandas as pd
from scipy import stats


def _p_text(p):
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def _strength_r(r):
    a = abs(r)
    return "negligible" if a < 0.1 else "weak" if a < 0.3 else "moderate" if a < 0.5 else "strong"


def _strength_d(d):
    a = abs(d)
    return "negligible" if a < 0.2 else "small" if a < 0.5 else "medium" if a < 0.8 else "large"


def _to_number(df, col):
    """Turns text like '15 min' into 15 so the column can be used in a correlation."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.to_numeric(df[col].astype(str).str.extract(r"(\d+\.?\d*)")[0], errors="coerce")


# Optional per-dataset cleanup steps. A claim opts in with "prep": "<name>".
def _prep_spotify(df):
    df = df.drop_duplicates("track_id").dropna(subset=["track_name"]).copy()
    df["title_length"] = df["track_name"].str.len()
    df["length_group"] = np.where(df["duration_ms"] < 180_000, "Under 3 min", "3 min or longer")
    return df


PREP = {"spotify": _prep_spotify}


def load_df(claim):
    df = pd.read_csv(claim["csv"])
    if claim.get("prep"):
        df = PREP[claim["prep"]](df)
    for new_col, expr in claim.get("derive", {}).items():
        df[new_col] = df.eval(expr)
    if claim["type"] == "corr":
        _to_number(df, claim["x"])
        _to_number(df, claim["y"])
    needed = [claim.get(k) for k in ("x", "y", "value", "group", "split_by", "column")]
    return df.dropna(subset=[c for c in needed if c]).copy()


def _corr(df, c):
    method = c.get("method", "pearson")
    fn = stats.spearmanr if method == "spearman" else stats.pearsonr
    r, p = fn(df[c["x"]], df[c["y"]])
    res = {
        "type": "corr", "method": method, "n": int(len(df)),
        "r": round(float(r), 3), "p_text": _p_text(p),
        "strength": _strength_r(r), "direction": "positive" if r > 0 else "negative",
        "supported": bool(p < 0.05 and (r > 0 if c.get("op", "greater") == "greater" else r < 0) and abs(r) >= 0.1),
        "headline_label": f"Correlation ({method.title()})", "headline_value": f"{r:.2f}",
    }
    if c.get("split_by"):
        res["by_group"] = {
            str(g): {"r": round(float(fn(d[c["x"]], d[c["y"]])[0]), 3), "n": int(len(d))}
            for g, d in df.groupby(c["split_by"])
        }
    return res


def _group(df, c):
    a = df.loc[df[c["group"]] == c["a"], c["value"]]
    b = df.loc[df[c["group"]] == c["b"], c["value"]]
    _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    ma, mb = float(a.mean()), float(b.mean())
    pooled = float(np.sqrt((a.var() + b.var()) / 2))
    d = (ma - mb) / pooled if pooled else 0.0
    higher = ma > mb
    claim_direction_ok = higher if c.get("op", "greater") == "greater" else not higher
    return {
        "type": "group", "n": int(len(a) + len(b)), "p_text": _p_text(p),
        "mean_a": round(ma, 2), "mean_b": round(mb, 2),
        "label_a": c["a"], "label_b": c["b"],
        "strength": _strength_d(d), "direction": "higher" if higher else "lower",
        "supported": bool(p < 0.05 and claim_direction_ok and abs(d) >= 0.2),
        "headline_label": f"Average: {c['a']} vs {c['b']}",
        "headline_value": f"{ma:.1f} vs {mb:.1f}",
    }


def _rate(df, c):
    """Compares how often outcome a happens vs outcome b (for example home wins vs away wins)."""
    na, nb = int((df[c["column"]] == c["a"]).sum()), int((df[c["column"]] == c["b"]).sum())
    total = int(len(df))
    p = stats.binomtest(na, na + nb, 0.5).pvalue  # if there were no edge, a and b would be 50/50
    gap = (na - nb) / total
    return {
        "type": "rate", "n": total, "p_text": _p_text(p),
        "count_a": na, "count_b": nb, "label_a": c["label_a"], "label_b": c["label_b"],
        "pct_a": round(100 * na / total, 1), "pct_b": round(100 * nb / total, 1),
        "strength": "small" if abs(gap) < 0.1 else "moderate" if abs(gap) < 0.2 else "large",
        "direction": "higher" if na > nb else "lower",
        "supported": bool(p < 0.05 and na > nb and abs(gap) >= 0.03),
        "headline_label": f"{c['label_a']} vs {c['label_b']}",
        "headline_value": f"{100 * na / total:.0f}% vs {100 * nb / total:.0f}%",
    }


def analyze(df, claim):
    if claim["type"] == "corr":
        return _corr(df, claim)
    if claim["type"] == "rate":
        return _rate(df, claim)
    return _group(df, claim)