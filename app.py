
import random

import numpy as np
import plotly.express as px
import streamlit as st

from ai import MODEL, explain
from analysis import analyze, load_df
from claims import CATEGORIES, CLAIMS


# --------------------------------------------------
# PAGE CONFIGURATION & THEME
# --------------------------------------------------

st.set_page_config(
    page_title="TrustYourGut",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Overall background */
    .stApp {
        background:
            radial-gradient(
                ellipse at top left,
                #8F250C 0%,
                transparent 42%
            ),
            linear-gradient(
                145deg,
                #691E06 0%,
                #691E06 55%,
                #691E06 100%
            );
        color: #FBBA72;
    }

    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 750 !important;
    }

    h1 {
        letter-spacing: -1.2px;
    }

    /* Supporting text */
    .stMarkdown p {
        color: #FBBA72;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        min-height: 45px;
        border: 1px solid #3c4264;
        border-radius: 12px;
        background: #8F250C;
        color: #f6f5ff;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #FBBA72;
        background: #BB4D00;
        color: #ffffff;
        transform: translateY(-2px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #BB4D00, #CA5310);
        border: none;
        color: white;
    }

    /* Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(25, 32, 54, 0.76);
        border: 1px solid #303954;
        border-radius: 18px;
        padding: 12px;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: rgba(30, 38, 63, 0.9);
        border: 1px solid #343e60;
        border-radius: 14px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #aeb9d5;
    }

    div[data-testid="stMetricValue"] {
        color: #FBBA72;
        font-weight: 800;
    }

    /* Radio buttons */
    div[role="radiogroup"] {
        gap: 10px;
    }

    div[role="radiogroup"] label {
        background: #1a2239;
        border: 1px solid #343e60;
        border-radius: 10px;
        padding: 8px 12px;
    }

    /* Progress bar */
    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #8b5cf6, #CA5310);
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* Separators */
    hr {
        border-color: #303954;
    }

    /* Mobile layout */
    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 1rem 2rem;
        }

        h1 {
            font-size: 2rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# GAME SETTINGS
# --------------------------------------------------

BETS = {
    "Low (1 pt)": 1,
    "Medium (2 pts)": 2,
    "High (3 pts)": 3,
}

MIXED_ROUNDS = 6

KEYS = [
    "category",
    "queue",
    "idx",
    "points",
    "history",
    "reveal",
]


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def get_df(claim_id):
    claim = next(c for c in CLAIMS if c["id"] == claim_id)
    return load_df(claim)


# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

def start_game(category):
    if category == "Mixed bag":
        pool = random.sample(
            CLAIMS,
            min(MIXED_ROUNDS, len(CLAIMS)),
        )
    else:
        pool = [
            c for c in CLAIMS
            if c["category"] == category
        ]

    if not pool:
        st.warning("There are no claims available in this category yet.")
        return

    st.session_state.update(
        category=category,
        queue=pool,
        idx=0,
        points=0,
        history=[],
        reveal=None,
    )

    st.rerun()


def reset_game():
    for key in KEYS:
        st.session_state.pop(key, None)

    st.rerun()


# --------------------------------------------------
# CHART GENERATION
# --------------------------------------------------

def make_chart(c, df):
    if c["type"] == "rate":
        counts = (
            df[c["column"]]
            .value_counts()
            .rename_axis("result")
            .reset_index(name="games")
        )

        fig = px.bar(
            counts,
            x="result",
            y="games",
            labels={
                "result": "Result (H = home win, A = away win, D = draw)",
                "games": "Number of games",
            },
            color="result",
            color_discrete_sequence=[
                "#FBBA72",
                "#CA5310",
                "#8F250C",
            ],
        )

    else:
        # Sample large datasets for chart performance.
        # Statistical analysis still uses the full dataset.
        if len(df) > 3000:
            df = df.sample(3000, random_state=0)

        labels = {
            c.get("x", ""): c.get("xlabel", ""),
            c.get("y", ""): c.get("ylabel", ""),
            c.get("value", ""): c.get("ylabel", ""),
        }

        if c["type"] == "corr":
            fig = px.scatter(
                df,
                x=c["x"],
                y=c["y"],
                color=c.get("split_by"),
                trendline="ols",
                opacity=0.7,
                log_y=c.get("log_y", False),
                labels=labels,
                color_discrete_sequence=[
                    "#FBBA72",
                    "#CA5310",
                    "#f59e0b",
                    "#BB4D00",
                ],
            )

            # Overall trend line when data is grouped.
            if c.get("split_by"):
                slope, intercept = np.polyfit(
                    df[c["x"]],
                    df[c["y"]],
                    1,
                )

                xs = np.array([
                    df[c["x"]].min(),
                    df[c["x"]].max(),
                ])

                fig.add_scatter(
                    x=xs,
                    y=slope * xs + intercept,
                    mode="lines",
                    name="Overall trend",
                    line=dict(
                        color="#f8fafc",
                        dash="dash",
                    ),
                )

        else:
            sub = df[
                df[c["group"]].isin([c["a"], c["b"]])
            ]

            fig = px.box(
                sub,
                x=c["group"],
                y=c["value"],
                points="all",
                labels=labels,
                color=c["group"],
                color_discrete_sequence=[
                    "#8b5cf6",
                    "#CA5310",
                ],
            )

    # Consistent chart styling
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            color="#dbe3f5",
            size=12,
        ),
        title_font_color="#ffffff",
        legend_title_text="",
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.12)",
            zerolinecolor="rgba(148,163,184,0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.12)",
            zerolinecolor="rgba(148,163,184,0.2)",
        ),
    )

    return fig


