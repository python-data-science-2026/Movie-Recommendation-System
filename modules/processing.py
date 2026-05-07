from modules import utils

import pandas as pd


def merge_preferencies(actor_df:pd.DataFrame, genre_df:pd.DataFrame, 
                       pref_actor_df:pd.DataFrame, pref_genre_df:pd.DataFrame) -> pd.DataFrame:
    tmp1 = pd.merge(pref_actor_df, actor_df.rename({"full_name":"actor_full_name",
                                                       "date_of_birth":"actor_date_of_birth",
                                                       "id":"actor_id"}, axis=1), 
                                      on="actor_id").drop(labels=['actor_id'], axis=1)
    
    tmp2 = pd.merge(tmp1, pref_genre_df, 
                    on="username", 
                    how="left").merge(genre_df.rename({"name":"genre_name", 
                                            "id":"genre_id"}, axis=1), on="genre_id").drop(labels=['genre_id'], axis=1)
    
    return tmp2

def merge_movies_details(movies_df:pd.DataFrame, actor_df:pd.DataFrame, 
                         genre_df:pd.DataFrame, detail_actor_df:pd.DataFrame, 
                         detail_genre_df:pd.DataFrame) -> pd.DataFrame:
    tmp1 = pd.merge(movies_df.rename({"id":"movie_id"}, axis=1), 
                    detail_actor_df, how="left", on="movie_id").merge(
                        actor_df.rename({"id":"actor_id", "full_name":"actor_full_name"}, axis=1), 
                        how="left", on="actor_id"
                    ).drop(['actor_id', 'date_of_birth'], axis=1)

    tmp2 = pd.merge(tmp1, detail_genre_df, on="movie_id", 
                    how="left").merge(
                        genre_df.rename({"id":"genre_id", "name": "genre_name"}, axis=1),
                        how="left", on="genre_id"
                    ).drop(['genre_id'], axis=1)
    
    tmp2 = tmp2.groupby(['title', 'release_date']).agg({'actor_full_name':lambda x: x.tolist(),
                                 'genre_name':lambda x: x.tolist()}).rename({'actor_full_name':'actors', 
                                                                             'genre_name':'genres'}, axis=1)
    return tmp2.reset_index() 


def watch_user_genres_mat(watch_movies_df:pd.DataFrame, movies_genres_df:pd.DataFrame):
    tmp = pd.merge(watch_movies_df, movies_genres_df, 
                   on="movie_id", how='left').drop(['comment', 'watch_date', 'movie_id'], axis=1)

    return tmp.groupby(['username', 'genre_id']).agg('mean').fillna(0).reset_index()

def watch_user_movies_mat(watch_movies_df:pd.DataFrame):
    return watch_movies_df[['username', 'movie_id', 'rating']]

def pref_user_mat(all_user_pref:pd.DataFrame, interest:str):
    tmp = all_user_pref.copy()
    tmp = tmp[['username', f"{interest}_id"]]
    tmp["pref"] = tmp['username'].apply(lambda x: 1)
    return pd.pivot(tmp, index="username", columns=f"{interest}_id",
                    values="pref").fillna(0)