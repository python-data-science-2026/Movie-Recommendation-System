from pathlib import Path
import pandas as pd 

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "genres.csv"

##=============================================
## genre module : To manage genre information 
##=============================================

class Genre:
    def __init__(self, genre_name: str):
        self.all_genre = pd.read_csv(DATA_PATH)
        self.name = genre_name.strip()

    def save(self):
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
        get_genre = self.all_genre[self.all_genre['name'] == self.name]
        return int(get_genre['id'])