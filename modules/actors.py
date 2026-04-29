from pathlib import Path
import pandas as pd 

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "actors.csv"

##=============================================
## Actor module : To manage actors information 
##=============================================
class Actors:
    
    def __init__(self, actor_fullname: str, actor_date_of_birth: str = None):
        self.all_actors = pd.read_csv(DATA_PATH)
        self.fullname = actor_fullname.strip()
        self.date_of_birth = actor_date_of_birth
    
    def save(self):
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
        
        get_actor = self.all_actors[self.all_actors['full_name'] == self.fullname]
        return int(get_actor['id'])