# --------------------------------------------------
# HOME SCREEN
# --------------------------------------------------

def menu():
    st.markdown(
        """
        <div style="text-align:center; padding:1.5rem 0 1rem;">
            <div style="font-size:3.5rem;">🧠</div>
            <h1 style="
                font-size:3.4rem;
                margin-bottom:0;
                letter-spacing:-1.5px;
            ">
                Trust<span style="color:#FBBA72;">YourGut</span>
            </h1>
            <p style="
                font-size:1.15rem;
                color:#FBBA72;
                margin-top:0.7rem;
            ">
                Your intuition has a theory. The data has receipts.
            </p>
            <p style="
                color:#8b96b5;
                font-size:0.85rem;
                letter-spacing:2px;
            ">
                PREDICT &nbsp; · &nbsp; BET &nbsp; · &nbsp; REVEAL
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.subheader("🎯 Choose your arena")
    st.caption(
        "Pick a topic, trust your instincts, and see what the evidence says."
    )

    # Three categories per row for a cleaner layout.
    category_items = list(CATEGORIES.items())

    for start in range(0, len(category_items), 3):
        cols = st.columns(3)

        for col, (name, icon) in zip(
            cols,
            category_items[start:start + 3],
        ):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="text-align:center; padding:0.6rem 0;">
                            <div style="font-size:2.2rem;">{icon}</div>
                            <div style="
                                font-size:1.1rem;
                                font-weight:700;
                                color:#FBBA72;
                                margin-top:0.4rem;
                            ">{name}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Play arena →",
                        key=f"arena_{name}",
                        type="primary",
                    ):
                        start_game(name)

    st.write("")

    with st.container(border=True):
        left, right = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        with left:
            st.markdown("### 🎲 Feeling unpredictable?")
            st.caption(
                "Mix topics, make six calls, and find out how well "
                "you really know the data."
            )

        with right:
            if st.button(
                "Random mix →",
                key="mixed_bag",
            ):
                start_game("Mixed bag")

    st.write("")
    st.caption(
        "Backed by real data. Explained with AI. "
        "Your score depends on your gut."
    )


# --------------------------------------------------
# PREDICTION SCREEN
# --------------------------------------------------

def vote(c):
    i = st.session_state.idx

    with st.container(border=True):
        st.caption("🔮 YOUR PREDICTION")
        st.markdown("### What does your gut say?")

        guess = st.radio(
            "Do you think this claim is supported by the data?",
            ["True", "False"],
            index=None,
            horizontal=True,
            key=f"guess_{i}",
        )

        st.divider()
        st.markdown("#### 🎲 Choose your confidence")

        bet = st.radio(
            "How much are you willing to risk?",
            list(BETS.keys()),
            horizontal=True,
            key=f"bet_{i}",
        )

        wager = BETS[bet]

        st.markdown(
            f"""
            <div style="
                background:rgba(139,92,246,0.12);
                border:1px solid rgba(167,139,250,0.35);
                border-radius:12px;
                padding:12px 16px;
                margin:0.7rem 0 1rem;
            ">
                <span style="color:#FBBA72; font-weight:700;">
                    Your wager: {wager} point{"s" if wager != 1 else ""}
                </span>
                <br>
                <span style="color:#b9c2d8; font-size:0.9rem;">
                    Correct: +{wager} points &nbsp; · &nbsp;
                    Incorrect: -{wager} points
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Lock in my prediction →",
            type="primary",
            disabled=guess is None,
            key=f"lock_{i}",
        ):
            df = get_df(c["id"])
            res = analyze(df, c)

            correct = (guess == "True") == res["supported"]
            pts = wager if correct else -wager

            with st.spinner(
                "🔎 Checking the evidence and asking the AI..."
            ):
                text, used_model = explain(c, res)

            st.session_state.points += pts

            st.session_state.history.append({
                "claim": c["claim"],
                "correct": correct,
                "pts": pts,
            })

            st.session_state.reveal = {
                "res": res,
                "correct": correct,
                "pts": pts,
                "text": text,
                "used_model": used_model,
            }

            st.rerun()


