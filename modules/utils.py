from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_LIST = {"users.csv":['username', 'lastname', 'firstname', 'date_of_birth', 'password'], 
                "actors.csv":['id', 'full_name', 'date_of_birth'],
                "genres.csv":['id', 'name'],
                "movies.csv":['id', 'title', 'release_date', 'genre_id'],
                "movies_actors.csv": ['movie_id', 'actor_id']}

def check_datasets():
    for key, val in DATASET_LIST.items():
        dataset_path = PROJECT_ROOT / "data" / key
        if not dataset_path.exists():
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(columns=val).to_csv(dataset_path, index=False)