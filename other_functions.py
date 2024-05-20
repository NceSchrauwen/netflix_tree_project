#Developed by: Nina Schrauwen
#Description: Functions to interact with other files within this project.
#Date: 20/05/2024

# Fumction to get the title object based on the show ID, will use the show_id based on the user input
def get_show_id_title(netflix_titles, show_id):
    # Preprocess show_id to remove whitespace and ensure it's in the desired format
    show_id = str(show_id).strip()  # Convert to string and remove leading/trailing whitespace
    show_id = int(show_id)  # Convert to integer

    # Loop through the Netflix titles to find the title with the given show ID
    for title in netflix_titles:
        # Check if the show ID matches the given show ID, then return the title of the corresponding show ID
        if title.show_id == show_id:
            print(f'Found show ID {show_id}')
            # print(f'Type of title: {type(title)}')
            return title  # Return the entire title object

    # Debug print statements to check the length of the Netflix titles list
    # print(f'Netflix titles test length: {len(netflix_titles)}')

    # If the show ID is not found, raise a ValueError
    raise ValueError(f'Invalid show ID: {show_id}')


# To print the attributes of the sample or selected title
def print_title_attributes(title):
    print("Title attributes:")
    print(f"Show ID: {title.show_id}")
    print(f"Type: {title.type}")
    print(f"Title: {title.title}")
    print(f"Listed In: {title.listed_in}")
    print(f"Review following criteria: ")
    print(f"Release Year: {title.release_year}")
    print(f'Country: {title.country}')
    print(f'Duration: {title.duration}')
    print(f'Age rating {title.rating}')
    # print(f"Listed In: {title.date_added}")
    # print(f"Listed In Year: {title.date_added.year}")
    print("-------------------------------------------------")