#Developed by: Nina Schrauwen
#Date: 31/05/2024
#Description: Functions that are being called in main.py but are being defined here to keep the code clean and to prevent circular imports.

from other_functions import print_title_attributes
from decision_tree import build_decision_tree, get_recommended_titles, filter_recommended_titles, check_reached_num_suggestions, recommended_threshold
from shared import new_print_title_attributes
import decision_tree

# Function to get the recommendations based on the selected title
def get_recommendations(gui_instance, netflix_titles, num_suggestions):
    # Get the selected title from the GUI
    selected_title = gui_instance.selected_title
    if selected_title == None:
        print("No title selected.")
        return

    # Prints the sample title and its attributes to the console
    print_title_attributes(selected_title)

    # Collect preferences set in the decision_tree module, otherwise it won't work properly in gui.py
    child_friendly = decision_tree.child_friendly_preference
    classic = decision_tree.classic_preference
    duration = decision_tree.duration_preference
    country = decision_tree.country_preference

    # Debug print statements
    # print(f"Child friendly: {child_friendly}, Classic: {classic}, Duration: {duration}, Country: {country}")

    # Build the decision tree
    decision_tree_root = build_decision_tree(netflix_titles, selected_title, num_suggestions, child_friendly, classic, duration, country)

    # Get the recommended titles from the decision tree
    recommended_titles = get_recommended_titles(decision_tree_root, num_suggestions)

    # Check if the recommended titles is None
    if recommended_titles is None:
        print("Error: Recommended titles is None.")

    # Prints the results and the attributes of the recommendations to the console
    # new_print_title_attributes(recommended_titles)

    # Filter the recommended titles based on jaccard_similarity score, use output from decision tree to filter
    filtered_recommended_titles = filter_recommended_titles(recommended_titles, recommended_threshold, num_suggestions)
    # Check if the filtered recommended titles is None
    if filtered_recommended_titles is None:
        print("Error: Filtered recommended titles is None.")

    # Print the filtered recommended titles
    new_print_title_attributes(filtered_recommended_titles)

    # Check if the number of suggestions has been reached
    check_reached_num_suggestions(filtered_recommended_titles, num_suggestions)

    # Populate the recommended titles in the GUI
    gui_instance.populate_rec_titles(filtered_recommended_titles)

    return filtered_recommended_titles