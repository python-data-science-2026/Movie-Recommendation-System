from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_LIST = {"users.csv":['username', 'lastname', 'firstname', 'date_of_birth', 'password'], 
                "actors.csv":['id', 'full_name', 'date_of_birth'],
                "genres.csv":['id', 'name'],
                "movies.csv":['id', 'title', 'release_date'],
                "movies_genres.csv": ['movie_id', 'genre_id'],
                "movies_actors.csv": ['movie_id', 'actor_id'],
                "user_genre.csv": ['username', 'genre_id'],
                "user_actors.csv": ['username', 'actor_id'],
                "watch_movies.csv": ['username', 'movie_id', 'watch_date', 'rating', 'comment']}

def check_datasets():
    """
    Checks for the existence of required CSV datasets and creates them with headers if missing.

    Iterates through the DATASET_LIST to ensure all necessary data files are present 
    in the project's data directory. If a file is missing, it is created with the 
    predefined columns.
    """
    for key, val in DATASET_LIST.items():
        dataset_path = PROJECT_ROOT / "data" / key
        if not dataset_path.exists():
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(columns=val).to_csv(dataset_path, index=False)


def load_datasets():
    datasets = dict()
    for key in DATASET_LIST.keys():
        dataset_path = PROJECT_ROOT / "data" / key
        datasets[key] = pd.read_csv(dataset_path)
    
    return datasets