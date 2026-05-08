"""
Movie watch history management module.

This module provides the Watch_Movie class and utility functions for tracking
and retrieving movie watch events for users.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "watch_movies.csv"
DATA_MOVIES_PATH = PROJECT_ROOT / "data" / "movies.csv"

class Watch_Movie:
    """
    Represents a movie watching event by a user.

    Attributes:
        all_data (pd.DataFrame): The history of all movie watching events.
        username (str): The username of the user who watched the movie.
        movie_id (int): The unique ID of the movie watched.
        watch_date (str): The date when the movie was watched.
        rating (float): The rating given by the user (0.0 to 5.0).
        comment (str, optional): A comment or review left by the user.
    """
    def __init__(self, username:str, movie_id:int, watch_date:str, rating:float = 0.0, comment:str = None):
        """
        Initializes a Watch_Movie instance.

        Args:
            username (str): The user's unique identifier.
            movie_id (int): The movie's unique identifier.
            watch_date (str): Date of watching.
            rating (float, optional): User rating. Defaults to 0.0.
            comment (str, optional): User comment. Defaults to None.
        """
        self.all_data = pd.read_csv(DATA_PATH)
        self.username = username
        self.movie_id = movie_id
        self.watch_date = watch_date
        self.rating = rating
        self.comment = comment
    
    def save(self):
        """
        Saves the watch event to the tracking database.
        """
        new_row = pd.DataFrame([{
            'username' : self.username,
            'movie_id' : self.movie_id,
            'watch_date' : self.watch_date,
            'rating' : self.rating,
            'comment' : self.comment
        }])

        self.all_data = pd.concat([self.all_data, new_row])
        self.all_data.to_csv(DATA_PATH, index=False)

def user_history(username:str):
    """
    Retrieves the watch history for a specific user.

    Args:
        username (str): The username to filter by.

    Returns:
        pd.DataFrame: A DataFrame containing all watch events for the user.
    """
    history = pd.read_csv(DATA_PATH)
    movies_df = pd.read_csv(DATA_MOVIES_PATH)
    all_data = pd.merge(history, movies_df.rename({'id':'movie_id'}, axis=1), on="movie_id")
    all_data = all_data[all_data['username'] == username]
    return all_data[['watch_date', 'rating', 'title', 'release_date']]

def get_all_watching():
    """
    Retrieves the complete history of all movie watch events in the system.

    Returns:
        pd.DataFrame: A DataFrame containing all recorded watch events.
    """
    return pd.read_csv(DATA_PATH)
        