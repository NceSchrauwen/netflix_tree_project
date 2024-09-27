#Developed by: Nina Schrauwen
#Date: 11/04/2024
#Description: This is the main file of the Netflix recommendation system. It connects to the database, retrieves the Netflix titles, and selects a random title. It then builds a decision tree and retrieves the recommended titles.

# Import the necessary functions from the other files
from gui import NetflixGUI
from shared import connect_db
import tkinter as tk

# Global variables to store the Netflix titles and the GUI instance
global netflix_titles
global gui_instance # Global variable to store the GUI instance

# Desired number of recommendations to be displayed
num_suggestions = 6

# Define the main function and it's functions to run the application
def main():
    # Create the window and the GUI instance
    window = tk.Tk()
    gui_instance = NetflixGUI(window)
    # Connect to the database and to retrieve the Netflix titles
    netflix_titles = connect_db(num_results=150)

    # Ensure treeview is populated
    gui_instance.populate_treeview()

    # Set up event handlers with their corresponding functions
    gui_instance.pref_button.config(command=lambda: gui_instance.go_to_preferences())
    gui_instance.recommend_button.config(command=lambda: gui_instance.submit_preferences(netflix_titles, num_suggestions))

    # Start the GUI main loop
    window.mainloop()

# Main function to run the application
if __name__ == '__main__':
    main()




