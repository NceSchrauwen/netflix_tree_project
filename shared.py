#Developed by: Nina Schrauwen
#Description: Functions that are being called in main.py but are being defined here to keep the code clean and organized.
#Date: 20/05/2024

# Importing the necessary modules
import mysql
import random
from title import NetflixTitle
import mysql.connector

# Global variable to store the Netflix titles
global netflix_titles

# Function to connect to the database and retrieve the Netflix titles (base function to connect to the db) and
# retreive all titles into a list as objects
def connect_db(num_results=200):
    global netflix_titles
    # Establish a connection to the MySQL server
    try:
        mydb = mysql.connector.connect(
            host="localhost",  # Replace with your MySQL host
            port="8080",  # Replace with your MySQL port
            user="Admin",  # Replace with your MySQL username
            password="Brownie#99",  # Replace with your MySQL password
            database="netflix_titles"  # Replace with your database name
        )

        # Create a cursor to execute SQL queries
        cursor = mydb.cursor()

        # Execute a select query to retrieve all rows from the table
        cursor.execute(
            "SELECT * FROM netflix_titles.test_netflix_movies;")  # Replaced with test_netflix_movies to test without pre existing data

        # Fetch all rows into a list containing NetflixTitle objects
        rows = cursor.fetchall()
        netflix_titles = [NetflixTitle(*row) for row in rows]

    # Catch any errors that might occur during the process
    except mysql.connector.Error as err:
        print(f"Error updating score in the database: {err}")

    # Close the connection to the database if the connection is still open
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    return netflix_titles

# To be able to print and number the attributes of the recommended titles and number them, input is the list of recommended titles
def new_print_title_attributes(titles):
    # Loop through the list of recommended titles and print the attributes while numbering them
    for index, title in enumerate(titles, start=1):
        print(f"-----------------{index} {title.title} {title.show_id} -----------------")
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

