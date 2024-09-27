#Developed by: Nina Schrauwen
#Description: Functions to interact with other files within this project.
#Date: 20/05/2024

# Import the necessary libraries
import csv
from collections import defaultdict

# Define the paths to the CSV and TXT files
CSV_FILE_PATH = 'genre_counts.csv'
ACHIEVEMENTS_FILE = 'completed_achievements.txt'

# Define global variables to store the genre counts and the completed achievements
global achievement_output

# Function to normalize the different genres that are similar
def normalize_genre(genre):
    # Dict to define which genres can be generalized
    normalization_dict = {
        "Horror Movies": "Horror",
        "TV Horror": "Horror",
        "Romantic Movies": "Romantic",
        "Romantic TV Shows": "Romantic",
        "Stand-Up Comedy": "Comedy",
        "Stand-Up Comedy & Talk Shows": "Comedy"
        "Classic & Cult TV: Classic"
        "Classic Movies: Classic"
    }
    # Return the normalized genre if one can be found, otherwise keep its original genre (both without trailing whitespace)
    return normalization_dict.get(genre.strip(), genre.strip())


# Function to be able to read the genre counts from the CSV file
def read_genre_counts():
    # Define genre_counts as a dict containing int
    genre_counts = defaultdict(int)
    try:
        # Able to open and read the file
        with open(CSV_FILE_PATH, mode='r', newline='') as file:
            # Get a reader in order to read the CSV file
            reader = csv.reader(file)
            # Loop through the rows and if a row does not consist of 2 parts then continue to the next row
            for row in reader:
                if len(row) != 2:  # Skip rows that do not have exactly 2 values
                    continue
                # If a row does consist of 2 parts then that row is valid and can be broken down into genre and their count
                genre, count = row
                # Strip genre of any trailing whitespace and make sure the count is an integer
                genre_counts[genre.strip()] = int(count)

    # If the file does not exist handle this error gracefully
    except FileNotFoundError:
        pass
    return genre_counts

# Function to be able to write the genre counts to the CSV file
def write_genre_counts(genre_counts):
    try:
        # Able to open and write the file
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            # Get a writer in order to write to the CSV file
            writer = csv.writer(file)
            # Loop through the genre_counts and write those genre and their counts with the writer
            for genre, count in genre_counts.items():
                writer.writerow([genre, count])

    # If the file does not exist handle this error gracefully
    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE_PATH}' was not found.")

# Function to be able to read the completed achievements from a file
def read_completed_achievements():
    # Create an empty dictionary to store the completed achievements
    completed_achievements = {}
    try:
        # Open the file and read the lines, only allowed to read
        with open('completed_achievements.txt', 'r') as file:
            # Loop through the lines and split them by the colon
            for line in file:
                parts = line.split(':')
                # If the line consists of 2 parts, store the achievement and its completion status
                if len(parts) == 2:
                    # Only true or false values are allowed
                    completed_achievements[parts[0].strip()] = parts[1].strip() == 'True'
                # If the line is malformed, print a warning and print the line
                else:
                    print(f"Skipping malformed line: {line.strip()}")

    # If the file doesn't exist, we assume no achievements have been completed
    except FileNotFoundError:
        pass
    return completed_achievements

# Function to write the completed achievements to a file and give permission to write
def write_completed_achievements(completed_achievements):
    # Open the file and write the achievements and their completion status, allowed to write
    with open('completed_achievements.txt', 'w') as file:
        # Loop through the achievements and their completion status
        for achievement, completed in completed_achievements.items():
            # Write the achievement and its completion status to the file
            file.write(f'{achievement}: {completed}\n')


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

    # Create a dictionary to store the achievements and whether they have been achieved, set to None by default
    # True = achieved not shown, False = achieved and shown, None is not yet unlocked
    achieved_milestones = {achievement: None for achievement in achievements}

    # Loop through achievements
    for achievement, (genre, count) in achievements.items():
        # If the genre is within the genre_count and the count is at or above the genre_count then see if the achievement has already been achieved or not
        if genre in genre_counts and genre_counts[genre] >= count:
            # If the achievement is not yet unlocked or is unlocked and not yet shown
            if completed_achievements.get(achievement, None) is None or completed_achievements[achievement] is True:
                achieved_milestones[achievement] = True # Set that genre for the dictionary to true to be able to track all achievements at this exact moment
                completed_achievements[achievement] = True  # Update completed_achievements TXT file to set the achievement to True
                print(f'Congratulations! You are a "{achievement}"! @other_functions.py:check_achievement()')
            # If the achievement has already been completed and shown then print a console message stating that fact and the genre
            elif completed_achievements[achievement] is False:
                print(f'You have already achieved the "{achievement}" milestone! @other_functions.py:check_achievement()')
            # Something might have went wrong with the reasing of the achievements etc. Print a message stating the data that is known.
            else:
                print(f'Something went wront with the processing of the achievements. Achievement: {achievement}, count: {count} @other_functions.py:check_achievement()')
        # Not enough count to be able to achieve the achievement so print a console message
        else:
            print(f'Not enough genre count titles to achieve "{achievement}" milestone. @other_functions.py:check_achievement()')

    write_completed_achievements(completed_achievements) # Update the completed achievements in the file
    write_genre_counts(genre_counts) # Update the genre counts in the CSV file
    # Return the achieved_milestones because the completed_achievements will change back to False in a bit and we still have to get to the popup
    return achieved_milestones

# Function to get the title object based on the show ID, will use the show_id based on the user input
# Then the genres will be counted and updated in the genre_counts.csv file
def get_show_id_title(netflix_titles, show_id):
    # Make sure the show id is an integer
    show_id = int(show_id)

    # Loop through the Netflix titles to find the title with the given show ID
    for title in netflix_titles:
        # Check if the show ID matches the given show ID, then return the title of the corresponding show ID
        if title.show_id == show_id:
            print(f'Found show ID {show_id}')

            # Read genre counts
            genre_counts = read_genre_counts()
            # Convert genres into a list separating them by the comma
            genres = title.listed_in.split(",")

            # Loop through the genres
            for genre in genres:
                # Look if the genre at hand can be normalized at the hand of the normalize_genre function
                normalized_genre = normalize_genre(genre)
                # If so update the now normalized genre with one genre count
                genre_counts[normalized_genre] += 1

            # Write the current genre counts
            write_genre_counts(genre_counts)

            # Check if there is any achievements that have been reached with the current genre count
            achievement_output = check_achievement(genre_counts)
            # If there is achievement output print it into the console to check
            if achievement_output:
                print(achievement_output)

            return title  # Return the entire title object

    # If the show ID is anything but an integer raise a value error
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
    print("-------------------------------------------------")

