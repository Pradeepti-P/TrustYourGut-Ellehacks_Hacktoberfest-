# TrustYourGut

Does your gut beat the data? 
A game where you guess whether a claim is true, then see what real data says and an open-weight AI explains the result!

Demo Video: [add link]

Hacktoberfect Hack Day at Ellehacks 2026 by:  Pradeepti Poudyal, Esha Gogna, Beenish Saeed, Arnaz Waniya

## Who it helps
People who want to build intuition about data and correlation, and teachers looking for a fun way to show "correlation is not causation."

## How it works
1. Pick a category (Food, Science, Entertainment, Sports or a Randomized mix)
2. Vote true or false on a claim and place a wager of 1, 2 or 3 points on how sure you are.
3. The code computes the real statistics (uses pandas and scipy to run statistical tests) and decides the verdict.
4. An open-weight model explains the statistical results and reasoning in plain English

The statistics are computed in code. The model only explains them, so it can't invent numbers.

## Model
Qwen3 4B (small language model, 4B parameters), run locally with Ollama.
License: Apache-2.0, https://huggingface.co/Qwen/Qwen3-4B

## Run it
ollama pull qwen3:4b
pip install -r requirements.txt
python scripts/fetch_data.py
streamlit run app.py
If Ollama isn't running, the app uses a built-in fallback explanation

## Tech Stack

- *Frontend:* Streamlit, with plotly charts
- *Statistics:* Python (pandas, NumPy, SciPy)
- *AI:* Qwen3 4B via Ollama (for explanations)

## Data
seaborn sample datasets (tips, penguins, planets, exercise) and the movies dataset from the vega-datasets repository.

## License
MIT. See the [LICENSE](LICENSE) file.
