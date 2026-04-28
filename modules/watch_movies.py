from .users import User
from .movies import Movies
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "watch_movies.csv"

class Watch_Movie:
    def __init__(self, username:str, movie_id:int, watch_date:str, rating:float = 0.0, comment:str = None):
        self.all_data = pd.read_csv(DATA_PATH)
        self.username = username
        self.movie_id = movie_id
        self.watch_date = watch_date
        self.rating = rating
        self.comment = comment
    
    def save(self):
        new_row = pd.DataFrame({
            'username' : self.username,
            'movie_id' : self.movie_id,
            'watch_date' : self.watch_date,
            'rating' : self.rating,
            'comment' : self.comment
        })

        self.all_data = pd.concat([self.all_data, new_row])
        self.all_data.to_csv(DATA_PATH)

def user_history(username:str):
    all_data = pd.read_csv(DATA_PATH)
    return all_data[all_data['username'] == username]

def get_all_watching():
    return pd.read_csv(DATA_PATH)
        
        
