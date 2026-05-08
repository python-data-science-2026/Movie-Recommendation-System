"""
Data processing and transformation module.

This module provides functions for merging datasets, preparing matrices for
recommendation algorithms, and filtering movies based on user history.
"""

import pandas as pd
import numpy as np


def merge_actor_preferencies(actor_df:pd.DataFrame, pref_actor_df:pd.DataFrame) -> pd.DataFrame:
    """
    Merges user preferences for actors into a single DataFrame.

    Args:
        actor_df (pd.DataFrame): The actors dataset.
        pref_actor_df (pd.DataFrame): User actor preferences.

    Returns:
        pd.DataFrame: A merged DataFrame containing comprehensive user preference data.
    """
    tmp1 = pd.merge(pref_actor_df.rename({'rating':'actor_rating'}, axis=1), actor_df.rename({"full_name":"actor_full_name",
                                        "date_of_birth":"actor_date_of_birth",
                                        "id":"actor_id"}, axis=1), 
                                      on="actor_id")
    return tmp1
    
def merge_genre_preferencies(genre_df:pd.DataFrame, pref_genre_df:pd.DataFrame) -> pd.DataFrame:
    """
    Merges user preferences for genres into a single DataFrame.

    Args:
        genre_df (pd.DataFrame): The genres dataset.
        pref_genre_df (pd.DataFrame): User genre preferences.

    Returns:
        pd.DataFrame: A merged DataFrame containing comprehensive user preference data.
    """
    tmp2 = pd.merge(pref_genre_df.rename({"rating":"genre_rating"}, axis=1), 
                    genre_df.rename({"name":"genre_name", 
                                "id":"genre_id"}, 
                                axis=1),
                    on="genre_id")
    
    return tmp2

def merge_movies_details(movies_df:pd.DataFrame, actor_df:pd.DataFrame, 
                         genre_df:pd.DataFrame, detail_actor_df:pd.DataFrame, 
                         detail_genre_df:pd.DataFrame) -> pd.DataFrame:
    """
    Merges movie details with their associated actors and genres.

    Groups the result by movie title and release date, aggregating actors and genres into lists.

    Args:
        movies_df (pd.DataFrame): The movies dataset.
        actor_df (pd.DataFrame): The actors dataset.
        genre_df (pd.DataFrame): The genres dataset.
        detail_actor_df (pd.DataFrame): Movie-actor associations.
        detail_genre_df (pd.DataFrame): Movie-genre associations.

    Returns:
        pd.DataFrame: A DataFrame with movie details and lists of actors and genres.
    """
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
    """
    Creates a user-genre rating matrix based on watch history.

    Calculates the average rating per user per genre.

    Args:
        watch_movies_df (pd.DataFrame): User watch history.
        movies_genres_df (pd.DataFrame): Movie-genre associations.

    Returns:
        pd.DataFrame: A matrix of user-genre average ratings.
    """
    tmp = pd.merge(watch_movies_df, movies_genres_df, 
                   on="movie_id", how='left').drop(['comment', 'watch_date', 'movie_id'], axis=1)

    return tmp.groupby(['username', 'genre_id']).agg('mean').fillna(0).reset_index()

def watch_user_movies_mat(watch_movies_df:pd.DataFrame):
    """
    Extracts the user-movie rating matrix from watch history.

    Args:
        watch_movies_df (pd.DataFrame): User watch history.

    Returns:
        pd.DataFrame: A DataFrame with username, movie_id, and rating.
    """
    return watch_movies_df[['username', 'movie_id', 'rating']]

def pref_user_mat(all_user_pref:pd.DataFrame, interest:str):
    """
    Extracts user preference matrix for a specific interest (actor or genre).

    Args:
        all_user_pref (pd.DataFrame): User preferences dataset.
        interest (str): The type of interest ('actor' or 'genre').

    Returns:
        pd.DataFrame: A DataFrame with username, interest_id, and interest_rating.
    """
    return all_user_pref[['username', f"{interest}_id", f"{interest}_rating"]].groupby(['username', f"{interest}_id"]).agg('mean')

def movies_not_yet_watched(username:str, movies_df:pd.DataFrame, watch_movies_df:pd.DataFrame):
    """
    Identifies movies that a specific user has not yet watched.

    Args:
        username (str): The username of the user.
        movies_df (pd.DataFrame): The complete movies dataset.
        watch_movies_df (pd.DataFrame): The complete watch history dataset.

    Returns:
        pd.DataFrame: A DataFrame of movies not watched by the user.
    """
    user_watched = watch_movies_df.loc[watch_movies_df['username']==username]
    not_watced_mask = ~np.isin(movies_df['id'], user_watched['movie_id'])
    return movies_df.loc[not_watced_mask]

def genre_not_yet_watched(movies_not_watched:pd.DataFrame, detail_genre_df:pd.DataFrame):
    """
    Maps unwatched movies to their associated genres.

    Args:
        movies_not_watched (pd.DataFrame): Dataset of movies not watched by the user.
        detail_genre_df (pd.DataFrame): Movie-genre associations.

    Returns:
        pd.DataFrame: A DataFrame with movie_id and genre_id for unwatched movies.
    """
    tmp = pd.merge(movies_not_watched.rename({"id":"movie_id"}, axis=1), 
                   detail_genre_df, how='left', on='movie_id')
    return tmp[['movie_id', 'genre_id']]