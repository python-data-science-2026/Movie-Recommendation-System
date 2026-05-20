"""
Main entry point for the Movie Recommendation System.

This module handles the user interface and orchestration of registration,
login, movie tracking, and preference management.
"""

from modules.utils import check_datasets, check_rating, validate_date, load_datasets
from modules.users import User
from modules.movies import Movies
from modules.watch_movies import Watch_Movie, user_history
from modules.recommendation import recommend_movies_by_genre_svd
from modules.processing import merge_genre_preferencies, merge_actor_preferencies
from modules.analysis import get_user_genre_trends, get_user_actor_trends, get_user_watch_activity, identify_discovery_genres


def register_flow():
    """
    Handles the user registration process.

    Collects user details from input and attempts to save a new User.

    Returns:
        User: The created User object if successful, None otherwise.
    """
    print("\n--- Register ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    lastname = input("Last name: ").strip()
    firstname = input("First name: ").strip()

    while True:
        date_of_birth = input("Date of birth (YYYY-MM-DD): ").strip()
        if validate_date(date_of_birth):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")

    user = User(username, password, lastname, firstname, date_of_birth)
    if user.save():
        print("User registered successfully.")
        return user
    else:
        print("Username already exists.")
        return None


def login_flow():
    """
    Handles the user login process.

    Collects credentials from input and attempts to authenticate the User.

    Returns:
        User: The authenticated User object if successful, None otherwise.
    """
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    user = User(username, password)
    if user.login():
        print(f"Welcome, {username}!")
        return user
    else:
        print("Invalid username or password.")
        return None


def add_movie_flow(username):
    """
    Handles the process of adding a movie that the user has watched.

    Collects movie details, rating, and watch date from input.

    Args:
        username (str): The username of the current user.
    """
    print("\n--- Add Watched Movie ---")
    title = input("Movie title: ").strip()
    
    while True:
        release_date = input("Release date (YYYY-MM-DD): ").strip()
        if validate_date(release_date):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")
        
    genres = input("Genres (comma separated): ").strip()
    actors = input("Actors (comma separated): ").strip()
    
    while True:
        watch_date = input("Watch date (YYYY-MM-DD): ").strip()
        if validate_date(watch_date):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        rating_input = input("Rating (1 to 5): ").strip()
        rating = check_rating(rating_input)
        if rating is not None:
            break
        print("Rating must be a number between 1 and 5.")

    comment = input("Comment (optional): ").strip()

    movie = Movies(title, release_date)
    movie.save()

    if genres:
        for genre in genres.split(","):
            movie.add_genre(genre)
    if actors:
        for actor in actors.split(","):
            movie.add_actor(actor)

    watch = Watch_Movie(username, movie.get_id(), watch_date, rating, comment)
    watch.save()

    print("Movie added successfully.")


def add_preferences_flow(user):
    """
    Handles the process of setting user preferences for genres and actors.

    Args:
        user (User): The current authenticated User object.
    """
    print("\n--- Set Preferences ---")
    genres = input("Favorite genres (comma separated): ").strip()
    genres_rating = input("Rate each genre between 1 and 5 (comma separated): ").strip()
    actors = input("Favorite actors (comma separated): ").strip()
    actors_rating = input("Rate each actor between 1 and 5 (comma separated): ").strip()
    if actors:
        actors_list = [a.strip() for a in actors.split(",") if a.strip()]
        actors_rating_list = [check_rating(r.strip()) for r in actors_rating.split(",")]
        for i, actor in enumerate(actors_list):
            rate = actors_rating_list[i] if i < len(actors_rating_list) and actors_rating_list[i] is not None else 5
            user.add_actors_preferencies(actor, rate)

    if genres:
        genres_list = [g.strip() for g in genres.split(",") if g.strip()]
        genres_rating_list = [check_rating(r.strip()) for r in genres_rating.split(",")]
        for i, genre in enumerate(genres_list):
            rate = genres_rating_list[i] if i < len(genres_rating_list) and genres_rating_list[i] is not None else 5
            user.add_genre_preferencies(genre, rate)

    print("Preferences saved successfully.")

def show_history_flow(username):
    """
    Displays the history of movies watched by the user.

    Args:
        username (str): The username of the current user.
    """
    print("\n--- Your Watched Movies ---")
    history = user_history(username)
    if history.empty:
        print("No movies watched yet.")
    else:
        print(history.to_string(index=False))


def show_preferences_flow(user):
    """
    Displays the current user's favorite genres and actors.

    Args:
        user (User): The current authenticated User object.
    """
    actors_df = load_datasets("actors.csv")
    genres_df = load_datasets("genres.csv")

    actors_user_pref = merge_actor_preferencies(actors_df, user.get_actors_preferencies())
    genres_user_pref = merge_genre_preferencies(genres_df, user.get_genre_preferencies())
    print("\n--- Your Preferences ---")
    print("Favourite genres:")
    print(genres_user_pref[['genre_name', 'genre_rating']].to_string(index=False))

    print("\nFavourite actors:")
    print(actors_user_pref[['actor_full_name','actor_rating', 'actor_date_of_birth']].to_string(index=False))


def get_recommendations_flow(username):
    """
    Generates and displays movie recommendations for the user.

    Args:
        username (str): The username of the current user.
    """
    print("\n--- Movie Recommendations ---")
    
    recommendations = recommend_movies_by_genre_svd(username, top_n=5)
    
    if recommendations.empty:
        print("Not enough data to provide personalized recommendations.")
        print("Please watch some movies or set your genre preferences!")
        return

    print("Based on your history and preferences, you might like:")
    print(recommendations[['title', 'release_date']].to_string(index=False))


def show_trends_flow(username):
    """
    Displays personal trends and discovery insights for the user.
    """
    print("\n--- Your Trends & Insights ---")
    
    genre_trends = get_user_genre_trends(username)
    if genre_trends.empty:
        print("Not enough data to analyze trends. Go watch some movies!")
        return

    print("\n[ Top Genres ]")
    print(genre_trends.head(5)[['name', 'watch_count', 'avg_rating']].to_string(index=False))

    activity = get_user_watch_activity(username)
    if not activity.empty:
        print("\n[ Watch Activity (Last 6 months) ]")
        print(activity.tail(6).to_string(index=False))

    discovery = identify_discovery_genres(username)
    if discovery:
        print("\n[ Discovery: New Genres to Explore ]")
        for g in discovery:
            print(f"- {g}")


def main():
    """
    The main control loop for the application.

    Initializes datasets and manages the top-level menu and user session.
    """
    check_datasets()
    current_user = None

    while current_user is None:
        print("\n=== Movie Recommendation System ===")
        print("1. Register")
        print("2. Login")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            current_user = register_flow()
        elif choice == "2":
            current_user = login_flow()
        elif choice == "0":
            print("Goodbye.")
            return
        else:
            print("Invalid option.")

    while True:
        print(f"\n=== Movie Recommendation System === [{current_user.username}]")
        print("1. Add watched movie")
        print("2. Set preferences")
        print("3. Show watched movies")
        print("4. Show preferences")
        print("5. Get recommendations")
        print("6. Show trends & insights")
        print("0. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_movie_flow(current_user.username)
        elif choice == "2":
            add_preferences_flow(current_user)
        elif choice == "3":
            show_history_flow(current_user.username)
        elif choice == "4":
            show_preferences_flow(current_user)
        elif choice == "5":
            get_recommendations_flow(current_user.username)
        elif choice == "6":
            show_trends_flow(current_user.username)
        elif choice == "0":
            print("Logged out.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
