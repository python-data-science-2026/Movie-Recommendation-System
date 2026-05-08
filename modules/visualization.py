##=============================================
## Visualization and Trend analysis
##=============================================
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_data():
    return {
        "movies": pd.read_csv(DATA_DIR / "movies.csv"),
        "genres": pd.read_csv(DATA_DIR / "genres.csv"),
        "actors": pd.read_csv(DATA_DIR / "actors.csv"),
        "movies_genres": pd.read_csv(DATA_DIR / "movies_genres.csv"),
        "movies_actors": pd.read_csv(DATA_DIR / "movies_actors.csv"),
        "watch_movies": pd.read_csv(DATA_DIR / "watch_movies.csv"),
    }


def get_user_movies(username):
    data = load_data()

    watches = data["watch_movies"]
    movies = data["movies"]

    user_watches = watches[watches["username"] == username]

    if user_watches.empty:
        return pd.DataFrame()

    return user_watches.merge(
        movies,
        left_on="movie_id",
        right_on="id",
        how="left"
    )


def plot_movies_by_genre(username):
    data = load_data()
    user_movies = get_user_movies(username)

    if user_movies.empty:
        print("No watched movies found.")
        return

    genre_data = (
        user_movies[["movie_id"]]
        .merge(data["movies_genres"], on="movie_id")
        .merge(data["genres"], left_on="genre_id", right_on="id")
    )

    genre_counts = genre_data["name"].value_counts()

    OUTPUT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    genre_counts.plot(kind="bar")
    plt.title(f"Movies watched by genre - {username}")
    plt.xlabel("Genre")
    plt.ylabel("Number of movies")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    path = OUTPUT_DIR / f"{username}_genres.png"
    plt.savefig(path)
    plt.show()

    print(f"Saved genre plot to: {path}")


def plot_movies_by_actor(username, top_n=10):
    data = load_data()
    user_movies = get_user_movies(username)

    if user_movies.empty:
        print("No watched movies found.")
        return

    actor_data = (
        user_movies[["movie_id"]]
        .merge(data["movies_actors"], on="movie_id")
        .merge(data["actors"], left_on="actor_id", right_on="id")
    )

    actor_counts = actor_data["full_name"].value_counts().head(top_n)

    OUTPUT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    actor_counts.plot(kind="bar")
    plt.title(f"Top actors in watched movies - {username}")
    plt.xlabel("Actor")
    plt.ylabel("Number of movies")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    path = OUTPUT_DIR / f"{username}_actors.png"
    plt.savefig(path)
    plt.show()

    print(f"Saved actor plot to: {path}")


def plot_rating_trend(username):
    user_movies = get_user_movies(username)

    if user_movies.empty:
        print("No watched movies found.")
        return

    user_movies["watch_date"] = pd.to_datetime(user_movies["watch_date"], errors="coerce")
    user_movies = user_movies.dropna(subset=["watch_date"]).sort_values("watch_date")

    if user_movies.empty:
        print("No valid watch dates found.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(user_movies["watch_date"], user_movies["rating"], marker="o")
    plt.title(f"Rating trend over time - {username}")
    plt.xlabel("Watch date")
    plt.ylabel("Rating")
    plt.ylim(0, 5)
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = OUTPUT_DIR / f"{username}_rating_trend.png"
    plt.savefig(path)
    plt.show()

    print(f"Saved rating trend plot to: {path}")


def recommend_movies(username, top_n=10):
    data = load_data()
    user_movies = get_user_movies(username)

    if user_movies.empty:
        print("No watched movies found. Cannot recommend movies yet.")
        return pd.DataFrame()

    genre_data = (
        user_movies[["movie_id"]]
        .merge(data["movies_genres"], on="movie_id")
        .merge(data["genres"], left_on="genre_id", right_on="id")
    )

    favorite_genres = genre_data["name"].value_counts().head(3).index.tolist()

    all_movie_genres = (
        data["movies_genres"]
        .merge(data["genres"], left_on="genre_id", right_on="id")
        .merge(data["movies"], left_on="movie_id", right_on="id")
    )

    watched_ids = user_movies["movie_id"].tolist()

    recommendations = all_movie_genres[
        (all_movie_genres["name"].isin(favorite_genres)) &
        (~all_movie_genres["movie_id"].isin(watched_ids))
    ]

    recommendations = recommendations[["title", "release_date", "name"]]
    recommendations = recommendations.drop_duplicates().head(top_n)

    print("\nRecommended movies based on your favorite genres:")
    print(recommendations.to_string(index=False))

    return recommendations


def show_user_analysis(username):
    print(f"\n=== Movie analysis for {username} ===")

    user_movies = get_user_movies(username)

    if user_movies.empty:
        print("No watched movies found.")
        return

    print("\nWatched movies:")
    print(user_movies[["title", "release_date", "watch_date", "rating"]].to_string(index=False))

    plot_movies_by_genre(username)
    plot_movies_by_actor(username)
    plot_rating_trend(username)
    recommend_movies(username)