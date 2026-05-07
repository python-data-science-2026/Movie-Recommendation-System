import pandas as pd
import numpy as np


def merge_preferencies(actor_df:pd.DataFrame, genre_df:pd.DataFrame, 
                       pref_actor_df:pd.DataFrame, pref_genre_df:pd.DataFrame) -> pd.DataFrame:
    tmp1 = pd.merge(pref_actor_df, actor_df.rename({"full_name":"actor_full_name",
                                                       "date_of_birth":"actor_date_of_birth",
                                                       "id":"actor_id",
                                                       'rating':'actor_rating'}, axis=1), 
                                      on="actor_id")
    
    tmp2 = pd.merge(tmp1, pref_genre_df, 
                    on="username", 
                    how="left").merge(genre_df.rename({"name":"genre_name", 
                                            "id":"genre_id", "rating":"genre_rating"}, 
                                            axis=1), on="genre_id")
    
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
    return all_user_pref[['username', f"{interest}_id", f"{interest}_rating"]]

def movies_not_yet_watched(username:str, movies_df:pd.DataFrame, watch_movies_df:pd.DataFrame):
    user_watched = watch_movies_df.loc[watch_movies_df['username']==username]
    not_watced_mask = ~np.isin(movies_df['id'], user_watched['movie_id'])
    return movies_df.loc[not_watced_mask]

def genre_not_yet_watched(movies_not_watched:pd.DataFrame, detail_genre_df:pd.DataFrame):
    tmp = pd.merge(movies_not_watched.rename({"id":"movie_id"}, axis=1), 
                   detail_genre_df, how='left', on='movie_id')
    return tmp[['movie_id', 'genre_id']]