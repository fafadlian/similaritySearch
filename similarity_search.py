from fuzzywuzzy import fuzz
import xml.etree.ElementTree as ET
import os
import glob
from loc_access import LocDataAccess


def find_similar_passengers(airport_data_access, firstname, surname, age, iata_o, iata_d, city_name, xml_dir):
    all_data = []

    # List all XML files in the directory
    xml_files = glob.glob(os.path.join(xml_dir, '*.xml'))

    # Parse each XML file and aggregate data
    for file_path in xml_files:
        data = parse_xml(file_path)
        all_data.extend(data)

    # Perform similarity search on the aggregated data
    similar_passengers = perform_similarity_search(query, all_data)

    return similar_passengers


def perform_similarity_search(query, data):
    threshold = 70  # Define a similarity threshold
    similar_items = []

    for item in data:
        # item structure: (xml_file, full_name, booking_id, date_of_birth, nationality)
        full_name = item[1]  # Full name is the second element in the tuple
        similarity_score = fuzz.ratio(query.lower(), full_name.lower())

        if similarity_score >= threshold:
            similar_items.append(item + (similarity_score,))
        
    no_similar = len(similar_items)
    similar_items_sorted = sorted(similar_items, key=lambda x: x[-1], reverse=True)



    return similar_items_sorted, no_similar

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []
    origin = root.find('.//FlightLeg/DepartureAirport').get('LocationCode') if root.find('.//FlightLeg/DepartureAirport') is not None else 'Unknown'
    destination = root.find('.//FlightLeg/ArrivalAirport').get('LocationCode') if root.find('.//FlightLeg/ArrivalAirport') is not None else 'Unknown'
    for pnr in root.findall('.//PNR'):
        bookID = pnr.find('.//BookingRefID').get('ID') if pnr.find('.//BookingRefID') is not None else 'Unknown'
        for passenger in pnr.findall('.//Passenger'):
            name = passenger.find('.//GivenName').text.strip() + ' ' + passenger.find('.//Surname').text.strip()
            # Example: Extracting date of birth and nationality
            date_of_birth = passenger.find('.//DOC_SSR/DOCS').get('DateOfBirth') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            nationality = passenger.find('.//DOC_SSR/DOCS').get('PaxNationality') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            sex = passenger.find('.//DOC_SSR/DOCS').get('Gender') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            city = passenger.find('.//DOC_SSR/DOCA').get('CityName') if passenger.find('.//DOC_SSR/DOCA') is not None else 'Unknown'

            # Add latitude, longitude, and age extraction if available
            data.append((file_path, name, bookID, date_of_birth, city, nationality, sex, origin, destination))
    return data

# Example usage
# user_query = 'Chris James'
# directory = 'XMLs'
# data, no_similar = find_similar_passengers(user_query, directory)
# print(data)
# print(no_similar)
