##=============================================
## Visualization and Trend analysis
##=============================================
from pathlib import Path
import pandas as pd

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