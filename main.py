from pathlib import Path

from movie import Movie
from preferences import Preferences
from movie_service import MovieService

DEFAULT_MOVIES_CSV_PATH = Path(__file__).parent / "data" / "movies.csv"


def clean_comma_input(text):
    return [item.strip() for item in text.split(",") if item.strip()]


def add_movie_flow(movie_service):
    print("\n--- Add Watched Movie ---")

    title = input("Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    try:
        year = int(input("Year: ").strip())
    except ValueError:
        print("Invalid year.")
        return

    genre = input("Genre: ").strip()
    if not genre:
        print("Genre cannot be empty.")
        return

    try:
        rating = float(input("Rating (1 to 5): ").strip())
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
    except ValueError:
        print("Invalid rating.")
        return

    actor = input("Actor (optional): ").strip()
    director = input("Director (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    movie = Movie(title, year, genre, rating, actor, director, notes)
    movie_service.add_movie(movie)

    print("Movie added successfully.")


def import_csv_flow(movie_service):
    print("\n--- Import Watched Movies from CSV ---")
    print(f"Default file: {DEFAULT_MOVIES_CSV_PATH}")

    if not DEFAULT_MOVIES_CSV_PATH.exists():
        print("Default CSV file not found.")
        print("Create the file in: data/movies.csv")
        return

    try:
        imported_count = movie_service.import_movies_from_csv(DEFAULT_MOVIES_CSV_PATH)
        print(f"{imported_count} movies imported successfully.")
    except ValueError as error:
        print(f"CSV error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")


def set_preferences_flow(preferences):
    print("\n--- Set User Preferences ---")

    genres = input("Favorite genres (comma separated): ").strip()
    actors = input("Favorite actors (comma separated): ").strip()
    directors = input("Favorite directors (comma separated): ").strip()

    preferences.set_genres(clean_comma_input(genres))
    preferences.set_actors(clean_comma_input(actors))
    preferences.set_directors(clean_comma_input(directors))

    print("Preferences saved successfully.")


def show_movies_flow(movie_service):
    print("\n--- Watched Movies ---")

    movies = movie_service.get_all_movies()
    if not movies:
        print("No movies added yet.")
        return

    for index, movie in enumerate(movies, start=1):
        print(f"{index}. {movie}")
        if movie.actor:
            print(f"   Actor: {movie.actor}")
        if movie.director:
            print(f"   Director: {movie.director}")
        if movie.notes:
            print(f"   Notes: {movie.notes}")


def show_preferences_flow(preferences):
    print("\n--- User Preferences ---")
    print(preferences)


def show_summary_flow(movie_service):
    print("\n--- Summary ---")
    print(f"Total watched movies: {movie_service.get_total_movies()}")
    print(f"Average rating: {movie_service.get_average_rating():.2f}")

    top_genre = movie_service.get_top_genre()
    if top_genre:
        print(f"Most watched genre: {top_genre}")
    else:
        print("Most watched genre: None")


def main():
    movie_service = MovieService()
    preferences = Preferences()

    while True:
        print("\n=== Movie Recommendation System ===")
        print("1. Add watched movie")
        print("2. Import watched movies from CSV")
        print("3. Set preferences")
        print("4. Show watched movies")
        print("5. Show preferences")
        print("6. Show summary")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_movie_flow(movie_service)
        elif choice == "2":
            import_csv_flow(movie_service)
        elif choice == "3":
            set_preferences_flow(preferences)
        elif choice == "4":
            show_movies_flow(movie_service)
        elif choice == "5":
            show_preferences_flow(preferences)
        elif choice == "6":
            show_summary_flow(movie_service)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()