import random

import numpy as np
import plotly.express as px
import streamlit as st

from ai import MODEL, explain
from analysis import analyze, load_df
from claims import CATEGORIES, CLAIMS

st.set_page_config(page_title="TrustYourGut", page_icon="🧠")

BETS = {"Low (1 pt)": 1, "Medium (2 pts)": 2, "High (3 pts)": 3}
MIXED_ROUNDS = 6
KEYS = ["category", "queue", "idx", "points", "history", "reveal"]


@st.cache_data
def get_df(claim_id):
    claim = next(c for c in CLAIMS if c["id"] == claim_id)
    return load_df(claim)


def start_game(category):
    if category == "Mixed bag":
        pool = random.sample(CLAIMS, MIXED_ROUNDS)
    else:
        pool = [c for c in CLAIMS if c["category"] == category]
    st.session_state.update(category=category, queue=pool, idx=0, points=0, history=[], reveal=None)
    st.rerun()


def reset_game():
    for k in KEYS:
        st.session_state.pop(k, None)
    st.rerun()


def make_chart(c, df):
    if c["type"] == "rate":
        counts = df[c["column"]].value_counts().rename_axis("result").reset_index(name="games")
        return px.bar(counts, x="result", y="games",
                      labels={"result": "Result (H = home win, A = away win, D = draw)"})
    if len(df) > 3000:  # keep the chart fast on big datasets (the stats still use every row)
        df = df.sample(3000, random_state=0)
    labels = {c.get("x", ""): c.get("xlabel", ""), c.get("y", ""): c.get("ylabel", ""),
              c.get("value", ""): c.get("ylabel", "")}
    if c["type"] == "corr":
        fig = px.scatter(df, x=c["x"], y=c["y"], color=c.get("split_by"), trendline="ols",
                         opacity=0.7, log_y=c.get("log_y", False), labels=labels)
        if c.get("split_by"):  # dashed line = the overall trend across all groups
            slope, intercept = np.polyfit(df[c["x"]], df[c["y"]], 1)
            xs = np.array([df[c["x"]].min(), df[c["x"]].max()])
            fig.add_scatter(x=xs, y=slope * xs + intercept, mode="lines", name="Overall trend",
                            line=dict(color="black", dash="dash"))
    else:
        sub = df[df[c["group"]].isin([c["a"], c["b"]])]
        fig = px.box(sub, x=c["group"], y=c["value"], points="all", labels=labels)
    return fig


def menu():
    st.title("TrustYourGut")
    st.write("Does your gut beat the data? Pick an arena, make your call, then see what the evidence says.")
    cols = st.columns(len(CATEGORIES))
    for col, (name, icon) in zip(cols, CATEGORIES.items()):
        if col.button(f"{icon} {name}"):
            start_game(name)
    if st.button("🎲 Mixed bag"):
        start_game("Mixed bag")


def vote(c):
    i = st.session_state.idx
    guess = st.radio("Your gut says...", ["True", "False"], index=None, horizontal=True, key=f"guess_{i}")
    bet = st.radio("How confident are you?", list(BETS), horizontal=True, key=f"bet_{i}")
    st.caption("Right answers win points, wrong answers lose the same amount.")
    if st.button("Lock it in", disabled=guess is None):
        df = get_df(c["id"])
        res = analyze(df, c)
        correct = (guess == "True") == res["supported"]
        pts = BETS[bet] if correct else -BETS[bet]
        with st.spinner("Asking the AI..."):
            text, used_model = explain(c, res)
        st.session_state.points += pts
        st.session_state.history.append({"claim": c["claim"], "correct": correct, "pts": pts})
        st.session_state.reveal = {"res": res, "correct": correct, "pts": pts, "text": text,
                                   "used_model": used_model}
        st.rerun()


def reveal(c):
    rv = st.session_state.reveal
    res = rv["res"]
    if rv["correct"]:
        st.success(f"Your gut was right! +{rv['pts']} points")
    else:
        st.error(f"Vibes vs. reality: the data disagrees. {rv['pts']} points")
    verdict = "SUPPORTED" if res["supported"] else "NOT SUPPORTED"
    st.markdown(f"**Verdict: the data says this claim is {verdict}.**")
    st.metric(res["headline_label"], res["headline_value"], f"{res['strength']} | n = {res['n']} | p {res['p_text']}",
              delta_color="off")
    st.plotly_chart(make_chart(c, get_df(c["id"])))
    st.info(rv["text"])
    st.caption(f"Explained by {MODEL} (open-weight, running locally)" if rv["used_model"]
               else "Model unavailable, showing a built-in explanation")
    last = st.session_state.idx == len(st.session_state.queue) - 1
    if st.button("See final score" if last else "Next round"):
        st.session_state.idx += 1
        st.session_state.reveal = None
        st.rerun()


def end():
    hist = st.session_state.history
    right = sum(h["correct"] for h in hist)
    share = right / len(hist)
    title = ("Your gut is a data scientist" if share == 1 else
             "Trust your gut (mostly)" if share >= 0.6 else "Maybe trust the data")
    st.title(title)
    st.metric("Final score", f"{st.session_state.points} pts", f"{right} of {len(hist)} gut calls right",
              delta_color="off")
    if share == 1:
        st.balloons()
    for h in hist:
        st.write(f"{'✅' if h['correct'] else '❌'} {h['claim']} ({h['pts']:+d})")
    col1, col2 = st.columns(2)
    if col1.button("Play this arena again"):
        start_game(st.session_state.category)
    if col2.button("Pick another arena"):
        reset_game()


if "category" not in st.session_state:
    menu()
else:
    q, i = st.session_state.queue, st.session_state.idx
    if i >= len(q):
        end()
    else:
        c = q[i]
        st.progress(i / len(q), text=f"{st.session_state.category} | Round {i + 1} of {len(q)}")
        st.subheader(c["claim"])
        if st.session_state.reveal is None:
            vote(c)
        else:
            reveal(c)