#Developed by: Nina Schrauwen
#Description: This is the decision tree file of the Netflix recommendation system. This file contains the decision tree class and functions to build the decision tree and get recommendations based on user input.
#Date: 11/04/2024

# Import necessary libraries
import random
import mysql
import mysql.connector
import time
from title import NetflixTitle

# Global variables
child_friendly_preference = None
classic_preference = None
duration_preference = None
country_preference = None
directions = []
criteria = []
criterion = None
recommended_titles = []
threshold = 0.0
recommended_threshold = 0.015
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

    # Define __str__ method to print information about the node to be able to check the decision tree process
    def __str__(self):
        return f"Criterion: {self.criterion}\n" \
               f"Left Child: {self.left_child}\n" \
               f"Right Child: {self.right_child}\n" \
            # f"Recommended Titles: {self.recommended_titles}\n"

# Function to retrieve all scored titles from the db and use this input for the calculation of the jaccard similarity
def get_scored_titles_from_db():
    scored_titles = []

    # Try to connect to the database and fetch the scored titles
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
        cursor.execute("SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM test_netflix_movies WHERE score != 0")

        # Fetch all the rows
        rows = cursor.fetchall()

    # Catch any errors that might occur
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Close the database connection once the data has been fetched
    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    # Loop through the rows and create NetflixTitle objects to store in a list
    for row in rows:
        scored_titles.append(NetflixTitle(*row))

    # Return the scored titles to later be able to determine the jaccard similarity scores
    return scored_titles


# Function to retrieve all non-scored titles from the db and use this input for the calculation of the jaccard similarity
def get_non_scored_titles_from_db():
    non_scored_titles = []

    # Try to connect to the database and fetch the non-scored titles
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
        cursor.execute("SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM test_netflix_movies WHERE score = 0")

        # Fetch all the rows
        rows = cursor.fetchall()

    # Catch any errors that might occur
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Close the database connection once the data has been fetched
    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    # Loop through the rows and create NetflixTitle objects to store in a list
    for row in rows:
        non_scored_titles.append(NetflixTitle(*row))

    # Return the non-scored titles to later be able to determine the jaccard similarity scores
    return non_scored_titles

# Function to update the jaccard similarity scores in the database, designed to only update the jaccard similarity
# scores that have changed or that have not been set yet.
def update_jaccard_similarity(jaccard_data):
    updated_jaccard_titles = []

    # Try to connect to the database and update the jaccard similarity scores
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

        # Retrieve all titles and their current jaccard similarity scores from the database
        # Whether a jaccard score is set or not is irrelevant at this point
        cursor.execute("SELECT title, jaccard_similarity FROM test_netflix_movies")
        current_jaccard_data = cursor.fetchall()

        # Create a dictionary to map the titles to their current jaccard similarity scores
        current_jaccard_dict = {title: jaccard_similarity for title, jaccard_similarity in current_jaccard_data}

        update_count = 0 # Initialize a counter to count the number of rows updated
        titles_to_update = [] # Create a list to store all titles to update

        # Extract the title and jaccard similarity from the jaccard dictionary
        for title, jaccard_similarity in jaccard_data.items():
            # Get the existing jaccard similarity score for the title, otherwise it'll be set to 0
            existing_score = current_jaccard_dict.get(title, 0)

            # Check if the existing score is 0 and if jaccard similarity is not 0
            if existing_score == 0 and existing_score != jaccard_similarity:
                # Append the title and jaccard similarity to the list of titles to update
                titles_to_update.append((jaccard_similarity, title))
                print(f"New score; {existing_score} to {jaccard_similarity} with title: {title}")
            # Check if the existing score is different from the new jaccard similarity score
            elif existing_score != jaccard_similarity:
                # Append the title and jaccard similarity to the list of titles to update
                titles_to_update.append((jaccard_similarity, title))
                print(f"Score changed from {existing_score} to {jaccard_similarity} with title: {title}")

        # Loop through the titles to update and update the jaccard similarity scores in the database
        for titles in titles_to_update:
            cursor.execute(
                "UPDATE test_netflix_movies SET jaccard_similarity = %s WHERE title = %s;", (titles[0], titles[1])
            )
            # Increment the update count to keep track of the number of rows updated
            update_count += 1

        # Commit the transaction to update the jaccard similarity scores
        mydb.commit()
        print(f"Number of rows updated: {update_count}") # Print the number of rows updated

        # Execute the SQL query to select titles with jaccard scores above 0
        select_query = "SELECT show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, score, jaccard_similarity FROM test_netflix_movies WHERE jaccard_similarity > 0"
        # Execute the select query to get the updated jaccard similarity scores
        cursor.execute(select_query)
        # Fetch all the rows and store them in a list of NetflixTitle objects
        updated_jaccard_titles = [NetflixTitle(*row) for row in cursor.fetchall()]

        print(f"Number of positive jaccard titles found AFTER updating: {len(updated_jaccard_titles)}")

        # If there are updated jaccard titles, then print a message that the titles are being updated
        if updated_jaccard_titles:
            print(f'Titles are being updated with the jaccard similarity scores.')
        else:
            print("No positive jaccard titles found.")

    # Catch any errors that might occur
    except Exception as e:
        print("Error:", e)

    # Close the database connection once the data has been fetched
    finally:
        # Close the database connection
        if mydb.is_connected():
            cursor.close()
            mydb.close()

    return updated_jaccard_titles

