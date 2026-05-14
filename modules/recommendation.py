"""
Movie recommendation engine.

This module uses the Surprise library to build an SVD-based recommendation model
and provide top movie recommendations for users.
"""

import pandas as pd
from surprise import SVD, Dataset, Reader

from .processing import watch_user_genres_mat, watch_user_movies_mat, movies_not_yet_watched, genre_not_yet_watched
from .utils import load_datasets

watch_movies_df =  load_datasets("watch_movies.csv")
movies_genre_df =  load_datasets("movies_genres.csv")

rating_genres = watch_user_genres_mat(watch_movies_df, movies_genre_df)
raiting_movies = watch_user_movies_mat(watch_movies_df)

def build_SVD_recommender(rating_data:pd.DataFrame):
    """
    Builds and trains an SVD recommendation model.

    Args:
        rating_data (pd.DataFrame): A DataFrame containing user-item ratings.

    Returns:
        SVD: A trained SVD model.
    """
    reader = Reader()
    data = Dataset.load_from_df(rating_data, reader)
    train_set = data.build_full_trainset()
    svd_model = SVD()
    svd_model.fit(train_set)
    return svd_model

def predict_recommendation(svd_model:SVD, username:str, item_id:int|str):
    """
    Predicts the rating for a specific user and item.

    Args:
        svd_model (SVD): The trained recommendation model.
        username (str): The user's unique identifier.
        item_id (int|str): The unique identifier of the item (movie or genre).

    Returns:
        float: The estimated rating.
    """
    return svd_model.predict(uid=username, iid=item_id).est

def top_recommendation(items_list:list, pred_list:list, top:int=10):
    """
    Selects the top-N recommended items based on predicted ratings.

    Args:
        items_list (list): List of item identifiers.
        pred_list (list): List of predicted ratings corresponding to the items.
        top (int, optional): Number of top recommendations to return. Defaults to 10.

    Returns:
        list: The top-N recommended item identifiers.
    """
    sorted_idx = sorted(range(len(pred_list)), key=lambda k: pred_list[k], reverse=True)
    
    return [items_list[i] for i in sorted_idx[:top]]

def recommend_movies_by_genre_svd(username: str, top_n: int = 10):
    """
    Recommends movies by combining SVD predictions with explicit user genre preferences.
    """

    movies_df = load_datasets("movies.csv")
    watch_movies_df = load_datasets("watch_movies.csv")
    movies_genres_df = load_datasets("movies_genres.csv")
    genres_df = load_datasets("genres.csv")
    user_genre_pref = load_datasets("user_genre.csv")

    if watch_movies_df.empty and user_genre_pref.empty:
        return pd.DataFrame()

    history_ratings = watch_user_genres_mat(watch_movies_df, movies_genres_df)
    explicit_ratings = user_genre_pref[['username', 'genre_id', 'rating']]
    
    combined_ratings = pd.concat([history_ratings, explicit_ratings]).groupby(['username', 'genre_id']).mean().reset_index()
    
    genre_model = build_SVD_recommender(combined_ratings)

    all_genre_ids = genres_df['id'].unique()
    genre_predictions = {gid: predict_recommendation(genre_model, username, gid) for gid in all_genre_ids}

    user_explicit = user_genre_pref[user_genre_pref['username'] == username]
    explicit_map = dict(zip(user_explicit['genre_id'], user_explicit['rating']))
    
    final_genre_scores = {}
    for gid in all_genre_ids:
        svd_score = genre_predictions.get(gid, 0)
        explicit_val = explicit_map.get(gid, svd_score)
        
        final_genre_scores[gid] = (0.8 * svd_score) + (0.2 * explicit_val)

    unwatched_movies = movies_not_yet_watched(username, movies_df, watch_movies_df)
    if unwatched_movies.empty: 
        return pd.DataFrame()
    
    unwatched_genres = genre_not_yet_watched(unwatched_movies, movies_genres_df)
    unwatched_genres['genre_score'] = unwatched_genres['genre_id'].map(final_genre_scores)
    
    movie_scores = unwatched_genres.groupby('movie_id')['genre_score'].mean().reset_index()

    recommendations = pd.merge(movie_scores, unwatched_movies, left_on='movie_id', right_on='id').drop('movie_id', axis=1)
    return recommendations.sort_values(by='genre_score', ascending=False).head(top_n)
