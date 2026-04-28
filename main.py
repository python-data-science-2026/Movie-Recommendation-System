from utils import check_datasets
from modules.users import User
from modules.movies import Movies
from modules.watch_movies import Watch_Movie, user_history


def register_flow():
    print("\n--- Register ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    lastname = input("Last name: ").strip()
    firstname = input("First name: ").strip()
    date_of_birth = input("Date of birth (YYYY-MM-DD): ").strip()

    user = User(username, password, lastname, firstname, date_of_birth)
    if user.save():
        print("User registered successfully.")
        return user
    else:
        print("Username already exists.")
        return None


def login_flow():
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
    print("\n--- Add Watched Movie ---")
    title = input("Movie title: ").strip()
    release_date = input("Release date (YYYY-MM-DD): ").strip()
    genre = input("Genre: ").strip()
    actor = input("Actor: ").strip()
    watch_date = input("Watch date (YYYY-MM-DD): ").strip()

    try:
        rating = float(input("Rating (1 to 5): ").strip())
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
    except ValueError:
        print("Invalid rating.")
        return

    comment = input("Comment (optional): ").strip()

    movie = Movies(title, release_date)
    movie.save()

    if genre:
        movie.add_genre(genre)
    if actor:
        movie.add_actor(actor)

    watch = Watch_Movie(username, movie.get_id(), watch_date, rating, comment)
    watch.save()

    print("Movie added successfully.")


def add_preferences_flow(user):
    print("\n--- Set Preferences ---")
    genres = input("Favorite genres (comma separated): ").strip()
    actors = input("Favorite actors (comma separated): ").strip()

    for genre in [g.strip() for g in genres.split(",") if g.strip()]:
        user.add_genre_preferencies(genre)

    for actor in [a.strip() for a in actors.split(",") if a.strip()]:
        user.add_actors_preferencies(actor)

    print("Preferences saved successfully.")


def show_history_flow(username):
    print("\n--- Your Watched Movies ---")
    history = user_history(username)
    if history.empty:
        print("No movies watched yet.")
    else:
        print(history.to_string(index=False))


def show_preferences_flow(user):
    print("\n--- Your Preferences ---")
    print("Favourite genres:")
    print(user.get_genre_preferencies().to_string(index=False))
    print("\nFavourite actors:")
    print(user.get_actors_preferencies().to_string(index=False))


def main():
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
        elif choice == "0":
            print("Logged out.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()