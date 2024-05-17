#Developed by: Nina Schrauwen
#Description: This is the decision tree file of the Netflix recommendation system. This file contains the decision tree class and functions to build the decision tree and get recommendations based on the user input.
#Date: 11/04/2024

import random
from collections import deque

import mysql
import mysql.connector
from title import NetflixTitle

country_preference = None
duration_preference = None
classic_preference = None
directions = []
criteria = []
criterion = None
recommended_titles = []
child_friendly_preference = None
threshold = 0.0
recommended_threshold = 0.01
updated_jaccard_titles = []
query_results = []
selected_title = []


# constructor of the node class
class DecisionTreeNode:
    def __init__(self, criterion, left_child=None, right_child=None, recommended_titles=None):
        self.criterion = criterion
        self.left_child = left_child
        self.right_child = right_child
        self.recommended_titles = recommended_titles if recommended_titles else []

    # Define __str__ method to print information about the node
    def __str__(self):
        return f"Criterion: {self.criterion}\n" \
               f"Left Child: {self.left_child}\n" \
               f"Right Child: {self.right_child}\n" \
            # f"Recommended Titles: {self.recommended_titles}\n"

def get_scored_titles_from_db():
    scored_titles = []

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

        # Execute the SQL query to select scored titles
        cursor.execute("SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM netflix_movies WHERE score != 0")

        # Fetch all the rows
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

        # print(f'--- Scored titles ---')

        # Loop through the rows and create NetflixTitle objects
    for row in rows:
        scored_titles.append(NetflixTitle(*row))

    #Use for loop to print the scored titles
    return scored_titles

def get_non_scored_titles_from_db():
    non_scored_titles = []

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

        # Execute the SQL query to select scored titles
        cursor.execute("SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM netflix_movies WHERE score = 0")

        # Fetch all the rows
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

        # print(f'--- Non-Scored titles ---')

        # Loop through the rows and create NetflixTitle objects
    for row in rows:
        non_scored_titles.append(NetflixTitle(*row))

    #Use for loop to print the scored titles
    return non_scored_titles

# Function to get all the matching titles and their information from the database
def get_user_query_title_from_db(query_title):
    query_results = []

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

        # Execute the SQL query to select scored titles
        query = "SELECT * FROM netflix_movies WHERE title LIKE '%{}%'".format(query_title.lower())
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

        # print(f'--- Non-Scored titles ---')

    # Loop through the rows and create NetflixTitle objects
    for row in rows:
        query_results.append(NetflixTitle(*row))

    if query_results:
        print(f'--- Query results ---')
        for index, result in enumerate(query_results):
            print(
                f"{index + 1}. Title: {result.title}, Show ID: {result.show_id}, Type: {result.type}, Listed In: {result.listed_in}, Score: {result.score}, Jaccard Similarity: {result.jaccard_similarity}")

    #Use for loop to print the scored titles
    return query_results


