from collections import deque

country_preference = None
duration_preference = None
classic_preference = None
directions = []
criteria = []
criterion = None
recommended_titles = []
child_friendly_preference = None


# constructor of the node class
class DecisionTreeNode:
    def __init__(self, criterion, left_child=None, right_child=None, recommended_titles=None):
        self.criterion = criterion
        self.left_child = left_child
        self.right_child = right_child
        self.recommended_titles = recommended_titles if recommended_titles else []

    # Define __str__ method to print information about the node
    def __str__(self):
        return f"Criterion: {self.criterion}\n" \
               f"Left Child: {self.left_child}\n" \
               f"Right Child: {self.right_child}\n" \
            # f"Recommended Titles: {self.recommended_titles}\n"

# to get user input on multiple criteria
def get_user_input():
    # Get user input
    global country_preference
    global duration_preference
    global child_friendly_preference
    global classic_preference

    # while True:
    #     preference = input("Do you want to watch a movie from the US or the UK? (yes/no): ").strip().lower()
    #     if preference in ["yes", "no"]:
    #         country_preference = preference
    #         break
    #     else:
    #         print("Invalid input. Please enter 'yes' or 'no'.")

    # while True:
    #     duration_pref = input("Do you want to watch a short movie/season? (yes/no): ").strip().lower()
    #     if duration_pref in ["yes", "no"]:
    #         duration_preference = duration_pref
    #         break
    #     else:
    #         print("Invalid input. Please enter 'yes' or 'no'.")

    while True:
        child_friendly_pref = input("Do you want to watch a child-friendly (under age 13) movie/season? (yes/no): ").strip().lower()
        if child_friendly_pref in ["yes", "no"]:
            child_friendly_preference = child_friendly_pref
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    while True:
        classic_pref = input("Do you want to watch a classic movie/season? (yes/no): ").strip().lower()
        if classic_pref in ["yes", "no"]:
            classic_preference = classic_pref
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")



# to build the decision tree and get the recommendations based on the user input
def build_decision_tree(netflix_data, selected_title, num_suggestions):
    root = DecisionTreeNode(criterion="Initial Criterion")
    get_user_input()

    recursive_build_tree(root, netflix_data, selected_title, num_suggestions)
    print(f'Root: {root}')
    return root


# function to build node and its path based on the direction input
def build_path(node, directions, criteria, recommended_titles):
    global criterion
    # if there are no directions left, then return the node
    if not directions:
        return node

    directions_copy = directions.copy()
    criterion = criteria.pop(0)

    # pop the first element of the list to get the current direction to process
    direction = directions_copy.pop(0)

    # if the direction is not left or right, then raise a ValueError
    if direction not in ['left', 'right']:
        raise ValueError(f"Invalid direction: {direction}. Only 'left' or 'right' are allowed.")

    # if the direction is left, then create a new node and set it to the left child of the current node
    if direction == 'left':
        if node.left_child is None:
            node.left_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then recurse and append the current node with a left child and the
        # remaining directions
        else:
            node.left_child.criterion = criterion
            node.left_child.recommended_titles = recommended_titles
        return build_path(node.left_child, directions_copy, criteria, recommended_titles)
    # if the direction is right, then create a new node and set it to the right child of the current node
    elif direction == 'right':
        if node.right_child is None:
            node.right_child = DecisionTreeNode(criterion=criterion, recommended_titles=recommended_titles)
        # if there is already a node set, then recurse and append the current node with a right child and the
        # remaining directions
        else:
            node.right_child.criterion = criterion
            node.right_child.recommended_titles = recommended_titles
        return build_path(node.right_child, directions_copy, criteria, recommended_titles)

    # if a new node is made then recurse with the new node and the remaining directions
    return build_path(node, directions_copy, criteria, recommended_titles)


