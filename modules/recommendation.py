"""
Movie recommendation engine.

This module uses the Surprise library to build an SVD-based recommendation model
and provide top movie recommendations for users.
"""

import pandas as pd
from surprise import SVD, Dataset, Reader

from .processing import watch_user_genres_mat, watch_user_movies_mat
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
    # Sort indices by predicted ratings in descending order
    sorted_idx = sorted(range(len(pred_list)), key=lambda k: pred_list[k], reverse=True)
    
    # Select the top N items using the sorted indices
    return [items_list[i] for i in sorted_idx[:top]]
