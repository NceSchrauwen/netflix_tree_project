#Developed by: Nina Schrauwen
#Description: This is the GUI file of the Netflix recommendation system. This file contains all elements and functionalities of the GUI.
#Date: 17/05/2024

import tkinter as tk
from tkinter import ttk
from db_functions import get_titles_to_select_from_db, get_query_title_from_db
from other_functions import get_show_id_title, print_title_attributes
from shared import connect_db
import decision_tree

global start_index
global end_index


class NetflixGUI:
    def __init__(self, window):
        # Set window title and size
        self.window = window
        self.window.title('Netflix Title Picker')
        self.window.geometry("1200x600")

        # Create a notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(window)
        self.notebook.pack(fill='both', expand=True)

        # Create the first tab
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Netflix Title Selection')

        # Label to display the title of the GUI
        self.label = ttk.Label(self.tab1, text="Netflix Recommendation System", font=("Ariel", 18))
        self.label.pack(pady=10)

        # Create a frame to hold the search bar and labels, buttons, etc
        self.search_frame = ttk.Frame(self.tab1)
        self.search_frame.pack(pady=10)

        self.search_label = ttk.Label(self.search_frame, text="Search for a title:")
        self.search_label.pack(pady=5)

        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', pady=5)

        # TODO: Update README to include the data source and how to set up the local database
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_title)
        self.search_button.pack(side='left', pady=5)

        # Create a frame to hold the Treeview and scrollbars
        tree_frame = ttk.Frame(self.tab1)
        tree_frame.pack(fill="both", expand=True)

        # Create a Treeview widget to display the titles
        self.columns = ("Type", "Title", "Country", "Release Year", "Rating", "Duration", "Listed In")
        self.treeView = ttk.Treeview(tree_frame, columns=self.columns, show='headings')

        # Scrollbar Setup (inside treeview_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeView.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.treeView.xview)

        # Set the scrollbar to the right side of the treeview so that it doesn't wander outside the treeview
        self.treeView.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)  # Allow Treeview to expand vertically
        tree_frame.grid_columnconfigure(0, weight=1)  # Allow Treeview to expand horizontally

        # Configure the Treeview to use the scrollbars
        self.treeView.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths
        for col in self.columns:
            self.treeView.heading(col, text=col) # Set column headings automatically

        # Define the current page and the number of titles to display per page
        self.current_page = 1
        self.titles_per_page = 50

        # Populate the Treeview with data from the database
        self.populate_treeview()

        # Buttons to go to the next and back to the previous page
        self.button = ttk.Button(self.tab1, text="Previous", command=self.prev_page)
        self.button.pack(side="left", pady=20)

        self.button = ttk.Button(self.tab1, text="Next", command=self.next_page)
        self.button.pack(side="left", pady=20)

        self.button = ttk.Button(self.tab1, text="Go to Preferences", command=self.go_to_preferences)
        self.button.pack(side="left", pady=20)

        # Button to trigger built-in function to exit window
        self.button = ttk.Button(self.tab1, text="Exit", command=lambda: self.window.destroy())
        self.button.pack(side="left", pady=20)

        # Set style for the Treeview and buttons (font and theme)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Ariel", 10))
        style.configure("Button", font=("Ariel", 8))
        style.theme_use("clam")

        # Allow the user to double-click on a title to select it
        self.treeView.bind("<Double-1>", self.on_double_click)

        # Attribute to store the selected title
        self.selected_title = None

        # Create the second tab
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Preferences')

        self.tab2_lbl = ttk.Label(self.tab2, text="Recommendation Preferences", font=("Ariel", 18))
        self.tab2_lbl.pack(pady=10)

        # Create a frame to hold the preferences
        self.tab2_frame = ttk.Frame(self.tab2)
        self.tab2_frame.pack(fill="both", expand=True)

        # Add user input widgets for preferences
        self.pg_label = ttk.Label(self.tab2_frame, text="Do you want to watch a child-friendly (under age 13) movie/season? (yes/no):")
        self.pg_label.pack(pady=5)
        self.pg_entry = ttk.Entry(self.tab2_frame, width=30)
        self.pg_entry.pack(pady=5)

        self.classic_label = ttk.Label(self.tab2_frame, text="Do you want to watch a classic movie/season? (yes/no): ")
        self.classic_label.pack(pady=5)
        self.classic_entry = ttk.Entry(self.tab2_frame, width=30)
        self.classic_entry.pack(pady=5)

        self.duration_label = ttk.Label(self.tab2_frame, text="Do you want to watch a short movie/season? (yes/no): ")
        self.duration_label.pack(pady=5)
        self.duration_entry = ttk.Entry(self.tab2_frame, width=30)
        self.duration_entry.pack(pady=5)

        self.country_label = ttk.Label(self.tab2_frame, text="Do you want to watch a movie from the US or the UK? (yes/no): ")
        self.country_label.pack(pady=5)
        self.country_entry = ttk.Entry(self.tab2_frame, width=30)
        self.country_entry.pack(pady=5)

        # TODO: Connect input to the decision-making algorithm
        # Button to get recommendations
        self.recommend_button = ttk.Button(self.tab2_frame, text="Get Recommendations",
                                           command=self.get_user_input)
        self.recommend_button.pack(pady=20)

        # Button to trigger built-in function to exit window
        self.button = ttk.Button(self.tab2, text="Exit", command=lambda: self.window.destroy())
        self.button.pack(side="left", pady=20)

    # Function to populate the Treeview with data from the database using function from db_functions.py
    def populate_treeview(self):
        for item in self.treeView.get_children():
            self.treeView.delete(item)

        start_index = (self.current_page - 1) * self.titles_per_page
        end_index = (self.current_page - 1) + self.titles_per_page

        titles = get_titles_to_select_from_db(start_index, end_index)  # Get titles from the database
        for title in titles:
            # Only include the values for the selected columns
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in)
            self.treeView.insert('', 'end', values=values)

    # Function to navigate to the previous page
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_treeview()

    # Function to navigate to the next page
    def next_page(self):
        self.current_page += 1
        self.populate_treeview()

    # Function to navigate to the preferences tab
    def go_to_preferences(self):
        self.notebook.select(self.tab2)

    # Function to search for a title in the database
    def search_title(self):
        query_title = self.search_entry.get()
        if query_title:
            results = get_query_title_from_db(query_title)
            self.display_search_results(results)

    # Function to display the search results in the Treeview
    def display_search_results(self, results):
        for item in self.treeView.get_children():
            self.treeView.delete(item)

        # If no results are found, insert a row with "No results found" message
        if not results:
            # Insert a row with "No results found" message
            self.treeView.insert('', 'end', values=("No results found", "", "", "", "", "", "", ""))
        else:
            # Insert the search results into the Treeview
            for result in results:
                values = (result.show_id, result.type, result.title, result.country, result.release_year,
                          result.rating, result.duration, result.listed_in)
                self.treeView.insert('', 'end', values=values)

    def on_double_click(self, event):
        try:
            selected_item = self.treeView.selection()[0]
            show_id = self.treeView.item(selected_item, 'values')[0]
            netflix_titles = connect_db()
            title = get_show_id_title(netflix_titles, show_id)
            self.selected_title = title   # Store the selected title in the class attribute to later access it in main.py
        except IndexError:
            # Handle the case when no item is selected
            print("Having trouble selecting the title. Please try again.")
            self.selected_title = None

    def get_user_input(self):
        child_friendly_preference = self.pg_entry.get()
        classic_preference = self.classic_entry.get()
        duration_preference = self.duration_entry.get()
        country_preference = self.country_entry.get()

        if child_friendly_preference in ["yes", "no"] and classic_preference in ["yes", "no"] and duration_preference in ["yes", "no"] and country_preference in ["yes", "no"]:
            decision_tree.child_friendly_preference = child_friendly_preference
            decision_tree.classic_preference = classic_preference
            decision_tree.duration_preference = duration_preference
            decision_tree.country_preference = country_preference
            print(f"User input: pg={child_friendly_preference}, classic={classic_preference}, duration={duration_preference}, country={country_preference}")
        else:
            print("Invalid input. Please enter 'yes' or 'no' for each preference.")

        return child_friendly_preference, classic_preference, duration_preference, country_preference


# Function to create the GUI instance, which will be called from main.py
def create_gui():
    window = tk.Tk()
    gui_instance = NetflixGUI(window)
    return gui_instance
