#Developed by: Nina Schrauwen
#Description: Functions to interact with the database.
#Date: 17/05/2024

import mysql.connector
from title import NetflixTitle

# Function to fetch titles from the database for the user to select in the GUI
def get_titles_to_select_from_db(start_index, end_index):
    titles_to_select = []

    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host="localhost",
            port="8080",
            user="Admin",
            password="Brownie#99",
            database="netflix_titles"
        )

        # Create a cursor to execute SQL queries
        cursor = mydb.cursor()

        # Execute the SQL query to select all titles from the database
        cursor.execute(f'select * from test_netflix_movies limit {start_index}, {end_index};') # Replaced with test_netflix_movies to test without pre existing data
        # cursor.execute(f'select * from netflix_movies limit {start_index}, {end_index};')

        # Fetch all the rows
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

        # print(f'--- Netflix Titles: ---')

    # Loop through the rows and create NetflixTitle objects
    for row in rows:
        netflix_title = NetflixTitle(*row)
        titles_to_select.append(netflix_title)
        # print(f'Title: {netflix_title.title} - Listed in: {netflix_title.listed_in} - Rating: {netflix_title.rating}')

    # Return the list of NetflixTitle objects to use in the GUI
    return titles_to_select

# Function to fetch specific titles regarding genre or names from the database
def get_genre_title_from_db(query_title, genre):
    query_results = []
    query = None

    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host="localhost",
            port="8080",
            user="Admin",
            password="Brownie#99",
            database="netflix_titles"
        )

        # Create a cursor to execute SQL queries
        cursor = mydb.cursor()

        # Execute the SQL query to select a title based on a part of the name, no genre specified
        if genre == "All" and query_title:
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%'".format(query_title.lower())
        # Execute the SQL query to select a title based on a specific part of a title and genre
        elif query_title and genre:
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%' AND listed_in LIKE '%{}%'".format(query_title.lower(), genre.lower())
        # Execute the SQL query to select a title based on a specific genre, no title specified
        elif genre and not query_title:
            query = "SELECT * FROM test_netflix_movies WHERE listed_in LIKE '%{}%'".format(genre.lower())

        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    # Loop through the rows and create NetflixTitle objects
    for row in rows:
        query_results.append(NetflixTitle(*row))

    return query_results
