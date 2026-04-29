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
    """
    Manages movie data and associations with actors and genres.

    Attributes:
        all_movies (pd.DataFrame): The collection of movies from the CSV database.
        all_movies_actors (pd.DataFrame): Associations between movies and actors.
        all_movies_genres (pd.DataFrame): Associations between movies and genres.
        title (str): The title of the movie.
        release_date (str, optional): The release date of the movie.
    """
    def __init__(self, title: str, release_date:str=None, ):
        """
        Initializes a Movies instance with the given title and optional release date.

        Args:
            title (str): The title of the movie.
            release_date (str, optional): The release date of the movie. Defaults to None.
        """
        self.all_movies = pd.read_csv(MOVIES_DATA_PATH)
        self.all_movies_actors = pd.read_csv(MOVIES_ACTORS_DATA_PATH)
        self.all_movies_genres = pd.read_csv(MOVIES_GENRES_DATA_PATH)
        
        self.title = title.strip()
        self.release_date = release_date

    def save(self):
        """
        Saves the movie to the database if it does not already exist.

        Returns:
            bool: True if the movie was successfully saved, False if it already exists.
        """
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
        """
        Retrieves the unique ID of the movie from the database.

        Returns:
            int: The movie's unique ID.
        """
        get_movie = self.all_movies[self.all_movies['title'] == self.title]
        return int(get_movie['id'])

    def add_actor(self, actor:str):
        """
        Associates an actor with this movie.

        Args:
            actor (str): The full name of the actor to add.

        Returns:
            bool: True if the association was successfully saved, False if it already exists.
        """
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
        """
        Associates a genre with this movie.

        Args:
            genre (str): The name of the genre to add.

        Returns:
            bool: True if the association was successfully saved, False if it already exists.
        """
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
