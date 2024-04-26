#Developed by: Nina Schrauwen
#Date: 11/04/2021
#Description: Class to store scored titles

class ScoredTitle:
    # constructor of class
    def __init__(self, show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score):
        self.show_id = show_id
        self.type = type
        self.title = title
        self.director = director
        self.cast = cast
        self.country = country
        self.date_added = date_added
        self.release_year = release_year
        self.rating = rating
        self.duration = duration
        self.listed_in = listed_in
        self.description = description
        self.score = score

    def __str__(self):
        return f"Title: {self.title} - Cast {self.cast} - Show ID: {self.show_id}  Listed In: {self.listed_in} - Score: {self.score}"