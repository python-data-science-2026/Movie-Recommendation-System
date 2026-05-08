"""
Utility functions for dataset management and validation.

This module provides tools for ensuring dataset existence, loading data,
and basic input validation.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_LIST = {"users.csv":['username', 'lastname', 'firstname', 'date_of_birth', 'password'], 
                "actors.csv":['id', 'full_name', 'date_of_birth'],
                "genres.csv":['id', 'name'],
                "movies.csv":['id', 'title', 'release_date'],
                "movies_genres.csv": ['movie_id', 'genre_id'],
                "movies_actors.csv": ['movie_id', 'actor_id'],
                "user_genre.csv": ['username', 'genre_id', 'rating'],
                "user_actors.csv": ['username', 'actor_id', 'rating'],
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


def check_rating(rating:str):
    """
    Validates if a rating string is a digit and within the 1-5 range.

    Args:
        rating (str): The rating string to check.

    Returns:
        float: The rating as a float if valid, None otherwise.
    """
    if rating.isdigit():
        val = float(rating)
        if 1 <= val <= 5:
            return val
    return None

def validate_date(date_str: str):
    """
    Validates if a date string follows the YYYY-MM-DD format.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    import datetime
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def load_datasets(filename:str):
    """
    Loads a dataset from a CSV file.

    Args:
        filename (str): The name of the CSV file to load.

    Returns:
        pd.DataFrame: The loaded dataset as a pandas DataFrame.
    """
    dataset_path = PROJECT_ROOT / "data" / filename
    dataset = pd.read_csv(dataset_path)
    
    return dataset