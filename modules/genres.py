"""
Genre management module.

This module provides the Genre class for handling movie genre information,
including saving to and retrieving from the genres database.
"""

from pathlib import Path
import pandas as pd 

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "genres.csv"

##=============================================
## genre module : To manage genre information 
##=============================================

class Genre:
    """
    Manages movie genre data and interactions with the genre database.

    Attributes:
        all_genre (pd.DataFrame): The current collection of genres from the CSV database.
        name (str): The name of the genre.
    """
    def __init__(self, genre_name: str):
        """
        Initializes a Genre instance with the given name.

        Args:
            genre_name (str): The name of the genre.
        """
        self.all_genre = pd.read_csv(DATA_PATH)
        self.name = genre_name.strip()

    def save(self):
        """
        Saves the genre to the CSV database if it does not already exist.

        Returns:
            bool: True if the genre was successfully saved, False if it 
                  already exists or the name is empty.
        """
        if not self.name:
            return False

        nrows = len(self.all_genre)
        get_genre = self.all_genre[self.all_genre['name'] == self.name]

        if len(get_genre) == 0:
            new_genre = pd.DataFrame([{
                'id': nrows+1,
                'name': self.name
            }])
            self.all_genre = pd.concat([self.all_genre, new_genre], ignore_index=True)
            self.all_genre.to_csv(DATA_PATH)
            return True
        else:
            return False

    def get_id(self):
        """
        Retrieves the unique ID of the genre from the database.

        Returns:
            int: The genre's unique ID.
        """
        get_genre = self.all_genre.loc[self.all_genre['name'] == self.name]
        return int(get_genre['id'].item())