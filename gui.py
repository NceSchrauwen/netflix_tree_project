#Developed by: Nina Schrauwen
#Description: This is the GUI file of the Netflix recommendation system. This file contains all elements and functionalities of the GUI.
#Date: 17/05/2024

import tkinter as tk
from tkinter import ttk
from db_functions import get_titles_to_select_from_db, get_query_title_from_db
from other_functions import get_show_id_title
from shared import connect_db
from recommendations import get_recommendations
import decision_tree


class NetflixGUI:
    def __init__(self, window):
        # Set window title and size
        self.window = window
        self.window.title('Netflix Title Picker')
        self.window.geometry("1200x600")

        # Create a notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(window)
        self.notebook.pack(fill='both', expand=True)

        # end of the GUI setup
        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

    def create_tab1(self):
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
        self.columns = ("Show-ID", "Type", "Title", "Country", "Release Year", "Rating", "Duration", "Listed In")
        self.treeView1 = ttk.Treeview(tree_frame, columns=self.columns, show='headings')

        # Scrollbar Setup (inside treeview_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeView1.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.treeView1.xview)

        # Set the scrollbar to the right side of the treeview so that it doesn't wander outside the treeview
        self.treeView1.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)  # Allow Treeview to expand vertically
        tree_frame.grid_columnconfigure(0, weight=1)  # Allow Treeview to expand horizontally

        # Configure the Treeview to use the scrollbars
        self.treeView1.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths
        for col in self.columns:
            self.treeView1.heading(col, text=col)  # Set column headings automatically

        # Define the current page and the number of titles to display per page
        self.current_page = 1
        self.titles_per_page = 50

        # Buttons to go to the next and back to the previous page
        self.prev_button = ttk.Button(self.tab1, text="Previous", command=self.prev_page)
        self.prev_button.pack(side="left", pady=20)

        self.next_button = ttk.Button(self.tab1, text="Next", command=self.next_page)
        self.next_button.pack(side="left", pady=20)

        self.pref_button = ttk.Button(self.tab1, text="Go to Preferences", command=self.go_to_preferences)
        self.pref_button.pack(side="left", pady=20)

        # Populate the Treeview with data from the database
        self.populate_treeview()

        # Button to trigger built-in function to exit window
        self.exit_button = ttk.Button(self.tab1, text="Exit", command=lambda: self.window.destroy())
        self.exit_button.pack(side="left", pady=20)

        # Set style for the Treeview and buttons (font and theme)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Ariel", 10))
        style.configure("Button", font=("Ariel", 8))
        style.theme_use("clam")

        # Allow the user to double-click on a title to select it
        self.treeView1.bind("<Double-1>", self.on_double_click)
        # Attribute to store the selected title
        self.selected_title = None

    def create_tab2(self):
        # Create the second tab
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Preferences')

        self.tab2_lbl = ttk.Label(self.tab2, text="Recommendation Preferences", font=("Ariel", 18))
        self.tab2_lbl.pack(pady=10)

        # Create a frame to hold the preferences
        self.tab2_frame = ttk.Frame(self.tab2)
        self.tab2_frame.pack(fill="both", expand=True)

        # Add user input widgets for preferences
        self.pg_label = ttk.Label(self.tab2_frame,
                                  text="Do you want to watch a child-friendly (under age 13) movie/season? (yes/no):")
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

        self.country_label = ttk.Label(self.tab2_frame,
                                       text="Do you want to watch a movie from the US or the UK? (yes/no): ")
        self.country_label.pack(pady=5)
        self.country_entry = ttk.Entry(self.tab2_frame, width=30)
        self.country_entry.pack(pady=5)

        self.button = ttk.Button(self.tab2, text="Go to Recommendations", command=self.go_to_recommendations)
        self.button.pack(side="left", pady=20)

        # TODO: Make event handler for this one too
        # Button to get recommendations
        self.recommend_button = ttk.Button(self.tab2_frame, text="Submit Preferences",
                                           command=self.get_user_input)
        self.recommend_button.pack(pady=20)

        # Button to trigger built-in function to exit window
        self.button = ttk.Button(self.tab2, text="Exit", command=lambda: self.window.destroy())
        self.button.pack(side="left", pady=20)

    def create_tab3(self):
        # Create the third tab
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text='Recommendations')

        self.tab3_lbl = ttk.Label(self.tab3, text="- Recommended Titles -", font=("Ariel", 18))
        self.tab3_lbl.pack(pady=10)

        # Create a frame to hold the preferences
        self.tab3_frame = ttk.Frame(self.tab3)
        self.tab3_frame.pack(fill="both", expand=True)

        # Create treeview for loading of results
        # Create a frame to hold the Treeview and scrollbars
        tree_frame3 = ttk.Frame(self.tab3)
        tree_frame3.pack(fill="both", expand=True)

        # Create a Treeview widget to display the titles
        self.columns = ("Show-ID", "Type", "Title", "Country", "Release Year", "Rating", "Duration", "Listed In")
        self.treeView2 = ttk.Treeview(tree_frame3, columns=self.columns, show='headings')

        # Scrollbar Setup (inside treeview_frame)
        vsb = ttk.Scrollbar(tree_frame3, orient="vertical", command=self.treeView2.yview)
        hsb = ttk.Scrollbar(tree_frame3, orient="horizontal", command=self.treeView2.xview)

        # Set the scrollbar to the right side of the treeview so that it doesn't wander outside the treeview
        self.treeView2.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame3.grid_rowconfigure(0, weight=1)  # Allow Treeview to expand vertically
        tree_frame3.grid_columnconfigure(0, weight=1)  # Allow Treeview to expand horizontally

        # Configure the Treeview to use the scrollbars
        self.treeView2.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths
        for col in self.columns:
            self.treeView2.heading(col, text=col)  # Set column headings automatically

        # Button to trigger built-in function to exit window
        self.exit3_button = ttk.Button(self.tab3, text="Exit", command=lambda: self.window.destroy())
        self.exit3_button.pack(side="left", pady=20)


    # Function to populate the Treeview with data from the database using function from db_functions.py
    def populate_treeview(self):
        self.treeView1.delete(*self.treeView1.get_children())  # Clear the Treeview efficiently

        start_index = (self.current_page - 1) * self.titles_per_page
        end_index = start_index + self.titles_per_page

        titles = get_titles_to_select_from_db(start_index, end_index)  # Get titles from the database
        if titles is None:
            print("No titles found in the database.")
            return

        for title in titles:
            # Only include the values for the selected columns
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in)
            self.treeView1.insert('', 'end', values=values)

        # Update button states
        self.prev_button.config(state="disabled" if self.current_page == 1 else "normal")
        self.next_button.config(state="disabled" if len(titles) < self.titles_per_page else "normal")


    # Function to navigate to the previous page
    def prev_page(self):
        # print("Previous page button clicked.")
        # print(f"Current page: {self.current_page}")
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_treeview()

    # Function to navigate to the next page
    def next_page(self):
        # print("Next page button clicked.")
        # print(f"Current page: {self.current_page}")
        self.current_page += 1
        self.populate_treeview()

    # Function to navigate to the preferences tab
    def go_to_preferences(self):
        self.notebook.select(self.tab2)

    def go_to_recommendations(self):
        self.notebook.select(self.tab3)

    # Function to search for a title in the database
    def search_title(self):
        query_title = self.search_entry.get()
        if query_title:
            results = get_query_title_from_db(query_title)
            self.display_search_results(results)

    # Function to display the search results in the Treeview
    def display_search_results(self, results):
        for item in self.treeView1.get_children():
            self.treeView1.delete(item)

        # If no results are found, insert a row with "No results found" message
        if not results:
            # Insert a row with "No results found" message
            self.treeView1.insert('', 'end', values=("No results found", "", "", "", "", "", "", ""))
        else:
            # Insert the search results into the Treeview
            for result in results:
                values = (result.show_id, result.type, result.title, result.country, result.release_year,
                          result.rating, result.duration, result.listed_in)
                self.treeView1.insert('', 'end', values=values)

    def on_double_click(self, event):
        try:
            selected_item = self.treeView1.identify_row(event.y) # Get the selected item
            print(f"--- Selected item: {selected_item} ---")

            if not selected_item:
                print("No item selected.")
                self.selected_title = None
                return

            # Get the values of the selected item from mouse pointer
            values = self.treeView1.item(selected_item, 'values')
            if not values:
                print("No values found.")
                self.selected_title = None
                return

            # Get the show ID of the selected item
            show_id = values[0]
            # print(f"Selected show ID: {show_id}")

            netflix_titles = connect_db()
            title = get_show_id_title(netflix_titles, show_id)
            self.selected_title = title   # Store the selected title in the class attribute to later access it in main.py
            print(f"Selected title: {self.selected_title}")
        # Handle exceptions
        except Exception as e:
            print(f"Error: {e}")
            self.selected_title = None


    # Function to get the user input from the preferences tab to use in the decision-making algorithm
    def get_user_input(self):
        # Get the values from the user input fields
        child_friendly_preference = self.pg_entry.get()
        classic_preference = self.classic_entry.get()
        duration_preference = self.duration_entry.get()
        country_preference = self.country_entry.get()

        # If the user input is valid, pass it to the decision tree
        if all(value in ['yes', 'no'] for value in [child_friendly_preference, classic_preference, duration_preference, country_preference]):
            decision_tree.get_user_input(child_friendly_preference, classic_preference, duration_preference, country_preference)
            print(f"User input: pg={child_friendly_preference}, classic={classic_preference}, duration={duration_preference}, country={country_preference}")
        else:
            print("Invalid input. Please enter 'yes' or 'no' for each preference.")

        return child_friendly_preference, classic_preference, duration_preference, country_preference

    # Function to submit the preferences and get the recommendations
    def submit_preferences(self, netflix_titles, num_suggestions):
        # Get the user input from the preferences tab
        self.get_user_input()
        # Go to recommendations tab
        self.go_to_recommendations()
        # Trigger recommendation process and get filtered recommended titles
        filtered_recommended_titles = get_recommendations(self, netflix_titles, num_suggestions)
        # First check if there are any recommended titles, then populate the treeview with the recommendations
        if filtered_recommended_titles:
            self.populate_rec_titles(filtered_recommended_titles)
        else:
            print("No filtered recommended titles to populate the GUI.")

    # Function to populate the Treeview with the recommended titles
    def populate_rec_titles(self, recommended_titles):
        # Go to the recommendations tab
        self.notebook.select(self.tab3)
        self.treeView2.delete(*self.treeView2.get_children())  # Clear the Treeview efficiently

        # Insert the recommended titles into the Treeview with the corresponding values
        for title in recommended_titles:
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in)
            self.treeView2.insert('', 'end', values=values)


