from pathlib import Path
import pandas as pd 
import hashlib

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "users.csv"

##=============================================
## User module : To manage users information 
##=============================================
class User:
    def __init__(self, username: str, password: str, lastname: str = '', firstname: str = None, date_of_birth: str = None):
        self.all_users = pd.read_csv(DATA_PATH, index_col="username")
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

