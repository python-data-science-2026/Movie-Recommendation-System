import pandas as pd
from surprise import SVD, Dataset, Reader

from .processing import watch_user_genres_mat, watch_user_movies_mat
from .utils import load_datasets

watch_movies_df =  load_datasets("watch_movies.csv")
movies_genre_df =  load_datasets("movies_genres.csv")

rating_genres = watch_user_genres_mat(watch_movies_df, movies_genre_df)
raiting_movies = watch_user_movies_mat(watch_movies_df)

def build_SVD_recommender(rating_data:pd.DataFrame):
    reader = Reader()
    data = Dataset.load_from_df(rating_data, reader)
    train_set = data.build_full_trainset()
    svd_model = SVD()
    svd_model.fit(train_set)
    return svd_model

def predict_recommendation(svd_model:SVD, username:str, item_id:int|str):
    return svd_model.predict(uid=username, iid=item_id).est

def top_recommendation(items_list:list, pred_list:list, top:int=10):
    sorted_idx = sorted(range(len(pred_list)), key=lambda k: pred_list[k])
    return items_list[sorted_idx[:top]]