# Function to update the jaccard similarity scores in the database
def update_jaccard_similarity(jaccard_data):
    updated_jaccard_titles = []

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

        # Expects more values then 2 because of jaccard_data being a nested list of tuples so it needs to be unpacked by using *_ in the for loop in order for the tile and jaccard_similarity to be extracted
        for title, jaccard_similarity in jaccard_data.items():
            cursor.execute(
                f'UPDATE netflix_movies SET jaccard_similarity = {jaccard_similarity} WHERE title = "{title}";')  # To wrap title in single quotes to prevent future SQL syntax errors

        mydb.commit()  # Commit the transaction

        print(f"Number of rows updated: {cursor.rowcount}") # Print the number of rows updated

        # Execute the SQL query to select titles with jaccard scores above 0
        select_query = "SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM netflix_movies WHERE jaccard_similarity > 0"
        cursor.execute(select_query)
        updated_jaccard_titles = [NetflixTitle(*row) for row in cursor.fetchall()]

        # print(f"Number of rows updated: {cursor.rowcount}")
        print(f"Number of positive jaccard titles found AFTER updating: {len(updated_jaccard_titles)}")

        if updated_jaccard_titles:
            # print(f'Titles are being updated with the jaccard similarity scores.')
            print(f'--- Positive jaccard titles ---')
            for title in updated_jaccard_titles:
                print(
                    f' -\ Updated Title: {title.title}, Jaccard Score: {title.jaccard_similarity}, Score: {title.score}, Show ID: {title.show_id}, Type: {title.type} /-')
        else:
            print("No positive jaccard titles found.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    return updated_jaccard_titles

# Function to calculate the Jaccard similarity between two sets
def calculate_jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Compare the scored titles and their cast to the non-scored titles and their cast to get the jaccard similarity scores
def get_recommendations_based_on_similarity(scored_titles, non_scored_titles):
    jaccard_similarities_scored = []
    jaccard_similarities_non_scored = []

    for scored_title in scored_titles:
        scored_cast = set(scored_title.cast.split(",")) if scored_title.cast else set()
        for non_scored_title in non_scored_titles:
            non_scored_cast = set(non_scored_title.cast.split(",")) if non_scored_title.cast else set()
            similarity_score = calculate_jaccard_similarity(scored_cast, non_scored_cast)
            jaccard_similarities_scored.append((scored_title.title, similarity_score))
            jaccard_similarities_non_scored.append((non_scored_title.title, similarity_score))

    return jaccard_similarities_scored, jaccard_similarities_non_scored


# Function to filter the positive similarity scores in the jaccard similarities for testing purposes to compare to the scores in the database and to use in the decision tree
def filter_positive_similarity_scores(jaccard_similarities, threshold):
    positive_scores = {} # Initialize an empty dictionary to store the positive similarity scores

    # Loop through the outer list to get access to the inner tuple containing the title and the jaccard similarity
    for inner_tuple in jaccard_similarities:
        # Unpack the inner tuple
        for title, jaccard_similarity in inner_tuple:
            # print(f"- POSITIVE Title: {title} AND Jaccard Similarity: {jaccard_similarity} -")
            try:
                if jaccard_similarity != threshold:  # If the jaccard similarity is not equal to the threshold then add it to the positive scores dictionary
                    positive_scores[title] = jaccard_similarity
            except ValueError:
                print(f"Invalid score value: {jaccard_similarity}")

    if not positive_scores:
        print("No positive similarity scores found.")

    # Print the amount of positive similarity scores
    print(f"Amount of positive similarity scores: {len(positive_scores)}")

    return positive_scores


# to get user input on multiple criteria
def get_user_input():
    # Get user input
    global country_preference
    global duration_preference
    global child_friendly_preference
    global classic_preference

    while True:
        child_friendly_pref = input("Do you want to watch a child-friendly (under age 13) movie/season? (yes/no): ").strip().lower()
        if child_friendly_pref in ["yes", "no"]:
            child_friendly_preference = child_friendly_pref
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    while True:
        classic_pref = input("Do you want to watch a classic movie/season? (yes/no): ").strip().lower()
        if classic_pref in ["yes", "no"]:
            classic_preference = classic_pref
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    while True:
        duration_pref = input("Do you want to watch a short movie/season? (yes/no): ").strip().lower()
        if duration_pref in ["yes", "no"]:
            duration_preference = duration_pref
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    while True:
        preference = input("Do you want to watch a movie from the US or the UK? (yes/no): ").strip().lower()
        if preference in ["yes", "no"]:
            country_preference = preference
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

# to build the decision tree and get the recommendations based on the user input
def build_decision_tree(netflix_data, selected_title, num_suggestions):
    root = DecisionTreeNode(criterion="Initial Criterion")
    get_user_input()

    recursive_build_tree(root, netflix_data, selected_title, num_suggestions)
    print(f'Root: {root}')
    # get_user_scores()
    return root


# function to build node and its path based on the direction input
def build_path(node, directions, criteria, recommended_titles):
    global criterion

    # if there are no directions left, then return the node with the recommended titles
    if not directions:
        node.recommended_titles = recommended_titles
        return node

    directions_copy = directions.copy()
    criterion = criteria.pop(0)

    # pop the first element of the list to get the current direction to process
    direction = directions_copy.pop(0)

    # if the direction is not left or right, then raise a ValueError
    if direction not in ['left', 'right']:
        raise ValueError(f"Invalid direction: {direction}. Only 'left' or 'right' are allowed.")

    # if the direction is left, then create a new node and set it to the left child of the current node
    if direction == 'left':
        if node.left_child is None:
            node.left_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then recurse and append the current node with a left child and the
        # remaining directions
        else:
            node.left_child.criterion = criterion
            node.left_child.recommended_titles = recommended_titles
        build_path(node.left_child, directions_copy, criteria, recommended_titles)

    # if the direction is right, then create a new node and set it to the right child of the current node
    elif direction == 'right':
        if node.right_child is None:
            node.right_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then recurse and append the current node with a right child and the
        # remaining directions
        else:
            node.right_child.criterion = criterion
            node.right_child.recommended_titles = recommended_titles
        build_path(node.right_child, directions_copy, criteria, recommended_titles)

    # if a new node is made then recurse with the new node and the remaining directions
    return node

# function to determine wheter the title is a movie or a tv show and then filter  and return the titles based on the duration
def decide_title_type(selected_title, duration_preference, previous_titles):
    new_titles = []

    if selected_title.duration is not None:
        if selected_title.type.lower() == "movie":
            if duration_preference == "yes":
                new_titles = [title for title in previous_titles if int(title.duration.split()[0]) <= 80]
            elif duration_preference == "no":
                new_titles = [title for title in previous_titles if int(title.duration.split()[0]) > 80]

        elif selected_title.type.lower() == "tv show":
            if duration_preference == "yes":
                new_titles = [title for title in previous_titles if int(title.duration.split()[0]) == 1]
            elif duration_preference == "no":
                new_titles = [title for title in previous_titles if int(title.duration.split()[0]) > 1]
        else:
            return "Invalid duration input"

    # Return the new list of titles
    return new_titles

# Filter the recommended titles based on the threshold and the number of suggestion, if the threshold is not met then add the remaining titles from the recommended titles list
def filter_recommended_titles(recommended_titles, threshold, num_suggestions):
    filtered_titles = [title for title in recommended_titles if title.jaccard_similarity > threshold]

    print(f'(Before) Length of filtered titles: {len(filtered_titles)}')

    # If not enough titles are found based on the threshold, then add back titles from the recommended_titles list
    if len(filtered_titles) < num_suggestions:
        num_to_add = num_suggestions - len(filtered_titles)
        print(f'Number of titles to add: {num_to_add}')
        filtered_titles.extend(recommended_titles[:num_to_add])

    print(f'Length of filtered titles: {len(filtered_titles)}')

    # Filter out all the duplicate entries from the filtered titles list
    filtered_titles = list(set(filtered_titles))

    # Shuffle the list to get a random selection of titles to avoid repetition of the same exact titles at the top of
    # the list
    random.shuffle(filtered_titles)

    print(f'--- Filtered Titles ---')
    for title in filtered_titles:
        print(f'Filtered Title: {title.title}, Show-ID: {title.show_id}, Jaccard Similarity: {title.jaccard_similarity}')

    # Return the filtered titles limited to the number of suggestions
    return filtered_titles[:num_suggestions]


# Check if the number of recommendations has been reached
def check_reached_num_suggestions(recommended_titles, num_suggestions):
    if len(recommended_titles) >= num_suggestions:
        print(f'Desired number of recommendations reached; {len(recommended_titles)} asked: {num_suggestions}')
    else:
        print(f'Cannot retrieve desired number of recommendations based on current filters, current length: {len(recommended_titles)} asked: {num_suggestions}')


# Function to search if there is a substring that matches US or UK in the country attribute of the title.country
def is_us_or_uk_title(title):
    return title.country and any(country_term in title.country.lower() for country_term in ["united states", "united kingdom"])

# to recursively run through the decision tree searching for the best recommendation
def recursive_build_tree(node, netflix_data, selected_title, num_suggestions):
    global country_preference
    global duration_preference
    global directions
    global criterion
    global criteria
    global recommended_titles
    global child_friendly_preference
    global classic_preference

    directions = []
    criteria = []
    recommended_titles = []

    if directions is None:
        directions = []

    us_uk_data = []
    other_data = []

    # If the node is the root node
    if node.criterion == "Initial Criterion":
        # Recommend titles based on (any of) the genre(s) that the selected title belongs to
        similar_genre_data = [title for title in netflix_data if any(
            genre.lower() in title.listed_in.lower() for genre in selected_title.listed_in.split(','))]

        # For testing purposes to see the amount of similar genre data
        # print(f'Similar genre data: {len(similar_genre_data)}')
        # for title in similar_genre_data:
        #     print(title)

        # If the sample title is a movie, then recommend movie titles
        if selected_title.type.lower() == "movie":
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "movie"]
        # If the sample title is a tv show, then recommend tv show titles
        elif selected_title.type.lower() == "tv show":
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "tv show"]
        else:
            print('Invalid title type')
            return

        # If no titles are found that have the same genre and type as the sample titl
        if not same_type_data:
            print('No titles found that have the same genre and type')
            return

        # If the user wants to watch a child-friendly movie/season, create a new list of titles that are rated with only the ages listed exluding "NR"
        if child_friendly_preference == "yes":
            child_friendly_data = [title for title in same_type_data if
                                title.rating and title.rating.lower() in ["g", "tv-y", "tv-y7", "tv-g", "pg", "tv-pg"] and title.rating.lower != "nr"]

            # If there is child_friendly_data, then add a left direction and the corresponding criteria to the list
            if child_friendly_data:
                directions.append("left")
                criteria.append("Child-Friendly Titles")
                recommended_titles = child_friendly_data

            # If the user wants to watch a classic movie/season, create a new list of titles that were released before or at year 2010
            if classic_preference == "yes":
                classic_data = [title for title in child_friendly_data if title.release_year <= 2010]
                # If there is classic_data, then add a left direction and the corresponding criteria to the list
                if classic_data:
                    directions.append("left")
                    criteria.append("Classic Titles")
                    recommended_titles = classic_data

                    # If the user wants to watch a short movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                    if duration_preference == "yes":
                        short_classic_data = decide_title_type(selected_title, duration_preference, classic_data)
                        # If there is short_classic_data, then add a left direction and the corresponding criteria to the list
                        if short_classic_data:
                            directions.append("left")
                            criteria.append("Short Titles")
                            recommended_titles = short_classic_data

                            # print(f'!!! Short classic data: {len(short_classic_data)} !!!')
                            # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                            if country_preference == "yes":
                                us_uk_short_classic_data = [title for title in short_classic_data if is_us_or_uk_title(title)]

                                # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                if us_uk_short_classic_data:
                                    directions.append("left")
                                    criteria.append("US/UK Titles")
                                    recommended_titles = us_uk_short_classic_data

                            # If the user wants to watch a title from another country outside the US/Uk, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                            elif country_preference == "no":
                                other_short_classic_data = [title for title in short_classic_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                              country.strip().lower() not in ["united states", "united kingdom"] for country in
                              title.country.lower().split(', '))]
                                # Add the new list of filtered other country titles into a decision tree node on the right side
                                if other_short_classic_data:
                                    directions.append("right")
                                    criteria.append("Other Titles")
                                    recommended_titles = other_short_classic_data
                            else :
                                print("No recommended titles found based on this country preference in combination with the short_classic_data criteria")

                    # If the user wants to watch a long movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                    elif duration_preference == "no":
                        long_classic_data = decide_title_type(selected_title, duration_preference, classic_data)
                        # If there is long_classic_data, then add a right direction and the corresponding criteria to the list
                        if long_classic_data:
                            directions.append("right")
                            criteria.append("Long Titles")
                            recommended_titles = long_classic_data

                            # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                            if country_preference == "yes":
                                us_uk_long_classic_data = [title for title in long_classic_data if is_us_or_uk_title(title)]

                                # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                if us_uk_long_classic_data:
                                    directions.append("left")
                                    criteria.append("US/UK Titles")
                                    recommended_titles = us_uk_long_classic_data
                            # If the user wants to watch a title from another country outside the US/Uk, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                            elif country_preference == "no":
                                other_long_classic_data = [title for title in long_classic_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                              country.strip().lower() not in ["united states", "united kingdom"] for country in
                              title.country.lower().split(', '))]
                                # Add the new lifst of filtered other country titles into a decision tree node on the right side
                                if other_long_classic_data:
                                    directions.append("right")
                                    criteria.append("Other Titles")
                                    recommended_titles = other_long_classic_data
                            else:
                                print("No recommended titles found based on this country preference in combination with the long_classic_data criteria")


            # If the user does not want to watch a classic movie/season, create a new list of titles that were released after year 2010
            elif classic_preference == "no":
                non_classic_data = [title for title in child_friendly_data if title.release_year > 2010]
                # If there is non-classic_data, then add a right direction and the corresponding criteria to the list
                if non_classic_data:
                    directions.append("right")
                    criteria.append("Non-Classic Titles")
                    recommended_titles = non_classic_data

                    # If the user wants to watch a short movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                    if duration_preference == "yes":
                        non_classic_short_data = decide_title_type(selected_title, duration_preference, non_classic_data)
                        # If there is short non-classic_data, then add a left direction and the corresponding criteria to the list
                        if non_classic_short_data:
                            directions.append("left")
                            criteria.append("Short Titles")
                            recommended_titles = non_classic_short_data

                            # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                            if country_preference == "yes":
                                us_uk_short_non_classic_data = [title for title in non_classic_short_data if is_us_or_uk_title(title)]

                                # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                if us_uk_short_non_classic_data:
                                    directions.append("left")
                                    criteria.append("US/UK Titles")
                                    recommended_titles = us_uk_short_non_classic_data
                            # If the user wants to watch a title from another country outside the US/Uk, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                            elif country_preference == "no":
                                other_short_non_classic_data = [title for title in non_classic_short_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                              country.strip().lower() not in ["united states", "united kingdom"] for country in
                              title.country.lower().split(', '))]
                                # Add the new list of filtered other country titles into a decision tree node on the right side
                                if other_short_non_classic_data:
                                    directions.append("right")
                                    criteria.append("Other Titles")
                                    recommended_titles = other_short_non_classic_data
                            else:
                                print("No recommended titles found based on this country preference in combination with the non_classic_short_data criteria")

                    # If the user wants to watch a long movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                    elif duration_preference == "no":
                        non_classic_long_data = decide_title_type(selected_title, duration_preference, non_classic_data)
                        # If there is long non_classic_data, then add a right direction and the corresponding criteria to the list
                        if non_classic_long_data:
                            directions.append("right")
                            criteria.append("Long Titles")
                            recommended_titles = non_classic_long_data

                            # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                            if country_preference == "yes":
                                us_uk_long_non_classic_data = [title for title in non_classic_long_data if is_us_or_uk_title(title)]

                                # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                if us_uk_long_non_classic_data:
                                    directions.append("left")
                                    criteria.append("US/UK Titles")
                                    recommended_titles = us_uk_long_non_classic_data
                            # If the user wants to watch a title from another country outside the US/Uk, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                            elif country_preference == "no":
                                other_non_classic_long_data = [title for title in non_classic_long_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                              country.strip().lower() not in ["united states", "united kingdom"] for country in
                              title.country.lower().split(', '))]
                                # Add the new list of filtered other country titles into a decision tree node on the right side
                                if other_non_classic_long_data:
                                    directions.append("right")
                                    criteria.append("Other Titles")
                                    recommended_titles = other_non_classic_long_data
                            else:
                                print("No recommended titles found based on this country preference in combination with the non_classic_long_data criteria")

        # If the user does not want to watch a child-friendly movie/season, create a new list of titles that are not rated with the ages listed (thus also inluding "NR")
        elif child_friendly_preference == "no":
            non_child_friendly_data = [title for title in same_type_data if title.rating and title.rating.lower() not in ["g", "tv-y", "tv-y7", "tv-g", "pg", "tv-pg"]]

            # If there is non_child_friendly_data, then add a right direction and the corresponding criteria to the list
            if non_child_friendly_data:
                directions.append("right")
                criteria.append("Non-Child-Friendly Titles")
                recommended_titles = non_child_friendly_data

                # If the user wants to watch a classic movie/season, create a new list of titles that were released before or at year 2010
                if classic_preference == "yes":
                    classic_non_child_friendly_data = [title for title in non_child_friendly_data if title.release_year <= 2010]
                    # If there is classic_non_child_friendly_data, then add a left direction and the corresponding criteria to the list
                    if classic_non_child_friendly_data:
                        directions.append("left")
                        criteria.append("Classic Titles")
                        recommended_titles = classic_non_child_friendly_data

                        # If the user wants to watch a short movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                        if duration_preference == "yes":
                            non_friendly_classic_short_data = decide_title_type(selected_title, duration_preference, classic_non_child_friendly_data)
                            # If there is non_friendly_classic_short_data, then add a left direction and the corresponding criteria to the list
                            if non_friendly_classic_short_data:
                                directions.append("left")
                                criteria.append("Short Titles")
                                recommended_titles = non_friendly_classic_short_data

                                # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                                if country_preference == "yes":
                                    us_uk_short_non_friendly_short_classic_data = [title for title in non_friendly_classic_short_data if is_us_or_uk_title(title)]

                                    # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                    if us_uk_short_non_friendly_short_classic_data:
                                        directions.append("left")
                                        criteria.append("US/UK Titles")
                                        recommended_titles = us_uk_short_non_friendly_short_classic_data
                                # If the user wants to watch a title from another country outside the US/UK, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                                elif country_preference == "no":
                                    other_short_non_friendly_short_classic_data = [title for title in non_friendly_classic_short_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                                  country.strip().lower() not in ["united states", "united kingdom"] for country in
                                  title.country.lower().split(', '))]
                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_short_non_friendly_short_classic_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_short_non_friendly_short_classic_data
                                else:
                                    print("No recommended titles found based on this country preference in combination with the non_friendly_classic_short_data criteria")

                        # If the user want to watch a long movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                        elif duration_preference == "no":
                            non_friendly_classic_long_data = decide_title_type(selected_title, duration_preference, classic_non_child_friendly_data)
                            # If there is non_friendly_classic_long_data, then add a right direction and the corresponding criteria to the list
                            if non_friendly_classic_long_data:
                                directions.append("right")
                                criteria.append("Long Titles")
                                recommended_titles = non_friendly_classic_long_data

                                # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                                if country_preference == "yes":
                                    us_uk_long_non_friendly_long_classic_data = [title for title in non_friendly_classic_long_data if is_us_or_uk_title(title)]

                                    # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                    if us_uk_long_non_friendly_long_classic_data:
                                        directions.append("left")
                                        criteria.append("US/UK Titles")
                                        recommended_titles = us_uk_long_non_friendly_long_classic_data
                                # If the user wants to watch a title from another country outside the US/UK, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                                elif country_preference == "no":
                                    other_non_friendly_long_classic_data = [title for title in non_friendly_classic_long_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(country.strip().lower() not in ["united states", "united kingdom"] for country in
                                  title.country.lower().split(', '))]
                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_non_friendly_long_classic_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_non_friendly_long_classic_data
                                else:
                                    print("No recommended titles found based on this country preference in combination with the non_friendly_classic_long_data criteria")

                # If the user does not want to watch a classic movie/season, create a new list of titles that were released after year 2010
                elif classic_preference == "no":
                    non_classic_non_child_friendly_data = [title for title in non_child_friendly_data if title.release_year > 2010]
                    # If there is non_classic_non_child_friendly_data, then add a right direction and the corresponding criteria to the list
                    if non_classic_non_child_friendly_data:
                        directions.append("right")
                        criteria.append("Non-Classic Titles")
                        recommended_titles = non_classic_non_child_friendly_data

                        # If the user wants to watch a short movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                        if duration_preference == "yes":
                            non_friendly_modern_short_data = decide_title_type(selected_title, duration_preference, non_classic_non_child_friendly_data)
                            # If there is non_friendly_modern_short_data, then add a left direction and the corresponding criteria to the list
                            if non_friendly_modern_short_data:
                                directions.append("left")
                                criteria.append("Short Titles")
                                recommended_titles = non_friendly_modern_short_data

                                # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                                if country_preference == "yes":
                                    us_uk_short_non_friendly_modern_short_data = [title for title in non_friendly_modern_short_data if is_us_or_uk_title(title)]

                                    # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                    if us_uk_short_non_friendly_modern_short_data:
                                        directions.append("left")
                                        criteria.append("US/UK Titles")
                                        recommended_titles = us_uk_short_non_friendly_modern_short_data
                                # If the user wants to watch a title from another country outside the US/UK, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                                elif country_preference == "no":
                                    other_short_non_friendly_modern_short_data = [title for title in non_friendly_modern_short_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                                  country.strip().lower() not in ["united states", "united kingdom"] for country in
                                  title.country.lower().split(', '))]
                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_short_non_friendly_modern_short_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_short_non_friendly_modern_short_data
                                else:
                                    print("No recommended titles found based on this country preference in combination with the non_friendly_modern_short_data criteria")

                        # If the user wants to watch a long movie/season, call the function decide_title_type to decide whether the title is a movie or a tv show and then filter the titles based on the corresponding duration
                        elif duration_preference == "no":
                            non_friendly_modern_long_data = decide_title_type(selected_title, duration_preference, non_classic_non_child_friendly_data)
                            # If there is non_friendly_modern_long_data, then add a right direction and the corresponding criteria to the list
                            if non_friendly_modern_long_data:
                                directions.append("right")
                                criteria.append("Long Titles")
                                recommended_titles = non_friendly_modern_long_data

                                # If the user wants to watch a title from the US or the UK, create a new list of titles that have the country listed as "United States" or "United Kingdom" (or both)
                                if country_preference == "yes":
                                    us_uk_non_friendly_modern_long_data = [title for title in non_friendly_modern_long_data if is_us_or_uk_title(title)]

                                    # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                    if us_uk_non_friendly_modern_long_data:
                                        directions.append("left")
                                        criteria.append("US/UK Titles")
                                        recommended_titles = us_uk_non_friendly_modern_long_data
                                # If the user wants to watch a title from another country outside the US/UK, create a new list of titles that have the country listed as something other than "United States" or "United Kingdom"
                                elif country_preference == "no":
                                    other_non_friendly_modern_long_data = [title for title in non_friendly_modern_long_data if title.country is not None and title.country.lower() not in ["united states", "united kingdom"] and all(
                                  country.strip().lower() not in ["united states", "united kingdom"] for country in
                                  title.country.lower().split(', '))]
                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_non_friendly_modern_long_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_non_friendly_modern_long_data
                                else:
                                    print("No recommended titles found based on this country preference in combination with the non_friendly_modern_long_data criteria")


    # Call the function build_path to build the path based on the directions and criteria and create new node objects
    # Only called here because it's always going to take 1 certain path and will end up here, this way it's only called once
    new_node = build_path(node, directions, criteria, recommended_titles)

    return new_node


