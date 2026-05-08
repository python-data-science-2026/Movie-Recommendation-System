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