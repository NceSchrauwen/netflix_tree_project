#Developed by: Nina Schrauwen
#Description: Functions that are being called in main.py but are being defined here to keep the code clean and organized.
#Date: 20/05/2024

import mysql
import random
from title import NetflixTitle
import mysql.connector

global netflix_titles

# Function to connect to the database and retrieve the Netflix titles (base function to connect to the db) and
# retreive all titles into a list
def connect_db(num_results=200):
    global netflix_titles
    # Establish a connection to the MySQL server
    mydb = mysql.connector.connect(
        host="localhost",      # Replace with your MySQL host
        port="8080",           # Replace with your MySQL port
        user="Admin",          # Replace with your MySQL username
        password="Brownie#99", # Replace with your MySQL password
        database="netflix_titles"      # Replace with your database name
    )

    # Create a cursor to execute SQL queries
    cursor = mydb.cursor()

    # Execute SQL query
    cursor.execute("SELECT * FROM netflix_titles.netflix_movies;")

    # Fetch all rows into a list
    rows = cursor.fetchall()
    netflix_titles = [NetflixTitle(*row) for row in rows]

    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # print_attributes(netflix_titles)

    return netflix_titles


# Function to clean the slate of all scores within the db to 0
def clean_slate():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            port="8080",
            user="Admin",
            password="Brownie#99",
            database="netflix_titles"
        )
        cursor = mydb.cursor()

        # Increment the score by 5 for the given title
        cursor.execute(f'UPDATE netflix_movies SET score = 0;')

        mydb.commit()
        print("Score updated successfully in the database.")

    except mysql.connector.Error as err:
        print(f"Error updating score in the database: {err}")

    finally:
        if mydb:
            cursor.close()
            mydb.close()

# Print the attributes of the Netflix titles list to the console
def print_attributes(netflix_titles):
    for title in netflix_titles:
        print(f"- - -Title attributes- - -")
        for attribute, value in vars(title).items():
            print(f"{attribute}: {value}")
        print("---------")


# To print and number the attributes of the recommended titles and number them, input is the list of recommended titles
def new_print_title_attributes(titles):
    for index, title in enumerate(titles, start=1):
        print(f"-----------------{index} {title.title} {title.show_id} -----------------")
        # print(f'Title {title.title}')
        # print(f"Show ID: {title.show_id}")
        print(f"Type: {title.type}")
        print(f"Listed In: {title.listed_in}")
        print(f"- Review the following criteria: -")
        print(f"Release Year: {title.release_year}")
        print(f'Country: {title.country}')
        print(f'Duration: {title.duration}')
        print(f'Age rating {title.rating}')
        print(f'Jaccardn Similarity: {title.jaccard_similarity}')
        print(f'Score: {title.score}')
        print("-------------------------------------------------")
    print("------------------------END-------------------------")

# Get a random sample title from the Netflix titles list using the random module
def get_sample_title(netflix_titles):
    if not netflix_titles:
        print("Error: Netflix titles set is empty.")
        return None

    selected_title = random.choice(list(netflix_titles))

    return selected_title

# Function to strictly get titles that contain the stand-up comedy genre for intensive testing
def get_standup_comedy_titles(netflix_titles):
    standup_comedy_titles = [title for title in netflix_titles if 'Stand-Up Comedy' in title.listed_in]

    if not standup_comedy_titles:
        print("Error: No stand-up comedy titles found.")
        return None

    selected_title = random.choice(standup_comedy_titles)

    return selected_title

# Function that strictly gets TV show titles from the Netflix titles list
def get_tv_show_titles(netflix_titles):
    tv_show_titles = [title for title in netflix_titles if title.type == 'TV Show']

    if not tv_show_titles:
        print("Error: No TV show titles found.")
        return None

    selected_title = random.choice(tv_show_titles)

    return selected_title

# Function that strictly gets movie titles from the Netflix titles list
def get_movie_titles(netflix_titles):
    movie_titles = [title for title in netflix_titles if title.type == 'Movie']

    if not movie_titles:
        print("Error: No movie titles found.")
        return None

    selected_title = random.choice(movie_titles)

    return selected_title
