
from fuzzywuzzy import fuzz
import pandas as pd
import numpy as np

def count_likelihood2(type, counter, num_records):
    """
    Calculates the likelihood based on counts from the counter, with internal defaults for unseen categories.

    :param type: The category to look up.
    :param counter: A collection with counts of each category.
    :param num_records: The total number of records.
    :return: A pandas Series containing the rarity and probability.
    """
    # Default values for unseen categories
    default_rarity = 1.0  # Adjust as needed, e.g., for very rare categories
    default_prob = 0.0  # or some other sensible default for your use case

    # Get the count of 'type', defaulting to 0 if not found
    type_count = counter.get(type.lower(), 0)
    
    # Calculate rarity and probability
    if type_count > 0 and num_records > 0:
        rarity = type_count / num_records
        prob = 1 / (type_count + 1)  # Adding 1 for Laplace smoothing to avoid division by zero
    else:
        rarity = default_rarity
        prob = default_prob

    return pd.Series([rarity, prob])

    
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
        
        str1_ll_inverse = 1 if str1_ll == 0 else 1 / str1_ll
        str2_ll_inverse = 1 if str2_ll == 0 else 1 / str2_ll
    except ZeroDivisionError:
        print("Division by zero encountered in likelihood calculation.")
    except Exception as e:
        print(f"Error during likelihood calculation: {e}")
    
    # Calculate probabilities, handling division by zero explicitly
    try:
        prob1 = 0 if str1_ll == 0 else 1 / (str1_ll * num_records)
        prob2 = 0 if str2_ll == 0 else 1 / (str2_ll * num_records)
    except ZeroDivisionError:
        prob1 = prob2 = 0  
    except Exception as e:
        print(f"Error during probability calculation: {e}")
        prob1 = prob2 = None
    
    return pd.Series([str_similarity, string1, string2, str1_ll, str2_ll, prob1, prob2])