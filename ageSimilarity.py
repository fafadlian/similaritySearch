from datetime import datetime

def calculate_age(dob):
    """Calculate age from DOB."""
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def age_similarity_score(query_age, dob):
    """Calculate a normalized similarity score for age."""
    actual_age = calculate_age(dob)
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

    # Calculate score (1 - (age difference / age range))
    if age_difference <= age_range:
        return 1 - (age_difference / age_range)
    else:
        return 0

# Example Usage
dob_example = datetime(2000, 1, 1)  # Example DOB
query_age =  12 # Example query age

similarity_score = age_similarity_score(query_age, dob_example)
print(f"Age similarity score: {similarity_score:.2f}")