# Function to calculate the Jaccard similarity between two sets by taking the intersection and union of the two sets
def calculate_jaccard_similarity(set1, set2):
    # Calculate the intersection and union of the two sets
    intersection = len(set1.intersection(set2))
    # Calculate the union of the two sets
    union = len(set1.union(set2))
    # Intersection is divided by the union of the two sets to get the jaccard similarity score, if the union is not 0
    return intersection / union if union != 0 else 0

# Compare the scored titles and their cast to the non-scored titles and their cast to get the jaccard similarity scores
def get_recommendations_based_on_similarity(scored_titles, non_scored_titles):
    # Define the jaccard similarities scored and non-scored lists to fill with the jaccard similarity scores
    jaccard_similarities_scored = []
    jaccard_similarities_non_scored = []

    # Loop through the scored titles and non-scored titles to calculate the jaccard similarity
    for scored_title in scored_titles:
        # Split the cast by comma and create a set of scored cast members, if empty set to an empty set
        scored_cast = set(scored_title.cast.split(",")) if scored_title.cast else set()
        # Loop through the non-scored titles to calculate the jaccard similarity
        for non_scored_title in non_scored_titles:
            # Split the cast by comma and create a set of non-scored cast members, if empty set to an empty set
            non_scored_cast = set(non_scored_title.cast.split(",")) if non_scored_title.cast else set()
            # Calculate the jaccard similarity score between the scored and non-scored cast members (Intersection/Union)
            similarity_score = calculate_jaccard_similarity(scored_cast, non_scored_cast)
            # Append the scored title with the similarity score to the jaccard similarities scored list
            jaccard_similarities_scored.append((scored_title.title, similarity_score))
            # Append the non-scored title with the similarity score to the jaccard similarities non-scored list
            jaccard_similarities_non_scored.append((non_scored_title.title, similarity_score))

    # Return both lists in order to be able to update (and to use) the jaccard similarity scores in the database and
    # application later on
    return jaccard_similarities_scored, jaccard_similarities_non_scored


# Function to filter out the positive similarity scores in the jaccard similarities list in order to update the jaccard similarity scores in the database later on
def filter_positive_similarity_scores(jaccard_similarities, threshold):
    positive_scores = {} # Initialize an empty dictionary to store the positive similarity scores

    # Loop through the outer list to get access to the inner tuple containing the title and the jaccard similarity
    for inner_tuple in jaccard_similarities:
        # Unpack the inner tuple to get access to the title and the jaccard similarity
        for title, jaccard_similarity in inner_tuple:
            try:
                if jaccard_similarity != threshold:  # If the jaccard similarity does not equal the threshold (0) then add it to the dictionary
                    positive_scores[title] = jaccard_similarity
            # Handle the ValueError if the jaccard similarity is not a float
            except ValueError:
                print(f"Invalid score value: {jaccard_similarity}")

    # If there are no positive similarity scores found, then print a message to the console
    if not positive_scores:
        print("No positive similarity scores found.")

    # Print the amount of positive similarity scores
    print(f"Amount of positive similarity scores: {len(positive_scores)}")

    return positive_scores