# It is only called in the main function to get the recommended titles with the decision tree logic
# Then it will be called recursively to transverse the tree and get the recommended titles
def get_recommended_titles(node, num_suggestions):
    recommended_titles = []
    # print(f'Recommended titles so far {len(node.recommended_titles)} at node {node.criterion}')

    # base case: if node is None, return an empty list
    if node is None:
        return recommended_titles

    # explore left tree for possible recommendations
    print(f"Exploring left child of node {node.criterion}.")
    # recursive call to get recommended titles from left child
    left_recommended = get_recommended_titles(node.left_child, num_suggestions)
    recommended_titles.extend(left_recommended)
    print(f"Recommended found left side: {len(left_recommended)}")

    # add titles from current node to recommended titles list (from one or either side of the tree)
    if node.recommended_titles:
        recommended_titles.extend(node.recommended_titles)

    # explore right tree for possible recommendations
    print(f"Exploring right child of node {node.criterion}.")
    # recursive call to get recommended titles from right child
    right_recommended = get_recommended_titles(node.right_child, num_suggestions)
    recommended_titles.extend(right_recommended)
    print(f"Recommended found right side: {len(right_recommended)}")

    # Remove duplicates from the list
    recommended_titles = list(set(recommended_titles))

    # is keeping score how many recommended titles are found so far in total (from left, right and current node)
    print(f"Recommended titles so far: {len(recommended_titles)}")

    # return the recommended titles list and limit the amount of suggestions to the user
    return recommended_titles
    # return recommended_titles[:num_suggestions]


