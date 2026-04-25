class Preferences:
    def __init__(self):
        self.favorite_genres = []
        self.favorite_actors = []
        self.favorite_directors = []

    def set_genres(self, genres):
        self.favorite_genres = genres

    def set_actors(self, actors):
        self.favorite_actors = actors

    def set_directors(self, directors):
        self.favorite_directors = directors

    def __str__(self):
        return (
            f"Favorite genres: {', '.join(self.favorite_genres) if self.favorite_genres else 'None'}\n"
            f"Favorite actors: {', '.join(self.favorite_actors) if self.favorite_actors else 'None'}\n"
            f"Favorite directors: {', '.join(self.favorite_directors) if self.favorite_directors else 'None'}"
        )