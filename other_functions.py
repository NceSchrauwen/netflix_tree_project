#Developed by: Nina Schrauwen
#Description: Functions to interact with other files within this project.
#Date: 20/05/2024

import csv
from collections import defaultdict

CSV_FILE_PATH = 'genre_counts.csv'

global achievement_output

# TODO: Add more normalization mappings as needed
# Function to normalize the genre names
def normalize_genre(genre):
    normalization_dict = {
        "Horror Movies": "Horror",
        "TV Horror": "Horror",
        "Romantic Movies": "Romantic",
        "Romantic TV Shows": "Romantic",
        "Stand-Up Comedy": "Comedy",
        "Stand-Up Comedy & Talk Shows": "Comedy"
        # Add more mappings as needed
    }
    return normalization_dict.get(genre.strip(), genre.strip())  # Default to the original genre if not found


# Function to read the genre counts from the CSV file
def read_genre_counts():
    genre_counts = defaultdict(int)
    try:
        with open(CSV_FILE_PATH, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                genre, count = row
                genre_counts[genre.strip()] = int(count)
    except FileNotFoundError:
        pass   # If the file does not exist, return an empty dictionary
    return genre_counts

# Function to write the genre counts to the CSV file
def write_genre_counts(genre_counts):
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        for genre, count in genre_counts.items():
            writer.writerow([genre, count])


def check_achievement(genre_counts):
    global achievement_output
    achievement_output = None

    achievements = {
        'Horror Fanatic': ('Horror', 3),
        'Comedy Lover': ('Comedy', 3),
        'Hopeless Romantic': ('Romantic', 3)
    }

    for achievement, (genre, count) in achievements.items():
        if genre_counts[genre] >= count:
            achievement_output = f'Congratulations! You are a "{achievement}"!'
            genre_counts[genre] = 0  # Reset the count for the genre after achieving the milestone

    write_genre_counts(genre_counts) # Update the genre counts in the CSV file
    return achievement_output

# Function to get the title object based on the show ID, will use the show_id based on the user input
# Then the genres will be counted and updated in the genre_counts.csv file
def get_show_id_title(netflix_titles, show_id):
    # Preprocess show_id to remove whitespace and ensure it's in the desired format
    show_id = str(show_id).strip()  # Convert to string and remove leading/trailing whitespace
    show_id = int(show_id)  # Convert to integer

    # Loop through the Netflix titles to find the title with the given show ID
    for title in netflix_titles:
        # Check if the show ID matches the given show ID, then return the title of the corresponding show ID
        if title.show_id == show_id:
            print(f'Found show ID {show_id}')

            # Update genre counts
            genre_counts = read_genre_counts()
            genres = title.listed_in.split(",")  # Split the genres by comma, bc most are a list of genres

            for genre in genres:
                normalized_genre = normalize_genre(genre)
                genre_counts[normalized_genre] += 1

            write_genre_counts(genre_counts)

            achievement_output = check_achievement(genre_counts)
            if achievement_output:
                print(achievement_output)

            return title  # Return the entire title object

    # Debug print statements to check the length of the Netflix titles list
    # print(f'Netflix titles test length: {len(netflix_titles)}')

    # If the show ID is not found, raise a ValueError
    raise ValueError(f'Invalid show ID: {show_id}')


# To print the attributes of the sample or selected title
def print_title_attributes(title):
    if title is None:
        print("Error: Title is None.")
        return
    print("Title attributes:")
    print(f"Show ID: {title.show_id}")
    print(f"Type: {title.type}")
    print(f"Title: {title.title}")
    print(f"Listed In: {title.listed_in}")
    print(f"Review following criteria: ")
    print(f"Release Year: {title.release_year}")
    print(f'Country: {title.country}')
    print(f'Duration: {title.duration}')
    print(f'Age rating {title.rating}')
    # print(f"Listed In: {title.date_added}")
    # print(f"Listed In Year: {title.date_added.year}")
    print("-------------------------------------------------")