# Update the score of the title in the database
def db_update_score(title):
    # Connecting with the db
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
        cursor.execute(f'UPDATE netflix_movies SET score = score + 5 WHERE show_id = {title.show_id};')
        # print(f'Title {title.title} ({title.show_id}) has been scored.')  # Print the new score

        # Commit the changes to the db
        mydb.commit()
        print("Score updated successfully in the database.")

        # Get the updated title from the database AFTER committing the previous changes
        cursor.execute(f'SELECT * FROM netflix_movies WHERE show_id = {title.show_id};')
        # Fetch the updated title in the form of a NetflixTitle object
        updated_title = NetflixTitle(*cursor.fetchone())

        # Print the new score
        print(f'Title {updated_title.title} ({updated_title.show_id}) has been scored. Score of this title is now: {updated_title.score}')

    # Handle errors if any
    except mysql.connector.Error as err:
        print(f"Error updating score in the database: {err}")

    # Close the connection to the db
    finally:
        if mydb:
            cursor.close()
            mydb.close()

# Ask the user to confirm if they want to continue without entering any indices
def confirm_continuation():
    while True:
        confirmation = input("No indices entered. Do you want to continue? (yes/no): ").strip().lower()
        if confirmation not in ("yes", "y"):
            print("Skipping scoring titles.")
            return False
        else:
            return True

