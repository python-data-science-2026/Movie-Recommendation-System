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

def top_recommendation(items_list: list, pred_list: list, top: int = 10):
    sorted_idx = sorted(
        range(len(pred_list)),
        key=lambda k: pred_list[k],
        reverse=True
    )

    return [items_list[i] for i in sorted_idx[:top]]

def recommend_movies(username: str, top_n: int = 5):
    model = build_SVD_recommender(raiting_movies)

    all_movies = raiting_movies["movie_id"].unique()

    # bereits gesehene Filme
    seen_movies = raiting_movies[
        raiting_movies["username"] == username
    ]["movie_id"].tolist()

    # nur neue Filme
    candidate_movies = [m for m in all_movies if m not in seen_movies]

    preds = [predict_recommendation(model, username, movie) for movie in candidate_movies]

    top_ids = top_recommendation(candidate_movies, preds, top=top_n)

    return top_ids