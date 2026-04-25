class Movie:
    def __init__(self, title, year, genre, rating, actor="", director="", notes=""):
        self.title = title
        self.year = year
        self.genre = genre
        self.rating = rating
        self.actor = actor
        self.director = director
        self.notes = notes

    def __str__(self):
        return (
            f"{self.title} ({self.year}) | Genre: {self.genre} | "
            f"Rating: {self.rating}/5"
        )