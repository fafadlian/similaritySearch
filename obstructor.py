from random import random, choice, choices, randint
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loc_access import LocDataAccess
import string


airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance


def introduce_dob_typos(dob, typo_rate):
    dob_parts = dob.split("-")
    old_dob = dob
    year = dob_parts[0]
    month = dob_parts[1]
    day = dob_parts[2]
    
    if random() < typo_rate:
        year = list(year)
        digit_to_change = randint(0, len(year) - 1)
        year[digit_to_change] = str(randint(0, 9))
        year = "".join(year)

    if random() < typo_rate:
        month = list(month)
        digit_to_change = randint(0, len(month) - 1)
        month[digit_to_change] = str(randint(0, 1))
        month = "".join(month)

    if random() < typo_rate:
        day = list(day)
        digit_to_change = randint(0, len(day) - 1)
        day[digit_to_change] = str(randint(0, 3))
        day = "".join(day)
        
    try:
        new_date = datetime(int(year), int(month), int(day))
    except ValueError:
        # Invalid date, correct it to a valid date
        year = dob_parts[0]
        month = dob_parts[1]
        day = dob_parts[2]
    if  (int(year) > 2100 or int(year) < 1900):
        year = dob_parts[0]

    return f"{year}-{month}-{day}"

def introduce_typos(text, typo_rate):
    """Introduces a diverse set of typos into a given text based on the specified typo rate.
    
    Args:
        text (str): The input text where typos will be introduced.
        typo_rate (float): The probability of introducing a typo at each character position.
    
    Returns:
        str: The text with introduced typos.
    """
    typo_text = list(text)
    operations = ['delete', 'insert', 'substitute', 'swap']
    for i in range(len(typo_text)):
        if random() < typo_rate:
            operation = choice(operations)
            if operation == 'delete':
                # Delete the character at the current position
                typo_text[i] = ''
            elif operation == 'insert':
                # Insert a random character at the current position
                typo_text[i] = typo_text[i] + choice(string.ascii_letters)
            elif operation == 'substitute':
                # Substitute the character at the current position with a random character
                typo_text[i] = choice(string.ascii_letters)
            elif operation == 'swap' and i < len(typo_text) - 1:
                # Swap the character with the next character
                typo_text[i], typo_text[i + 1] = typo_text[i + 1], typo_text[i]
    
    # Filter out empty strings resulting from deletions and join the list back into a string
    return ''.join(filter(None, typo_text))

def introduce_error_airport(row, airport_column, airports_df, replacement_preference, error_rate):
    # Generate a random number between 0 and 1 to compare with the error rate
    if random() > error_rate:
        # If the generated number is greater than the error rate, don't introduce an error
        return row[airport_column]
    
    current_airport = row[airport_column]
    city, country = airports_df[airports_df['IATA'] == current_airport][['City', 'HH_ISO']].iloc[0]
    
    if replacement_preference == 'city':
        city_airports = airports_df[(airports_df['City'] == city) & (airports_df['IATA'] != current_airport)]
        if not city_airports.empty:
            return np.random.choice(city_airports['IATA'].values)
    
    if replacement_preference in ['city', 'country']:
        country_airports = airports_df[(airports_df['HH_ISO'] == country) & (airports_df['IATA'] != current_airport)]
        if not country_airports.empty:
            return np.random.choice(country_airports['IATA'].values)
    
    return np.random.choice(airports_df[airports_df['IATA'] != current_airport]['IATA'].values)

def introduce_error_nat_city(row, geocrosswalk, column_df, column_geo, error_rate):
    if random() > error_rate:
        return row[column_df]
    
    new_value = choice(geocrosswalk[column_geo].unique())
    row[column_df] = new_value
    return new_value

def introduce_error_sex(row, error_rate):
    if random() > error_rate:
        return row['Sex']
    
    new_value = choice(['M', 'F'])
    row['Sex'] = new_value
    return new_value

def update_loc_airport(row, changed_col):
    lon, lat = airport_data_access.get_airport_lon_lat_by_iata(row[changed_col])
    city = airport_data_access.get_city_by_airport_iata(row[changed_col])
    country = airport_data_access.get_country_by_airport_iata(row[changed_col])
    return pd.Series([lat, lon, city, country])