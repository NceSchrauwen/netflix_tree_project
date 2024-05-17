#Developed by: Nina Schrauwen
#Description: Functions to interact with the database.
#Date: 17/05/2024

import mysql.connector
from title import NetflixTitle

# Function to fetch titles from the database for the user to select in the GUI
def get_titles_to_select_from_db():
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

        # TODO: Remove limit 150 and see what happens if you load all 8807 titles into the treeview
        # Execute the SQL query to select all titles from the database
        cursor.execute("select * from netflix_movies limit 150")

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