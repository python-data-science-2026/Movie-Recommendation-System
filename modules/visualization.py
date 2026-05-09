##=============================================
## Visualization and Trend analysis
##=============================================
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MOVIES_PATH = DATA_DIR / "movies.csv"
WATCH_MOVIES_PATH = DATA_DIR / "watch_movies.csv"


def load_movies():
    movies = pd.read_csv(MOVIES_PATH)
    watch_movies = pd.read_csv(WATCH_MOVIES_PATH)
    return movies, watch_movies


def show_user_analysis(username):
    movies, watch_movies = load_movies()

    user_watches = watch_movies[watch_movies["username"] == username]

    if user_watches.empty:
        print("\nNo watched movies found yet.")
        return

    user_movies = user_watches.merge(
        movies,
        left_on="movie_id",
        right_on="id",
        how="left"
    )

    print("\n=== Your watched movies ===")
    print(user_movies[["title", "release_date", "watch_date", "rating", "comment"]].to_string(index=False))
    show_genre_breakdown(username)
    show_actor_breakdown(username)
    show_rating_trend(username)

def show_genre_breakdown(username):
    from pathlib import Path
    import pandas as pd

    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"

    movies = pd.read_csv(DATA_DIR / "movies.csv")
    watch_movies = pd.read_csv(DATA_DIR / "watch_movies.csv")
    movies_genres = pd.read_csv(DATA_DIR / "movies_genres.csv")
    genres = pd.read_csv(DATA_DIR / "genres.csv")

    user_watches = watch_movies[watch_movies["username"] == username]

    if user_watches.empty:
        print("\nNo watched movies.")
        return

    user_movies = user_watches.merge(
        movies,
        left_on="movie_id",
        right_on="id",
        how="left"
    )

    genre_data = (
        user_movies[["movie_id"]]
        .merge(movies_genres, on="movie_id")
        .merge(genres, left_on="genre_id", right_on="id")
    )

    genre_counts = genre_data["name"].value_counts()

    print("\n=== Movies by Genre ===")
    for genre, count in genre_counts.items():
        print(f"{genre:10} {'█' * count}")

    plt.figure(figsize=(8, 5))
    genre_counts.plot(kind="bar")

    plt.title(f"Movies by Genre - {username}")
    plt.xlabel("Genre")
    plt.ylabel("Count")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.show(block=True)
    plt.savefig(DATA_DIR / f"{username}_genre_plot.png")

def show_actor_breakdown(username):
    movies = pd.read_csv(DATA_DIR / "movies.csv")
    watch_movies = pd.read_csv(DATA_DIR / "watch_movies.csv")
    movies_actors = pd.read_csv(DATA_DIR / "movies_actors.csv")
    actors = pd.read_csv(DATA_DIR / "actors.csv")

    user_watches = watch_movies[watch_movies["username"] == username]

    if user_watches.empty:
        return

    user_movies = user_watches.merge(
        movies,
        left_on="movie_id",
        right_on="id",
        how="left"
    )

    actor_data = (
        user_movies[["movie_id", "title"]]
        .merge(movies_actors, on="movie_id")
        .merge(actors, left_on="actor_id", right_on="id")
    )

    actor_counts = actor_data["full_name"].value_counts()

    print("\n=== Movies by Actor ===")
    for actor, count in actor_counts.items():
        print(f"{actor:25} {'█' * count}")

    plt.figure(figsize=(10, 5))

    actor_counts.plot(kind="bar")

    plt.title(f"Movies by Actor - {username}")
    plt.xlabel("Actor")
    plt.ylabel("Count")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.show(block=True)
    plt.savefig(DATA_DIR / f"{username}_actor_plot.png")


def show_rating_trend(username):
    watch_movies = pd.read_csv(DATA_DIR / "watch_movies.csv")

    user_watches = watch_movies[watch_movies["username"] == username].copy()

    if user_watches.empty:
        return

    user_watches["watch_date"] = pd.to_datetime(
        user_watches["watch_date"], errors="coerce"
    )

    user_watches = user_watches.dropna(subset=["watch_date"])
    user_watches = user_watches.sort_values("watch_date")

    print("\n=== Rating Trend ===")

    for _, row in user_watches.iterrows():
        date = row["watch_date"].date()
        rating = row["rating"]
        print(f"{date} → {rating}")

    plt.figure(figsize=(8, 5))

    plt.plot(
        user_watches["watch_date"],
        user_watches["rating"],
        marker="o"
    )

    plt.title(f"Rating Trend Over Time - {username}")
    plt.xlabel("Watch Date")
    plt.ylabel("Rating")
    plt.ylim(0, 5)

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()