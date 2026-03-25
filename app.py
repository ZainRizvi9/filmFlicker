"""
FilmFlicker
Uses TMDB API for movie data and optionally Claude AI for smart recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import numpy as np
import random

TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4NDA3ZmNiZmYzYWE2MmY4ZDgwMmRhNzAzZjZlMGI4ZSIsIm5iZiI6MTczNTE1MTkwNi4wMjIsInN1YiI6IjY3NmM1MTIyY2I4YzA0OGE4YjI5OWMyYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.mc_sPJO_u_dTlHbsVmXpup-1Nc6qgteJ8S8MMPIgNa8"
TMDB_URL = "https://api.themoviedb.org/3"

st.set_page_config(page_title="FilmFlicker", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #14181c; }
    .rating-stars { color: #00e054; font-size: 18px; }
    .liked-card {
        border: 3px solid #00e054;
        border-radius: 8px;
        padding: 5px;
    }
    .rec-card {
        background: linear-gradient(135deg, #2c3440 0%, #14181c 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #00e054;
    }
</style>
""", unsafe_allow_html=True)

POPULAR_MOVIES = [
    "Back to the Future", "The Breakfast Club", "Ferris Bueller's Day Off", "Die Hard",
    "E.T. the Extra-Terrestrial", "Raiders of the Lost Ark", "Ghostbusters", "Top Gun",
    "The Terminator", "Scarface", "The Shining", "Blade Runner", "Aliens",
    "Dirty Dancing", "Footloose", "The Princess Bride", "Stand by Me",
    "Pulp Fiction", "The Shawshank Redemption", "Fight Club", "Forrest Gump",
    "The Matrix", "Goodfellas", "Se7en", "The Silence of the Lambs", "Titanic",
    "Jurassic Park", "The Lion King", "Toy Story", "Home Alone", "Mrs. Doubtfire",
    "Good Will Hunting", "Saving Private Ryan", "American Beauty", "The Sixth Sense",
    "Scream", "Clueless", "10 Things I Hate About You", "American Pie",
    "The Dark Knight", "Gladiator", "The Lord of the Rings: The Fellowship of the Ring",
    "Spider-Man", "Finding Nemo", "The Departed", "No Country for Old Men",
    "Superbad", "The Hangover", "Mean Girls", "Anchorman", "Step Brothers",
    "The Notebook", "500 Days of Summer", "Juno", "Little Miss Sunshine",
    "Avatar", "Slumdog Millionaire", "The Bourne Identity",
    "Inception", "The Social Network", "Django Unchained", "The Wolf of Wall Street",
    "Interstellar", "Mad Max: Fury Road", "Whiplash", "La La Land", "Get Out",
    "Parasite", "Joker", "Black Panther", "Avengers: Endgame", "John Wick",
    "Gone Girl", "The Grand Budapest Hotel", "Birdman", "Moonlight",
    "A Star Is Born", "Bohemian Rhapsody", "Baby Driver",
    "Everything Everywhere All at Once", "Dune", "Oppenheimer", "Top Gun: Maverick",
    "Spider-Man: No Way Home", "Barbie", "The Batman", "Knives Out"
]


@st.cache_data(ttl=3600)
def get_genres():
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    res = requests.get(f"{TMDB_URL}/genre/movie/list", headers=headers, timeout=20)
    if res.status_code == 200:
        return {g["id"]: g["name"] for g in res.json().get("genres", [])}
    return {}


@st.cache_data(ttl=3600)
def search_movie(title):
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    res = requests.get(f"{TMDB_URL}/search/movie", headers=headers, params={"query": title}, timeout=20)
    if res.status_code == 200 and res.json().get("results"):
        return res.json()["results"][0]
    return None


@st.cache_data(ttl=3600)
def get_similar(movie_id):
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    res = requests.get(f"{TMDB_URL}/movie/{movie_id}/recommendations", headers=headers, timeout=20)
    if res.status_code == 200:
        results = res.json().get("results", [])
        filtered = [
            m for m in results
            if m.get("release_date", "")[:4] >= "1980"
            and m.get("vote_count", 0) > 500
        ]
        return filtered[:15]
    return []


@st.cache_data(ttl=3600)
def load_movies(titles):
    movies = []
    for title in titles:
        movie = search_movie(title)
        if movie and movie.get("release_date", "")[:4] >= "1980":
            movies.append(movie)
    return movies


