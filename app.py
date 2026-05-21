"""
Movie Recommendation System Application.

This module implements a Streamlit-based web application for a movie recommendation system.
It includes features for user authentication, preference management for genres and actors,
recording watched movies with ratings, and generating personalized recommendations 
using collaborative filtering (SVD).
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from modules.utils import check_datasets, load_datasets
from modules.users import User
from modules.movies import Movies
from modules.watch_movies import Watch_Movie
from modules.recommendation import build_SVD_recommender, predict_recommendation, top_recommendation, recommend_movies_by_genre_svd
from modules.processing import movies_not_yet_watched, merge_genre_preferencies, merge_actor_preferencies, merge_movies_details
from modules.analysis import get_user_genre_trends, get_user_actor_trends, get_user_watch_activity, identify_discovery_genres, get_global_genre_trends

st.set_page_config(page_title="MovieRec", page_icon="🎬", layout="wide")

check_datasets()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def auth_view():
    st.title("Movie Recommendation System")
    col1, col2 = st.columns(2)
    with col2:
        st.image("images/unibe_img.jpeg")
    with col1:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    user = User(u, p)
                    if user.login():
                        st.session_state.user = user
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab2:
            with st.form("register_form"):
                new_u = st.text_input("Username*")
                new_p = st.text_input("Password*", type="password")
                confirm_p = st.text_input("Confirm Password*", type="password")
                fn = st.text_input("First Name")
                ln = st.text_input("Last Name")
                dob = st.date_input("Date of Birth", min_value=datetime(1920, 1, 1), max_value=datetime.now())
                if st.form_submit_button("Register", use_container_width=True):
                    if new_u and new_p and confirm_p:
                        if new_p == confirm_p:
                            user = User(new_u, new_p, ln, fn, dob.strftime('%Y-%m-%d'))
                            if user.save():
                                st.success("Account created! Please login.")
                            else:
                                st.error("Username already exists.")
                        else:
                            st.error("Passwords do not match.")
                    else:
                        st.error("Username, Password and Confirmation are required.")


def get_classic_recommendations(username, watch_data, unwatched_movies, num_recs):
    model = build_SVD_recommender(watch_data)
    movie_ids = unwatched_movies['id'].tolist()
    preds = [predict_recommendation(model, username, mid) for mid in movie_ids]
    top_ids = top_recommendation(movie_ids, preds, top=num_recs)
    return unwatched_movies[unwatched_movies['id'].isin(top_ids)]

def get_genre_discovery_recommendations(username, num_recs):
    return recommend_movies_by_genre_svd(username, top_n=num_recs)

def user_account_view():
    user = st.session_state.user
    st.title(f"Welcome {user.username}")
    
    genres_list = load_datasets("genres.csv")['name'].tolist()
    actors_list = load_datasets("actors.csv")['full_name'].tolist()
    
    tab_pref, tab_watch, tab_hist, tab_rec, tab_trends = st.tabs(["Preferences", "Add Watched Movie", "Watch History", "Recommendations", "Insights & Trends"])
    
    with tab_pref:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Add Preferences")
            p_type = st.radio("Type", ["Genre", "Actor"], horizontal=True)
            
            options = genres_list if p_type == "Genre" else actors_list
            selected_items = st.multiselect(f"Select {p_type}s", options=options)
            extra_items = st.text_input(f"Can't find a {p_type}? Type name(s) here (comma separated):")
            p_rate = st.slider("Preference Strength", 1, 5, 5)
            
            if st.button("Save Preferences"):
                all_items = selected_items.copy()
                if extra_items:
                    new_ones = [x.strip() for x in extra_items.split(',') if x.strip()]
                    all_items.extend(new_ones)

                if all_items:
                    for item in all_items:
                        if p_type == "Genre":
                            user.add_genre_preferencies(item, p_rate)
                        else:
                            user.add_actors_preferencies(item, p_rate)
                    st.success("Preferences updated!")
                    st.rerun()
                else:
                    st.warning("Please select at least one item.")
        
        with col2:
            st.subheader("Edit/View My Preferences")
            
            u_genres = load_datasets("user_genre.csv")
            u_genres = u_genres[u_genres['username'] == user.username].drop_duplicates(subset=['genre_id'])
            
            u_actors = load_datasets("user_actors.csv")
            u_actors = u_actors[u_actors['username'] == user.username].drop_duplicates(subset=['actor_id'])

            if not u_genres.empty:
                with st.expander("**My Genres**"):
                    merged_g = merge_genre_preferencies(load_datasets("genres.csv"), u_genres)
                    for _, row in merged_g.iterrows():
                        new_val = st.slider(row['genre_name'], 1, 5, int(row['genre_rating']), key=f"edit_g_{row['genre_id']}")
                        if new_val != row['genre_rating']:
                            user.add_genre_preferencies(row['genre_name'], new_val)
                            st.rerun()

            if not u_actors.empty:
                with st.expander("**My Actors**"):
                    merged_a = merge_actor_preferencies(load_datasets("actors.csv"), u_actors)
                    for _, row in merged_a.iterrows():
                        new_val = st.slider(row['actor_full_name'], 1, 5, int(row['actor_rating']), key=f"edit_a_{row['actor_id']}")
                        if new_val != row['actor_rating']:
                            user.add_actors_preferencies(row['actor_full_name'], new_val)
                            st.rerun()

    with tab_watch:
        st.subheader("Record a Watch")
        
        movies_df = load_datasets("movies.csv")
        
        st.info("Search for an existing movie to pre-fill its details, or just type a new one below.")
        search_title = st.selectbox("Search for a movie in our database", 
                                    options=[""] + sorted(movies_df['title'].unique().tolist()),
                                    index=0,
                                    placeholder="Start typing...")
        
        default_rel_date = datetime.now()
        default_genres = []
        default_actors = []
        
        if search_title:
            m_info = movies_df[movies_df['title'] == search_title].iloc[0]
            try:
                default_rel_date = datetime.strptime(m_info['release_date'], '%Y-%m-%d')
            except: pass
            
            m_genres_df = load_datasets("movies_genres.csv")
            m_actors_df = load_datasets("movies_actors.csv")
            
            mid = m_info['id']
            genres_lookup = load_datasets("genres.csv")
            g_ids = m_genres_df[m_genres_df['movie_id'] == mid]['genre_id'].tolist()
            default_genres = genres_lookup[genres_lookup['id'].isin(g_ids)]['name'].tolist()
            
            actors_lookup = load_datasets("actors.csv")
            a_ids = m_actors_df[m_actors_df['movie_id'] == mid]['actor_id'].tolist()
            default_actors = actors_lookup[actors_lookup['id'].isin(a_ids)]['full_name'].tolist()

        with st.form("add_watch"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Movie Title", value=search_title if search_title else "")
                rel_date = st.date_input("Release Date", min_value=datetime(1920, 1, 1), value=default_rel_date, max_value=datetime.now())
                watch_date = st.date_input("Watch Date", min_value=datetime(1920, 1, 1), value=datetime.now(), max_value=datetime.now())
            with col_b:
                rating = st.select_slider("My Rating", options=[1, 2, 3, 4, 5], value=3)
                sel_genres = st.multiselect("Genres", options=genres_list, default=default_genres)
                sel_actors = st.multiselect("Actors", options=actors_list, default=default_actors)
                extra_actors = st.text_input("Other Actors (comma separated)")
            
            comment = st.text_area("Comment")
            
            if st.form_submit_button("Save Movie History"):
                if title:
                    movie = Movies(title, rel_date.strftime('%Y-%m-%d'))
                    movie.save()
                    for g in sel_genres: movie.add_genre(g)
                    for a in sel_actors: movie.add_actor(a)
                    
                    if extra_actors:
                        for a in [x.strip() for x in extra_actors.split(',') if x.strip()]:
                            movie.add_actor(a)
                    
                    wm = Watch_Movie(user.username, movie.get_id(), watch_date.strftime('%Y-%m-%d'), rating, comment)
                    wm.save()
                    st.success(f"'{title}' added to history!")
                else:
                    st.error("Title is required.")

    with tab_hist:
        st.subheader("My Watch History")
        
        watch_df = load_datasets("watch_movies.csv")
        user_watch = watch_df[watch_df['username'] == user.username]
        
        if user_watch.empty:
            st.info("You haven't recorded any movies yet.")
        else:
            movies_df = load_datasets("movies.csv")
            actors_df = load_datasets("actors.csv")
            genres_df = load_datasets("genres.csv")
            m_actors_df = load_datasets("movies_actors.csv")
            m_genres_df = load_datasets("movies_genres.csv")
            
            base_details = merge_movies_details(movies_df, actors_df, genres_df, m_actors_df, m_genres_df)
            user_watch_with_info = pd.merge(user_watch, movies_df, left_on='movie_id', right_on='id')
            full_history = pd.merge(user_watch_with_info, base_details, on=['title', 'release_date'])
            
            with st.expander("Search My History", expanded=False):
                h_col1, h_col2, h_col3 = st.columns(3)
                with h_col1:
                    h_q_title = st.text_input("Search by title...", key="hist_search_title")
                with h_col2:
                    h_q_genres = st.multiselect("Filter by Genre", options=sorted(genres_df['name'].unique().tolist()), key="hist_search_genre")
                with h_col3:
                    h_valid_dates = pd.to_datetime(full_history['watch_date'], errors='coerce')
                    h_years = h_valid_dates.dt.year.dropna().unique().astype(int)
                    if len(h_years) > 0:
                        h_min_y, h_max_y = int(min(h_years)), int(max(h_years))
                        if h_min_y == h_max_y:
                            st.write(f"Watch Year: {h_min_y}")
                            h_q_years = (h_min_y, h_max_y)
                        else:
                            h_q_years = st.slider("Watch Year Range", h_min_y, h_max_y, (h_min_y, h_max_y), key="hist_search_year")
                    else:
                        h_q_years = None

            filtered_history = full_history.copy()
            if h_q_title:
                filtered_history = filtered_history[filtered_history['title'].str.contains(h_q_title, case=False, na=False)]
            if h_q_genres:
                filtered_history = filtered_history[filtered_history['genres'].apply(
                    lambda x: any(g in x for g in h_q_genres) if isinstance(x, list) else False
                )]
            if h_q_years:
                h_v_dates = pd.to_datetime(filtered_history['watch_date'], errors='coerce')
                filtered_history = filtered_history[(h_v_dates.dt.year >= h_q_years[0]) & (h_v_dates.dt.year <= h_q_years[1])]

            display_hist = filtered_history.copy()
            display_hist['genres'] = display_hist['genres'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
            display_hist['actors'] = display_hist['actors'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
            
            st.dataframe(
                display_hist.sort_values('watch_date', ascending=False)[['title', 'watch_date', 'rating', 'genres', 'actors', 'comment']].rename(columns={
                    'title': 'Movie Title',
                    'watch_date': 'Watched On',
                    'rating': 'My Rating',
                    'genres': 'Genres',
                    'actors': 'Actors',
                    'comment': 'Comment'
                }),
                use_container_width=True,
                hide_index=True
            )

    with tab_rec:
        st.subheader("Recommended for you")
        movies_df = load_datasets("movies.csv")
        watch_df = load_datasets("watch_movies.csv")
        
        user_watches = watch_df[watch_df['username'] == user.username]
        if len(user_watches) < 1:
            st.info("Start watching and rating movies to see recommendations here!")
        else:
            rec_strategy = st.radio("Recommendation Strategy", 
                                    ["Match My Preferences", "Discover Something New"], 
                                    horizontal=True,
                                    help="Classic uses direct movie ratings. Genre Discovery predicts your interest in genres to find new types of movies.")
            
            unwatched = movies_not_yet_watched(user.username, movies_df, watch_df)
            if unwatched.empty:
                st.write("You've seen everything in our catalog!")
            else:
                num_recs = st.slider("Number of recommendations to display", 1, 20, 5)
                with st.spinner("Calculating best matches..."):
                    if rec_strategy == "Discover Something New":
                        recs = get_classic_recommendations(
                             user.username, 
                             watch_df[['username', 'movie_id', 'rating']], 
                             unwatched, 
                             num_recs
                         )
                    else:
                        recs = get_genre_discovery_recommendations(user.username, num_recs)
                    
                    actors_df = load_datasets("actors.csv")
                    genres_df = load_datasets("genres.csv")
                    m_actors_df = load_datasets("movies_actors.csv")
                    m_genres_df = load_datasets("movies_genres.csv")
                    
                    if not recs.empty:
                        enriched_recs = merge_movies_details(recs, actors_df, genres_df, m_actors_df, m_genres_df)
                        
                        display_recs = enriched_recs.copy()
                        display_recs['genres'] = display_recs['genres'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
                        display_recs['actors'] = display_recs['actors'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
                        
                        st.dataframe(
                            display_recs[['title', 'release_date', 'genres', 'actors']].rename(columns={
                                'title': 'Title',
                                'release_date': 'Released',
                                'genres': 'Genres',
                                'actors': 'Actors'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("No recommendations found for this strategy.")

    with tab_trends:
        st.header("Personal & Community Insights")
        
        genre_trends = get_user_genre_trends(user.username)
        actor_trends = get_user_actor_trends(user.username)
        watch_activity = get_user_watch_activity(user.username)
        discovery_genres = identify_discovery_genres(user.username)
        global_genre_trends = get_global_genre_trends()

        if genre_trends.empty:
            st.info("Watch more movies to see your trends and insights!")
        else:
            m1, m2, m3 = st.columns(3)
            with m1:
                total_watched = int(len(full_history))
                st.metric("My Total Movies Watched", total_watched)
            with m2:
                top_genre = genre_trends.iloc[0]['name']
                st.metric("My Favorite Genre", top_genre)
            with m3:
                avg_user_rating = genre_trends['avg_rating'].mean()
                st.metric("My Avg Rating", f"{avg_user_rating:.1f}")

            st.divider()

            val = st.selectbox("View by", options=['Avg rating', 'Total watches'])
            col1, col2 = st.columns(2, gap="large")
            dict1 = {"Avg rating":"avg_rating","Total watches":"total_watches"}
            dict2 = {"Avg rating":"avg_rating","Total watches":"watch_count"}
            dict3 = {"Total watches":"watch_count", "Avg rating":"avg_rating"}
            colors = {"Avg rating":"blue","Total watches":"green"}
            with col1:
                with st.container():
                    st.subheader("My Top Genres")
                    st.bar_chart(genre_trends.set_index('name')[dict2[val]], height=300, color=colors[val])
                
                st.divider()
                
                with st.container():
                    st.subheader("Watch Activity")
                    if not watch_activity.empty:
                        st.line_chart(watch_activity.set_index('month_year')[dict3[val]], height=250, color=colors[val])
                    else:
                        st.write("No activity data available yet.")

            with col2:
                with st.container():
                    st.subheader("Community Trends")
                    if not global_genre_trends.empty:
                        community_top = global_genre_trends[global_genre_trends['total_watches'] >= 1].sort_values(dict1[val], ascending=False).head(10)
                        st.bar_chart(community_top.set_index('name')[dict1[val]], height=300, color=colors[val])
                    else:
                        st.write("Not enough community data yet.")
                
                st.divider()
                
                with st.container():
                    st.subheader("My Favorite Actors")
                    if not actor_trends.empty:
                        st.dataframe(
                            actor_trends.head(5)[['full_name', 'watch_count', 'avg_rating']].rename(columns={
                                'full_name': 'Actor',
                                'watch_count': 'Watches',
                                'avg_rating': 'Avg Rating'
                            }), 
                            hide_index=True, 
                            use_container_width=True
                        )
                    else:
                        st.write("No actor preferences recorded.")

            st.divider()
            
            # Discovery Section
            with st.container():
                st.subheader("Discovery: Expand Your Horizons")
                if discovery_genres:
                    st.write("Based on your preferences, you might enjoy exploring these genres you haven't watched much:")
                    
                    disc_cols = st.columns(len(discovery_genres))
                    for i, genre in enumerate(discovery_genres):
                        with disc_cols[i]:
                            st.info(f"**{genre}**")
                    
                    if st.button("Find movies in these genres", use_container_width=True):
                        st.session_state.discovery_genre_filter = discovery_genres
                        st.toast("Filters applied! Go to 'Search Movies' to see results.")
                else:
                    st.write("Keep rating genres in 'Preferences' to unlock discovery insights.")

def search_movies_view():
    st.title("Explore Movies")

    movies_df = load_datasets("movies.csv")
    watch_df = load_datasets("watch_movies.csv")
    actors_df = load_datasets("actors.csv")
    genres_df = load_datasets("genres.csv")
    m_actors_df = load_datasets("movies_actors.csv")
    m_genres_df = load_datasets("movies_genres.csv")

    base_df = merge_movies_details(movies_df, actors_df, genres_df, m_actors_df, m_genres_df)

    if not watch_df.empty:
        stats = watch_df.groupby('movie_id').agg(
            watch_count=('movie_id', 'count'),
            mean_rating=('rating', 'mean')
        ).reset_index()
        stats_with_info = pd.merge(stats, movies_df[['id', 'title', 'release_date']], left_on='movie_id', right_on='id')
        results = pd.merge(base_df, stats_with_info[['title', 'release_date', 'watch_count', 'mean_rating']], 
                           on=['title', 'release_date'], how='left').fillna(0)
    else:
        results = base_df.copy()
        results['watch_count'] = 0
        results['mean_rating'] = 0.0

    with st.expander("Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            q_title = st.text_input("Search by title...", placeholder="e.g. Inception")
        with col2:
            default_g = st.session_state.get('discovery_genre_filter', [])
            q_genres = st.multiselect("Filter by Genre", 
                                      options=sorted(genres_df['name'].unique().tolist()),
                                      default=default_g)
            # Clear it after use so it doesn't persist forever
            if 'discovery_genre_filter' in st.session_state:
                del st.session_state['discovery_genre_filter']
        with col3:
            valid_dates = pd.to_datetime(results['release_date'], errors='coerce')
            years = valid_dates.dt.year.dropna().unique().astype(int)
            if len(years) > 0:
                min_y, max_y = int(min(years)), int(max(years))
                if min_y == max_y:
                    st.write(f"Year: {min_y}")
                    q_years = (min_y, max_y)
                else:
                    q_years = st.slider("Year Range", min_y, max_y, (min_y, max_y))
            else:
                q_years = None

    filtered_results = results.copy()
    if q_title:
        filtered_results = filtered_results[filtered_results['title'].str.contains(q_title, case=False, na=False)]
    if q_genres:
        filtered_results = filtered_results[filtered_results['genres'].apply(
            lambda x: any(g in x for g in q_genres) if isinstance(x, list) else False
        )]
    if q_years:
        v_dates = pd.to_datetime(filtered_results['release_date'], errors='coerce')
        filtered_results = filtered_results[(v_dates.dt.year >= q_years[0]) & (v_dates.dt.year <= q_years[1])]

    display_df = filtered_results.copy()
    display_df['genres'] = display_df['genres'].apply(lambda x: ", ".join([str(i) for i in x if pd.notna(i)]) if isinstance(x, list) else "")
    display_df['actors'] = display_df['actors'].apply(lambda x: ", ".join([str(i) for i in x if pd.notna(i)]) if isinstance(x, list) else "")

    st.dataframe(
        display_df[['title', 'release_date', 'genres', 'actors', 'watch_count', 'mean_rating']].rename(columns={
            'title': 'Title',
            'release_date': 'Released',
            'genres': 'Genres',
            'actors': 'Actors',
            'watch_count': 'Total Watches',
            'mean_rating': 'Avg Rating'
        }),
        use_container_width=True,
        hide_index=True
    )

if not st.session_state.logged_in:
    auth_view()
else:
    st.sidebar.title("MovieRec")
    st.sidebar.write(f"Logged in: **{st.session_state.user.username}**")
    
    nav = st.sidebar.radio("Go to", ["User Account", "Search Movies"])
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.logged_in = False
        st.rerun()
        
    if nav == "User Account":
        user_account_view()
    else:
        search_movies_view()
