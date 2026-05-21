"""
User preference analysis and discovery module.

This module provides functions to analyze trends in user movie preferences 
based on their watch history and explicit preferences.
"""

import pandas as pd
import numpy as np
from .utils import load_datasets

def get_user_genre_trends(username: str):
    """
    Analyzes the genres most watched and highest rated by a user.
    """
    watch_df = load_datasets("watch_movies.csv")
    movies_genres_df = load_datasets("movies_genres.csv")
    genres_df = load_datasets("genres.csv")
    
    user_watch = watch_df[watch_df['username'] == username]
    if user_watch.empty:
        return pd.DataFrame()
        
    merged = pd.merge(user_watch, movies_genres_df, on="movie_id")
    merged = pd.merge(merged, genres_df, left_on="genre_id", right_on="id")
    
    genre_stats = merged.groupby('name').agg(
        watch_count=('movie_id', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    
    return genre_stats.sort_values(by='watch_count', ascending=False)

def get_user_actor_trends(username: str):
    """
    Analyzes the actors most watched and highest rated by a user.
    """
    watch_df = load_datasets("watch_movies.csv")
    movies_actors_df = load_datasets("movies_actors.csv")
    actors_df = load_datasets("actors.csv")
    
    user_watch = watch_df[watch_df['username'] == username]
    if user_watch.empty:
        return pd.DataFrame()
        
    merged = pd.merge(user_watch, movies_actors_df, on="movie_id")
    merged = pd.merge(merged, actors_df, left_on="actor_id", right_on="id")
    
    actor_stats = merged.groupby('full_name').agg(
        watch_count=('movie_id', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    
    return actor_stats.sort_values(by='watch_count', ascending=False)

def get_user_watch_activity(username: str):
    """
    Analyzes user watch activity over time.
    """
    watch_df = load_datasets("watch_movies.csv")
    user_watch = watch_df[watch_df['username'] == username].copy()
    if user_watch.empty:
        return pd.DataFrame()
        
    user_watch['watch_date'] = pd.to_datetime(user_watch['watch_date'])
    user_watch['month_year'] = user_watch['watch_date'].dt.to_period('M').astype(str)
    
    activity = user_watch.groupby('month_year').agg(
        watch_count=('movie_id', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    return activity.sort_values('month_year')

def identify_discovery_genres(username: str, top_n: int = 3):
    """
    Identifies genres that align with user interests but are under-explored in their watch history.
    """
    user_genre_pref = load_datasets("user_genre.csv")
    watch_df = load_datasets("watch_movies.csv")
    movies_genres_df = load_datasets("movies_genres.csv")
    genres_df = load_datasets("genres.csv")

    user_prefs = user_genre_pref[user_genre_pref['username'] == username]
    user_watch = watch_df[watch_df['username'] == username]

    if user_prefs.empty and user_watch.empty:
        return []

    # Genres explicitly liked but not watched much
    watched_genres_count = pd.merge(user_watch, movies_genres_df, on="movie_id")['genre_id'].value_counts()
    
    # Discovery score: high preference rating but low watch count
    discovery_candidates = []
    for _, row in user_prefs.iterrows():
        gid = row['genre_id']
        pref_rating = row['rating']
        watch_count = watched_genres_count.get(gid, 0)
        
        # Simple discovery score
        score = pref_rating / (watch_count + 1)
        discovery_candidates.append({'genre_id': gid, 'score': score})
    
    discovery_df = pd.DataFrame(discovery_candidates)
    if discovery_df.empty:
        return []
        
    discovery_df = discovery_df.sort_values(by='score', ascending=False).head(top_n)
    
    genre_names = pd.merge(discovery_df, genres_df, left_on='genre_id', right_on='id')['name'].tolist()
    return genre_names

def get_global_genre_trends():
    """
    Analyzes the genres most watched and highest rated across all users.
    """
    watch_df = load_datasets("watch_movies.csv")
    movies_genres_df = load_datasets("movies_genres.csv")
    genres_df = load_datasets("genres.csv")
    
    if watch_df.empty:
        return pd.DataFrame()
        
    merged = pd.merge(watch_df, movies_genres_df, on="movie_id")
    merged = pd.merge(merged, genres_df, left_on="genre_id", right_on="id")
    
    genre_stats = merged.groupby('name').agg(
        total_watches=('movie_id', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    
    return genre_stats.sort_values(by='avg_rating', ascending=False)
