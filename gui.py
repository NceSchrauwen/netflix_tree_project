#Developed by: Nina Schrauwen
#Description: This is the GUI file of the Netflix recommendation system. This file contains all elements and functionalities of the GUI.
#Date: 17/05/2024

import tkinter as tk  # This imports tkinter and aliases it as tk
from tkinter import ttk, messagebox  # This imports ttk and messagebox specifically


from db_functions import get_titles_to_select_from_db, get_genre_title_from_db
from other_functions import get_show_id_title, read_genre_counts, check_achievement, read_completed_achievements, write_completed_achievements
from shared import connect_db
from recommendations import get_recommendations
from decision_tree import incorporate_user_feedback, process_recommendations, threshold
import decision_tree


class NetflixGUI:
    def __init__(self, window):
        # Set window title and size
        self.window = window
        self.window.title('Netflix Title Assistant')
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

        self.search_label = ttk.Label(self.search_frame, text="Search for a title/genre:")
        self.search_label.pack(pady=5)

        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', pady=5)

        self.genre_var = tk.StringVar()
        self.genre_dropdown = ttk.Combobox(self.search_frame, textvariable=self.genre_var)
        self.genre_dropdown['values'] = [
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
        self.genre_dropdown.set("All")  # Set the default value to 'All'
        self.genre_dropdown.pack(side='left', pady=5)

        # TODO: Update README to include the data source and how to set up the local database
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_title)
        self.search_button.pack(side='left', pady=5)

        # Reset button
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

        # Create a frame to hold the Treeview and scrollbars
        tree_frame3 = ttk.Frame(self.tab3)
        tree_frame3.pack(fill="both", expand=True)

        # Create a Treeview widget to display the titles
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

        # Configure the Treeview to use the scrollbars
        self.treeView2.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Set column headings and widths
        for col in self.columns:
            self.treeView2.heading(col, text=col)  # Set column headings automatically

        # Create a frame to hold score input
        tab3_frame = ttk.Frame(self.tab3)
        tab3_frame.pack(fill="both", expand=True)

        # Label for user input score
        self.label = ttk.Label(self.tab3_frame, text="Which recommendations do you want to score?: ", font=("Ariel", 15))
        self.label.pack(pady=10)

        self.score_entry = ttk.Entry(self.tab3_frame, width=30)
        self.score_entry.pack(pady=5)

        # TODO: Link a function to this button to update the score in the database
        # Button to get recommendations
        self.score_submit_btn = ttk.Button(self.tab3_frame, text="Submit Score(s)",
                                           command=self.get_user_scores)
        self.score_submit_btn.pack(pady=20)

        # Label to display scored show IDs
        self.scored_label = ttk.Label(self.tab3_frame, text="", font=("Ariel", 12))
        self.scored_label.pack(pady=10)

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
                      title.rating, title.duration, title.listed_in, title.score, title.jaccard_similarity)
            self.treeView1.insert('', 'end', values=values)

        # Update button states based on amount of results
        self.prev_button.config(state="disabled" if self.current_page == 1 else "normal") # Disable previous button if on first page
        self.next_button.config(state="disabled" if len(titles) < self.titles_per_page else "normal") # Disable next button if on last page


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
        results = None # Initialize results to None, so it can be filled within the if-elif block
        query_title = self.search_entry.get() # Get the query title from the search entry field
        selected_genre = self.genre_var.get()  # Get the selected genre from the dropdown menu

        # Give search results based on specific genre and title name
        if query_title and selected_genre:
            results = get_genre_title_from_db(query_title, selected_genre)
        # Give search results based on title name only
        elif selected_genre == "All" and query_title:
            selected_genre.lower()
            results = get_genre_title_from_db(query_title, selected_genre)
        # Give search results based on genre only
        elif selected_genre and not query_title:
            results = get_genre_title_from_db(query_title, selected_genre)

        # Display the search results in the Treeview by calling the display_search_results function with the results
        self.display_search_results(results)

    # Function to reset the treeview to the original unfiltered set of titles
    def reset_search(self):
        self.search_entry.delete(0, 'end') # Empty the search entry field
        self.genre_dropdown.set("All") # Set the genre dropdown to "All" so all titles will show
        self.populate_treeview() # Repopulate the treeview with the original set of titles (which it had before)

    # Function to display the search results in the Treeview
    def display_search_results(self, results):
        for item in self.treeView1.get_children():
            self.treeView1.delete(item)

        # If no results are found, insert a row with "No results found" message
        if not results:
            # Insert a row with "No results found" message
            self.treeView1.insert('', 'end', values=("No results found", "", "", "", "", "", "", "", "", ""))
        else:
            # Insert the search results into the Treeview
            for result in results:
                values = (result.show_id, result.type, result.title, result.country, result.release_year,
                          result.rating, result.duration, result.listed_in, result.score, result.jaccard_similarity)
                self.treeView1.insert('', 'end', values=values)

        # Update button states based on amount of results
        self.prev_button.config(state="disabled" if self.current_page == 1 else "normal")  # Disable previous button if on first page
        self.next_button.config(state="disabled" if len(results) < self.titles_per_page else "normal")  # Disable next button if on last page

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
            self.selected_title = title   # Store the selected title in the class attribute to later access via the gui_instance in main.py
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

        # Calculate and update jaccard similarity scores in the database
        process_recommendations(threshold)

        genre_counts = read_genre_counts()
        # Convert the genre counts to a dictionary (it converted differently somewhat than expected)
        # genre_counts = dict(genre_counts)
        genre_counts = {k: int(v) for k, v in genre_counts.items()}  # Ensure the counts are integers
        # print(f'Converted genre counts: {genre_counts}')

        # Check if the user has achieved any milestones based on the genre counts
        achieved_milestones = check_achievement(genre_counts)

        # Ensure achieved_milestones is not None
        if achieved_milestones is None:
            achieved_milestones = {}

        # Process the achievements based on the milestones achieved with a popup message
        self.process_achievements(achieved_milestones)

        print(f'Output should be: {achieved_milestones} @gui.py:submit_preferences')

        return filtered_recommended_titles

    # Function to populate the Treeview with the recommended titles
    def populate_rec_titles(self, recommended_titles):
        # Go to the recommendations tab
        self.notebook.select(self.tab3)
        self.treeView2.delete(*self.treeView2.get_children())  # Clear the Treeview efficiently

        # Insert the recommended titles into the Treeview with the corresponding values
        for title in recommended_titles:
            values = (title.show_id, title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in, title.score, title.jaccard_similarity)
            self.treeView2.insert('', 'end', values=values)

        # Set filtered titles, to later use in get_user_scores
        self.filtered_recommended_titles = recommended_titles

    # Function to get the user scores and update the database based on show IDs
    def get_user_scores(self):
        # Get the user input from the score entry field
        user_input = self.score_entry.get().strip()
        try:
            # Convert the user input to a list of integers and remove the commas
            selected_show_ids = [int(show_id) for show_id in user_input.split(",")]
            # Check if the number of scores exceeds the number of recommended titles
            if len(selected_show_ids) > len(self.filtered_recommended_titles):
                # If the number of scores exceeds the number of recommended titles, print an error message
                print("Error: Number of scores exceeds the number of recommended titles.")
                return
            # Otherwise incorporate the user feedback and update the database based on the show IDs
            incorporate_user_feedback(selected_show_ids)
            # Convert the list of show IDs to a string and display it in the label once the scores have been submitted
            scored_ids_str = ", ".join(map(str, selected_show_ids))
            self.scored_label.config(text=f"Show IDs {scored_ids_str} have been scored.")
        # Handle exceptions
        except ValueError:
            print("Error: Invalid input. Please enter a comma-separated list of integers. (e.g. 1, 32, 234, etc.)")

    # Function to create a message for the achievement popup based on the achieved milestones
    def process_achievements(self, achieved_milestones):
        completed_achievements = read_completed_achievements()

        # Debug print statements
        # print(f'Achieved milestones: {achieved_milestones}')
        # print(f'Completed achievements before processing: {completed_achievements}')

        # Loop through the achieved milestones
        for achievement, achieved in achieved_milestones.items():
            # print(f'Processing achievement: {achievement}, Achieved: {achieved}')
            # If the milestone has been achieved, create a message based on the milestone achieved and show a popup
            if completed_achievements.get(achievement, True): # If achieved and not yet shown, aka True
                print(f'Achievement {achievement} achieved and not previously completed.')
                message = f"Congratulations! You have achieved the milestone: {achievement}!"
                self.show_achievement_popup(message)
                completed_achievements[achievement] = False
                print(f'Output should be: {message} @gui.py:process_achievements')
            elif completed_achievements.get(achievement, False):
                print(f'Achievement {achievement} has already been completed.')
            else:
                print(f'Already completed or not enough genre count. Achievement: {achievement}')

        write_completed_achievements(completed_achievements)  # Update the completed achievements in the file


    # Function to show a popup with the achievement message, message created in process_achievements
    def show_achievement_popup(self, message):
        # print(f'Showing popup with achievement: {message} @gui.py:show_achievement_popup')  # Debug print statement
        messagebox.showinfo("Achievement Unlocked!", message)
        print(f'Showing popup with message: {message}')




