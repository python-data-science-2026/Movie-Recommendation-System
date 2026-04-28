import pandas as pd
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
        required_columns = ["title", "year", "genre", "rating"]

        df = pd.read_csv(file_path)

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df = df.dropna(subset=required_columns)

        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df = df.dropna(subset=["year", "rating"])

        df["year"] = df["year"].astype(int)
        df["actor"] = df["actor"].fillna("") if "actor" in df.columns else ""
        df["director"] = df["director"].fillna("") if "director" in df.columns else ""
        df["notes"] = df["notes"].fillna("") if "notes" in df.columns else ""

        imported_count = 0
        for _, row in df.iterrows():
            movie = Movie(
                title=str(row["title"]).strip(),
                year=int(row["year"]),
                genre=str(row["genre"]).strip(),
                rating=float(row["rating"]),
                actor=str(row["actor"]).strip(),
                director=str(row["director"]).strip(),
                notes=str(row["notes"]).strip(),
            )
            self.add_movie(movie)
            imported_count += 1

        return imported_count