# Function to retreive user input from the gui.py to use as the user preferences
def get_user_input(child_friendly, classic, duration, country):
    # Set the global variables to the user input to be able to use them in the decision tree
    global child_friendly_preference
    global classic_preference
    global duration_preference
    global country_preference

    # Set the global variables to the user input from the gui to be able to use them in the decision tree
    child_friendly_preference = child_friendly
    classic_preference = classic
    duration_preference = duration
    country_preference = country

    # Print the user preferences to the console to check if the input is correct
    print(f'--- User Preferences ---')
    print(f'--- Child-Friendly Preference {child_friendly_preference} ---')
    print(f'--- Classic Preference {classic_preference} ---')
    print(f'--- Duration Preference {duration_preference} ---')
    print(f'--- Country Preference {country_preference} ---')

    # Return the user preferences to be able to use them in the decision tree
    return child_friendly_preference, classic_preference, duration_preference, country_preference

# Function to build the decision tree based on the user input and the Netflix data
def build_decision_tree(netflix_data, selected_title, num_suggestions, child_friendly_preference, classic_preference, duration_preference, country_preference):
    # Define the root node of the decision tree
    root = DecisionTreeNode(criterion="Initial Criterion")
    # Get the user input to use as the user preferences
    get_user_input(child_friendly_preference, classic_preference, duration_preference, country_preference)

    # Call the recursive build tree function to build the decision tree based on the user input and the Netflix data
    recursive_build_tree(root, netflix_data, selected_title, child_friendly_preference, classic_preference, duration_preference, country_preference)
    print(f'Root: {root}')
    return root


# Function to build the path of the decision tree based on the directions and criteria, it is made recursively in order to define the whole path of the decision tree
def build_path(node, directions, criteria, recommended_titles):
    # if there are no directions left, then return the node with the recommended titles
    if not directions:
        node.recommended_titles = recommended_titles
        return node

    # pop the first element of the list to get the current criterion to process
    criterion = criteria.pop(0)

    # pop the first element of the list to get the current direction to process
    direction = directions.pop(0)

    # if the direction is not left or right, then raise a ValueError
    if direction not in ['left', 'right']:
        raise ValueError(f"Invalid direction: {direction}. Only 'left' or 'right' are allowed.")

    # if the direction is left, then create a new node and set it to the left child of the current node
    if direction == 'left':
        if node.left_child is None:
            node.left_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then append a left child to the current node and then recurse with that node
        else:
            node.left_child.criterion = criterion
            node.left_child.recommended_titles = recommended_titles
        build_path(node.left_child, directions, criteria, recommended_titles)

    # if the direction is right, then create a new node and set it to the right child of the current node
    elif direction == 'right':
        if node.right_child is None:
            node.right_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then append a right child to the current node and then recurse with that node
        else:
            node.right_child.criterion = criterion
            node.right_child.recommended_titles = recommended_titles
        build_path(node.right_child, directions, criteria, recommended_titles)

    # Otherwise there is an invalid direction so raise a value error
    else:
        raise ValueError(f"Invalid direction: {direction}. Only 'left' or 'right' are allowed.")

    # Return the node to be able to use it in the decision tree
    return node


# Function to determine whether the title is a movie or a tv show and then filter based on the duration preference
def decide_title_type(selected_title, duration_preference, previous_titles):
    # Set the new_titles list to an empty list
    new_titles = []

    # If the selected title is a movie, then filter the titles based on minutes
    # Less than or equal to 80 minutes or more than 80 minutes, depending on the duration preference
    if selected_title.type.lower() == "movie":
        if duration_preference == "yes":
            new_titles = [title for title in previous_titles if int(title.duration.split()[0]) <= 80]
        elif duration_preference == "no":
            new_titles = [title for title in previous_titles if int(title.duration.split()[0]) > 80]
    # If the selected title is a tv show, then filter the titles based on the number of seasons
    # One or more season in this case, depending on duration preference
    elif selected_title.type.lower() == "tv show":
        if duration_preference == "yes":
            new_titles = [title for title in previous_titles if int(title.duration.split()[0]) == 1]
        elif duration_preference == "no":
            new_titles = [title for title in previous_titles if int(title.duration.split()[0]) > 1]
    else:
        # If the title type is not defined as a movie or tv show then print an error message and return an empty list
        print("Invalid duration input")
        return []

    # Return the list of titles filtered based on the duration preference
    return new_titles