def incorporate_user_feedback(recommended_titles, valid_indices):
    # Loop through the indexes and update the score of the title in the database
    for index in valid_indices:
        if 1 <= index <= len(recommended_titles):  # Check if the index is within the range of the recommended titles
            title = recommended_titles[index - 1]
            # Call the function to update the score of the title within the database
            db_update_score(title)
        else:
            print(f"Invalid index: {index}. Skipping this index.")  # Index out of bounds

# Get user input for the scores of the recommended titles, this will be used to calculate the score of the titles
def get_user_scores(recommended_titles):
    while True:
        # Ask the user to enter the indices of the titles they want to score
        user_input = input("Enter the indices of the titles you want to score (e.g., '1, 2, 4'): ").strip().lower()
        # print(f'User input: {user_input}')

        # If there's no input form the user, ask for confirmation to continue
        if not user_input:
            if confirm_continuation():
                continue
            else:
                return None  # Exit the function if the user doesn't want to continue

        try:
            selected_indices = [int(idx.strip()) for idx in user_input.split(",")]
            # If the index is within the range of the recommended titles then it's a valid index
            valid_indices = [idx for idx in selected_indices if 1 <= idx <= len(recommended_titles)]
            # If the length of the valid indices is equal to the length of the selected indices then break the loop
            if len(valid_indices) == len(selected_indices):
                incorporate_user_feedback(recommended_titles, valid_indices)
                return valid_indices
            else:
                print("Invalid input. Please enter valid indices.")  # Invalid indices, retry
        except ValueError:
            print("Invalid input. Please enter valid indices (positive integers).")  # Invalid input, retry

