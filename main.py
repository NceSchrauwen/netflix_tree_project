#Developed by: Nina Schrauwen
#Date: 11/04/2024
#Description: This is the main file of the Netflix recommendation system. It connects to the database, retrieves the Netflix titles, and selects a random title. It then builds a decision tree and retrieves the recommended titles.
import tkinter as tk

# Import the necessary functions from the other files
from decision_tree import get_scored_titles_from_db, get_non_scored_titles_from_db, get_recommendations_based_on_similarity, filter_positive_similarity_scores, update_jaccard_similarity, threshold, recommended_threshold, filter_recommended_titles, get_flexible_title_query, check_reached_num_suggestions
from gui import NetflixGUI
from shared import connect_db, clean_slate, print_attributes, new_print_title_attributes, get_sample_title, get_standup_comedy_titles, get_tv_show_titles, get_movie_titles
from recommendations import get_recommendations

global netflix_titles
global gui_instance # Global variable to store the GUI instance

num_suggestions = 4

# All the function calls needed to run the application are placed in the main function
def main():
    # Create the GUI instance to be able to access the selected title
    window = tk.Tk()
    gui_instance = NetflixGUI(window)
    # Connect to the database and retrieve the Netflix titles
    netflix_titles = connect_db(num_results=150)

    # Ensure treeview is populated
    gui_instance.populate_treeview()

    # Set up event handlers for the buttons
    gui_instance.search_button.config(command=lambda: gui_instance.search_title())
    gui_instance.pref_button.config(command=lambda: gui_instance.go_to_preferences())
    gui_instance.recommend_button.config(command=lambda: gui_instance.submit_preferences(netflix_titles, num_suggestions))

    # Calculate and update jaccard similarity scores in the database
    # process_recommendations(threshold)

    # Start the GUI main loop
    window.mainloop()


# Main function to run the application
if __name__ == '__main__':
    main()

# --- Old code snippets ---
# filtered_recommended_titles = get_recommendations(gui_instance, netflix_titles, num_suggestions)
    #
    # # Call it here in order to get the user scores AFTER the recommendations have been printed
    # # Switch out the filtered_recommended_titles with recommended_titles to test the function
    # get_user_scores(
    #     filtered_recommended_titles)
    # TODO: Find a way to incorporate the jaccard_similarities and updated_jaccard_scores while GUI is running
    # # Get the scored titles from the database
    # scored_titles = get_scored_titles_from_db()
    # # Get non-scored titles from the database
    # non_scored_titles = get_non_scored_titles_from_db()
    #
    #
    # # Get the recommendations based on similarity
    # jaccard_similarities = get_recommendations_based_on_similarity(scored_titles, non_scored_titles)
    # # print(f"Similarity score: {jaccard_similarities}")
    #
    # # Return and print all the titles that have a positive similarity score
    # positive_scores = filter_positive_similarity_scores(jaccard_similarities, threshold)
    # # print(f"Filtered positive similarity scores: {positive_scores}")
    #
    # # Update the jaccard similarity scores in the database - DON'T FORGET TO TURN THIS ON TO UPDATE THE DATABASE (but don't forget to turn it off again either due to performance issues)
    # # updated_jaccard_scores = update_jaccard_similarity(positive_scores)
    #
    # # Get the flexible title query and score the queried titles based on the user input
    # get_flexible_title_query()


