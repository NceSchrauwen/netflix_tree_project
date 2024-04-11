#Developed by: Nina Schrauwen
#Date: 11/04/2021
class NetflixTitle:
    # constructor of class
    def __init__(self, show_id, type, title, director, cast,country,date_added,release_year,rating,duration,listed_in,description,score):
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
        self.suggested_titles = []  # New attribute for suggested titles

    def __str__(self):
        return f"Title: {self.title} - Release Year: {self.release_year} - Date Added: {self.date_added} - Listed In: {self.listed_in} - Type: {self.type}"


