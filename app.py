"""
FilmFlicker - movie recommendation app
picks movies you'll actually want to watch, not obscure arthouse stuff
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
import random

TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4NDA3ZmNiZmYzYWE2MmY4ZDgwMmRhNzAzZjZlMGI4ZSIsIm5iZiI6MTczNTE1MTkwNi4wMjIsInN1YiI6IjY3NmM1MTIyY2I4YzA0OGE4YjI5OWMyYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.mc_sPJO_u_dTlHbsVmXpup-1Nc6qgteJ8S8MMPIgNa8"
TMDB_URL = "https://api.themoviedb.org/3"

st.set_page_config(page_title="FilmFlicker", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #14181c; }
    .rating-stars { color: #00e054; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# vibe-based lists, inspired by letterboxd list culture
# keeping it to stuff people have actually heard of
VIBE_LISTS = {
    "Heist": [
        "Heat", "Ocean's Eleven", "The Italian Job", "Inside Man", "The Town",
        "Baby Driver", "Logan Lucky", "Widows", "The Score", "Snatch",
        "American Animals", "Den of Thieves", "The Bank Job", "Set It Off",
        "Quick Change", "Now You See Me", "Tower Heist", "A Fish Called Wanda",
        "The Great Train Robbery", "Thief",
    ],
    "Stoner Comedy": [
        "The Big Lebowski", "Pineapple Express", "Half Baked", "Dazed and Confused",
        "Friday", "Super Troopers", "Harold & Kumar Go to White Castle",
        "Jay and Silent Bob Strike Back", "How High", "Ted",
        "This Is the End", "Fear and Loathing in Las Vegas",
        "Inherent Vice", "Tenacious D in The Pick of Destiny",
    ],
    "Cult Classic": [
        "Donnie Darko", "The Rocky Horror Picture Show", "They Live",
        "A Clockwork Orange", "Brazil", "Requiem for a Dream",
        "Fight Club", "Trainspotting", "Kids", "Clerks",
        "Repo Man", "Blue Velvet", "Eraserhead", "Happiness",
        "Mulholland Drive",
    ],
    "Feel Good": [
        "Chef", "Julie & Julia", "The Secret Life of Walter Mitty",
        "About Time", "Paddington 2", "Hunt for the Wilderpeople",
        "Sing Street", "The Intouchables", "Amelie", "Midnight in Paris",
        "The Grand Budapest Hotel", "Spirited Away", "My Neighbor Totoro",
        "Big Fish", "Edward Scissorhands", "Chocolat", "The Full Monty",
        "Billy Elliot", "Cinema Paradiso", "Life Is Beautiful",
    ],
    "Mind Bending": [
        "Inception", "Memento", "Primer", "Coherence", "Triangle",
        "Predestination", "Annihilation", "Enemy", "Timecrimes",
        "Eternal Sunshine of the Spotless Mind", "Being John Malkovich",
        "The One I Love", "Under the Skin", "Upstream Color",
        "A Ghost Story", "Synecdoche New York",
    ],
    "Late Night Vibes": [
        "Drive", "Lost in Translation", "Her", "Collateral",
        "Nightcrawler", "Spring Breakers", "Vanilla Sky",
        "Mandy", "Good Time", "After Hours", "Only God Forgives",
        "Under the Silver Lake", "The Neon Demon", "Heaven Knows What",
    ],
    "A24": [
        "Hereditary", "Midsommar", "Uncut Gems", "Moonlight", "Lady Bird",
        "The Lighthouse", "Ex Machina", "Room", "The Witch",
        "Green Room", "Eighth Grade", "The Farewell", "Minari",
        "Everything Everywhere All at Once", "Talk to Me",
        "Past Lives", "Saltburn", "Beau Is Afraid",
    ],
    "Pure Adrenaline": [
        "Mad Max: Fury Road", "John Wick", "The Raid", "Speed",
        "Die Hard", "Point Break", "Face/Off", "Con Air",
        "Sicario", "Fury", "Dredd", "Upgrade",
        "Atomic Blonde", "Crank", "Shoot 'Em Up",
    ],
    "Slow Burn Thriller": [
        "Prisoners", "Zodiac", "Parasite", "Oldboy", "Gone Girl",
        "The Gift", "Blue Ruin", "Take Shelter", "Wind River",
        "Three Billboards Outside Ebbing Missouri", "Martha Marcy May Marlene",
        "Compliance", "No Country for Old Men", "Memories of Murder",
        "A Tale of Two Sisters", "The Wailing",
    ],
    "Dark Comedy": [
        "In Bruges", "Four Lions", "Burn After Reading",
        "The Death of Stalin", "Fargo", "Happiness",
        "Very Bad Things", "Observe and Report",
        "I Don't Feel at Home in This World Anymore",
        "Tucker and Dale vs Evil", "One Cut of the Dead",
        "The Lobster", "A Serious Man", "Barton Fink",
    ],
    "Coming of Age": [
        "Stand by Me", "The Perks of Being a Wallflower",
        "Moonrise Kingdom", "Adventureland", "The Way Way Back",
        "Kings of Summer", "Mud", "The Spectacular Now",
        "Dazed and Confused", "Almost Famous", "Boyhood",
        "The Edge of Seventeen", "Eighth Grade", "Mid90s",
        "Booksmart", "Superbad", "Submarine",
    ],
    "Guy Ritchie Vibes": [
        "Lock Stock and Two Smoking Barrels", "Snatch", "RocknRolla",
        "Layer Cake", "The Long Good Friday", "Sexy Beast",
        "Legend", "The Limey", "Smokin' Aces", "Running Scared",
        "Gangster No. 1",
    ],
    "Based on True Events": [
        "Spotlight", "The Big Short", "Argo", "Zero Dark Thirty",
        "Catch Me If You Can", "The Social Network", "Moneyball",
        "Sully", "127 Hours", "Into the Wild", "Goodfellas",
        "Zodiac", "Frost/Nixon", "All the President's Men",
        "The Insider", "Serpico", "Dog Day Afternoon",
        "Bohemian Rhapsody", "Rocketman", "I, Tonya",
    ],
    "For When You Want to Feel Something": [
        "Aftersun", "Past Lives", "Manchester by the Sea",
        "Blue Valentine", "Eternal Sunshine of the Spotless Mind",
        "Her", "Lost in Translation", "Marriage Story",
        "The Florida Project", "Eighth Grade", "Short Term 12",
        "Good Will Hunting", "About Time", "Beginners",
        "Call Me by Your Name", "Brokeback Mountain", "Moonlight",
        "The Perks of Being a Wallflower", "Atonement", "Never Let Me Go",
    ],
    "Everyone Should Watch": [
        "The Godfather", "Schindler's List", "Pulp Fiction",
        "The Shawshank Redemption", "Goodfellas", "Taxi Driver",
        "Apocalypse Now", "2001: A Space Odyssey", "Blade Runner",
        "Do the Right Thing", "Chinatown", "Network",
        "One Flew Over the Cuckoo's Nest", "Annie Hall",
        "Rear Window", "Vertigo", "Psycho", "Dr. Strangelove",
        "Lawrence of Arabia", "The Deer Hunter",
    ],
}

POPULAR_MOVIES = [
    # 80s crowd pleasers + classics
    "Back to the Future", "The Breakfast Club", "Ferris Bueller's Day Off",
    "Die Hard", "Ghostbusters", "The Terminator", "Aliens",
    "Top Gun", "Scarface", "The Shining", "Blade Runner",
    "Raiders of the Lost Ark", "E.T. the Extra-Terrestrial",
    "Full Metal Jacket", "Platoon", "Dirty Dancing", "Footloose",
    "The Princess Bride", "Stand by Me", "Heathers",
    "Say Anything", "Fast Times at Ridgemont High",
    "Risky Business", "Pretty in Pink", "Some Kind of Wonderful",
    "Sixteen Candles", "Weird Science", "Lost Boys",
    "River's Edge", "Raising Arizona", "Blood Simple",
    "Manhunter", "The Thing", "Videodrome",

    # 90s
    "Pulp Fiction", "The Shawshank Redemption", "Fight Club",
    "Fargo", "The Big Lebowski", "Goodfellas", "Se7en",
    "Heat", "Boogie Nights", "Magnolia", "Eyes Wide Shut",
    "Trainspotting", "Reservoir Dogs", "Jackie Brown",
    "Before Sunrise", "Dazed and Confused", "Clerks",
    "Good Will Hunting", "Saving Private Ryan", "American Beauty",
    "The Sixth Sense", "Scream", "Clueless",
    "10 Things I Hate About You", "American Pie",
    "Forrest Gump", "Jurassic Park", "The Lion King",
    "Toy Story", "Home Alone", "Mrs. Doubtfire",
    "Boyz n the Hood", "Menace II Society", "Do the Right Thing",
    "Rushmore", "The Royal Tenenbaums", "Bottle Rocket",
    "L.A. Confidential", "The Usual Suspects", "Donnie Brasco",
    "Carlito's Way", "Casino", "The Silence of the Lambs",
    "Titanic", "The Matrix", "Men in Black",

    # 2000s
    "Memento", "Eternal Sunshine of the Spotless Mind",
    "Lost in Translation", "Adaptation", "Punch-Drunk Love",
    "Sideways", "Ghost World", "Oldboy",
    "City of God", "Y Tu Mama Tambien", "Amores Perros",
    "Zodiac", "No Country for Old Men", "There Will Be Blood",
    "Gone Baby Gone", "In Bruges", "The Dark Knight",
    "Gladiator", "Inception", "The Social Network",
    "The Departed", "Spider-Man", "Finding Nemo",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Superbad", "The Hangover", "Mean Girls", "Anchorman",
    "Step Brothers", "The Notebook", "500 Days of Summer",
    "Juno", "Little Miss Sunshine", "Slumdog Millionaire",
    "The Bourne Identity", "Kill Bill: Volume 1",
    "Requiem for a Dream", "Moulin Rouge!",

    # 2010s
    "Drive", "The Master", "Mud", "Take Shelter",
    "Winter's Bone", "Blue Valentine", "Beginners",
    "Her", "Enemy", "Gone Girl",
    "Moonlight", "The Witch", "Green Room",
    "Eighth Grade", "Mid90s", "Booksmart", "The Farewell",
    "Parasite", "Uncut Gems", "The Lighthouse", "Midsommar",
    "Once Upon a Time in Hollywood", "Marriage Story",
    "Knives Out", "Get Out", "Hereditary",
    "Django Unchained", "The Wolf of Wall Street",
    "Interstellar", "Mad Max: Fury Road", "Whiplash",
    "La La Land", "Black Panther", "Avengers: Endgame",
    "John Wick", "The Grand Budapest Hotel", "Birdman",
    "A Star Is Born", "Bohemian Rhapsody", "Baby Driver",
    "Joker", "1917", "Dunkirk",

    # 2020s
    "Everything Everywhere All at Once", "The Banshees of Inisherin",
    "Tar", "Past Lives", "Oppenheimer", "Dune",
    "Top Gun: Maverick", "Spider-Man: No Way Home",
    "Barbie", "The Batman", "Killers of the Flower Moon",
    "Poor Things", "Saltburn", "All of Us Strangers",
    "Aftersun", "The Holdovers", "May December",
    "Drive My Car", "Nomadland", "Minari", "Sound of Metal",
]

ALL_TITLES = list(set(POPULAR_MOVIES + [t for titles in VIBE_LISTS.values() for t in titles]))


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
    res = requests.get(f"{TMDB_URL}/search/movie", headers=headers,
                       params={"query": title}, timeout=20)
    if res.status_code == 200 and res.json().get("results"):
        return res.json()["results"][0]
    return None


@st.cache_data(ttl=3600)
def get_similar(movie_id):
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    res = requests.get(f"{TMDB_URL}/movie/{movie_id}/recommendations",
                       headers=headers, timeout=20)
    if res.status_code == 200:
        return [
            m for m in res.json().get("results", [])
            if m.get("release_date", "")[:4] >= "1980"
            and m.get("vote_count", 0) > 500
        ][:15]
    return []


@st.cache_data(ttl=3600)
def get_trending():
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    res = requests.get(f"{TMDB_URL}/trending/movie/week", headers=headers, timeout=20)
    if res.status_code == 200:
        return [m for m in res.json().get("results", [])
                if m.get("vote_count", 0) > 500][:15]
    return []


@st.cache_data(ttl=3600)
def load_movies(titles):
    movies = []
    for title in titles:
        movie = search_movie(title)
        if movie and movie.get("release_date", "")[:4] >= "1980":
            movies.append(movie)
    return movies


def get_fallback_recommendations(liked_movies):
    liked_ids = [m["id"] for m in liked_movies if m.get("id")]
    all_recs = []
    for movie in liked_movies:
        if not movie.get("id"):
            continue
        for s in get_similar(movie["id"]):
            sid = s.get("id")
            if not sid or sid in liked_ids:
                continue
            if sid in [r.get("tmdb_id") for r in all_recs]:
                continue
            overview = s.get("overview", "")
            why = (overview[:120] + "...") if len(overview) > 120 else overview or "Similar vibe to your picks"
            all_recs.append({
                "title": s.get("title", ""),
                "year": (s.get("release_date", "") or "")[:4],
                "why": why,
                "poster_path": s.get("poster_path"),
                "rating": s.get("vote_average", 0),
                "tmdb_id": sid,
            })
    all_recs.sort(key=lambda x: float(x.get("rating") or 0), reverse=True)
    return {"recommendations": all_recs[:5]}


def to_stars(rating):
    score = (rating or 0) / 2
    full = int(score)
    half = score - full >= 0.5
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))


def _safe_year(release_date):
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


def genre_donut_chart(df_genres):
    if df_genres.empty:
        return None
    g = (
        df_genres.groupby("genre").size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )
    fig = px.pie(g, names="genre", values="count", hole=0.5,
                 title="Your Taste Profile — Genre Breakdown",
                 color_discrete_sequence=px.colors.sequential.Greens_r)
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def rating_preference_analysis(liked_df, pool_df):
    liked_avg = float(liked_df["rating"].mean()) if not liked_df.empty else 0.0
    pool_avg = float(pool_df["rating"].mean()) if not pool_df.empty else 0.0
    corr = np.nan
    if "pick_index" in liked_df.columns and liked_df["rating"].notna().sum() >= 2:
        corr = float(liked_df[["pick_index", "rating"]].corr(numeric_only=True).iloc[0, 1])
    fig = px.scatter(
        liked_df, x="pick_index", y="rating", hover_name="title",
        title="Pick Order vs TMDB Rating",
        color_discrete_sequence=["#00e054"]
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
    sim = np.clip(0.75 * genre_sim + 0.25 * num_sim, 0.0, 1.0)
    labels = liked_df.set_index("id").loc[ids]["title"].tolist()
    n = sim.shape[0]
    mask = ~np.eye(n, dtype=bool)
    avg_sim = float(sim[mask].mean()) if n > 1 else np.nan
    return sim, labels, avg_sim


def similarity_heatmap(sim, labels):
    fig = px.imshow(
        sim, x=labels, y=labels, zmin=0, zmax=1, aspect="auto",
        title="How similar your picks are to each other",
        color_continuous_scale="Greens"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=520)
    return fig


# simple KNN-style vibe matcher
# looks at what genres/vibes appear most in liked movies
# and matches against the vibe lists to suggest a category
def get_vibe_match(liked_movies, genre_map):
    if not liked_movies:
        return None, None

    genre_ids = []
    for m in liked_movies:
        genre_ids.extend(m.get("genre_ids") or [])

    genre_counts = {}
    for gid in genre_ids:
        name = genre_map.get(gid, "")
        if name:
            genre_counts[name] = genre_counts.get(name, 0) + 1

    if not genre_counts:
        return None, None

    top_genre = max(genre_counts, key=genre_counts.get)

    genre_to_vibe = {
        "Action": "Pure Adrenaline",
        "Thriller": "Slow Burn Thriller",
        "Crime": "Heist",
        "Comedy": "Dark Comedy",
        "Drama": "For When You Want to Feel Something",
        "Science Fiction": "Mind Bending",
        "Horror": "A24",
        "Romance": "For When You Want to Feel Something",
        "Animation": "Feel Good",
        "Adventure": "Everyone Should Watch",
        "Mystery": "Slow Burn Thriller",
        "Music": "Feel Good",
        "History": "Based on True Events",
        "War": "Everyone Should Watch",
    }

    vibe = genre_to_vibe.get(top_genre, "Everyone Should Watch")
    return vibe, top_genre


def build_taste_persona(liked_df, liked_genres, liked_avg, pool_avg, avg_sim):
    if liked_genres is not None and not liked_genres.empty:
        top = (
            liked_genres.groupby("genre").size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        top_genres = top["genre"].head(3).tolist()
    else:
        top_genres = []

    diff = liked_avg - pool_avg
    if diff >= 0.4:
        rating_lean = "You lean toward higher-rated picks."
    elif diff <= -0.4:
        rating_lean = "You don't chase ratings — you pick on vibe."
    else:
        rating_lean = "Your ratings align pretty closely with the pool average."

    if pd.isna(avg_sim):
        cluster = "Pick more movies to build out your profile."
    elif avg_sim >= 0.65:
        cluster = "Your taste is consistent — you stay in a lane."
    elif avg_sim >= 0.45:
        cluster = "You have a few main lanes but branch out sometimes."
    else:
        cluster = "You're all over the place — in a good way."

    genre_line = f"Top genres: {', '.join(top_genres)}." if top_genres else "Pick more movies to sharpen your genre profile."

    shows = []
    if any(g in top_genres for g in ["Action", "Adventure", "Thriller", "Science Fiction"]):
        shows += ["fast-paced thrillers", "sci-fi series", "high-stakes action"]
    if any(g in top_genres for g in ["Comedy", "Romance"]):
        shows += ["comfort comedies", "rom-coms", "character-driven stuff"]
    if any(g in top_genres for g in ["Drama", "Mystery", "Crime"]):
        shows += ["prestige drama", "crime/mystery shows", "slow-burn storytelling"]
    if any(g in top_genres for g in ["Animation", "Family"]):
        shows += ["animated films", "feel-good series", "rewatchable classics"]
    if not shows:
        shows = ["whatever has a strong vibe", "stuff worth recommending to friends"]

    return genre_line, rating_lean, cluster, shows


def render_visuals_bottom(liked_movies, all_movies, genre_map):
    if not liked_movies:
        return

    st.markdown("---")
    st.subheader("Your Data")

    try:
        liked_df, liked_genres = build_movies_df(liked_movies, genre_map, include_pick_index=True)
        pool_df, _ = build_movies_df(all_movies, genre_map)

        fig1 = genre_donut_chart(liked_genres)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        liked_avg, pool_avg, corr, corr_fig = rating_preference_analysis(liked_df, pool_df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg rating (your picks)", f"{liked_avg:.1f}/10")
        c2.metric("Avg rating (movie pool)", f"{pool_avg:.1f}/10")
        c3.metric("Pick order vs rating correlation", "N/A" if pd.isna(corr) else f"{corr:+.2f}")
        st.plotly_chart(corr_fig, use_container_width=True)

        st.markdown("---")

        sim, labels, avg_sim = compute_similarity_matrix(liked_df, liked_genres)
        if sim is None or len(labels) < 2:
            st.info("Pick at least 2 movies to see your similarity matrix.")
            return

        k1, k2 = st.columns([1, 3])
        with k1:
            st.metric("Avg similarity (0–1)", f"{avg_sim:.2f}")
            st.caption("Higher = your picks are in a similar lane.")
        with k2:
            st.plotly_chart(similarity_heatmap(sim, labels), use_container_width=True)

        st.markdown("---")

        # vibe match using genre-based KNN logic
        vibe, top_genre = get_vibe_match(liked_movies, genre_map)
        if vibe:
            st.markdown(f"**Based on your picks, your vibe most closely matches: {vibe}**")
            vibe_titles = VIBE_LISTS.get(vibe, [])
            liked_titles = {m.get("title") for m in liked_movies}
            suggestions = [t for t in vibe_titles if t not in liked_titles][:3]
            if suggestions:
                st.write(f"You might also like: {', '.join(suggestions)}")

        st.markdown("---")

        genre_line, rating_lean, cluster, shows = build_taste_persona(
            liked_df, liked_genres, liked_avg, pool_avg, avg_sim
        )
        st.markdown("**Your taste profile:**")
        st.write(genre_line)
        st.write(rating_lean)
        st.write(cluster)
        st.write(f"You'd probably enjoy: {', '.join(shows[:3])}.")

    except Exception as e:
        st.error(f"Something went wrong with the visuals: {e}")


def build_rec_pool(liked_movies):
    liked_ids = {m.get("id") for m in liked_movies if m.get("id")}
    pool = []
    for movie in liked_movies:
        mid = movie.get("id")
        if not mid:
            continue
        for s in get_similar(mid):
            sid = s.get("id")
            if not sid or sid in liked_ids:
                continue
            overview = s.get("overview", "")
            why = (overview[:120] + "...") if len(overview) > 120 else overview or "Similar vibe to your picks"
            pool.append({
                "title": s.get("title", ""),
                "year": (s.get("release_date", "") or "")[:4],
                "why": why,
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


def pick_replacement(rec_pool, exclude_ids):
    candidates = [r for r in rec_pool if r.get("tmdb_id") not in exclude_ids]
    return random.choice(candidates) if candidates else None


def normalize_recs(recs_obj, liked_movies):
    liked_titles = {m.get("title") for m in liked_movies if m.get("title")}
    out = []
    for r in recs_obj.get("recommendations", []):
        title = r.get("title", "")
        if not title or title in liked_titles:
            continue
        movie_data = search_movie(title)
        overview = movie_data.get("overview", "") if movie_data else ""
        why = (overview[:120] + "...") if len(overview) > 120 else overview or r.get("why", "Similar vibe to your picks")
        out.append({
            "title": title,
            "year": movie_data.get("release_date", "")[:4] if movie_data else r.get("year", ""),
            "why": why,
            "poster_path": movie_data.get("poster_path") if movie_data else r.get("poster_path"),
            "rating": movie_data.get("vote_average") if movie_data else r.get("rating", 0),
            "tmdb_id": movie_data.get("id") if movie_data else r.get("tmdb_id"),
        })
    return out


def ensure_session_defaults():
    defaults = {
        "liked": [], "seen": set(), "show_results": False,
        "recs_current": [], "rec_pool": [], "recs_seen_ids": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main():
    st.title("FilmFlicker")
    st.write("Pick movies you like. Get recommendations that actually make sense.")

    ensure_session_defaults()

    genre_map = get_genres()

    # mix trending with curated list, sample randomly so it's different each session
    trending = get_trending()
    curated = load_movies(random.sample(ALL_TITLES, min(100, len(ALL_TITLES))))
    seen_ids = {m["id"] for m in trending + curated}
    all_movies = trending + [m for m in curated if m["id"] not in {t["id"] for t in trending}]
    random.shuffle(all_movies)

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
            st.warning("You didn't pick any movies. Start over and grab some favorites.")
            if st.button("Start Over"):
                for k in ["liked", "recs_current", "rec_pool"]:
                    st.session_state[k] = []
                st.session_state.seen = set()
                st.session_state.recs_seen_ids = set()
                st.session_state.show_results = False
                st.rerun()
        else:
            st.subheader("Your Recommendations")

            if not st.session_state.recs_current:
                with st.spinner("Finding movies for you..."):
                    recs_obj = get_fallback_recommendations(st.session_state.liked)
                    st.session_state.recs_current = normalize_recs(recs_obj, st.session_state.liked)[:5]
                    st.session_state.rec_pool = build_rec_pool(st.session_state.liked)

            for i, rec in enumerate(st.session_state.recs_current, 1):
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    if rec.get("poster_path"):
                        st.image(f"https://image.tmdb.org/t/p/w200{rec['poster_path']}", width=120)
                with col2:
                    st.markdown(f"### {i}. {rec.get('title', '')} ({rec.get('year', '')})")
                    st.write(rec.get("why", ""))
                    st.write(f"{to_stars(rec.get('rating', 0))} ({float(rec.get('rating', 0) or 0):.1f}/10)")
                with col3:
                    if st.button("Not interested", key=f"rep_{i}", use_container_width=True):
                        exclude = {r.get("tmdb_id") for r in st.session_state.recs_current}
                        exclude |= st.session_state.recs_seen_ids
                        if rec.get("tmdb_id"):
                            exclude.add(rec["tmdb_id"])
                        replacement = pick_replacement(st.session_state.rec_pool, exclude)
                        if replacement:
                            st.session_state.recs_seen_ids.add(rec.get("tmdb_id"))
                            st.session_state.recs_current[i - 1] = replacement
                            st.rerun()
                        else:
                            st.warning("No more replacements available.")
                st.markdown("---")

            render_visuals_bottom(st.session_state.liked, all_movies, genre_map)

            if st.button("Start Over", type="primary"):
                for k in ["liked", "recs_current", "rec_pool"]:
                    st.session_state[k] = []
                st.session_state.seen = set()
                st.session_state.recs_seen_ids = set()
                st.session_state.show_results = False
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
            st.write(f"**{movie['title'][:22]}**")
            st.write(f"{movie.get('release_date', '')[:4]} · {to_stars(movie.get('vote_average', 0))}")
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