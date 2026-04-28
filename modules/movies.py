from pathlib import Path
import pandas as pd 
from .genres import Genre
from .actors import Actors

PROJECT_ROOT = Path(__file__).parent.parent
MOVIES_DATA_PATH = PROJECT_ROOT / "data" / "movies.csv"
MOVIES_ACTORS_DATA_PATH = PROJECT_ROOT / "data" / "movies_actors.csv"
MOVIES_GENRES_DATA_PATH = PROJECT_ROOT / "data" / "movies_genres.csv"

##=============================================
## Movies module : To manage movies information 
##=============================================
class Movies:
    def __init__(self, title: str, release_date:str=None, ):
        self.all_movies = pd.read_csv(MOVIES_DATA_PATH)
        self.all_movies_actors = pd.read_csv(MOVIES_ACTORS_DATA_PATH)
        self.all_movies_genres = pd.read_csv(MOVIES_GENRES_DATA_PATH)
        
        self.title = title.strip()
        self.release_date = release_date

    def save(self):
        nrows = len(self.all_movies)
        get_movie = self.all_movies[self.all_movies['title'] == self.title]

        if len(get_movie) == 0:
            new_movie = pd.DataFrame([{
                'id': nrows+1,
                'title': self.title,
                'release_date': self.release_date
            }])

            self.all_movies = pd.concat([self.all_movies, new_movie])
            self.all_movies.to_csv(MOVIES_DATA_PATH, index=False)
            return True
        
        return False
    
    def get_id(self):
        get_movie = self.all_movies[self.all_movies['title'] == self.title]
        return int(get_movie['id'])

    def add_actor(self, actor:str):
        actor_object = Actors(actor)
        _ = actor_object.save()

        filtered_row = self.all_movies_actors[(self.all_movies_actors['movie_id'] == self.get_id())&
                                                    (self.all_movies_actors['actor_id'] == actor_object.get_id())]

        if len(filtered_row) == 0:
            new_row = pd.DataFrame({
                'movie_id':self.get_id(),
                'actor_id' : actor_object.get_id()
            })

            self.all_movies_actors = pd.concat([self.all_movies_actors, new_row])
            self.all_movies_actors.to_csv(MOVIES_ACTORS_DATA_PATH)
            return True
        return False

    def add_genre(self, genre:str):
        genre_object = Genre(genre)
        _ = genre_object.save()

        filtered_row = self.all_movies_genres[(self.all_movies_genres['movie_id'] == self.get_id())&
                                                    (self.all_movies_genres['genre_id'] == genre_object.get_id())]
        if len(filtered_row) == 0:
            new_row = pd.DataFrame({
                'movie_id': self.get_id(),
                'genre_id' : genre_object.get_id()
            })

            self.all_movies_genres = pd.concat([self.all_movies_genres, new_row])
            self.all_movies_genres.to_csv(MOVIES_GENRES_DATA_PATH)
            return True
        return False
