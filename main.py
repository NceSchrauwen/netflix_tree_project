#Developed by: Nina Schrauwen
#Date: 11/04/2024
#Description: This is the main file of the Netflix recommendation system. It connects to the database, retrieves the Netflix titles, and selects a random title. It then builds a decision tree and retrieves the recommended titles.
import tkinter as tk

# Import the necessary functions from the other files
from decision_tree import DecisionTreeNode, build_decision_tree, get_recommended_titles, get_user_scores, recommended_titles, get_scored_titles_from_db, get_non_scored_titles_from_db, get_recommendations_based_on_similarity, filter_positive_similarity_scores, update_jaccard_similarity, threshold, recommended_threshold, filter_recommended_titles, get_flexible_title_query, check_reached_num_suggestions
from gui import create_gui
from other_functions import get_show_id_title, print_title_attributes
from shared import connect_db, clean_slate, print_attributes, new_print_title_attributes, get_sample_title, get_standup_comedy_titles, get_tv_show_titles, get_movie_titles


global netflix_titles
global titles_to_select
global gui_instance # Global variable to store the GUI instance


# All the function calls needed to run the application are placed in the main function
def main():
    # Create the GUI instance to be able to access the selected title
    gui_instance = create_gui()

    # def get_selected_title(event=None):
    #     # Get the selected title from the GUI
    #     selected_title = gui_instance.on_double_click(event)
    #     if selected_title:
    #         # Print the attributes of the selected title
    #         print("-- Selected title: --")
    #         print(
    #             f"Title: {selected_title.title} - Release Year: {selected_title.release_year} - Date Added: {selected_title.date_added} - Listed In: {selected_title.listed_in} - Type: {selected_title.type}")
    #     return selected_title

    # # Bind the function to an event in the GUI
    # gui_instance.treeView.bind("<Double-1>", get_selected_title)

    # Connect to the database and retrieve the Netflix titles
    netflix_titles = connect_db(num_results=150)

    # Ensure treeview is populated
    gui_instance.populate_treeview()

    # Run the GUI main loop
    gui_instance.window.mainloop()

    # Get the selected title after the GUI main loop has finished
    selected_title = gui_instance.selected_title

    if selected_title == None:
        print("No title selected.")
        return

    # Debug print statements to check if the selected title has been loaded
    # if selected_title:
    #     print(f"!!! Selected title: {selected_title} !!!")
    # else:
    #     print(f"! Failed to load selected title; {selected_title} !")

    # Reset the all scores of all titles to 0
    # clean_slate()

    # original sample title pick function
    # selected_title = get_sample_title(netflix_titles)

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

    # Call it here in order to get the user scores AFTER the recommendations have been printed
    # Switch out the filtered_recommended_titles with recommended_titles to test the function
    get_user_scores(
        filtered_recommended_titles)

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


# Main function to run the application
if __name__ == '__main__':
    main()





