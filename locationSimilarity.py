import math
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import jaccard_score
import numpy as np
import pandas as pd


def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def location_similarity_score(lon1, lat1, lon2, lat2, max_distance):
    """Calculate a normalized similarity score based on the distance between two locations."""
    distance = haversine(lon1, lat1, lon2, lat2)
    distance = min(distance, max_distance)
    # Normalize the score such that it is 100 for 0 distance and scales down to 0 as distance reaches max_distance
    score = (1 - (distance / max_distance)) * 100
    exp_score = math.exp(-distance/max_distance)
    score = max(0, score)

    return pd.Series([score, exp_score])

def address_str_similarity_score(string1, string2):
    # FuzzyWuzzy similarity
    str_similarity = fuzz.ratio(string1.lower(), string2.lower())
    
    # Vectorize the input strings for n-gram analysis
    vectorizer2 = CountVectorizer(analyzer='char', ngram_range=(3, 3))
    X = vectorizer2.fit_transform([string1.lower(), string2.lower()]).toarray()
    
    # Calculate Jaccard similarity based on the n-gram presence/absence
    # Jaccard similarity = (Intersection of A and B) / (Union of A and B)
    # Since X is a binary array, we can use logical operations
    intersection = np.logical_and(X[0], X[1]).sum()
    union = np.logical_or(X[0], X[1]).sum()
    jcd_score = intersection / union if union != 0 else 0
    
    return pd.Series([str_similarity, jcd_score])

def location_matching(location1, location2):
    if location1 == location2:
        return 1
    else:
        return 0
