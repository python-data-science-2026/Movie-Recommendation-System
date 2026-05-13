import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from modules.utils import check_datasets, load_datasets
from modules.users import User
from modules.movies import Movies
from modules.watch_movies import Watch_Movie, user_history
from modules.recommendation import build_SVD_recommender, predict_recommendation, top_recommendation
from modules.processing import movies_not_yet_watched, merge_genre_preferencies, merge_actor_preferencies, merge_movies_details


# --- Configuration ---
st.set_page_config(page_title="MovieRec", page_icon="🎬", layout="wide")

# --- Initialization ---
check_datasets()

# --- Session State ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- View: Auth ---
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
                fn = st.text_input("First Name")
                ln = st.text_input("Last Name")
                dob = st.date_input("Date of Birth", min_value=datetime(1920, 1, 1), max_value=datetime.now())
                if st.form_submit_button("Register", use_container_width=True):
                    if new_u and new_p:
                        user = User(new_u, new_p, ln, fn, dob.strftime('%Y-%m-%d'))
                        if user.save():
                            st.success("Account created! Please login.")
                        else:
                            st.error("Username already exists.")
                    else:
                        st.error("Username and Password are required.")

# --- View: User Account ---
def user_account_view():
    user = st.session_state.user
    st.title(f"My Account: {user.username}")
    
    # Load available options for multiselect
    genres_list = load_datasets("genres.csv")['name'].tolist()
    actors_list = load_datasets("actors.csv")['full_name'].tolist()
    
    tab_pref, tab_watch, tab_rec = st.tabs(["Preferences", "Add Watched Movie", "Recommendations"])
    
    # 1. Preferences
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
            
            # Use updated User methods that handle overwriting
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

    # 2. Add Watched Movie
    with tab_watch:
        st.subheader("Record a Watch")
        with st.form("add_watch"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Movie Title")
                rel_date = st.date_input("Release Date")
                watch_date = st.date_input("Watch Date", value=datetime.now())
            with col_b:
                rating = st.select_slider("My Rating", options=[1, 2, 3, 4, 5], value=3)
                # For adding a movie, we might want to allow choosing from existing OR adding new.
                # Here we use multiselect for existing, but could also add a text field for "Other".
                sel_genres = st.multiselect("Genres", options=genres_list)
                sel_actors = st.multiselect("Actors", options=actors_list)
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

    # 3. Recommendations
    with tab_rec:
        st.subheader("Personalized Recommendations")
        movies_df = load_datasets("movies.csv")
        watch_df = load_datasets("watch_movies.csv")
        
        user_watches = watch_df[watch_df['username'] == user.username]
        if len(user_watches) < 1:
            st.info("Start watching and rating movies to see recommendations here!")
        else:
            unwatched = movies_not_yet_watched(user.username, movies_df, watch_df)
            if unwatched.empty:
                st.write("You've seen everything in our catalog!")
            else:
                with st.spinner("Calculating best matches..."):
                    model = build_SVD_recommender(watch_df[['username', 'movie_id', 'rating']])
                    movie_ids = unwatched['id'].tolist()
                    preds = [predict_recommendation(model, user.username, mid) for mid in movie_ids]
                    top_ids = top_recommendation(movie_ids, preds, top=5)
                    recs = unwatched[unwatched['id'].isin(top_ids)]
                    st.dataframe(recs[['title', 'release_date']], use_container_width=True, hide_index=True)

# --- View: Search Movies ---
def search_movies_view():
    st.title("Explore Movies")

    # Load all necessary datasets
    movies_df = load_datasets("movies.csv")
    watch_df = load_datasets("watch_movies.csv")
    actors_df = load_datasets("actors.csv")
    genres_df = load_datasets("genres.csv")
    m_actors_df = load_datasets("movies_actors.csv")
    m_genres_df = load_datasets("movies_genres.csv")

    # Use the pre-built function for base data
    base_df = merge_movies_details(movies_df, actors_df, genres_df, m_actors_df, m_genres_df)

    # Calculate watch and rating stats
    if not watch_df.empty:
        stats = watch_df.groupby('movie_id').agg(
            watch_count=('movie_id', 'count'),
            mean_rating=('rating', 'mean')
        ).reset_index()
        # Need to map movie_id back to title/release_date for merging with base_df
        stats_with_info = pd.merge(stats, movies_df[['id', 'title', 'release_date']], left_on='movie_id', right_on='id')
        results = pd.merge(base_df, stats_with_info[['title', 'release_date', 'watch_count', 'mean_rating']], 
                           on=['title', 'release_date'], how='left').fillna(0)
    else:
        results = base_df.copy()
        results['watch_count'] = 0
        results['mean_rating'] = 0.0

    # UI Filters
    with st.expander("Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            q_title = st.text_input("Search by title...", placeholder="e.g. Inception")
        with col2:
            q_genres = st.multiselect("Filter by Genre", options=sorted(genres_df['name'].unique().tolist()))
        with col3:
            # Handle empty/invalid release_date safely
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

    # Apply filters
    filtered_results = results.copy()
    if q_title:
        filtered_results = filtered_results[filtered_results['title'].str.contains(q_title, case=False, na=False)]
    if q_genres:
        # Check if movie has any of the selected genres
        filtered_results = filtered_results[filtered_results['genres'].apply(
            lambda x: any(g in x for g in q_genres) if isinstance(x, list) else False
        )]
    if q_years:
        v_dates = pd.to_datetime(filtered_results['release_date'], errors='coerce')
        filtered_results = filtered_results[(v_dates.dt.year >= q_years[0]) & (v_dates.dt.year <= q_years[1])]

    # Formatting lists for display
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

# --- App Controller ---
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
