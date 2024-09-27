#Developed by: Nina Schrauwen
#Description: Functions to interact with the database and fetch the results.
#Date: 17/05/2024

import mysql.connector
from title import NetflixTitle

# Function to fetch titles from the database for the user to select in the GUI
# With specific start and end indexes due to only being able to display a certain amount of titles per page
def get_titles_to_select_from_db(start_index, end_index):
    titles_to_select = []

    # Try to connect to the database and fetch the titles with specific indexes
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

    # Loop through the rows and store them as NetflixTitle objects in a list
    for row in rows:
        netflix_title = NetflixTitle(*row)
        titles_to_select.append(netflix_title)

    # Return the list of NetflixTitle objects to be able to use in the GUI
    return titles_to_select

# Function to fetch specific titles regarding genre and/or titles from the database
def get_genre_title_from_db(query_title, genre, type):
    query_results = []
    query = None

    # Try to connect to the database and fetch the titles based on a specific genre and/or title
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

        # If only the title is specified, fetch all titles that contain the title
        if genre == "All" and query_title and type == "All":
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%'".format(query_title.lower())
        # If the title and genre are specified, fetch all titles that contain the title and are of the specified genre
        elif query_title and genre and type == "All":
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%' AND listed_in LIKE '%{}%'".format(query_title.lower(), genre.lower())
        # If only the genre is specified, fetch all titles that are of the specified genre
        elif genre and not query_title and type == "All":
            query = "SELECT * FROM test_netflix_movies WHERE listed_in LIKE '%{}%'".format(genre.lower())
        # If the title and type are specified, fetch all titles that contain the title and are of the specified type
        elif query_title and type and genre == "All":
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%' AND type LIKE '%{}%'".format(query_title.lower(), type.lower())
        # If only the type is specified, fetch all titles that are of the specified type
        elif type and not query_title and genre == "All":
            query = "SELECT * FROM test_netflix_movies WHERE type LIKE '%{}%'".format(type.lower())
        # If genre and type are specified, fetch all titles that are of the specified genre and type
        elif genre and type and not query_title:
            query = "SELECT * FROM test_netflix_movies WHERE listed_in LIKE '%{}%' AND type LIKE '%{}%'".format(genre.lower(), type.lower())
        # If all three are specified, fetch all titles that contain the title, are of the specified genre and type
        elif query_title and genre and type:
            query = "SELECT * FROM test_netflix_movies WHERE title LIKE '%{}%' AND listed_in LIKE '%{}%' AND type LIKE '%{}%'".format(query_title.lower(), genre.lower(), type.lower())

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

    # Catch any errors that might occur
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Close the database connection once the query is done
    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    # Loop through the rows and create NetflixTitle objects to store in a list
    for row in rows:
        query_results.append(NetflixTitle(*row))

    # Return the list of NetflixTitle objects to be able to use in the GUI
    return query_results
