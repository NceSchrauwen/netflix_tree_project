#Developed by: Nina Schrauwen
#Description: Functions to interact with other files within this project.
#Date: 20/05/2024

import csv
from collections import defaultdict

CSV_FILE_PATH = 'genre_counts.csv'
ACHIEVEMENTS_FILE = 'completed_achievements.txt'

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
        "Classic & Cult TV: Classic"
        "Classic Movies: Classic"
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
                if len(row) != 2:  # Skip rows that do not have exactly 2 values
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

# Function to read the completed achievements from a file
def read_completed_achievements():
    completed_achievements = {}
    with open('completed_achievements.txt', 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line:
                continue  # Skip empty or whitespace-only lines
            parts = line.split(':')  # Split the line by colon
            if len(parts) == 2:
                completed_achievements[parts[0].strip()] = parts[1].strip() == 'True'
            else:
                print(f"Skipping malformed line: {line}")
    return completed_achievements


# Function to write the completed achievements to a file
def write_completed_achievements(completed_achievements):
    with open(ACHIEVEMENTS_FILE, 'w') as file:
        for achievement, shown in completed_achievements.items():
            file.write(f"{achievement}:{shown}\n")

# Function to reset the completed achievement status after showing the achievement, not used for now
def reset_achievement_status(achievement):
    completed_achievements = read_completed_achievements()
    completed_achievements[achievement] = True
    write_completed_achievements(completed_achievements)


# Function to check if the user has achieved any of the achievements
def check_achievement(genre_counts):
    # Define the achievements and the required count for each genre
    achievements = {
        'Horror Fanatic': ('Horror', 3),
        'Comedy Lover': ('Comedy', 3),
        'Hopeless Romantic': ('Romantic', 3),
        'Classic Enthusiast': ('Classic', 3)
    }

    # Read the completed achievements from the file
    completed_achievements = read_completed_achievements()

    # Create a dictionary to store the achievements and whether they have been achieved, set to False by default
    achieved_milestones = {achievement: False for achievement in achievements}

    # Debug print statements
    # print(f'Genre counts: {genre_counts}')
    # print(f'Completed achievements: {completed_achievements}')

    for achievement, (genre, count) in achievements.items():
        # If the achievement is true it has been completed, genre count has to be equal to the count
        if genre in genre_counts and genre_counts[genre] == count and not completed_achievements.get(achievement, False):
            achieved_milestones[achievement] = True
            print(f'Congratulations! You are a "{achievement}"! @other_functions.py:check_achievement()')
            completed_achievements[achievement] = True # Update the completed achievements genre

    write_completed_achievements(completed_achievements) # Update the completed achievements in the file
    write_genre_counts(genre_counts) # Update the genre counts in the CSV file
    # print(f'Final achieved milestones: {achieved_milestones}')
    return achieved_milestones

# print(
    #     f'Achievements after checking: {achieved_milestones} @other_functions.py:check_achievement()')  # Debug statement
    # print(f'Genre counts after checking: {genre_counts} @other_functions.py:check_achievement()' )  # Debug statement

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