# to recursively run through the decision tree searching for the best recommendation
def recursive_build_tree(node, netflix_data, selected_title, num_suggestions):
    global country_preference
    global duration_preference
    global directions
    global criterion
    global criteria
    global recommended_titles
    global child_friendly_preference
    global classic_preference

    directions = []
    criteria = []
    recommended_titles = []

    if directions is None:
        directions = []

    us_uk_data = []
    other_data = []

    # If the node is the root node
    if node.criterion == "Initial Criterion":
        # Recommend titles based on (any of) the genre(s) that the selected title belongs to
        similar_genre_data = [title for title in netflix_data if any(
            genre.lower() in title.listed_in.lower() for genre in selected_title.listed_in.split(','))]

        # print(f'Similar genre data: {len(similar_genre_data)}')
        # for title in similar_genre_data:
        #     print(title)

        # If the sample title is a movie, then recommend movie titles
        if selected_title.type.lower() == "movie":
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "movie"]
        # If the sample title is a tv show, then recommend tv show titles
        elif selected_title.type.lower() == "tv show":
            same_type_data = [title for title in similar_genre_data if title.type.lower() == "tv show"]
        else:
            print('Invalid title type')
            return

        # If no titles are found that have the same genre and type as the sample titl
        if not same_type_data:
            print('No titles found that have the same genre and type')
            return

        # TODO: Put decision tree logic here

        if child_friendly_preference == "yes":
            child_friendly_data = [title for title in same_type_data if
                                   title.rating and title.rating.lower() in ["g", "tv-y", "tv-y7", "tv-g", "pg", "tv-pg"]]
            if child_friendly_data:
                directions.append("left")
                criteria.append("Child-Friendly Titles")
                recommended_titles = child_friendly_data
            if classic_preference == "yes":
                classic_data = [title for title in child_friendly_data if title.release_year <= 2010]
                if classic_data:
                    directions.append("left")
                    criteria.append("Classic Titles")
                    recommended_titles = classic_data
            elif classic_preference == "no":
                non_classic_data = [title for title in child_friendly_data if title.release_year > 2010]
                if non_classic_data:
                    directions.append("right")
                    criteria.append("Non-Classic Titles")
                    recommended_titles = non_classic_data

        elif child_friendly_preference == "no":
            non_child_friendly_data = [title for title in same_type_data if title.rating and title.rating.lower() not in ["g", "tv-y", "tv-y7", "tv-g", "pg", "tv-pg"]]

            if non_child_friendly_data:
                directions.append("right")
                criteria.append("Non-Child-Friendly Titles")
                recommended_titles = non_child_friendly_data
            if classic_preference == "yes":
                classic_non_child_friendly_data = [title for title in non_child_friendly_data if title.release_year <= 2010]
                if classic_non_child_friendly_data:
                    directions.append("left")
                    criteria.append("Classic Titles")
                    recommended_titles = classic_non_child_friendly_data
            elif classic_preference == "no":
                non_classic_non_child_friendly_data = [title for title in non_child_friendly_data if title.release_year > 2010]
                if non_classic_non_child_friendly_data:
                    directions.append("right")
                    criteria.append("Non-Classic Titles")
                    recommended_titles = non_classic_non_child_friendly_data

    new_node = build_path(node, directions, criteria, recommended_titles)

    return


# It is only called in the main function to get the recommended titles with the decision tree logic
# Then it will be called recursively to transverse the tree and get the recommended titles
def get_recommended_titles(node, num_suggestions):
    recommended_titles = []
    # print(f'Recommended titles so far {len(node.recommended_titles)} at node {node.criterion}')

    # base case: if node is None, return an empty list
    if node is None:
        return recommended_titles

    # explore left tree for possible recommendations
    print(f"Exploring left child of node {node.criterion}.")
    # recursive call to get recommended titles from left child
    left_recommended = get_recommended_titles(node.left_child, num_suggestions)
    recommended_titles.extend(left_recommended)
    print(f"Recommended found left side: {len(left_recommended)}")

    # add titles from current node to recommended titles list (from one or either side of the tree)
    if node.recommended_titles:
        recommended_titles.extend(node.recommended_titles)

    # explore right tree for possible recommendations
    print(f"Exploring right child of node {node.criterion}.")
    # recursive call to get recommended titles from right child
    right_recommended = get_recommended_titles(node.right_child, num_suggestions)
    recommended_titles.extend(right_recommended)
    print(f"Recommended found right side: {len(right_recommended)}")

    # is keeping score how many recommended titles are found so far in total (from left, right and current node)
    print(f"Recommended titles so far: {len(recommended_titles)}")

    # return the recommended titles list and limit the amount of suggestions to the user
    return recommended_titles[:num_suggestions]

