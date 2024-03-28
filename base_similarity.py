
from fuzzywuzzy import fuzz
import pandas as pd
import numpy as np

def count_likelihood2(type, counter, num_records):
    # Ensure data_count is a dictionary
    # if not isinstance(counter, dict):
    #     raise ValueError("data_count must be a dictionary.")

    # Get the likelihood of 'type', defaulting to 0 if not found
    type_ll = counter.get(type, 0)
    prob1 = float('inf') if type_ll == 0 else 1 / (type_ll * num_records)

    try:
        # Handle division by zero if 'type' is not found or has a count of 0
        if type_ll == 0:
            raise ValueError(f"The specified type '{type}' was not found or has zero occurrences in the data.")
        return pd.Series([type_ll, prob1])
    except ZeroDivisionError:
        print("Division by zero encountered. This is likely due to the specified type not being present in the data or having zero occurrences.")
        return pd.Series([None, None])
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return pd.Series([None, None])
    
def string_similarity(string1, string2, string_counts, num_records):
    # Ensure input strings are valid
    if not isinstance(string1, str) or not isinstance(string2, str):
        raise ValueError("Both string1 and string2 must be valid strings.")
    
    # Ensure string_counts is accessible and num_records is valid
    # if not isinstance(string_counts, dict):
    #     raise ValueError("string_counts must be a dictionary.")
    if not isinstance(num_records, int) or num_records <= 0:
        raise ValueError("num_records must be a positive integer.")
    
    # Calculate string similarity
    try:
        str_similarity = fuzz.ratio(string1.lower(), string2.lower())
    except Exception as e:
        print(f"Error calculating string similarity: {e}")
        return None, None, None
    
    # Initialize default values for inverse likelihoods
    str1_ll_inverse = str2_ll_inverse = None
    # Attempt to calculate likelihoods, handling division by zero
    try:
        str1_ll = string_counts.get(string1.lower(), 0)
        str2_ll = string_counts.get(string2.lower(), 0)
        
        str1_ll_inverse = float('inf') if str1_ll == 0 else 1 / str1_ll
        str2_ll_inverse = float('inf') if str2_ll == 0 else 1 / str2_ll
    except ZeroDivisionError:
        print("Division by zero encountered in likelihood calculation.")
    except Exception as e:
        print(f"Error during likelihood calculation: {e}")
    
    # Calculate probabilities, handling division by zero explicitly
    try:
        prob1 = float('inf') if str1_ll == 0 else 1 / (str1_ll * num_records)
        prob2 = float('inf') if str2_ll == 0 else 1 / (str2_ll * num_records)
    except ZeroDivisionError:
        prob1 = prob2 = float('inf')  # Assign infinity if division by zero occurs
    except Exception as e:
        print(f"Error during probability calculation: {e}")
        prob1 = prob2 = None
    
    return pd.Series([str_similarity, string1, string2, str1_ll, str2_ll, prob1, prob2])