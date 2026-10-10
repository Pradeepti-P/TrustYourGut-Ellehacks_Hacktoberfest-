def analyze(df, claim):
    return {"r": 0.0, "p": 1.0, "n": len(df), "strength": "weak",
            "direction": "positive", "supported": False}
