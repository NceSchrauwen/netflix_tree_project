import random
from title import NetflixTitle
import mysql.connector

global netflix_titles


def connect_db(num_results=200):
    global netflix_titles
    # Establish a connection to the MySQL server
    mydb = mysql.connector.connect(
        host="localhost",      # Replace with your MySQL host
        port="8080",           # Replace with your MySQL port
        user="Admin",          # Replace with your MySQL username
        password="Brownie#99", # Replace with your MySQL password
        database="netflix_titles"      # Replace with your database name
    )

    # Create a cursor to execute SQL queries
    cursor = mydb.cursor()

    # Execute SQL query
    cursor.execute("SELECT * FROM netflix_titles.netflix_movies;")

    # Fetch all rows into a list
    rows = cursor.fetchall()
    netflix_titles = [NetflixTitle(*row) for row in rows]

    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # print_attributes(netflix_titles)

    return netflix_titles


def print_attributes(netflix_titles):
    for title in netflix_titles:
        print(f"- - -Title attributes- - -")
        for attribute, value in vars(title).items():
            print(f"{attribute}: {value}")
        print("---------")


def print_title_attributes(title):
    print("Title attributes:")
    print(f"Show ID: {title.show_id}")
    print(f"Type: {title.type}")
    print(f"Title: {title.title}")
    print(f"Release Year: {title.release_year}")
    print(f"Listed In: {title.listed_in}")
    print(f'Country: {title.country}')
    print(f'Duration: {title.duration}')
    print(f'Age rating {title.rating}')
    # print(f"Listed In: {title.date_added}")
    # print(f"Listed In Year: {title.date_added.year}")


def get_sample_title(netflix_titles):
    if not netflix_titles:
        print("Error: Netflix titles set is empty.")
        return None

    selected_title = random.choice(list(netflix_titles))

    return selected_title

def get_standup_comedy_titles(netflix_titles):
    standup_comedy_titles = [title for title in netflix_titles if 'Stand-Up Comedy' in title.listed_in]

    if not standup_comedy_titles:
        print("Error: No stand-up comedy titles found.")
        return None

    selected_title = random.choice(standup_comedy_titles)

    return selected_title

def get_tv_show_titles(netflix_titles):
    tv_show_titles = [title for title in netflix_titles if title.type == 'TV Show']

    if not tv_show_titles:
        print("Error: No TV show titles found.")
        return None

    selected_title = random.choice(tv_show_titles)

    return selected_title

def get_movie_titles(netflix_titles):
    movie_titles = [title for title in netflix_titles if title.type == 'Movie']

    if not movie_titles:
        print("Error: No movie titles found.")
        return None

    selected_title = random.choice(movie_titles)

    return selected_title

# Main function to run the application
if __name__ == '__main__':
    # connect_db(num_results=10)

    netflix_titles = connect_db(num_results=150)

    #original sample title pick function
    selected_title = get_sample_title(netflix_titles)
    print_title_attributes(selected_title)

    # custom title pick functions
    # selected_title = get_movie_titles(netflix_titles)
    # selected_title = get_tv_show_titles(netflix_titles)

    # For intensive testing of long movie titles with this genre use the following line
    # selected_title = get_standup_comedy_titles(netflix_titles)
    # print_title_attributes(selected_title)
    #
    # num_suggestions = 5
    # decision_tree_root = build_decision_tree(netflix_titles, selected_title, num_suggestions)
    # #
    #
    # #
    # recommended_titles = get_recommended_titles(decision_tree_root, num_suggestions)
    # print(f'Recommended Titles:')
    # for title in recommended_titles:
    #     print_title_attributes(title)
    #     print('--- end ---')