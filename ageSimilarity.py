from datetime import datetime

def calculate_age(dob):
    """Calculate age from DOB."""
    today = datetime.today()
    dob = datetime.strptime(dob, "%Y-%m-%d")
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def age_similarity_score(query_dob, dob):
    """Calculate a normalized similarity score for age."""
    actual_age = calculate_age(dob)
    query_age = calculate_age(query_dob)
    # try:
    #     query_age = int(query_age)
    # except ValueError:
    #     # Handle the case where query_age cannot be converted to an integer
    #     print("Error: query_age is not a valid integer.")
    #     return 0
    age_difference = abs(query_age - actual_age)

    # Define dynamic age range based on query_age
    if query_age < 18:
        age_range = 2
    elif 18 <= query_age <= 25:
        age_range = 4
    elif 25 < query_age <= 60:
        age_range = 10
    else:
        age_range = 5

    # Adjusted calculation to scale score to 0-100
    # If the age difference is within the age range, calculate a diminishing score
    if age_difference <= age_range:
        # Scale factor to adjust the effect of age difference within the range
        scale_factor = 100 / age_range
        # Calculate the similarity score such that it decreases with age difference
        score = 100 - (age_difference * scale_factor)
    else:
        # If the age difference is beyond the range, consider the score as 0 for simplicity
        score = 0
    return score

# Example Usage
# dob_example = datetime(2000, 1, 1)  # Example DOB
# query_age =  12 # Example query age

# similarity_score = age_similarity_score(query_age, dob_example)
# print(f"Age similarity score: {similarity_score:.2f}")