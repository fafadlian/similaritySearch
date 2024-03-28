import math

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

    return score, exp_score

def airport_likelihood(is_airport_match, airport_iata, airport_counts):
    if is_airport_match:
        # Look up the airport's base rate; default to a small value if not found to avoid division by zero
        airport_base_rate = airport_counts.get(airport_iata, 0.001)
        # The rarer the airport, the higher the score. Inverting the base rate serves as a simple proxy.
        return 1 / airport_base_rate
    else:
        # Airport mismatch significantly decreases the likelihood of a match
        return 0  # Or you might choose a small value to indicate low likelihood





# Example Usage
# city1 = (lon1, lat1)  # Longitude and latitude of city 1
# city2 = (lon2, lat2)  # Longitude and latitude of city 2
# max_distance = 500  # Maximum distance for comparison in kilometers

# similarity_score = location_similarity_score(*city1, *city2, max_distance)
# print(f"Location similarity score: {similarity_score:.2f}")
