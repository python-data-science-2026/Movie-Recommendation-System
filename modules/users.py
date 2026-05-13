"""
User management module.

This module provides the User class for handling user accounts, authentication,
and managing user-specific preferences for genres and actors.
"""

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
    """
    Manages user accounts, authentication, and preferences.

    Attributes:
        all_users (pd.DataFrame): User database indexed by username.
        all_genre_preferencies (pd.DataFrame): User genre preferences.
        all_actors_preferencies (pd.DataFrame): User actor preferences.
        username (str): The unique username of the user.
        lastname (str): The user's last name.
        firstname (str, optional): The user's first name.
        date_of_birth (str, optional): The user's date of birth.
        password (str): The hashed password of the user.
    """
    def __init__(self, username: str, password: str, lastname: str = '', firstname: str = None, date_of_birth: str = None):
        """
        Initializes a User instance.

        Args:
            username (str): Unique identifier for the user.
            password (str): Plain-text password (will be hashed).
            lastname (str, optional): User's last name. Defaults to ''.
            firstname (str, optional): User's first name. Defaults to None.
            date_of_birth (str, optional): User's date of birth. Defaults to None.
        """
        self.all_users = pd.read_csv(DATA_PATH, index_col="username")
        self.all_genre_preferencies = pd.read_csv(GENRE_PREF_DATA_PATH)
        self.all_actors_preferencies = pd.read_csv(ACTORS_PREF_DATA_PATH)

        self.username = username.strip()
        self.lastname = lastname.strip()
        self.firstname = firstname.strip() if firstname else None
        self.date_of_birth = date_of_birth
        self.password = self._hash_password(password)
        
    def _hash_password(self, password: str) -> str:
        """
        Hashes a password using SHA-256.

        Args:
            password (str): The plain-text password.

        Returns:
            str: The hexadecimal representation of the hash.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        """
        Authenticates the user by checking the username and password against the database.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        if self.username in self.all_users.index:
            return str(self.all_users.loc[self.username, 'password']) == self.password
        return False
    
    def save(self):
        """
        Saves the new user to the database if the username is unique.

        Returns:
            bool: True if the user was successfully saved, False if the username already exists.
        """
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
        """
        Updates user information in the database.

        Args:
            lastname (str, optional): New last name.
            password (str, optional): New plain-text password.
            firstname (str, optional): New first name.
            date_of_birth (str, optional): New date of birth.

        Returns:
            bool: True if the update was successful, False if the user does not exist.
        """
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

    def add_genre_preferencies(self, genre:str, rate=5):
        """
        Adds or updates a genre in the user's preferences.

        Args:
            genre (str): The name of the genre to add/update.
            rate (int): The rating to assign.

        Returns:
            bool: True if the preference was saved.
        """
        genre_object = Genre(genre)
        _ = genre_object.save()
        gid = genre_object.get_id()

        mask = (self.all_genre_preferencies['username'] == self.username) & \
               (self.all_genre_preferencies['genre_id'] == gid)
        
        if not self.all_genre_preferencies[mask].empty:
            self.all_genre_preferencies.loc[mask, 'rating'] = rate
        else:
            new_row = pd.DataFrame([{
                'username': self.username,
                'genre_id': gid,
                'rating': rate
            }])
            self.all_genre_preferencies = pd.concat([self.all_genre_preferencies, new_row], ignore_index=True)

        self.all_genre_preferencies.to_csv(GENRE_PREF_DATA_PATH, index=False)
        return True

    def add_actors_preferencies(self, actor:str, rate = 5):
        """
        Adds or updates an actor in the user's preferences.

        Args:
            actor (str): The full name of the actor to add/update.
            rate (int): The rating to assign.

        Returns:
            bool: True if the preference was saved.
        """
        actor_object = Actors(actor)
        _ = actor_object.save()
        aid = actor_object.get_id()

        mask = (self.all_actors_preferencies['username'] == self.username) & \
               (self.all_actors_preferencies['actor_id'] == aid)

        if not self.all_actors_preferencies[mask].empty:
            self.all_actors_preferencies.loc[mask, 'rating'] = rate
        else:
            new_row = pd.DataFrame([{
                'username': self.username,
                'actor_id': aid,
                'rating': rate
            }])
            self.all_actors_preferencies = pd.concat([self.all_actors_preferencies, new_row], ignore_index=True)

        self.all_actors_preferencies.to_csv(ACTORS_PREF_DATA_PATH, index=False)
        return True
    
    def get_genre_preferencies(self):
        """
        Retrieves the user's genre preferences.

        Returns:
            pd.DataFrame: A DataFrame containing the user's preferred genre IDs.
        """
        return  self.all_genre_preferencies[(self.all_genre_preferencies['username'] == self.username)]

    def get_actors_preferencies(self):
        """
        Retrieves the user's actor preferences.

        Returns:
            pd.DataFrame: A DataFrame containing the user's preferred actor IDs.
        """
        return self.all_actors_preferencies[self.all_actors_preferencies['username'] == self.username]