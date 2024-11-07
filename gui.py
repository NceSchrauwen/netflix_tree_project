#Developed by: Nina Schrauwen
#Description: This is the GUI file of the Netflix recommendation system. This file contains all elements and functionalities of the user interface.
#Date: 17/05/2024

# Import the necessary modules
import tkinter as tk  # This imports tkinter and aliases it as tk
from tkinter import ttk, messagebox  # This imports ttk and messagebox specifically

# Import the necessary functions from the other files
from db_functions import get_titles_to_select_from_db, get_genre_title_from_db
from other_functions import get_show_id_title, read_genre_counts, check_achievement, read_completed_achievements, write_completed_achievements
from shared import connect_db
from recommendations import get_recommendations
from decision_tree import incorporate_user_feedback, process_recommendations, threshold
import decision_tree

# Define the GUI class
class NetflixGUI:
    def __init__(self, window):
        # Set window title and size
        self.window = window
        self.window.title('Netflix Title Assistant')
        self.window.geometry("1200x600")

        # Create a notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(window)
        self.notebook.pack(fill='both', expand=True)

        # Call the function to create the tabs
        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

    # Function to create the first tab
    def create_tab1(self):
        # Create the first tab and set the title
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Netflix Title Selection')

        # Define the label for the title of the GUI
        self.label = ttk.Label(self.tab1, text="Netflix Recommendation System", font=("Ariel", 18))
        self.label.pack(pady=10)

        # Create a frame to hold the search bar and labels, buttons, etc
        self.search_frame = ttk.Frame(self.tab1)
        self.search_frame.pack(pady=10)

        # Create a label and entry for the search bar
        self.search_label = ttk.Label(self.search_frame, text="Search for a title/genre:")
        self.search_label.pack(pady=5)

        # Create an entry widget for the search bar
        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', pady=5)

        # Bind the search function to the key release event for real-time search
        # Whenever you type a key, it will trigger the search function
        self.search_entry.bind("<KeyRelease>", self.search_title)

        # Define the genre variable and set it to a StringVar
        self.genre_var = tk.StringVar()
        # Define the type variable and set it to a StringVar
        self.type_var = tk.StringVar()

        # List of genres with 'All' at the top
        genres = [
            "All",  # Include an 'All' option to show all genres
            "Anime Features", "Children & Family Movies", "Classic & Cult TV", "Classic Movies",
            "Comedies", "Crime TV Shows", "Cult Movies", "Documentaries", "Docuseries", "Dramas",
            "Faith & Spirituality", "Horror Movies", "Independent Movies", "International Movies",
            "International TV Shows", "Kids' TV", "Korean TV Shows", "LGBTQ Movies", "Music & Musicals",
            "Reality TV", "Romantic Movies", "Romantic TV Shows", "Sci-Fi & Fantasy", "Science & Nature TV",
            "Spanish-Language TV Shows", "Sports Movies", "Stand-Up Comedy", "Stand-Up Comedy & Talk Shows",
            "Teen TV Shows", "Thrillers", "TV Action & Adventure", "TV Comedies", "TV Dramas", "TV Horror",
            "TV Mysteries", "TV Sci-Fi & Fantasy", "TV Thrillers", "Action & Adventure", "Anime Series",
            "British TV Shows", "Movies"
        ]

        # List of types with 'All' at the top
        types = ["All", "Movie", "TV Show"]

        # Start slicing from index 1 to exclude 'All' from the sorted list, then sort alphabetically
        sorted_genres = ["All"] + sorted(genres[1:])

        # Start slicing from index 1 to exclude 'All' from the sorted list, then sort alphabetically
        sorted_types = ["All"] + sorted(types[1:])

        # Define the genre dropdown menu and set the sorted genres as the values
        self.genre_combobox = ttk.Combobox(self.search_frame, textvariable=self.genre_var, values=sorted_genres)
        self.genre_combobox.set("All")  # Set the default value to 'All'
        self.genre_combobox.pack(side='left', pady=5)

        self.type_combobox = ttk.Combobox(self.search_frame, textvariable=self.type_var, values=sorted_types)
        self.type_combobox.set("All")  # Set the default value to 'All'
        self.type_combobox.pack(side='left', pady=5)

        # Bind the search function to the combobox selection event to be able to search with a click
        # Whenever you select a genre, it will trigger the search function
        self.genre_combobox.bind("<<ComboboxSelected>>", self.search_title)

        # Bind the search function to the combobox selection event to be able to search with a click
        # Whenever you select a type, it will trigger the search function
        self.type_combobox.bind("<<ComboboxSelected>>", self.search_title)

        # Define reset button and set it to the reset_search function
        self.reset_button = ttk.Button(self.search_frame, text="Reset", command=self.reset_search)
        self.reset_button.pack(side='right', pady=5)

        # Create a frame to hold the Treeview and scrollbars
        tree_frame = ttk.Frame(self.tab1)
        tree_frame.pack(fill="both", expand=True)

        # Create a Treeview widget to display the titles
        self.columns = ("Show-ID", "Type", "Title", "Country", "Release Year", "Rating", "Duration", "Listed In", "Score", "Jaccard Similarity")
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

        # Configure the Treeview to be able to use the scrollbars
        self.treeView1.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths automatically
        for col in self.columns:
            self.treeView1.heading(col, text=col)

        # Define the current page and the number of titles to display per page
        self.current_page = 1
        self.titles_per_page = 50

        # Buttons to go to the next and back to the previous page, set to the corresponding function
        self.prev_button = ttk.Button(self.tab1, text="Previous", command=self.prev_page)
        self.prev_button.pack(side="left", pady=20)

        # Button to go to the next page, set to the corresponding function
        self.next_button = ttk.Button(self.tab1, text="Next", command=self.next_page)
        self.next_button.pack(side="left", pady=20)

        # Button to go to the preferences tab, set to the corresponding function
        self.pref_button = ttk.Button(self.tab1, text="Go to Preferences", command=self.go_to_preferences)
        self.pref_button.pack(side="left", pady=20)

        # Populate the Treeview with data from the database
        self.populate_treeview()

        # Button to trigger built-in function to exit window using the destroy method
        self.exit_button = ttk.Button(self.tab1, text="Exit", command=lambda: self.window.destroy())
        self.exit_button.pack(side="left", pady=20)

        # Set style for the Treeview and buttons (font and theme)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Ariel", 10))
        style.configure("Button", font=("Ariel", 8))
        style.theme_use("clam")

        # Allow the user to double-click on a title to be able to select it
        self.treeView1.bind("<Double-1>", self.on_double_click)
        # Attribute to store the selected title, first set to None to later store the selected title
        self.selected_title = None

    # Function to create the second tab
    def create_tab2(self):
        # Create the second tab
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Preferences')

        # Label for the recommendation preferences tab
        self.tab2_lbl = ttk.Label(self.tab2, text="Recommendation Preferences", font=("Ariel", 18))
        self.tab2_lbl.pack(pady=10)

        # Create a frame to hold the preferences
        self.tab2_frame = ttk.Frame(self.tab2)
        self.tab2_frame.pack(fill="both", expand=True)

        # User input fields (with labels) for child-friendly, classic, duration, and country preferences
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

        # Button to go to the recommendations tab, set to the corresponding function
        self.button = ttk.Button(self.tab2, text="Go to Recommendations", command=self.go_to_recommendations)
        self.button.pack(side="left", pady=20)

        # Button to get recommendations, set to the corresponding function
        self.recommend_button = ttk.Button(self.tab2_frame, text="Submit Preferences",
                                           command=self.get_user_input)
        self.recommend_button.pack(pady=20)

        # Button to trigger built-in function to exit window, set to the destroy method
        self.button = ttk.Button(self.tab2, text="Exit", command=lambda: self.window.destroy())
        self.button.pack(side="left", pady=20)

        # Label to display error messages if the user input is invalid
        self.error_message_lbl = ttk.Label(self.tab2_frame, text="", font=("Ariel", 12), foreground="red")
        self.error_message_lbl.pack(side="left", pady=20)

    # Function to create the third tab
    def create_tab3(self):
        # Create the third tab
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text='Recommendations')

        # Label for the recommended titles tab
        self.tab3_lbl = ttk.Label(self.tab3, text="- Recommended Titles -", font=("Ariel", 18))
        self.tab3_lbl.pack(pady=10)

        # Create a frame to hold the preferences
        self.tab3_frame = ttk.Frame(self.tab3)
        self.tab3_frame.pack(fill="both", expand=True)

        # Create a frame to hold the Treeview and scrollbars
        tree_frame3 = ttk.Frame(self.tab3)
        tree_frame3.pack(fill="both", expand=True)

        # Create a Treeview widget to be able to display the titles
        self.columns = ("Show-ID", "Type", "Title", "Country", "Release Year", "Rating", "Duration", "Listed In", "Score", "Jaccard Similarity")
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

        # Configure the Treeview to be able to use the scrollbars
        self.treeView2.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths automatically
        for col in self.columns:
            self.treeView2.heading(col, text=col)

        # Create a frame to hold score input, buttons, etc.
        tab3_frame = ttk.Frame(self.tab3)
        tab3_frame.pack(fill="both", expand=True)

        # Label for user input score
        self.label = ttk.Label(self.tab3_frame, text="Which recommendations do you want to score?: ", font=("Ariel", 15))
        self.label.pack(pady=10)

        # Entry field for the user to input the score
        self.score_entry = ttk.Entry(self.tab3_frame, width=30)
        self.score_entry.pack(pady=5)

        # Button to get recommendations, set to the corresponding function
        self.score_submit_btn = ttk.Button(self.tab3_frame, text="Submit Score(s)",
                                           command=self.get_user_scores)
        self.score_submit_btn.pack(pady=20)

        # Label to display scored show IDs, is set to empty string initially
        # Will only be updated when the user has submitted a score
        self.scored_label = ttk.Label(self.tab3_frame, text="", font=("Ariel", 12))
        self.scored_label.pack(pady=10)

        # Button to go back to the preferences tab, sets of the action of resetting entries and selections while navigating to tab1
        self.back_button = ttk.Button(self.tab3, text="Start over", command=self.go_to_tab1)
        self.back_button.pack(side="left", pady=20)

        # Button to trigger built-in function to exit window using the destroy method
        self.exit3_button = ttk.Button(self.tab3, text="Exit", command=lambda: self.window.destroy())
        self.exit3_button.pack(side="right", pady=20)

    # Function to populate the Treeview with data from the database using the db_functions function
    def populate_treeview(self):
        self.treeView1.delete(*self.treeView1.get_children())  # Clear the Treeview
        # Calculate the start and end index for the titles to display on the current page
        start_index = (self.current_page - 1) * self.titles_per_page
        end_index = start_index + self.titles_per_page

        # Get the titles from the database based on the start and end index
        titles = get_titles_to_select_from_db(start_index, end_index)
        # If no titles are found, print a message to the console
        if titles is None:
            print("No titles found in the database.")
            return

        # If there are titles found, insert them into the Treeview into the corresponding columns
        for title in titles:
            # Only include the values for the selected columns
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in, title.score, title.jaccard_similarity)
            self.treeView1.insert('', 'end', values=values)

        # Update button states based on amount of results
        self.prev_button.config(state="disabled" if self.current_page == 1 else "normal") # Disable previous button if you're on first page
        self.next_button.config(state="disabled" if len(titles) < self.titles_per_page else "normal") # Disable next button if you're on last page

    # Function to navigate to the previous page based on the current page
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            # When the current page is figured out, repopulate the treeview with the titles for that page
            self.populate_treeview()

    # Function to navigate to the next page based on the current page
    def next_page(self):
        self.current_page += 1
        # When the current page is figured out, repopulate the treeview with the titles for that page
        self.populate_treeview()

    # Function to navigate to tab 2 (preferences tab)
    def go_to_preferences(self):
        self.notebook.select(self.tab2)

    #Function to navigate to the tab 3 (recommendations tab)
    def go_to_recommendations(self):
        self.notebook.select(self.tab3)

    # Function to navigate to tab 1 (selection tab) and reset all entries and selections
    def go_to_tab1(self):
        # Clear the search field and reset the genre dropdown
        self.search_entry.delete(0, 'end')  # Clear the search field
        self.genre_combobox.set("All")  # Reset the genre dropdown to "All"
        self.type_combobox.set("All")  # Reset the type dropdown to "All"

        # Clear the TreeView selections and refill it with the original titles
        self.treeView1.selection_remove(self.treeView1.selection())  # Remove any blue selection highlight
        # Reset the current page to tab1 (selection tab)
        self.current_page = 1
        # Repopulate the treeview with the original set of titles for the first page
        self.populate_treeview()

        # Reset the scrollbar back to the top
        self.treeView1.yview_moveto(0)  # Scroll vertical scrollbar to top
        self.treeView1.xview_moveto(0)  # Scroll horizontal scrollbar to left

        # Clear any selected title variable
        self.selected_title = None

        # Clear the recommendation entry fields
        self.pg_entry.delete(0, 'end')  # Clear preferences entry for child-friendly
        self.classic_entry.delete(0, 'end')  # Clear preferences entry for classic
        self.duration_entry.delete(0, 'end')  # Clear preferences entry for duration
        self.country_entry.delete(0, 'end')  # Clear preferences entry for country

        # Clear the user feedback entry field
        self.score_entry.delete(0, 'end')  # Clear the score entry field

        # Switch to the first tab after clearing and resetting every other tab
        self.notebook.select(self.tab1)

    # Function to search for a title in the database
    def search_title(self, event=None):
        results = None # Initialize results to None, so it can be filled later
        query_title = self.search_entry.get() # Get the query title from the search entry field
        selected_genre = self.genre_var.get()  # Get the selected genre from the dropdown menu
        selected_type = self.type_var.get()  # Get the selected type from the dropdown menu

        # If there is a query title, selected genre, and selected type, search for the title in the database
        if query_title and selected_genre and selected_type:
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is only a query title, search for the title in the database
        elif selected_genre == "All" and query_title and selected_type == "All":
            selected_genre.lower()
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is a selected genre, search for the title in the database
        elif selected_genre and not query_title and selected_type == "All":
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is a genre and a type, search for the title in the database
        elif selected_genre and selected_type and not query_title:
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is a genre and a query title, search for the title in the database
        elif selected_genre and query_title and selected_type == "All":
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is a type and a query title, search for the title in the database
        elif selected_type and query_title and selected_genre == "All":
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)
        # If there is only a type, search for the title in the database
        elif selected_type and not query_title and selected_genre == "All":
            results = get_genre_title_from_db(query_title, selected_genre, selected_type)

        # Display the search results in the Treeview by calling the display_search_results function with the results
        self.display_search_results(results)

    # Function to reset the treeview to the original unfiltered set of titles
    def reset_search(self):
        self.search_entry.delete(0, 'end') # Empty the search entry field
        self.genre_combobox.set("All") # Set the genre dropdown to "All" so all titles will show
        self.type_combobox.set("All")  # Set the type dropdown to "All" so all titles will show
        self.populate_treeview() # Repopulate the treeview with the original set of titles (which it had before)

        # Reset the scrollbar back to the top
        self.treeView1.yview_moveto(0)  # Scroll vertical scrollbar to top
        self.treeView1.xview_moveto(0)  # Scroll horizontal scrollbar to left

    # Function to display the search results in the Treeview
    def display_search_results(self, results):
        # Clear the Treeview to display the search results later on
        for item in self.treeView1.get_children():
            self.treeView1.delete(item)

        # If no results are found, insert a row with "No results found" message
        if not results:
            # Insert a row with "No results found" message
            self.treeView1.insert('', 'end', values=("No results found", "", "", "", "", "", "", "", "", ""))
        # If there are results found, display them in the Treeview
        else:
            # Loop through the results and insert them into the Treeview with the corresponding values
            for result in results:
                values = (result.show_id, result.type, result.title, result.country, result.release_year,
                          result.rating, result.duration, result.listed_in, result.score, result.jaccard_similarity)
                self.treeView1.insert('', 'end', values=values)

        # Update button states based on amount of results
        self.prev_button.config(state="disabled" if self.current_page == 1 else "normal")  # Disable previous button if on first page
        self.next_button.config(state="disabled" if len(results) < self.titles_per_page else "normal")  # Disable next button if on last page

    # Function to be able to double click on a title to select it
    def on_double_click(self, event):
        # Get the selected item from the Treeview
        try:
            # Identify the selected item based on the mouse pointer
            selected_item = self.treeView1.identify_row(event.y) # Get the selected item
            print(f"--- Selected item: {selected_item} ---")

            # If no item is selected, print an error message and set the selected title to None
            if not selected_item:
                print("No item selected.")
                self.selected_title = None
                return

            # Get the values of the selected item from mouse pointer
            values = self.treeView1.item(selected_item, 'values')
            # If no values are found, print an error message and set the selected title to None
            if not values:
                print("No values found.")
                self.selected_title = None
                return

            # Get the show ID of the selected item
            show_id = values[0]

            # Get all netflix titles from the database
            netflix_titles = connect_db()
            # Search the specific title based on the show ID with the netflix titles
            title = get_show_id_title(netflix_titles, show_id)
            # Store the selected title in the class attribute to later access via the gui_instance in main.py
            self.selected_title = title
            print(f"Selected title: {self.selected_title}")

        # Handle exceptions if any occur
        except Exception as e:
            print(f"Error: {e}")
            self.selected_title = None

    # Function to get the user input from the preferences tab to use in the decision-making algorithm
    def get_user_input(self):
        # Get the values from the user input fields
        def get_valid_input(entry):
            value = entry.get().strip().lower()
            # Validate the input to only accept 'yes' or 'no' as input
            if value in ['yes', 'no']:
                return value
            else:
                # If the input is invalid, print an error message and return None
                print("Invalid input. Please enter 'yes' or 'no' for each preference.")
                return None

        # Get the user input from the preferences tab and validate the input
        child_friendly_preference = get_valid_input(self.pg_entry)
        classic_preference = get_valid_input(self.classic_entry)
        duration_preference = get_valid_input(self.duration_entry)
        country_preference = get_valid_input(self.country_entry)

        # If any of the inputs are invalid, print an error message and return None
        if None in [child_friendly_preference, classic_preference, duration_preference, country_preference]:
            print("One or more inputs are invalid. Please correct them and try again.")
            return None
        # If all inputs are valid, print the user input and return the validated preferences
        else:
            decision_tree.get_user_input(child_friendly_preference, classic_preference, duration_preference,
                                         country_preference)
            print(
                f"User input: pg={child_friendly_preference}, classic={classic_preference}, duration={duration_preference}, country={country_preference}")

        return child_friendly_preference, classic_preference, duration_preference, country_preference

    # Function to submit the preferences and get the recommendations
    def submit_preferences(self, netflix_titles, num_suggestions):
        # Get the user input from the preferences tab
        user_input = self.get_user_input()

        # If the user input is invalid, print an error message and return None
        if user_input is None:
            # If the user input is invalid, print an error message in the label to notify the user
            self.error_message_lbl.config(text="Error: Invalid input. Please correct the input and try again.")
            return None

        # Go to recommendations tab
        self.go_to_recommendations()

        # Calculate and update jaccard similarity scores in the database, only the scores that are subject to change
        process_recommendations(threshold)

        # Trigger recommendation process and get filtered recommended titles
        filtered_recommended_titles = get_recommendations(self, netflix_titles, num_suggestions)
        # First check if there are any recommended titles, then populate the treeview with the recommendations
        if filtered_recommended_titles:
            self.populate_rec_titles(filtered_recommended_titles)
        # If there are no recommended titles, print an error message
        else:
            print("No filtered recommended titles to populate the GUI.")

        # Function to read out the CSV regarding the genre counts
        genre_counts = read_genre_counts()
        # Convert the genre counts to a dictionary with the genre as the key (k) and the count as the value (v)
        genre_counts = {k: int(v) for k, v in genre_counts.items()}  # Ensure the counts are integers

        # Check if the user has achieved any milestones based on the genre counts
        achieved_milestones = check_achievement(genre_counts)

        # If there are no achieved milestones, make it an empty dictionary
        if achieved_milestones is None:
            achieved_milestones = {}

        # Process the achievements based on the achieved milestones achieved with a popup message
        self.process_achievements(achieved_milestones)

        return filtered_recommended_titles

    # Function to populate the Treeview with the recommended titles
    def populate_rec_titles(self, recommended_titles):
        # Go to the recommendations tab
        self.notebook.select(self.tab3)
        self.treeView2.delete(*self.treeView2.get_children())  # Clear the Treeview to be able to display the recommended titles

        # Insert the recommended titles into the Treeview with the corresponding values
        for title in recommended_titles:
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in, title.score, title.jaccard_similarity)
            self.treeView2.insert('', 'end', values=values)

        # Set filtered titles to use them later in the get_user_scores function
        self.filtered_recommended_titles = recommended_titles

    # Function to get the user scores and update the database based on show IDs
    def get_user_scores(self):
        # Get the user input from the score entry field, make sure to strip any leading/trailing whitespace
        user_input = self.score_entry.get().strip()
        try:
            # Convert the user input to a list of integers and remove the commas
            selected_show_ids = [int(show_id) for show_id in user_input.split(",")]
            # Check if the number of scores selected by the user exceeds the number of recommended titles
            if len(selected_show_ids) > len(self.filtered_recommended_titles):
                # If the number of scores exceeds the number of recommended titles, print an error message
                print("Error: Number of scores exceeds the number of recommended titles.")
                return
            # If the number of scores is valid, enter the selected show IDs to update the database
            incorporate_user_feedback(selected_show_ids)
            # Convert the list of show IDs to a string and display it in the label once the scores have been submitted
            scored_ids_str = ", ".join(map(str, selected_show_ids))
            # Update the previous blank label to show the scored show IDs
            self.scored_label.config(text=f"Show IDs {scored_ids_str} have been scored.")
        # Handle exceptions
        except ValueError:
            print("Error: Invalid input. Please enter a comma-separated list of integers. (e.g. 1, 32, 234, etc.)")

    # Function to create a message for the achievement popup based on the achieved milestones
    def process_achievements(self, achieved_milestones):
        # Read the completed achievements from the TXT file
        completed_achievements = read_completed_achievements()

        # Loop through the achieved milestones
        for achievement, achieved in achieved_milestones.items():
            print(f'Completed achievements debug: {completed_achievements}')
            # If the milestone has been achieved yet not shown, create a message based on the milestone achieved and show a popup
            if completed_achievements.get(achievement, True):
                print(f'Achievement {achievement} achieved and not previously completed.')
                # Display a popup message with the achievement regarding the milestone achieved
                message = f"Congratulations! You have achieved the milestone: {achievement}!"
                # Display the achievement popup message
                self.show_achievement_popup(message)
                # After the popup is shown, set the achievement to completed in the dictionary so it will not be shown again
                completed_achievements[achievement] = False
                print(f'Output should be: {message} @gui.py:process_achievements')
            # If the milestone has already been achieved and shown, print a message that the achievement has already been completed
            elif not completed_achievements[achievement]:
                print(f'Achievement {achievement} has already been completed.')
            # If the milestone has not been achieved yet, print a message that the milestone has not been defined yet
            else:
                print(f'Milestone not defined yet, not enough genre count. Achievement: {achievement}, achieved: {achieved}')
                # print(f'Achievement {achievement}, achieved: {achieved}')

        # Write the completed achievements to the TXT file
        write_completed_achievements(completed_achievements)  # Update the completed achievements in the file

    # Function to show a popup with the achievement message, message created in process_achievements
    def show_achievement_popup(self, message):
        # Show a popup message with the achievement message
        messagebox.showinfo("Achievement Unlocked!", message)
        print(f'Showing popup with message: {message}')




