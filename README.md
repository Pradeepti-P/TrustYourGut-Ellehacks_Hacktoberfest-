# TrustYourGut

Does your gut beat the data? 
A game where you guess whether a claim is true, then see what real data says and an open-weight AI explains the result!

## Who it helps
People who want to build intuition about data and correlation, and teachers looking for a fun way to show "correlation is not causation."

## How it works
1. Pick a category (Food, Science, Entertainment, Sports)
2. Vote on a claim and place a confidence bet
3. Code computes the real statistics (pandas and scipy)
4. An open-weight model explains the results in plain English

The statistics are computed in code. The model only explains them, so it can't invent numbers.

## Model
Qwen3 4B (small language model, 4B parameters), run locally with Ollama.
License: Apache-2.0, https://huggingface.co/Qwen/Qwen3-4B

## Run it
ollama pull qwen3:4b
pip install -r requirements.txt
streamlit run app.py
If Ollama isn't running, the app uses a built-in fallback explanation.

## Data
Datasets from seaborn and vega_datasets (sources linked here).
=======
Does your gut beat the data? Pick a category, guess whether a claim is true, then see real statistics and an AI explanation.

## Who it helps
People learning to read data, and anyone curious how often intuition is wrong.

## How it works
1. Pick a category (Food, Science, Entertainment, Sports)
2. Vote True or False and place a confidence bet
3. Python (pandas, scipy) computes the real statistics
4. An open-weight model explains the result in plain English

The numbers and the verdict come from code. The model only explains them, so it can't invent statistics.

## Model
Qwen3 4B, a small language model (4B parameters), run locally with Ollama.
License: Apache-2.0, https://huggingface.co/Qwen/Qwen3-4B

## Run it
    ollama pull qwen3:4b
    pip install -r requirements.txt
    python scripts/fetch_data.py
    streamlit run app.py

If Ollama is not running, the app shows a built-in explanation instead.

## Data
seaborn sample datasets (tips, penguins, planets, exercise) and the movies dataset from the vega-datasets repository.
>>>>>>> c0e5fdf (Working baseline with all categories)

## License
MIT