def get_flexible_title_query():
    global query_results
    global selected_titles

    query_results = []

    while True:  # Loop until we get valid scores or the user exits

        search_title = input("Enter the (a part of the) title you'd want to search to recommend: ").strip().lower()

        if not search_title:
            confirmation = input("No title entered. Do you want to continue? (yes/no): ").strip().lower()
            if confirmation not in ("yes", "y"):
                print("Skipping scoring titles.")
                return None

        # Debug print statement
        # print(f'Searching for titles with the query: {search_title}')
        query_results = get_user_query_title_from_db(search_title)

        if query_results:
            score_confirmation = input("Do you want to score any of these titles? (yes/no): ").strip().lower()
            if score_confirmation.isdigit():
                print("Invalid input, please enter yes or no.")
            elif score_confirmation in ("yes", "y"):
                try:
                    choice = input(
                        "Enter the indices of the titles you want to score of the query results (e.g., '1, 2, 4'): ")
                    selected_indices = [int(idx.strip()) for idx in choice.split(",")]
                    valid_indices = [idx - 1 for idx in selected_indices if
                                     1 <= idx <= len(query_results)]  # Subtract 1 for indexing

                    if len(valid_indices) == len(selected_indices):
                        selected_titles = [query_results[idx] for idx in valid_indices]
                        print("You have selected the following titles for scoring:")
                        for title in selected_titles:
                            print(
                                f"The following title will be scored: {title.title}, Show-ID: {title.show_id}, "
                                f"Jaccard Similarity: {title.jaccard_similarity}, Score: {title.score}")  # Do your
                            # scoring logic with each title
                            db_update_score(title)  # Update the score of the title in the database
                        break  # Break out of the loop if input is valid
                    else:
                        print("Invalid input. Please enter valid indices.")
                except ValueError:
                    print("Invalid input. Please enter valid indices (positive integers).")
            else:
                print("Skipping scoring titles.")
        else:
            print("No titles found based on the search query.")
            return None

















