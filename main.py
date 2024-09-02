#Developed by: Nina Schrauwen
#Date: 11/04/2024
#Description: This is the main file of the Netflix recommendation system. It connects to the database, retrieves the Netflix titles, and selects a random title. It then builds a decision tree and retrieves the recommended titles.

# Import the necessary functions from the other files
from gui import NetflixGUI
from shared import connect_db
import tkinter as tk

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

    # Start the GUI main loop
    window.mainloop()


# Main function to run the application
if __name__ == '__main__':
    main()




