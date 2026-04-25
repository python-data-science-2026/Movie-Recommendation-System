import csv
from movie import Movie


class MovieService:
    def __init__(self):
        self.watched_movies = []

    def add_movie(self, movie):
        self.watched_movies.append(movie)

    def get_all_movies(self):
        return self.watched_movies

    def get_average_rating(self):
        if not self.watched_movies:
            return 0
        total = sum(movie.rating for movie in self.watched_movies)
        return total / len(self.watched_movies)

    def get_total_movies(self):
        return len(self.watched_movies)

    def get_top_genre(self):
        if not self.watched_movies:
            return None

        genre_count = {}
        for movie in self.watched_movies:
            genre_count[movie.genre] = genre_count.get(movie.genre, 0) + 1

        return max(genre_count, key=genre_count.get)

    def import_movies_from_csv(self, file_path):
        imported_count = 0

        with open(file_path, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            required_fields = ["title", "year", "genre", "rating"]

            if reader.fieldnames is None:
                raise ValueError("The CSV file is empty or has no header.")

            for field in required_fields:
                if field not in reader.fieldnames:
                    raise ValueError(f"Missing required column: {field}")

            for row in reader:
                title = row["title"].strip()
                genre = row["genre"].strip()

                if not title or not genre:
                    continue

                try:
                    year = int(row["year"])
                    rating = float(row["rating"])
                except ValueError:
                    continue

                actor = row.get("actor", "").strip()
                director = row.get("director", "").strip()
                notes = row.get("notes", "").strip()

                movie = Movie(title, year, genre, rating, actor, director, notes)
                self.add_movie(movie)
                imported_count += 1

        return imported_count