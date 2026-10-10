"""Run once from the project root:  python scripts/fetch_data.py
Saves every dataset into data/ so the app never needs the internet while running."""
import os
import pandas as pd
import seaborn as sns

os.makedirs("data", exist_ok=True)

for name in ["tips", "penguins", "planets", "exercise"]:
    sns.load_dataset(name).to_csv(f"data/{name}.csv", index=False)
    print("saved", name)

# Movies dataset from the vega-datasets repo (column names have spaces, so we swap them for underscores)
url = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/movies.json"
movies = pd.read_json(url)
movies.columns = [c.replace(" ", "_") for c in movies.columns]
movies.to_csv("data/movies.csv", index=False)
print("saved movies")