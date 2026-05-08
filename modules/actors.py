from pathlib import Path
import pandas as pd 

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "actors.csv"

##=============================================
## Actor module : To manage actors information 
##=============================================
class Actors:
    """
    Manages actor data and interactions with the actor database.

    Attributes:
        all_actors (pd.DataFrame): The current collection of actors from the CSV database.
        fullname (str): The full name of the actor.
        date_of_birth (str, optional): The actor's birth date.
    """
    def __init__(self, actor_fullname: str, actor_date_of_birth: str = None):
        """
        Initializes an Actor instance with the given name and optional birth date.

        Args:
            actor_fullname (str): The full name of the actor.
            actor_date_of_birth (str, optional): The actor's date of birth. Defaults to None.
        """
        self.all_actors = pd.read_csv(DATA_PATH)
        self.fullname = actor_fullname.strip()
        self.date_of_birth = actor_date_of_birth
    
    def save(self):
        """
        Saves the actor to the CSV database if they do not already exist.

        Returns:
            bool: True if the actor was successfully saved, False if the actor 
                  already exists or the name is empty.
        """
        if not self.fullname:
            return False

        nrows = len(self.all_actors)
        get_actor = self.all_actors[self.all_actors['full_name'] == self.fullname]
        
        if len(get_actor) == 0:
            
            new_actor = pd.DataFrame([{
                'id': nrows+1,
                'full_name': self.fullname,
                'date_of_birth': self.date_of_birth
            }])

            self.all_actors = pd.concat([self.all_actors, new_actor])
            self.all_actors.to_csv(DATA_PATH, index=False)
            return True
        
        return False
    
    def get_id(self):
        """
        Retrieves the unique ID of the actor from the database.

        Returns:
            int: The actor's unique ID.
        """
        get_actor = self.all_actors[self.all_actors['full_name'] == self.fullname]
        return int(get_actor["id"].iloc[0])