# Filter the recommended titles based on the threshold and the number of suggestion, if there are no titles that have been scored yet remaining titles will be added to the list
def filter_recommended_titles(recommended_titles, threshold, num_suggestions):
    # Filter the recommended titles based on the threshold, make sure the jaccard similarity is not None and is
    # greater than the threshold (0.015)
    filtered_titles = [title for title in recommended_titles if title.jaccard_similarity is not None and title.jaccard_similarity > threshold]

    # Initialize the scored and unscored titles lists to fill later
    scored_titles = []
    unscored_titles_jaccard = []
    unscored_titles = []

    print(f'(Before) Length of filtered titles: {len(filtered_titles)}')

    # If not enough titles are found based on the threshold, then add back titles from the recommended_titles list (without the threshold)
    if len(filtered_titles) < num_suggestions:
        filtered_titles.extend(recommended_titles[:num_suggestions - len(filtered_titles)])

    print(f'Length of filtered titles: {len(filtered_titles)}')

    # Filter out all the duplicate entries from the filtered titles list
    filtered_titles = list(set(filtered_titles))

    # Print the filtered titles to check in the console, see if the filtering is working correctly
    print(f'--- Filtered Titles ---')
    for title in filtered_titles:
        print(
            f'Filtered Title: {title.title}, Show-ID: {title.show_id}, Jaccard Similarity: {title.jaccard_similarity}, Score: {title.score}')

    # Loop through the filtered titles to determine which titles are scored, unscored, or have a jaccard similarity
    for title in filtered_titles:
        # If the score is 0 and the jaccard similarity is greater than 0 add to the unscored titles jaccard list
        if title.score == 0 and title.jaccard_similarity > 0:
            unscored_titles_jaccard.append(title)
            # Because the titles have already surpassed the requirements of the score, shuffle them to avoid repetition
            random.shuffle(unscored_titles_jaccard) # Shuffle the list to get a random selection of titles to avoid repetition of the same exact titles at the top of the list
        # If the score is greater than 0, then add to the scored titles list
        elif title.score > 0:
            scored_titles.append(title)
            # Because the titles have already surpassed the requirements of the score, shuffle them to avoid repetition
            random.shuffle(scored_titles)
        # If the score is 0 and the jaccard similarity is 0, then add to the unscored titles list
        elif title.score == 0 and title.jaccard_similarity == 0:
            unscored_titles.append(title)
            # Because the titles have already surpassed the requirements of the score, shuffle them to avoid repetition
            random.shuffle(unscored_titles)
        else:
            print(f"Title {title.title} does not match the score requirements. Score: {title.score}, Jaccard: {title.jaccard_similarity}.")

    # Print the scored, unscored, and unscored titles jaccard to check in the console
    print(f'Length of scored titles: {len(scored_titles)}')
    print(f'Length of unscored titles: {len(unscored_titles_jaccard)}')

    # Define the final titles list to fill with the final recommendations
    final_titles = []
    # If there are scored titles, then add 2 (shuffled) scored titles to the final titles list
    final_titles.extend(scored_titles[:2])

    # Figure out how many remaining spots are left to fill
    remaining_spots = num_suggestions - len(final_titles)
    # If there are remaining spots left to fill, then add the remaining jaccard similarity (shuffled) titles to the final
    # titles list
    if remaining_spots > 0:
        final_titles.extend(unscored_titles_jaccard[:remaining_spots])

    # Figure out how many remaining spots are left to fill
    remaining_spots = num_suggestions - len(final_titles)

    # If there are remaining spots left to fill, then add the remaining unscored (shuffled) titles to the final
    if remaining_spots > 0:
        final_titles.extend((unscored_titles[:remaining_spots]))

    # Print final set of titles to check in the console
    print(f'--- ! Final Titles ! ---')
    for title in final_titles:
        print(f'Final Title: {title.title}, Show-ID: {title.show_id}, Jaccard Similarity: {title.jaccard_similarity}, Score: {title.score}')

    # Return the final titles limited to the number of suggestions
    return final_titles[:num_suggestions]

# Checks if the number of recommendations are reached
def check_reached_num_suggestions(recommended_titles, num_suggestions):
    # If the number of recommendations is greater than or equal to the number of suggestions, then print a message stating that the desired number of recommendations has been reached
    if len(recommended_titles) >= num_suggestions:
        print(f'Desired number of recommendations reached; {len(recommended_titles)} asked: {num_suggestions}')
    # If the number of recommendations is less than the number of suggestions, then print a message stating that the desired number of recommendations has not been reached
    else:
        print(f'Cannot retrieve desired number of recommendations based on current filters, current length: {len(recommended_titles)} asked: {num_suggestions}')

