import random
from pathlib import Path

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
    page_icon="trust.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at top left, #8F250C 0%, transparent 42%),
            linear-gradient(145deg, #691E06 0%, #691E06 55%, #691E06 100%);
        color: #FBBA72;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] {
        background: #4a1504 !important;
        border-right: 1px solid #3c4264;
    }

    [data-testid="stSidebar"] button {
        visibility: visible !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #FBBA72;
    }

    .block-container {
        max-width: 1050px;
        padding-top: 4.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 750 !important;
    }

    h1 {
        letter-spacing: -1.2px;
    }

    .stMarkdown p {
        color: #FBBA72;
    }

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

    .stButton > button:hover:not(:disabled) {
        border-color: #FBBA72;
        background: #BB4D00;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow:
            0 0 0 2px rgba(251, 186, 114, 0.55),
            0 6px 16px rgba(0, 0, 0, 0.35);
    }

    .stButton > button:active:not(:disabled) {
        transform: translateY(0);
        box-shadow: 0 0 0 2px rgba(251, 186, 114, 0.8);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #BB4D00, #CA5310);
        border: none;
        color: white;
    }

    .stButton > button[kind="primary"]:hover:not(:disabled) {
        background: linear-gradient(100deg, #E0640F, #F07A25);
        color: #ffffff;
    }

    .stButton > button:disabled {
        opacity: 0.4;
        transform: none;
    }

    .st-key-category_grid div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 1rem;
    }

    .st-key-category_grid div[data-testid="stColumn"],
    .st-key-category_grid div[data-testid="column"] {
        flex: 1 1 280px;
        min-width: min(280px, 100%);
    }

    [class*="st-key-category_"] button {
        width: 100% !important;
        min-height: 145px !important;
        height: 145px !important;
        white-space: pre-wrap !important;
        text-align: center !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #FBBA72 !important;
        background: rgba(25, 32, 54, 0.76) !important;
        border: 1px solid #303954 !important;
        border-radius: 18px !important;
        transition: all 0.2s ease !important;
    }

    [class*="st-key-category_"] button:hover:not(:disabled) {
        background: rgba(187, 77, 0, 0.38) !important;
        border: 1px solid #FBBA72 !important;
        color: #ffffff !important;
        transform: translateY(-3px) !important;
        box-shadow:
            0 0 0 2px rgba(251, 186, 114, 0.4),
            0 10px 24px rgba(0, 0, 0, 0.3) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(25, 32, 54, 0.76);
        border: 1px solid #303954;
        border-radius: 18px;
        padding: 12px;
    }

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

    div[role="radiogroup"] {
        gap: 10px;
    }

    div[role="radiogroup"] label {
        background: #1a2239;
        border: 1px solid #343e60;
        border-radius: 10px;
        padding: 8px 12px;
    }

    div[role="radiogroup"] label:hover {
        border-color: #FBBA72;
        background: #8F250C;
        cursor: pointer;
    }

    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #8b5cf6, #CA5310);
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    hr {
        border-color: #303954;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 4rem 1rem 2rem;
        }

        h1 {
            font-size: 2rem !important;
        }

        [class*="st-key-category_"] button {
            min-height: 125px !important;
            height: 125px !important;
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
GAME_KEYS = ["category", "queue", "idx", "answers"]


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def get_df(claim_id):
    claim = next(c for c in CLAIMS if c["id"] == claim_id)
    return load_df(claim)


# --------------------------------------------------
# STATE + NAVIGATION
# --------------------------------------------------

ss = st.session_state

ss.setdefault("view", "landing")
ss.setdefault("gid", 0)


def has_game():
    return "queue" in ss


def points():
    return sum(a["pts"] for a in ss.get("answers", {}).values())


def start_game(category):
    if category == "Mixed bag":
        pool = random.sample(CLAIMS, min(MIXED_ROUNDS, len(CLAIMS)))
    else:
        pool = [c for c in CLAIMS if c["category"] == category]

    if not pool:
        ss.notice = "There are no claims available in this category yet."
        return

    ss.update(
        category=category,
        queue=pool,
        idx=0,
        answers={},
        view="game",
    )
    ss.gid += 1


def go_home():
    """Leave the game screen but keep the game so it can be resumed."""
    ss.view = "home"


def go_landing():
    """Return to the logo landing page without deleting an active game."""
    ss.view = "landing"


def resume_game():
    ss.view = "game"


def quit_game():
    """Throw away the current game and return to the category picker."""
    for key in GAME_KEYS:
        ss.pop(key, None)
    ss.view = "home"


def goto(i):
    ss.idx = i
    ss.view = "game"


def step(delta):
    """Move between rounds. The last step lands on the final score screen."""
    ss.idx = max(0, min(ss.idx + delta, len(ss.queue)))


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

def sidebar():
    st.sidebar.title("TrustYourGut")

    st.sidebar.button(
        "Start page",
        key="sb_landing",
        on_click=go_landing,
    )

    st.sidebar.button(
        "Categories",
        key="sb_home",
        on_click=go_home,
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "Choose a category"
        + (" (replaces current game)" if has_game() else "")
    )

    for name, icon in CATEGORIES.items():
        st.sidebar.button(
            f"{icon} {name}",
            key=f"sb_category_{name}",
            on_click=start_game,
            args=(name,),
        )

    st.sidebar.button(
        "🎲 Random mix",
        key="sb_random",
        on_click=start_game,
        args=("Mixed bag",),
    )

    if not has_game():
        return

    st.sidebar.divider()
    st.sidebar.markdown(f"**{ss.category}**")
    st.sidebar.metric("Your points", points())
    st.sidebar.caption("Jump to a round")

    for i in range(len(ss.queue)):
        answer = ss.answers.get(i)
        mark = "⬜" if answer is None else (
            "✅" if answer["correct"] else "❌"
        )
        here = "▶ " if ss.idx == i and ss.view == "game" else ""

        st.sidebar.button(
            f"{here}{mark} Round {i + 1}",
            key=f"sb_round_{i}",
            on_click=goto,
            args=(i,),
        )

    st.sidebar.button(
        "🏆 Final score",
        key="sb_final",
        on_click=goto,
        args=(len(ss.queue),),
    )

    st.sidebar.divider()

    st.sidebar.button(
        "🚪 Quit game",
        key="sb_quit",
        on_click=quit_game,
    )


def nav_bar():
    """Categories / Previous / Next, shown above every round."""
    i, n = ss.idx, len(ss.queue)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("🏠 Home", key="nav_home", on_click=go_home)

    with c2:
        st.button(
            "← Previous",
            key="nav_prev",
            on_click=step,
            args=(-1,),
            disabled=i == 0,
        )

    with c3:
        if i == n - 1:
            label = "🏆 Final score" if i in ss.answers else "Skip to final →"
        else:
            label = "Next →" if i in ss.answers else "Skip →"

        st.button(
            label,
            key="nav_next",
            on_click=step,
            args=(1,),
        )


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
            sub = df[df[c["group"]].isin([c["a"], c["b"]])]

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
# LANDING SCREEN
# --------------------------------------------------

def landing():
    """Full-page landing screen focused on the TrustYourGut logo."""

    logo_path = Path(__file__).resolve().parent / "trust.png"

    # Use the full available page width and create a centered hero section.
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 100% !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    ellipse at 50% 35%,
                    rgba(187, 77, 0, 0.3) 0%,
                    transparent 55%
                ),
                linear-gradient(
                    145deg,
                    #691E06 0%,
                    #4a1504 100%
                );
        }

        .landing-spacer {
            height: 8vh;
        }

        .landing-tagline {
            text-align: center;
            color: #FBBA72;
            font-size: clamp(1rem, 2vw, 1.4rem);
            margin-top: 1rem;
            letter-spacing: 1px;
        }

        .landing-subtitle {
            text-align: center;
            color: #ffffff;
            opacity: 0.85;
            font-size: clamp(1rem, 1.5vw, 1.2rem);
            margin-top: 0.8rem;
        }

        div.st-key-landing_start button {
            min-height: 60px !important;
            font-size: 1.25rem !important;
            font-weight: 800 !important;
            letter-spacing: 2px !important;
            border-radius: 16px !important;
            background: linear-gradient(
                100deg,
                #BB4D00,
                #E0640F
            ) !important;
            border: 1px solid #FBBA72 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            .landing-spacer {
                height: 4vh;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="landing-spacer"></div>', unsafe_allow_html=True)

    # Center the logo while giving it significantly more space.
    left, center, right = st.columns([1, 3, 1])

    with center:
        if logo_path.is_file():
            st.image(
                str(logo_path),
                use_container_width=True,
            )
        else:
            st.markdown(
                """
                <div style="
                    text-align:center;
                    padding:3rem 0;
                ">
                    <div style="font-size:5rem;">🧠</div>
                    <div style="
                        font-size:clamp(3rem, 7vw, 6rem);
                        font-weight:900;
                        letter-spacing:-2px;
                        color:#ffffff;
                    ">
                        Trust<span style="color:#FBBA72;">YourGut</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="landing-tagline">
            YOUR INSTINCTS. THE DATA. ONE FINAL VERDICT.
        </div>
        <div class="landing-subtitle">
            Think you can tell fact from fiction?
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    _, button_col, _ = st.columns([2, 1, 2])

    with button_col:
        st.button(
            "PLAY NOW!",
            key="landing_start",
            type="primary",
            on_click=go_home,
            use_container_width=True,
        )

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#FBBA72;
            opacity:0.7;
            font-size:0.85rem;
            margin-top:3rem;
        ">
            TRUST YOUR GUT. THEN CHECK THE DATA.
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# CATEGORY MENU
# --------------------------------------------------

def menu():
    # Three numbered steps displayed side by side using Streamlit
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        with st.container(border=True):
            st.markdown(
                "<h2 style='color:#FBBA72;'>1</h2>",
                unsafe_allow_html=True,
            )
            st.markdown("### Trust Your Gut")
            st.write("Vote Yes or No and place your confidence bet.")

    with col2:
        with st.container(border=True):
            st.markdown(
                "<h2 style='color:#FBBA72;'>2</h2>",
                unsafe_allow_html=True,
            )
            st.markdown("### Beat the Data")
            st.write("Reveal the statistics and earn points.")

    with col3:
        with st.container(border=True):
            st.markdown(
                "<h2 style='color:#FBBA72;'>3</h2>",
                unsafe_allow_html=True,
            )
            st.markdown("### See Your Score")
            st.write("Check your results and see how well you did.")

    st.write("")

    if "notice" in ss:
        st.warning(ss.pop("notice"))

    # Resume card, only when a game is already in progress
    if has_game():
        n = len(ss.queue)
        done = len(ss.answers)

        with st.container(border=True):
            left, right = st.columns(
                [3, 1],
                vertical_alignment="center",
            )

            with left:
                st.markdown(f"### ▶ Game in progress: {ss.category}")
                st.caption(
                    f"{done} of {n} rounds answered · {points()} points"
                )

            with right:
                st.button(
                    "Resume →",
                    key="resume",
                    type="primary",
                    on_click=resume_game,
                )

        st.write("")

    # Category selection, without "Choose Your Category"
    st.subheader("Pick a topic")

    st.caption(
        "Choose a topic and see how your guesses stack up against the data."
        + (
            " Starting a new topic will replace your current game."
            if has_game()
            else ""
        )
    )

    category_items = list(CATEGORIES.items())

    with st.container(key="category_grid"):
        for start in range(0, len(category_items), 2):
            cols = st.columns(2)

            for col, (name, icon) in zip(
                cols,
                category_items[start:start + 2],
            ):
                with col:
                    st.button(
                        f"{icon}\n\n{name}",
                        key=f"category_{name}",
                        on_click=start_game,
                        args=(name,),
                        use_container_width=True,
                    )

    st.write("")

    # Random mix card
    with st.container(border=True, key="card_random"):
        left, right = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        with left:
            st.markdown("### 🎲 Mix it up")
            st.caption(
                "Get six claims from different topics and see how many "
                "you can call correctly."
            )

        with right:
            st.button(
                "Random mix →",
                key="mixed_bag",
                on_click=start_game,
                args=("Mixed bag",),
            )

    st.write("")


# --------------------------------------------------
# PREDICTION SCREEN
# --------------------------------------------------

def vote(c):
    i = ss.idx
    suffix = f"{ss.gid}_{i}"

    with st.container(border=True):
        st.caption("YOUR TURN")
        st.markdown("### Trust your gut")

        guess = st.radio(
            "Do you think this claim is true or false?",
            ["True", "False"],
            index=None,
            horizontal=True,
            key=f"guess_{suffix}",
        )

        st.divider()
        st.markdown("#### How sure are you?")

        bet = st.radio(
            "Choose how many points to put on your guess.",
            list(BETS.keys()),
            horizontal=True,
            key=f"bet_{suffix}",
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
                <span style="color:#FBBA72;font-weight:700;">
                    Your wager: {wager} point{"s" if wager != 1 else ""}
                </span>
                <br>
                <span style="color:#b9c2d8;font-size:0.9rem;">
                    Correct: +{wager} points &nbsp; · &nbsp;
                    Incorrect: -{wager} points
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Lock in my guess →",
            type="primary",
            disabled=guess is None,
            key=f"lock_{suffix}",
        ):
            df = get_df(c["id"])
            res = analyze(df, c)

            correct = (guess == "True") == res["supported"]
            pts = wager if correct else -wager

            with st.spinner("Checking the data..."):
                text, used_model = explain(c, res)

            ss.answers[i] = {
                "claim": c["claim"],
                "guess": guess,
                "wager": wager,
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
    rv = ss.answers[ss.idx]
    res = rv["res"]

    if rv["correct"]:
        st.success(f"You called it! +{rv['pts']} points")
    else:
        st.error(f"The data disagrees! {rv['pts']} points")

    st.caption(
        f"You said **{rv['guess']}** with a {rv['wager']}-point wager."
    )

    verdict = "SUPPORTED" if res["supported"] else "NOT SUPPORTED"
    verdict_color = "#FBBA72" if res["supported"] else "#CA5310"

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

    st.markdown("### What the numbers show")

    st.metric(
        res["headline_label"],
        res["headline_value"],
        f"{res['strength']} | n = {res['n']} | p {res['p_text']}",
        delta_color="off",
    )

    st.markdown("### The data")

    fig = make_chart(c, get_df(c["id"]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### What it means")

    with st.container(border=True):
        st.markdown(rv["text"])

    if rv["used_model"]:
        st.caption(
            f"Explained by {MODEL} "
            "(open-weight model running locally)"
        )
    else:
        st.caption(
            "Built-in explanation shown because the AI model "
            "was unavailable."
        )

    st.write("")

    last = ss.idx == len(ss.queue) - 1

    st.button(
        "See final score" if last else "Next round →",
        type="primary",
        key=f"next_{ss.gid}_{ss.idx}",
        on_click=step,
        args=(1,),
    )


# --------------------------------------------------
# FINAL SCORE SCREEN
# --------------------------------------------------

def end():
    answers = ss.answers
    n = len(ss.queue)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("🏠 Home", key="end_home", on_click=go_home)

    with c2:
        st.button(
            "← Back to last round",
            key="end_back",
            on_click=goto,
            args=(n - 1,),
        )

    with c3:
        st.button(
            "🚪 Quit game",
            key="end_quit",
            on_click=quit_game,
        )

    if not answers:
        st.title("Game over")
        st.write(
            "You skipped every round. Go back and make a prediction "
            "to see your score."
        )

        st.button(
            "▶ Start from round 1",
            type="primary",
            key="end_start",
            on_click=goto,
            args=(0,),
        )
        return

    right = sum(a["correct"] for a in answers.values())
    total = len(answers)
    skipped = n - total
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
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:3.2rem;">🏆</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title(title)

    st.caption(
        f"You completed the {ss.category} challenge."
        + (
            f" ({skipped} round{'s' if skipped != 1 else ''} skipped.)"
            if skipped
            else ""
        )
    )

    with st.container(border=True):
        st.metric(
            "Final score",
            f"{points()} pts",
            f"{right} of {total} predictions correct",
            delta_color="off",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Accuracy", f"{share:.0%}")

        with col2:
            st.metric("Rounds played", total)

    if share == 1 and not skipped:
        st.balloons()

    st.markdown("### 📝 Your round-by-round results")

    for i, claim in enumerate(ss.queue):
        answer = answers.get(i)

        with st.container(border=True):
            left, mid, right_col = st.columns(
                [4, 1, 1],
                vertical_alignment="center",
            )

            with left:
                icon = (
                    "⬜"
                    if answer is None
                    else ("✅" if answer["correct"] else "❌")
                )

                st.markdown(f"**{icon} Round {i + 1}**")
                st.write(claim["claim"])

            with mid:
                if answer is None:
                    st.caption("Skipped")
                else:
                    st.metric(
                        "Points",
                        f"{answer['pts']:+d}",
                        delta_color="off",
                    )

            with right_col:
                st.button(
                    "Answer" if answer is None else "Review",
                    key=f"review_{ss.gid}_{i}",
                    on_click=goto,
                    args=(i,),
                )

    st.write("")
    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Play this category again",
            type="primary",
            key="end_again",
            on_click=start_game,
            args=(ss.category,),
        )

    with col2:
        st.button(
            "Pick another category",
            key="end_pick",
            on_click=quit_game,
        )


# --------------------------------------------------
# MAIN APP ROUTER
# --------------------------------------------------

sidebar()

if ss.view == "landing":
    landing()

elif ss.view == "home" or not has_game():
    menu()

else:
    queue = ss.queue
    idx = ss.idx

    if idx >= len(queue):
        end()

    else:
        claim = queue[idx]

        nav_bar()
        st.write("")

        left, right = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        with left:
            # Show the topic's own emoji (🍔 🔬 🎬 🏀), or 🎲 for the random mix.
            icon = CATEGORIES.get(ss.category, "🎲")
            st.caption(f"{icon} {ss.category.upper()}")

            st.progress(
                (idx + 1) / len(queue),
                text=f"Round {idx + 1} of {len(queue)}",
            )

        with right:
            st.metric("Your points", points())

        st.divider()
        st.subheader(claim["claim"])

        if idx in ss.answers:
            reveal(claim)
        else:
            vote(claim)