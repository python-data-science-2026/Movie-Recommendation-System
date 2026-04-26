from pathlib import Path
import pandas as pd 
from .genres import Genre
from .actors import Actors

PROJECT_ROOT = Path(__file__).parent.parent
MOVIES_DATA_PATH = PROJECT_ROOT / "data" / "movies.csv"
MOVIES_ACTORS_DATA_PATH = PROJECT_ROOT / "data" / "movies_actors.csv"

##=============================================
## Movies module : To manage movies information 
##=============================================
class Movies:
    def __init__(self, title: str, release_date:str=None, genre: str = '', actors: list = None):
        self.all_movies = pd.read_csv(MOVIES_DATA_PATH)
        self.all_movies_actors = pd.read_csv(MOVIES_ACTORS_DATA_PATH)
        self.title = title.strip()
        self.genre = genre.strip()
        self.actors = actors if actors else []
        self.release_date = release_date

    def save(self):
        if not self.title:
            return False
        
        nrows = len(self.all_movies)
        get_movie = self.all_movies[self.all_movies['title'] == self.title]
        genre_id = Genre(self.genre).get_id()

        if len(get_movie) == 0:
            new_movie = pd.DataFrame([{
                'id': nrows+1,
                'title': self.title,
                'release_date': self.release_date,
                'genre_id': genre_id
            }])

            self.all_movies = pd.concat([self.all_movies, new_movie])
            self.all_movies.to_csv(MOVIES_DATA_PATH, index=False)

            if len(self.actors)!=0:
                actors_id = [Actors(actor).get_id() for actor in self.actors]
                movie_id = [ nrows + 1 for _ in self.actors]
                new_movie_actors = pd.DataFrame(
                    {
                        'movie_id': movie_id,
                        'actor_id': actors_id
                    }
                )
                self.all_movies_actors = pd.concat([self.all_movies_actors, new_movie_actors])
                self.all_movies_actors.to_csv(MOVIES_ACTORS_DATA_PATH, index=False)
            return True
        
        return False