# Function to search if there is A substring that matches US or UK in the country attribute of the title.country
# This means 'Belgium, France, UK' is also a possible match because it contains 'UK'
def is_us_or_uk_title(title):
    # Search the country attribute of the title for the substring 'US' or 'UK' and return True if found to later filter the titles based on the country preference
    return title.country and any(country.strip().lower() in ["united states", "united kingdom"] for country in title.country.lower().split(', '))

# Function to search if there is A substring that matches US or UK in the country attribute of the title.country
def is_outside_us_uk_title(title):
    # Search the country attribute of the title for the substring 'US' or 'UK' and return True if NOT found to later filter the titles based on the country preference
    return title.country is not None and all(country.strip().lower() not in ["united states", "united kingdom"] for country in title.country.lower().split(', '))

# Function to build the decision tree based on the user input and the Netflix data to be able to filter the recommended titles
def recursive_build_tree(node, netflix_data, selected_title, child_friendly_preference, classic_preference, duration_preference, country_preference):
    # Set the global variables to be able to use them in the decision tree
    global directions
    global criterion
    global criteria
    global recommended_titles

    # Set some variables to an empty list to be able to use them in the decision tree
    directions = []
    criteria = []
    recommended_titles = []

    # If directions have not been set yet, then set them to an empty list
    if directions is None:
        directions = []

    # Root node of the decision tree
    if node.criterion == "Initial Criterion":
        # Filter out the selected title from the Netflix data to make sure the selected title is not recommended
        altered_netflix_data = [title for title in netflix_data if title.show_id != selected_title.show_id]

        # Recommend titles based on (any of) the genre(s) that the selected title belongs to
        similar_genre_data = [title for title in altered_netflix_data if any(
            genre.lower() in title.listed_in.lower() for genre in selected_title.listed_in.split(','))]

        # If the sample title is a movie, then recommend movie titles
        if selected_title.type.lower() == "movie":
            # Loop through the similar genre data to get the titles that are movies
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "movie"]
        # If the sample title is a tv show, then recommend tv show titles
        elif selected_title.type.lower() == "tv show":
            # Loop through the similar genre data to get the titles that are tv shows
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "tv show"]
        # If the title type is not defined as a movie or tv show then print an error message
        else:
            print('Invalid title type')
            return

        # If no titles are found that have the same genre and type as the sample title print a message to the console
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

                                # If the user wants to watch a title from the US or the UK, call the function is_us_or_uk_title to find out whether the title is from the US/UK and if that returns true then filter the titles based on the country preference
                                if country_preference == "yes":
                                    us_uk_short_classic_data = [title for title in short_classic_data if is_us_or_uk_title(title)]

                                    # Add the new list of filtered US/UK titles into a decision tree node on the left side
                                    if us_uk_short_classic_data:
                                        directions.append("left")
                                        criteria.append("US/UK Titles")
                                        recommended_titles = us_uk_short_classic_data

                                # If the user wants to watch a title from another country outside the US/Uk, call the function is_us_or_uk_title to find out whether the title is from the US/UK and if that returns true then filter the titles based on the country preference
                                elif country_preference == "no":
                                    other_short_classic_data = [title for title in short_classic_data if is_outside_us_uk_title(title)]

                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_short_classic_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_short_classic_data
                                else:
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
                                    other_long_classic_data = [title for title in long_classic_data if is_outside_us_uk_title(title)]

                                    # Add the new list of filtered other country titles into a decision tree node on the right side
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
                                    other_short_non_classic_data = [title for title in non_classic_short_data if is_outside_us_uk_title(title)]

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
                                    other_non_classic_long_data = [title for title in non_classic_long_data if is_outside_us_uk_title(title)]

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
                                    other_short_non_friendly_short_classic_data = [title for title in
                                                                                   non_friendly_classic_short_data if is_outside_us_uk_title(title)]

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
                                    other_non_friendly_long_classic_data = [title for title in
                                                                            non_friendly_classic_long_data if is_outside_us_uk_title(title)]

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
                                    other_short_non_friendly_modern_short_data = [title for title in
                                                                                  non_friendly_modern_short_data if is_outside_us_uk_title(title)]

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
                                    other_non_friendly_modern_long_data = [title for title in
                                                                           non_friendly_modern_long_data if is_outside_us_uk_title(title)]

                                    # Add the new list of filtered other country titles into a decision tree node on the right side
                                    if other_non_friendly_modern_long_data:
                                        directions.append("right")
                                        criteria.append("Other Titles")
                                        recommended_titles = other_non_friendly_modern_long_data
                                else:
                                    print("No recommended titles found based on this country preference in combination with the non_friendly_modern_long_data criteria")


    # Call the function build_path to build the path based on the directions and criteria and create new node objects
    # Only called here because it's always going to take 1 certain path (due to the decision tree structure) and collect all the data needed due to the collection of the directions, criteria and recommended_titles
    build_path(node, directions, criteria, recommended_titles)

    return node

