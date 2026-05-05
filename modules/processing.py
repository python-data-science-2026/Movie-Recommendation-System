from modules import utils

import numpy as np 
import pandas as pd


def merge_preferencies(user_df:pd.DataFrame, actor_df:pd.DataFrame, genre_df:pd.DataFrame, 
                       pref_actor_df:pd.DataFrame, pref_genre_df:pd.DataFrame) -> pd.DataFrame:
    tmp1 = pd.merge(user_df, pref_actor_df, 
                    on="username", 
                    how="left").merge(actor_df.rename({"full_name":"actor_full_name",
                                                       "date_of_birth":"actor_date_of_birth",
                                                       "id":"actor_id"}), 
                                      on="actor_id").drop(labels=['actor_id'], axis=1)
    
    tmp2 = pd.merge(tmp1, pref_genre_df, 
                    on="username", 
                    how="left").merge(genre_df.rename({"name":"genre_name"}), 
                                      left_on="genre_id", right_on="id")
    
    return tmp2

def merge_movies_details(movies_df:pd.DataFrame, actor_df:pd.DataFrame, 
                         genre_df:pd.DataFrame, detail_actor_df:pd.DataFrame, 
                         detail_genre_df:pd.DataFrame) -> pd.DataFrame:
    tmp1 = pd.merge(movies_df.rename({"id":"movie_id"}), 
                    detail_actor_df, how="left", on="movie_id").merge(
                        actor_df.rename({"id":"actor_id", "full_name":"actor_full_name"}), 
                        how="left", on="actor_id"
                    )
    tmp2 = pd.merge(tmp1, detail_genre_df, on="movie_id", 
                    how="left").merge(
                        genre_df.rename({"id":"genre_id", "name": "genre_name"}),
                        how="left", on="genre_id"
                    )
    return tmp2 


def build_user_movie_matrix(watch_movies_df:pd.DataFrame):
    pass

