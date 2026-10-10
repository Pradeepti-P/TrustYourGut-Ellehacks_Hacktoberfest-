"""Every game question lives here. To add a question, add a dict. No other file needs to change."""

CATEGORIES = {"Food": "🍔", "Science": "🔬", "Entertainment": "🎬", "Sports": "🏀"}

# type "corr"  : two number columns (x, y). Optional: split_by, method ("spearman"), derive, log_y
# type "group" : compares the average of `value` for group a vs group b in column `group`.
#                op "greater" = claim says a is higher than b, op "less" = claim says a is lower.
# Order inside a category = round order (easy warm-up first, surprise last).
CLAIMS = [
    # ---------------- FOOD (tips dataset) ----------------
    {"id": "dinner_lunch", "category": "Food", "type": "group",
     "claim": "Dinner bills are bigger than lunch bills.",
     "csv": "data/tips.csv", "value": "total_bill", "group": "time",
     "a": "Dinner", "b": "Lunch", "op": "greater", "ylabel": "Bill ($)",
     "caveat": "The data is a small sample of bills from one restaurant."},
    {"id": "party_tip", "category": "Food", "type": "corr",
     "claim": "Bigger parties tip a bigger percentage.",
     "csv": "data/tips.csv", "derive": {"tip_pct": "tip / total_bill * 100"},
     "x": "size", "y": "tip_pct", "xlabel": "Party size", "ylabel": "Tip (%)",
     "caveat": "The data is a small sample of bills from one restaurant."},
    {"id": "bill_tip", "category": "Food", "type": "corr",
     "claim": "Bigger restaurant bills mean people tip a bigger percentage.",
     "csv": "data/tips.csv", "derive": {"tip_pct": "tip / total_bill * 100"},
     "x": "total_bill", "y": "tip_pct", "xlabel": "Bill ($)", "ylabel": "Tip (%)",
     "caveat": "Tips tend to have a fixed-looking floor, so big bills can mean a smaller percentage."},

    # ---------------- SCIENCE (penguins, planets) ----------------
    {"id": "flipper_mass", "category": "Science", "type": "corr",
     "claim": "Heavier penguins have longer flippers.",
     "csv": "data/penguins.csv", "x": "body_mass_g", "y": "flipper_length_mm",
     "xlabel": "Body mass (g)", "ylabel": "Flipper length (mm)",
     "caveat": "Three penguin species with different body sizes are mixed together."},
    {"id": "planet_year_mass", "category": "Science", "type": "corr",
     "claim": "Exoplanets discovered more recently are heavier than ones found earlier.",
     "csv": "data/planets.csv", "x": "year", "y": "mass", "method": "spearman", "log_y": True,
     "xlabel": "Year discovered", "ylabel": "Mass (Jupiter masses, log scale)",
     "caveat": "Detection methods improved over time, so newer telescopes can find smaller planets."},
    {"id": "penguin_bills", "category": "Science", "type": "corr",
     "claim": "Penguins with longer bills also have deeper bills.",
     "csv": "data/penguins.csv", "x": "bill_length_mm", "y": "bill_depth_mm", "split_by": "species",
     "xlabel": "Bill length (mm)", "ylabel": "Bill depth (mm)",
     "caveat": "The overall trend and the trend inside each species can point in opposite directions (Simpson's paradox)."},

    # ---------------- ENTERTAINMENT (movies) ----------------
    {"id": "critics_audience", "category": "Entertainment", "type": "corr",
     "claim": "Movies that critics rate highly are also rated highly by audiences.",
     "csv": "data/movies.csv", "x": "Rotten_Tomatoes_Rating", "y": "IMDB_Rating",
     "xlabel": "Rotten Tomatoes rating", "ylabel": "IMDB rating",
     "caveat": "Only movies that have both ratings are included."},
    {"id": "runtime_rating", "category": "Entertainment", "type": "corr",
     "claim": "Longer movies get higher IMDB ratings.",
     "csv": "data/movies.csv", "x": "Running_Time_min", "y": "IMDB_Rating",
     "xlabel": "Running time (min)", "ylabel": "IMDB rating",
     "caveat": "Only movies with a recorded running time are included."},
    {"id": "budget_rating", "category": "Entertainment", "type": "corr",
     "claim": "Bigger-budget movies get higher IMDB ratings.",
     "csv": "data/movies.csv", "x": "Production_Budget", "y": "IMDB_Rating", "method": "spearman",
     "xlabel": "Production budget ($)", "ylabel": "IMDB rating",
     "caveat": "Only movies with a recorded budget are included."},

    # ---------------- SPORTS (exercise dataset) ----------------
    {"id": "run_walk", "category": "Sports", "type": "group",
     "claim": "Running raises your pulse more than walking.",
     "csv": "data/exercise.csv", "value": "pulse", "group": "kind",
     "a": "running", "b": "walking", "op": "greater", "ylabel": "Pulse (bpm)",
     "caveat": "Only 30 people took part, each measured several times."},
    {"id": "time_pulse", "category": "Sports", "type": "corr",
     "claim": "The longer you work out, the higher your pulse.",
     "csv": "data/exercise.csv", "x": "time", "y": "pulse",
     "xlabel": "Minutes of exercise", "ylabel": "Pulse (bpm)",
     "caveat": "Only 30 people took part, each measured several times."},
    {"id": "diet_pulse", "category": "Sports", "type": "group",
     "claim": "A no-fat diet gives you a lower exercise pulse than a low-fat diet.",
     "csv": "data/exercise.csv", "value": "pulse", "group": "diet",
     "a": "no fat", "b": "low fat", "op": "less", "ylabel": "Pulse (bpm)",
     "caveat": "Only 30 people took part, so a small difference could be chance."},
]