#Developed by: Nina Schrauwen
#Description: This is the GUI file of the Netflix recommendation system. This file contains all elements and functionalities of the GUI.
#Date: 17/05/2024

import tkinter as tk
from tkinter import ttk
from db_functions import get_titles_to_select_from_db

class NetflixGUI:
    def __init__(self, window):
        # Set window title and size
        self.window = window
        self.window.title('Netflix Title Picker')
        self.window.geometry("1400x600")

        # Label to display the title of the GUI
        self.label = ttk.Label(window, text="Netflix Recommendation System")
        self.label.pack(pady=10)

        # Create a frame to hold the Treeview and scrollbars
        tree_frame = ttk.Frame(window)
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

        # Populate the Treeview with data from the database
        self.populate_treeview()

        # Button to trigger built-in function to exit window
        self.button = ttk.Button(window, text="Exit", command=lambda: self.window.destroy())
        self.button.pack(pady=20)

    # Function to populate the Treeview with data from the database using function from db_functions.py
    def populate_treeview(self):
        titles = get_titles_to_select_from_db()  # Get titles from the database
        for title in titles:
            # Only include the values for the selected columns
            values = (title.type, title.title, title.country, title.release_year,
                      title.rating, title.duration, title.listed_in)
            self.treeView.insert('', 'end', values=values)

# Function to create the GUI, which will be called from main.py
def create_gui():
    window = tk.Tk()
    NetflixGUI(window)
    window.mainloop()