# Is being called when the nodes are being created to build the path based on the directions and criteria
# Then it will be called recursively to transverse the tree and get the recommended titles
def get_recommended_titles(node, num_suggestions):
    recommended_titles = []

    # If the node is None then return the recommended titles
    if node is None:
        return recommended_titles

    print(f"Exploring left child of node {node.criterion}.")
    # explore left tree for possible recommendations
    # recursive call to get all possible recommended titles from left child
    left_recommended = get_recommended_titles(node.left_child, num_suggestions)
    # add the left recommended titles to the recommended titles list
    recommended_titles.extend(left_recommended)
    print(f"Recommended found left side: {len(left_recommended)}")

    # add titles from current node to recommended titles list (from one or either side of the tree)
    if node.recommended_titles:
        recommended_titles.extend(node.recommended_titles)

    print(f"Exploring right child of node {node.criterion}.")
    # explore right tree for possible recommendations
    # recursive call to get recommended titles from right child
    right_recommended = get_recommended_titles(node.right_child, num_suggestions)
    # add the right recommended titles to the recommended titles list
    recommended_titles.extend(right_recommended)
    print(f"Recommended found right side: {len(right_recommended)}")

    # Remove duplicates from the list
    recommended_titles = list(set(recommended_titles))

    # is keeping score how many recommended titles are found so far in total
    print(f"Recommended titles so far: {len(recommended_titles)}")

    # return the recommended titles
    return recommended_titles


# Update the score of the title in the database based on the show_id
def db_update_score(show_id):
    # Try to connect to the database and update the score of the title
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            port="8080",
            user="Admin",
            password="Brownie#99",
            database="netflix_titles"
        )
        # Create a cursor object to interact with the database
        cursor = mydb.cursor()

        # Increment the score by 5 for the given title
        cursor.execute(f'UPDATE test_netflix_movies SET score = score + 5 WHERE show_id = {show_id};')

        # Commit the changes to the db
        mydb.commit()
        print("Score updated successfully in the database.")

        # Get the updated title from the database AFTER committing the previous changes so that the updated score is fetched
        cursor.execute(f'SELECT * FROM test_netflix_movies WHERE show_id = {show_id};') # Replaced with test_netflix_movies to test without pre existing data

        # Fetch the updated title as a NetflixTitle object
        updated_title = NetflixTitle(*cursor.fetchone())

        # Print the new score
        print(f'Title {updated_title.title} ({updated_title.show_id}) has been scored. Score of this title is now: {updated_title.score}')

    # Handle errors if they occur
    except mysql.connector.Error as err:
        print(f"Error updating score in the database: {err}")

    # Close the connection to the db after the queries have been executed
    finally:
        if mydb:
            cursor.close()
            mydb.close()

# Function to be able to score the selected recommendations based on their show_id's and update the score in the database
def incorporate_user_feedback(show_ids):
    # Loop through the show_ids and update the score of the title in the database via the db_update_score function
    for show_id in show_ids:
        db_update_score(show_id)

# Function to bring several functions together to calculate and update the jaccard similarity scores in the database
def process_recommendations(threshold):
    # Start the timer to calculate the elapsed time
    start_time = time.time()
    # Get scored titles from the database
    scored_titles = get_scored_titles_from_db()
    # Get non-scored titles from the database
    non_scored_titles = get_non_scored_titles_from_db()

    # Calculate jaccard similarity based on scored and non-scored titles to identify a pattern of user preferences in
    # casting
    jaccard_similarities = get_recommendations_based_on_similarity(scored_titles, non_scored_titles)
    # Filter out only the positive similarity scores
    positive_scores = filter_positive_similarity_scores(jaccard_similarities, threshold)
    # Update only the values that are new or have been changed by using the update_jaccard_similarity function
    updated_jaccard_scores = update_jaccard_similarity(positive_scores)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print(f" !-!-! Elapsed time to update the jaccard similarity scores in the database: {elapsed_time} seconds !-!-!")
    print(f'Lenght of updated jaccard scores: {len(updated_jaccard_scores)}')













