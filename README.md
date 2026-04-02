# FilmFlicker

A movie recommendation engine that figures out your taste and finds films you'll actually want to watch.


**Live:** https://filmflicker.streamlit.app  
**Demo:** https://youtu.be/OVAbEVROX_w

## What it does

Pick a few movies you love and FilmFlicker builds a taste profile from them. It uses cosine similarity across normalized feature vectors (genre, rating, year, popularity) to find similar films, then runs a KNN vibe classifier to map your taste to one of 15 curated categories like "cerebral thrillers" or "feel-good comfort watches."

The movie pool refreshes every session using TMDB's trending API alongside 300+ hand-curated titles.

## Features

- Cosine similarity recommendation engine with genre one-hot encoding
- KNN vibe classifier across 15 hand-labeled taste categories
- Genre donut chart, pick-order vs rating scatter plot, film similarity heatmap
- TMDB API integration for live trending data and movie metadata
- Vote threshold and release year filters

## Tech Stack

- Python, Streamlit, Pandas, Plotly
- TMDB API
- Deployed on Streamlit Cloud

## Running locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