def get_ai_recommendations(liked_movies, api_key):
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None

    titles = [m.get("title", "") for m in liked_movies]

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""The user liked these movies: {', '.join(titles)}

Based on their taste, recommend 5 movies they'd love. Rules:
- Only movies from 1980 or later
- Must be popular/well-known (not obscure arthouse)
- Actually similar in vibe/tone to what they liked
- No movies they already picked

Return JSON only:
{{
  "recommendations": [
    {{
      "title": "Movie Name",
      "year": 2023,
      "why": "One sentence why they'd like it based on their picks"
    }}
  ]
}}
"""
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        st.error(f"AI error: {e}")

    return None


def get_fallback_recommendations(liked_movies):
    all_recs = []
    liked_ids = [m["id"] for m in liked_movies if m.get("id") is not None]

    for movie in liked_movies:
        if movie.get("id") is None:
            continue
        for s in get_similar(movie["id"]):
            sid = s.get("id")
            if sid is None:
                continue
            if sid not in liked_ids and sid not in [r.get("tmdb_id") for r in all_recs]:
                all_recs.append({
                    "title": s.get("title", ""),
                    "year": (s.get("release_date", "") or "")[:4],
                    "why": "Similar vibe to movies you liked",
                    "poster_path": s.get("poster_path"),
                    "rating": s.get("vote_average", 0),
                    "tmdb_id": sid
                })

    all_recs.sort(key=lambda x: float(x.get("rating") or 0), reverse=True)
    return {"recommendations": all_recs[:5]}


def to_stars(rating):
    score = (rating or 0) / 2
    full = int(score)
    half = score - full >= 0.5
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))


def _safe_year(release_date: str):
    if not release_date:
        return np.nan
    y = release_date[:4]
    return int(y) if y.isdigit() else np.nan


def build_movies_df(movies, genre_map, include_pick_index=False):
    rows = []
    for idx, m in enumerate(movies):
        genre_ids = m.get("genre_ids") or []
        genres = [genre_map.get(gid, str(gid)) for gid in genre_ids] if genre_ids else ["Unknown"]
        row = {
            "id": m.get("id"),
            "title": m.get("title", "Unknown"),
            "year": _safe_year(m.get("release_date", "")),
            "rating": float(m.get("vote_average") or 0),
            "votes": float(m.get("vote_count") or 0),
            "popularity": float(m.get("popularity") or 0),
            "genres": genres,
        }
        if include_pick_index:
            row["pick_index"] = idx + 1
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df, df
    df_genres = df.explode("genres").rename(columns={"genres": "genre"})
    df_genres["genre"] = df_genres["genre"].fillna("Unknown")
    return df, df_genres


def genre_breakdown_chart(df_genres):
    if df_genres.empty:
        return None
    g = (
        df_genres.groupby("genre")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(12)
    )
    fig = px.bar(g, x="genre", y="count", title="Your Taste Profile — Genre Breakdown")
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def rating_preference_analysis(liked_df, pool_df):
    liked_avg = float(liked_df["rating"].mean()) if not liked_df.empty else 0.0
    pool_avg = float(pool_df["rating"].mean()) if not pool_df.empty else 0.0

    corr = np.nan
    if "pick_index" in liked_df.columns and liked_df["rating"].notna().sum() >= 2:
        corr = float(liked_df[["pick_index", "rating"]].corr(numeric_only=True).iloc[0, 1])

    fig = px.scatter(
        liked_df,
        x="pick_index",
        y="rating",
        hover_name="title",
        title="Rating Correlation — Pick Order vs TMDB Rating",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return liked_avg, pool_avg, corr, fig


def _minmax(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return s.fillna(0.0)
    mn, mx = float(s.min()), float(s.max())
    if mx - mn == 0:
        return s.fillna(0.0) * 0.0
    return ((s - mn) / (mx - mn)).fillna(0.0)


def compute_similarity_matrix(liked_df, df_genres):
    if liked_df.empty:
        return None, [], np.nan

    genre_ohe = (
        df_genres.assign(val=1)
        .pivot_table(index="id", columns="genre", values="val", aggfunc="max", fill_value=0)
    )

    base = liked_df.set_index("id")[["year", "rating", "popularity"]].copy()
    base["year"] = pd.to_numeric(base["year"], errors="coerce")

    num = pd.DataFrame({
        "year_n": _minmax(base["year"]),
        "rating_n": _minmax(base["rating"]),
        "pop_n": _minmax(base["popularity"]),
    }, index=base.index).fillna(0.0)

    ids = [i for i in liked_df["id"].tolist() if i in genre_ohe.index and i in num.index]
    if len(ids) < 2:
        return None, liked_df["title"].tolist(), np.nan

    G = genre_ohe.loc[ids].to_numpy(dtype=float)
    N = num.loc[ids].to_numpy(dtype=float)

    norm = np.linalg.norm(G, axis=1, keepdims=True)
    norm = np.where(norm == 0, 1.0, norm)
    G2 = G / norm
    genre_sim = G2 @ G2.T

    dist = np.sqrt(((N[:, None, :] - N[None, :, :]) ** 2).sum(axis=2))
    max_dist = np.sqrt(N.shape[1]) if N.shape[1] > 0 else 1.0
    num_sim = 1.0 - (dist / max_dist if max_dist else dist)

    sim = 0.75 * genre_sim + 0.25 * num_sim
    sim = np.clip(sim, 0.0, 1.0)

    labels = liked_df.set_index("id").loc[ids]["title"].tolist()

    n = sim.shape[0]
    mask = ~np.eye(n, dtype=bool)
    avg_sim = float(sim[mask].mean()) if n > 1 else np.nan
    return sim, labels, avg_sim


def similarity_heatmap(sim, labels):
    fig = px.imshow(
        sim,
        x=labels,
        y=labels,
        zmin=0,
        zmax=1,
        aspect="auto",
        title="Similarity Score — How close your picks are to each other",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=520)
    return fig


def build_taste_persona(liked_df, liked_genres, liked_avg, pool_avg, avg_sim):
    if liked_genres is not None and not liked_genres.empty:
        top = (
            liked_genres.groupby("genre")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        top_genres = top["genre"].head(3).tolist()
    else:
        top_genres = []

    diff = liked_avg - pool_avg
    if diff >= 0.4:
        rating_lean = "You lean toward higher-rated picks (you usually want the “good stuff”)."
    elif diff <= -0.4:
        rating_lean = "You don’t chase ratings — you pick based on vibe, not scores."
    else:
        rating_lean = "You’re pretty aligned with the average rating of the pool."

    if pd.isna(avg_sim):
        cluster = "Not enough picks yet to confidently profile."
    elif avg_sim >= 0.65:
        cluster = "Your taste is consistent — you stay in a specific lane."
    elif avg_sim >= 0.45:
        cluster = "You have a few main lanes, but you branch out sometimes."
    else:
        cluster = "You’re eclectic — lots of variety across genres/vibes."

    if top_genres:
        genre_line = f"Top genres showing up in your picks: {', '.join(top_genres)}."
    else:
        genre_line = "Your genre profile will sharpen as you pick more movies."

    shows = []
    if any(g in top_genres for g in ["Action", "Adventure", "Thriller", "Science Fiction"]):
        shows += ["fast-paced thrillers", "sci-fi or action series", "high-stakes plots"]
    if any(g in top_genres for g in ["Comedy", "Romance"]):
        shows += ["comfort comedies", "rom-coms", "character-driven shows"]
    if any(g in top_genres for g in ["Drama", "Mystery", "Crime"]):
        shows += ["prestige drama", "mystery/crime shows", "slow-burn storytelling"]
    if any(g in top_genres for g in ["Animation", "Family"]):
        shows += ["animated films", "feel-good series", "rewatchable favorites"]

    if not shows:
        shows = ["popular mainstream movies", "whatever has a strong vibe", "stuff you can recommend to friends"]

    return genre_line, rating_lean, cluster, shows


def render_visuals_bottom(liked_movies, all_movies, genre_map):
    if not liked_movies:
        return

    st.markdown("---")
    st.subheader("📊 Your Data Visualizations")

    try:
        liked_df, liked_genres = build_movies_df(liked_movies, genre_map, include_pick_index=True)
        pool_df, _ = build_movies_df(all_movies, genre_map, include_pick_index=False)

        fig1 = genre_breakdown_chart(liked_genres)
        if fig1 is not None:
            st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        liked_avg, pool_avg, corr, corr_fig = rating_preference_analysis(liked_df, pool_df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg rating (your picks)", f"{liked_avg:.1f}/10")
        c2.metric("Avg rating (movie pool)", f"{pool_avg:.1f}/10")
        c3.metric("Pick-order ↔ rating correlation", "N/A" if pd.isna(corr) else f"{corr:+.2f}")
        st.plotly_chart(corr_fig, use_container_width=True)

        st.markdown("---")

        sim, labels, avg_sim = compute_similarity_matrix(liked_df, liked_genres)
        if sim is None or len(labels) < 2:
            st.info("Pick at least 2 movies to compute similarity.")
            return

        k1, k2 = st.columns([1, 3])
        with k1:
            st.metric("Avg similarity (0–1)", f"{avg_sim:.2f}")
            st.caption("Higher = your picks cluster tightly (similar genres/vibe).")
        with k2:
            st.plotly_chart(similarity_heatmap(sim, labels), use_container_width=True)

        st.markdown("---")

        genre_line, rating_lean, cluster, shows = build_taste_persona(liked_df, liked_genres, liked_avg, pool_avg, avg_sim)

        st.markdown("**What this is telling you (quick vibe/personality read):**")
        st.write(
            f"{genre_line} "
            f"{rating_lean} "
            f"{cluster} "
            f"Based on that, you’ll probably like: {', '.join(shows[:3])}."
        )

    except Exception as e:
        st.error(f"Visuals failed (app still running): {e}")


def build_rec_pool(liked_movies):
    liked_ids = {m.get("id") for m in liked_movies if m.get("id") is not None}
    pool = []

    for movie in liked_movies:
        mid = movie.get("id")
        if mid is None:
            continue
        for s in get_similar(mid):
            sid = s.get("id")
            if sid is None or sid in liked_ids:
                continue
            pool.append({
                "title": s.get("title", ""),
                "year": (s.get("release_date", "") or "")[:4],
                "why": "Similar vibe to movies you liked",
                "poster_path": s.get("poster_path"),
                "rating": s.get("vote_average", 0),
                "tmdb_id": sid,
            })

    uniq = {}
    for r in pool:
        if r.get("tmdb_id") not in uniq:
            uniq[r.get("tmdb_id")] = r
    pool = list(uniq.values())
    pool.sort(key=lambda x: float(x.get("rating") or 0), reverse=True)
    return pool


def pick_replacement_from_pool(rec_pool, exclude_ids):
    candidates = [r for r in rec_pool if r.get("tmdb_id") not in exclude_ids]
    if not candidates:
        return None
    return random.choice(candidates)


def normalize_recs(recs_obj, liked_movies):
    liked_titles = {m.get("title") for m in liked_movies if m.get("title")}
    out = []
    for r in recs_obj.get("recommendations", []):
        title = r.get("title", "")
        if not title or title in liked_titles:
            continue
        movie_data = search_movie(title)
        tmdb_id = movie_data.get("id") if movie_data else r.get("tmdb_id")
        poster = movie_data.get("poster_path") if movie_data else r.get("poster_path")
        rating = movie_data.get("vote_average") if movie_data else r.get("rating", 0)
        year = (movie_data.get("release_date", "")[:4] if movie_data else r.get("year", ""))

        out.append({
            "title": title,
            "year": year,
            "why": r.get("why", "Similar vibe to movies you liked"),
            "poster_path": poster,
            "rating": rating,
            "tmdb_id": tmdb_id,
        })
    return out


def ensure_session_defaults():
    if "liked" not in st.session_state:
        st.session_state.liked = []
    if "seen" not in st.session_state:
        st.session_state.seen = set()
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "recs_current" not in st.session_state:
        st.session_state.recs_current = []
    if "rec_pool" not in st.session_state:
        st.session_state.rec_pool = []
    if "recs_seen_ids" not in st.session_state:
        st.session_state.recs_seen_ids = set()


def main():
    st.title("FilmFlicker")
    st.write("Swipe through movies. Pick your favorites. Get recommendations.")

    st.sidebar.header("Settings")
    api_key = st.sidebar.text_input("Anthropic API Key (optional)", type="password")
    if api_key:
        st.sidebar.success("AI mode on")

    ensure_session_defaults()

    genre_map = get_genres()
    all_movies = load_movies(POPULAR_MOVIES)
    unseen = [m for m in all_movies if m["id"] not in st.session_state.seen]

    st.markdown("---")

    if st.session_state.liked:
        st.write(f"**Your picks ({len(st.session_state.liked)}):**")
        liked_cols = st.columns(min(len(st.session_state.liked), 8))
        for i, movie in enumerate(st.session_state.liked[:8]):
            with liked_cols[i]:
                if movie.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w92{movie['poster_path']}", width=60)
        st.markdown("---")

    if st.session_state.show_results or len(unseen) < 4:
        if not st.session_state.liked:
            st.warning("You didn't pick any movies! Start over and pick some favorites.")
            if st.button("Start Over"):
                st.session_state.liked = []
                st.session_state.seen = set()
                st.session_state.show_results = False
                st.session_state.recs_current = []
                st.session_state.rec_pool = []
                st.session_state.recs_seen_ids = set()
                st.rerun()
        else:
            st.subheader("Your Recommendations")

            if not st.session_state.recs_current:
                with st.spinner("Finding movies for you..."):
                    recs_obj = get_ai_recommendations(st.session_state.liked, api_key) if api_key else None
                    if not recs_obj:
                        recs_obj = get_fallback_recommendations(st.session_state.liked)

                    normalized = normalize_recs(recs_obj, st.session_state.liked)
                    st.session_state.recs_current = normalized[:5]

                st.session_state.rec_pool = build_rec_pool(st.session_state.liked)

            if st.session_state.recs_current:
                for i, rec in enumerate(st.session_state.recs_current, 1):
                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col1:
                        if rec.get("poster_path"):
                            st.image(f"https://image.tmdb.org/t/p/w200{rec['poster_path']}", width=120)
                    with col2:
                        st.markdown(f"### {i}. {rec.get('title','')} ({rec.get('year','')})")
                        st.write(rec.get("why", ""))
                        st.write(f"{to_stars(rec.get('rating', 0))} ({float(rec.get('rating',0) or 0):.1f}/10)")
                    with col3:
                        if st.button("Seen it → Replace", key=f"rep_{i}", use_container_width=True):
                            current_ids = {r.get("tmdb_id") for r in st.session_state.recs_current if r.get("tmdb_id")}
                            current_ids |= set(st.session_state.recs_seen_ids)
                            if rec.get("tmdb_id"):
                                current_ids.add(rec.get("tmdb_id"))

                            replacement = pick_replacement_from_pool(st.session_state.rec_pool, current_ids)
                            if replacement is None:
                                st.warning("No more replacements available right now. Try picking more movies first.")
                            else:
                                st.session_state.recs_seen_ids.add(rec.get("tmdb_id"))
                                st.session_state.recs_current[i - 1] = replacement
                                st.rerun()

                    st.markdown("---")

            render_visuals_bottom(st.session_state.liked, all_movies, genre_map)

            if st.button("Start Over", type="primary"):
                st.session_state.liked = []
                st.session_state.seen = set()
                st.session_state.show_results = False
                st.session_state.recs_current = []
                st.session_state.rec_pool = []
                st.session_state.recs_seen_ids = set()
                st.rerun()
        return

    st.subheader("Pick your favorite (or skip)")

    current_4 = unseen[:4]
    cols = st.columns(4)

    for i, movie in enumerate(current_4):
        with cols[i]:
            if movie.get("poster_path"):
                st.image(f"https://image.tmdb.org/t/p/w300{movie['poster_path']}", use_container_width=True)
            else:
                st.write("No poster")

            st.write(f"**{movie['title'][:20]}**")
            year = movie.get("release_date", "")[:4]
            rating = movie.get("vote_average", 0)
            st.write(f"{year} · {to_stars(rating)}")

            if st.button("Pick this", key=f"pick_{movie['id']}", use_container_width=True, type="primary"):
                st.session_state.liked.append(movie)
                for m in current_4:
                    st.session_state.seen.add(m["id"])
                st.rerun()

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Skip these", use_container_width=True):
            for m in current_4:
                st.session_state.seen.add(m["id"])
            st.rerun()
    with c2:
        if st.button("Haven't seen any", use_container_width=True):
            for m in current_4:
                st.session_state.seen.add(m["id"])
            st.rerun()
    with c3:
        if len(st.session_state.liked) >= 3:
            if st.button("Done, show recommendations", use_container_width=True, type="primary"):
                st.session_state.show_results = True
                st.session_state.recs_current = []
                st.session_state.rec_pool = []
                st.session_state.recs_seen_ids = set()
                st.rerun()
        else:
            st.write(f"Pick {3 - len(st.session_state.liked)} more")

    render_visuals_bottom(st.session_state.liked, all_movies, genre_map)


if __name__ == "__main__":
    main()