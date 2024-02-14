from fuzzywuzzy import fuzz
import xml.etree.ElementTree as ET
import os
import glob
from loc_access import LocDataAccess
from distanceSimilarity import haversine, location_similarity_score
from ageSimilarity import age_similarity_score, calculate_age
import pandas as pd



def find_similar_passengers(airport_data_access, firstname, surname, name, age, iata_o, iata_d, city_name, xml_dir, nameThreshold, ageThreshold, locationThreshold):
    airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance
    all_data = []
    name_comb = firstname+" "+surname
    # List all XML files in the directory
    # print("name_comb: ", name_comb, " name: ,", name)
    xml_files = glob.glob(os.path.join(xml_dir, '*.xml'))

    # Parse each XML file and aggregate data
    for file_path in xml_files:
        data = parse_xml(file_path)
        all_data.extend(data)

    # Perform similarity search on the aggregated data
    lon_o, lat_o = airport_data_access.get_airport_lon_lat_by_iata(iata_o)
    lon_d, lat_d = airport_data_access.get_airport_lon_lat_by_iata(iata_d)
    lon_c, lat_c = airport_data_access.get_airport_lon_lat_by_city(city_name)
    similar_passengers = perform_similarity_search(name, iata_o, lat_o, lon_o, iata_d, lat_d, lon_d, age, city_name, lat_c, lon_c,  all_data, nameThreshold, ageThreshold, locationThreshold)

    return similar_passengers


def perform_similarity_search(name, iata_o, lat_o, lon_o, iata_d, lat_d, lon_d, age, city_name, lat_c, lon_c, data, nameThreshold, ageThreshold, locationThreshold):
    similar_items = []
    max_distance = 20037.5
    for item in data:
        # Assuming item structure is updated to include lon/lat for origin, destination, city
        full_name = item[2]  # Adjust according to the updated structure
        origin_lon, origin_lat = item[4], item[5]  # Adjust based on new structure
        destination_lon, destination_lat = item[7], item[8]  # Adjust based on new structure
        city_lon, city_lat = item[11], item[12]  # Adjust based on new structure
        DOB = item[9]

        # Calculate name similarity
        # print("query name: ", name, "// db name: ", full_name)
        name_similarity_score = fuzz.ratio(name.lower(), full_name.lower())

        # Calculate geographical similarities
        origin_distance = location_similarity_score(lon_o, lat_o, origin_lon, origin_lat, max_distance)
        destination_distance = location_similarity_score(lon_d, lat_d, destination_lon, destination_lat, max_distance)
        city_distance = location_similarity_score(lon_c, lat_c, city_lon, city_lat, max_distance)  # Handle cases where city data may not be available
        ageDistance = age_similarity_score(age, DOB)

        origin_distance = origin_distance if origin_distance is not None else 0
        destination_distance = destination_distance if destination_distance is not None else 0
        city_distance = city_distance if city_distance is not None else 0
        ageDistance = ageDistance if ageDistance is not None else 0

        compound_similarity = (name_similarity_score + origin_distance + destination_distance + city_distance + ageDistance) / 5

        


        # Check if all criteria are met
        if name_similarity_score >= int(nameThreshold):
            if origin_distance >= int(locationThreshold):
                if destination_distance >= int(locationThreshold):
                    if city_distance >= int(locationThreshold):
                        if ageDistance >= int(ageThreshold):
                            similar_items.append(item + (name_similarity_score, origin_distance, destination_distance, city_distance, ageDistance, compound_similarity))


    no_similar = len(similar_items)
    similar_items_sorted = sorted(similar_items, key=lambda x: x[-1], reverse=True)

    return similar_items_sorted, no_similar

def parse_xml(file_path):
    airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance

    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []
    # Fetch the IATA codes
    origin_code = root.find('.//FlightLeg/DepartureAirport').get('LocationCode') if root.find('.//FlightLeg/DepartureAirport') is not None else None
    destination_code = root.find('.//FlightLeg/ArrivalAirport').get('LocationCode') if root.find('.//FlightLeg/ArrivalAirport') is not None else None

    # Use LocDataAccess to get lat/lon for origin and destination
    origin_lat, origin_lon = airport_data_access.get_airport_lon_lat_by_iata(origin_code) if origin_code else (None, None)
    destination_lat, destination_lon = airport_data_access.get_airport_lon_lat_by_iata(destination_code) if destination_code else (None, None)

    for pnr in root.findall('.//PNR'):
        bookID = pnr.find('.//BookingRefID').get('ID') if pnr.find('.//BookingRefID') is not None else 'Unknown'
        for passenger in pnr.findall('.//Passenger'):
            name = passenger.find('.//GivenName').text.strip() + ' ' + passenger.find('.//Surname').text.strip()
            date_of_birth = passenger.find('.//DOC_SSR/DOCS').get('DateOfBirth') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            nationality = passenger.find('.//DOC_SSR/DOCS').get('PaxNationality') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            sex = passenger.find('.//DOC_SSR/DOCS').get('Gender') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            city_name = passenger.find('.//DOC_SSR/DOCA').get('CityName') if passenger.find('.//DOC_SSR/DOCA') is not None else None
            
            # Get lat/lon for the city
            city_lat, city_lon = airport_data_access.get_airport_lon_lat_by_city(city_name) if city_name else (None, None)

            # Append data including lat/lon for origin, destination, and city
            data.append((file_path, bookID, name, origin_code, origin_lat, origin_lon, destination_code, destination_lat, destination_lon, date_of_birth, city_name, city_lat, city_lon, nationality, sex))
    columns = ['FilePath', 'BookingID', 'Name', 'OriginIATA', 'OriginLat', 'OriginLon', 'DestinationIATA', 'DestinationLat', 'DestinationLon', 'DOB', 'CityName', 'CityLat', 'CityLon', 'Nationality', 'Sex']
    df = pd.DataFrame(data, columns=columns)
    df.to_csv('parsedXML.csv', index = False)
    return data

# Example usage
# user_query = 'Chris James'
# directory = 'XMLs'
# data, no_similar = find_similar_passengers(user_query, directory)
# print(data)
# print(no_similar)
