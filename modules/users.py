from pathlib import Path
import pandas as pd 
import hashlib
from .genres import Genre
from .actors import Actors

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "users.csv"
GENRE_PREF_DATA_PATH = PROJECT_ROOT / "data" / "user_genre.csv"
ACTORS_PREF_DATA_PATH = PROJECT_ROOT / "data" / "user_actors.csv"

##=============================================
## User module : To manage users information 
##=============================================
class User:
    def __init__(self, username: str, password: str, lastname: str = '', firstname: str = None, date_of_birth: str = None):
        self.all_users = pd.read_csv(DATA_PATH, index_col="username")
        self.all_genre_preferencies = pd.read_csv(GENRE_PREF_DATA_PATH)
        self.all_actors_preferencies = pd.read_csv(ACTORS_PREF_DATA_PATH)

        self.username = username.strip()
        self.lastname = lastname.strip()
        self.firstname = firstname.strip() if firstname else None
        self.date_of_birth = date_of_birth
        self.password = self._hash_password(password)
        
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        if self.username in self.all_users.index:
            return str(self.all_users.loc[self.username, 'password']) == self.password
        return False
    
    def save(self):
        if self.username not in self.all_users.index: 
            current_user = pd.DataFrame(
                [{
                    'username': self.username,
                    'lastname': self.lastname,
                    'firstname': self.firstname,
                    'date_of_birth': self.date_of_birth,
                    'password': self.password
                }]
            )
            current_user = current_user.set_index('username')

            self.all_users = pd.concat([self.all_users, current_user], axis=0)
            self.all_users.to_csv(DATA_PATH)
            return True
        return False
    
    def edit_data(self, lastname: str = '', password: str = '', firstname: str = None, date_of_birth: str = None):
        if self.username not in self.all_users.index:
            return False

        if lastname != '':
            self.all_users.at[self.username, 'lastname'] = lastname
        if password != '':
            self.all_users.at[self.username, 'password'] = self._hash_password(password)
        if firstname is not None:
            self.all_users.at[self.username, 'firstname'] = firstname
        if date_of_birth is not None:
            self.all_users.at[self.username, 'date_of_birth'] = date_of_birth
        
        self.all_users.to_csv(DATA_PATH)
        return True

    def add_genre_preferencies(self, genre:str):
        genre_object = Genre(genre)
        _ = genre_object.save()

        filtered_row = self.all_genre_preferencies[(self.all_genre_preferencies['username'] == self.username)&
                                                    (self.all_genre_preferencies['genre_id'] == genre_object.get_id())]
        if len(filtered_row) == 0:
            new_row = pd.DataFrame({
                'username':self.username,
                'genre_id' : genre_object.get_id()
            })

            self.all_genre_preferencies = pd.concat([self.all_genre_preferencies, new_row])
            self.all_genre_preferencies.to_csv(GENRE_PREF_DATA_PATH)
            return True
        return False


    def add_actors_preferencies(self, actor:str):
        actor_object = Actors(actor)
        _ = actor_object.save()

        filtered_row = self.all_actors_preferencies[(self.all_actors_preferencies['username'] == self.username)&
                                                    (self.all_actors_preferencies['actor_id'] == actor_object.get_id())]

        if len(filtered_row) == 0:
            new_row = pd.DataFrame({
                'username':self.username,
                'actor_id' : actor_object.get_id()
            })

            self.all_actors_preferencies = pd.concat([self.all_actors_preferencies, new_row])
            self.all_actors_preferencies.to_csv(ACTORS_PREF_DATA_PATH)
            return True
        return False
    
    def get_genre_preferencies(self):
        return  self.all_genre_preferencies[(self.all_genre_preferencies['username'] == self.username)]

    def get_actors_preferencies(self):
        return self.all_actors_preferencies[self.all_actors_preferencies['username'] == self.username]