# --------------------------------------------------
# EVIDENCE REVEAL SCREEN
# --------------------------------------------------

def reveal(c):
    rv = st.session_state.reveal
    res = rv["res"]

    if rv["correct"]:
        st.success(f"🎯 You called it! +{rv['pts']} points")
    else:
        st.error(
            f"🫣 The data disagrees. {rv['pts']} points"
        )

    verdict = (
        "SUPPORTED"
        if res["supported"]
        else "NOT SUPPORTED"
    )

    verdict_color = (
        "#FBBA72"
        if res["supported"]
        else "#CA5310"
    )

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:1.7rem 1rem;
            background:rgba(30,38,63,0.85);
            border:1px solid #343e60;
            border-radius:20px;
            margin:1rem 0;
        ">
            <div style="
                color:#aeb9d5;
                font-size:0.8rem;
                letter-spacing:2.5px;
            ">
                THE VERDICT
            </div>
            <div style="
                color:{verdict_color};
                font-size:2.4rem;
                font-weight:850;
                margin:0.5rem 0;
            ">
                {verdict}
            </div>
            <div style="color:#FBBA72;">
                Here's what the evidence actually tells us.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📈 The numbers behind the claim")

    st.metric(
        res["headline_label"],
        res["headline_value"],
        f"{res['strength']} | n = {res['n']} | p {res['p_text']}",
        delta_color="off",
    )

    st.markdown("### 📊 Show me the evidence")

    fig = make_chart(c, get_df(c["id"]))

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.markdown("### 🤖 The AI breakdown")

    with st.container(border=True):
        st.markdown(rv["text"])

    if rv["used_model"]:
        st.caption(
            f"✨ Explained by {MODEL} "
            "(open-weight model running locally)"
        )
    else:
        st.caption(
            "Built-in explanation shown because the AI model "
            "was unavailable."
        )

    st.write("")

    last = (
        st.session_state.idx
        == len(st.session_state.queue) - 1
    )

    if st.button(
        "🏆 See final score" if last else "Next round →",
        type="primary",
        key=f"next_{st.session_state.idx}",
    ):
        st.session_state.idx += 1
        st.session_state.reveal = None
        st.rerun()


# --------------------------------------------------
# FINAL SCORE SCREEN
# --------------------------------------------------

def end():
    hist = st.session_state.history

    if not hist:
        st.title("Game over")
        st.write("Play a round to see your score.")
        if st.button("Back to arenas", type="primary"):
            reset_game()
        return

    right = sum(h["correct"] for h in hist)
    total = len(hist)
    share = right / total

    title = (
        "Your gut is a data scientist 🧠"
        if share == 1
        else "Trust your gut (mostly) ✨"
        if share >= 0.6
        else "Maybe trust the data 📊"
    )

    st.markdown(
        """
        <div style="text-align:center; padding:1rem 0;">
            <div style="font-size:3.2rem;">🏆</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title(title)
    st.caption(
        f"You completed the {st.session_state.category} challenge."
    )

    with st.container(border=True):
        st.metric(
            "Final score",
            f"{st.session_state.points} pts",
            f"{right} of {total} predictions correct",
            delta_color="off",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Accuracy", f"{share:.0%}")

        with col2:
            st.metric("Rounds played", total)

    if share == 1:
        st.balloons()

    st.markdown("### 📝 Your round-by-round results")

    for index, h in enumerate(hist, start=1):
        icon = "✅" if h["correct"] else "❌"

        with st.container(border=True):
            left, right_col = st.columns(
                [4, 1],
                vertical_alignment="center",
            )

            with left:
                st.markdown(
                    f"**{icon} Round {index}**"
                )
                st.write(h["claim"])

            with right_col:
                st.metric(
                    "Points",
                    f"{h['pts']:+d}",
                    delta_color="off",
                )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Play this arena again",
            type="primary",
        ):
            start_game(st.session_state.category)

    with col2:
        if st.button("🎯 Pick another arena"):
            reset_game()


# --------------------------------------------------
# MAIN APP ROUTER
# --------------------------------------------------

if "category" not in st.session_state:
    menu()

else:
    queue = st.session_state.queue
    idx = st.session_state.idx

    if idx >= len(queue):
        end()

    else:
        claim = queue[idx]

        # Round progress and current score
        left, right = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        with left:
            st.caption(
                f"🎮 {st.session_state.category.upper()}"
            )

            st.progress(
                (idx + 1) / len(queue),
                text=f"Round {idx + 1} of {len(queue)}",
            )

        with right:
            st.metric(
                "Your points",
                st.session_state.points,
            )

        st.divider()
        st.subheader(claim["claim"])

        if st.session_state.reveal is None:
            vote(claim)
        else:
            reveal(claim)
