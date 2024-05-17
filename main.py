#Developed by: Nina Schrauwen
#Date: 11/04/2021
#Description: This is the main file of the Netflix recommendation system. It connects to the database, retrieves the Netflix titles, and selects a random title. It then builds a decision tree and retrieves the recommended titles.

import random
from title import NetflixTitle
import mysql.connector
from decision_tree import DecisionTreeNode, build_decision_tree, get_recommended_titles, get_user_scores, recommended_titles, get_scored_titles_from_db, get_non_scored_titles_from_db, get_recommendations_based_on_similarity, filter_positive_similarity_scores, update_jaccard_similarity, threshold, recommended_threshold, filter_recommended_titles, get_flexible_title_query, check_reached_num_suggestions

global netflix_titles

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


def print_attributes(netflix_titles):
    for title in netflix_titles:
        print(f"- - -Title attributes- - -")
        for attribute, value in vars(title).items():
            print(f"{attribute}: {value}")
        print("---------")

# To print the attributes of the sample or selected title
def print_title_attributes(title):
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

# To print and number the attributes of the recommended titles
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


def get_sample_title(netflix_titles):
    if not netflix_titles:
        print("Error: Netflix titles set is empty.")
        return None

    selected_title = random.choice(list(netflix_titles))

    return selected_title

def get_standup_comedy_titles(netflix_titles):
    standup_comedy_titles = [title for title in netflix_titles if 'Stand-Up Comedy' in title.listed_in]

    if not standup_comedy_titles:
        print("Error: No stand-up comedy titles found.")
        return None

    selected_title = random.choice(standup_comedy_titles)

    return selected_title

def get_tv_show_titles(netflix_titles):
    tv_show_titles = [title for title in netflix_titles if title.type == 'TV Show']

    if not tv_show_titles:
        print("Error: No TV show titles found.")
        return None

    selected_title = random.choice(tv_show_titles)

    return selected_title

def get_movie_titles(netflix_titles):
    movie_titles = [title for title in netflix_titles if title.type == 'Movie']

    if not movie_titles:
        print("Error: No movie titles found.")
        return None

    selected_title = random.choice(movie_titles)

    return selected_title

def get_show_id_title(netflix_titles, show_id):
    for title in netflix_titles:
        if title.show_id == show_id:
            print(f'Found show ID {show_id}')
            return title  # Return the entire title object

    print(f'Error: No title with show ID {show_id} found.')
    raise ValueError(f'Invalid show ID: {show_id}')


# Main function to run the application
if __name__ == '__main__':
    # TODO: Add frontend to the application, preferably using some library like Flask or Django
    # Connect to the database and retrieve the Netflix titles
    netflix_titles = connect_db(num_results=150)

    # Reset the all scores of all titles to 0
    # clean_slate()

    #original sample title pick function
    selected_title = get_sample_title(netflix_titles)

    # custom title pick functions
    # selected_title = get_movie_titles(netflix_titles)
    # selected_title = get_tv_show_titles(netflix_titles)

    # For intensive testing of long movie titles with this genre use the following line
    # selected_title = get_standup_comedy_titles(netflix_titles)

    # For testing using a specific show_id, country problem with id 2418
    # selected_title = get_show_id_title(netflix_titles, 8005)

    # Prints the sample title and its attributes to the console
    print_title_attributes(selected_title)

    # Number of recommendations to be made
    num_suggestions = 4
    # Build the decision tree
    decision_tree_root = build_decision_tree(netflix_titles, selected_title, num_suggestions)
    # #
    #
    # #
    recommended_titles = get_recommended_titles(decision_tree_root, num_suggestions)
    # Prints the results and the attributes of the recommendations to the console
    # new_print_title_attributes(recommended_titles)

    # Filter the recommended titles based on jaccard_similarity score, use output from decision tree to filter
    filtered_recommended_titles = filter_recommended_titles(recommended_titles, recommended_threshold, num_suggestions)
    new_print_title_attributes(filtered_recommended_titles)

    # Check if the number of suggestions has been reached
    check_reached_num_suggestions(filtered_recommended_titles, num_suggestions)

    # Call it here in order to get the user scores AFTER the recommendations have been printed out
    get_user_scores(filtered_recommended_titles) # Switch out the filtered_recommended_titles with recommended_titles to test the function

    # Get the scored titles from the database
    scored_titles = get_scored_titles_from_db()
    # Get non-scored titles from the database
    non_scored_titles = get_non_scored_titles_from_db()

    # Debug print statements
    # Print the scored titles
    # for scored_title in scored_titles:
    #     print(f"Title: {scored_title.title} - Cast: {scored_title.cast} - Score: {scored_title.score}")

    # Print the non-scored titles
    # for non_scored_title in non_scored_titles:
    #     print(f"Title: {non_scored_title.title} - Listed in: {non_scored_title.listed_in} - Score: {non_scored_title.score}")

    # Get the recommendations based on similarity
    jaccard_similarities = get_recommendations_based_on_similarity(scored_titles, non_scored_titles)
    # print(f"Similarity score: {jaccard_similarities}")
    # print(f'Type of similarity score: {type(jaccard_similarities)}') # Nested tuples within a list inside a tuple

    # Return and print all the titles that have a positive similarity score
    positive_scores = filter_positive_similarity_scores(jaccard_similarities, threshold)
    # print(f"Filtered positive similarity scores: {positive_scores}")
    # print(f'Type of positive scores: {type(positive_scores)}') # Dictionary

    # Update the jaccard similarity scores in the database - DON'T FORGET TO TURN THIS ON TO UPDATE THE DATABASE (but don't forget to turn it off again either due to performance issues)
    # updated_jaccard_scores = update_jaccard_similarity(positive_scores)

    # Get the flexible title query and score the queried titles based on the user input
    get_flexible_title_query()



