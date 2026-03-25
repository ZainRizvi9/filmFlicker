# FilmFlicker

An intelligent movie recommendation dashboard powered by Claude AI. Select a movie you love, choose your matching criteria (actor, director, genre, Letterboxd lists), and get personalized recommendations with explanations.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Claude AI](https://img.shields.io/badge/Claude-AI--Powered-purple)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **AI-Powered Recommendations**: Uses Claude to analyze movies and provide intelligent suggestions
- **Smart Matching Parameters**:
  - 🎭 Same Actor - find movies with shared cast members
  - 🎬 Same Director - discover a director's filmography
  - 🎪 Same Genre - explore similar genres
  - 📋 Letterboxd Lists - recommendations based on community-curated lists
- **Letterboxd-Style UI**: Dark theme with star ratings (converted from TMDB's 10-point scale)
- **Interactive Visualizations**: Rating distributions, genre breakdowns, popularity analysis
- **Real-Time Data**: Pulls trending movies from TMDB API

## Tech Stack

- **Python** - Core language
- **Streamlit** - Dashboard framework
- **Claude AI (Anthropic)** - Intelligent recommendations
- **Pandas** - Data processing
- **Plotly** - Interactive charts
- **TMDB API** - Movie database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ZainRizvi9/filmflicker.git
cd filmflicker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run app.py
```

4. Enter your Anthropic API key in the sidebar (get one at [console.anthropic.com](https://console.anthropic.com))

## How It Works

1. **Select a Movie**: Pick from the trending movies list
2. **Choose Parameters**: Select what you want to match (actor, director, genre, Letterboxd lists)
3. **Get AI Recommendations**: Claude analyzes your selection and suggests 5 movies with detailed explanations
4. **Explore**: Each recommendation shows why it matches your criteria

## Project Structure

```
movie-recommender/
├── app.py              # Main application with AI integration
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## API Keys Required

- **TMDB API**: Already configured (demo key included)
- **Anthropic API**: Required for AI recommendations - enter in sidebar

## License

MIT License
