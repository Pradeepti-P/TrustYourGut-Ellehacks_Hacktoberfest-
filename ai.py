"""The open-weight model (Qwen3 4B via Ollama) explains results that analysis.py already computed.
If Ollama is not running, a plain template explanation is used so the app never breaks."""
import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


def build_prompt(claim, res):
    caveat = claim.get("caveat", "")
    extra = ""
    if res.get("by_group"):
        extra = ("The result is also split by group (see by_group). If the overall result and the "
                 "group results point in different directions, say so clearly. ")
    return f"""You are the friendly explainer in a game called TrustYourGut. A player guessed whether a claim is true.
Category: {claim['category']}
Claim: {claim['claim']}
Verdict (already decided by code, do not change it): the claim is {'SUPPORTED' if res['supported'] else 'NOT SUPPORTED'} by the data.
Computed results (use only these numbers, never invent any): {json.dumps(res)}
Context you may use: {caveat}

Write exactly 3 short sentences in plain English for a general audience:
1) what the data shows, 2) what it does NOT prove (correlation is not causation), 3) one limitation.
{extra}Do not use bullet points or headings. /no_think"""


def fallback(claim, res):
    """Used when the model is unavailable. Still honest, just less chatty."""
    if res["type"] == "corr":
        text = (f"Across {res['n']} data points, the relationship is {res['strength']} and {res['direction']} "
                f"({res['headline_label']} = {res['r']}). This shows an association, not a cause.")
        if res.get("by_group"):
            parts = ", ".join(f"{g}: {v['r']}" for g, v in res["by_group"].items())
            text += f" Inside each group the pattern can differ ({parts})."
    elif res["type"] == "rate":
        text = (f"Out of {res['n']} games, {res['label_a']} happened {res['pct_a']}% of the time and "
                f"{res['label_b']} {res['pct_b']}%. This shows a pattern, not a cause.")
    else:
        text = (f"The average for {res['label_a']} was {res['mean_a']} compared with {res['mean_b']} for "
                f"{res['label_b']} ({res['n']} rows, {res['strength']} difference). This shows a difference, not a cause.")
    caveat = claim.get("caveat")
    return f"{text} Limitation: {caveat}" if caveat else text


def explain(claim, res):
    """Returns (text, used_model). used_model is False when the fallback was used."""
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": build_prompt(claim, res), "stream": False,
                  "think": False, "options": {"temperature": 0.3}},
            timeout=60,
        )
        r.raise_for_status()
        text = re.sub(r"<think>.*?</think>", "", r.json()["response"], flags=re.S).strip()
        if len(text) < 20:
            raise ValueError("empty answer")
        return text, True
    except Exception:
        return fallback(claim, res), False