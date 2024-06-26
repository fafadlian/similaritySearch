from fuzzywuzzy import fuzz
import xml.etree.ElementTree as ET
import os
import glob
import pandas as pd
import string
import joblib


from data_loader import load_json_data
from loc_access import LocDataAccess
from locationSimilarity import haversine, location_similarity_score, location_matching, address_str_similarity_score
from ageSimilarity import age_similarity_score, calculate_age
from base_similarity import count_likelihood2, string_similarity
# from obstructor import introduce_dob_typos, introduce_error_airport, introduce_error_nat_city, introduce_error_sex, introduce_typos, update_loc_airport



# Firstname = 'Jamie'
# Surname = 'Smooth'
# name_comb = Firstname + ' ' + Surname
# OriginIATA = 'DXB'
# DestinationIATA = 'AMS' 
# DOB_q = '1973-05-22'
# CityName = 'DUBAI'
# Nationality = 'PYF'
# Sex = 'M'
# Address = '41658 Mckinney Ridges Apartment no. 270 Shawmouth, Wyoming 27446'



def find_similar_passengers(airport_data_access, firstname, surname, name, dob, iata_o, iata_d, city_name, address, sex, nationality, xml_dir, nameThreshold, ageThreshold, locationThreshold):
    airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance
    all_data = pd.DataFrame()
    similar_passengers = pd.DataFrame()
    name_comb = firstname+" "+surname
    # List all XML files in the directory
    # print("name_comb: ", name_comb, " name: ,", name)
    xml_files = glob.glob(os.path.join(xml_dir, '*.xml'))

    # Parse each XML file and aggregate data
    for file_path in xml_files:
        data = parse_xml(file_path)
        all_data = pd.concat([all_data, data], ignore_index=True)

    # Perform similarity search on the aggregated data
    lon_o, lat_o = airport_data_access.get_airport_lon_lat_by_iata(iata_o)
    lon_d, lat_d = airport_data_access.get_airport_lon_lat_by_iata(iata_d)
    lon_c, lat_c = airport_data_access.get_airport_lon_lat_by_city(city_name)
    country = airport_data_access.get_country_by_city(city_name)
    ctry_org = airport_data_access.get_country_by_airport_iata(iata_o)
    ctry_dest = airport_data_access.get_country_by_airport_iata(iata_d)
    city_org = airport_data_access.get_city_by_airport_iata(iata_o)
    city_dest = airport_data_access.get_city_by_airport_iata(iata_d)
    similar_passengers = perform_similarity_search(firstname, surname, name, iata_o, lat_o, lon_o, city_org, ctry_org, iata_d, lat_d, lon_d, city_dest, ctry_dest, dob, city_name, lat_c, lon_c, country,  nationality, sex, address, all_data, nameThreshold, ageThreshold, locationThreshold)

    return similar_passengers


def perform_similarity_search(firstname, surname, name, iata_o, lat_o, lon_o, city_org, ctry_org, iata_d, lat_d, lon_d, city_dest, ctry_dest, dob, city_name, lat_c, lon_c, country,  nationality, sex, address, df, nameThreshold, ageThreshold, locationThreshold):
    similar_items = []
    max_distance = 20037.5
    similarity_df = pd.DataFrame()
    num_records = df.shape[0]
    model_path = 'model/None_xgboost_model.joblib'
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'unique_id'}, inplace=True)

    gender_counts = df['Sex'].str.lower().value_counts(normalize=True)
    origin_airport_counts = df['OriginIATA'].str.lower().value_counts(normalize=True)
    origin_city_counts = df['OriginCity'].str.lower().value_counts(normalize=True)
    origin_country_counts = df['OriginCountry'].str.lower().value_counts(normalize=True)
    destination_airport_counts = df['DestinationIATA'].str.lower().value_counts(normalize=True)
    destination_city_counts = df['DestinationCity'].str.lower().value_counts(normalize=True)
    destination_country_counts = df['DestinationCountry'].str.lower().value_counts(normalize=True)
    city_address_counts = df['CityName'].str.lower().value_counts(normalize=True)
    country_address_counts = df['Country of Address'].str.lower().value_counts(normalize=True)
    nationality_counts = df['Nationality'].str.lower().value_counts(normalize=True)
    DOB_counts = df['DOB'].value_counts(normalize=True)
    firstname_counts = df['Firstname'].str.lower().value_counts(normalize=True)
    surname_counts = df['Surname'].str.lower().value_counts(normalize=True)

    similarity_df[['FNSimilarity', 'FN1', 'FN2', 'FN_rarity1', 'FN_rarity2', 'FN_prob1', 'FN_prob2']] = df['Firstname'].str.lower().apply(lambda x: string_similarity(firstname.lower(), x, firstname_counts, num_records))
    similarity_df[['SNSimilarity', 'SN1', 'SN2', 'SN_rarity1', 'SN_rarity2', 'SN_prob1', 'SN_prob2']] = df['Surname'].str.lower().apply(lambda x: string_similarity(surname.lower(), x, surname_counts, num_records))
    similarity_df[['DOBSimilarity', 'DOB1', 'DOB2', 'DOB_rarity1', 'DOB_rarity2', 'DOB_prob1', 'DOB_prob2']] = df['DOB'].str.lower().apply(lambda x: string_similarity(dob.lower(), x, DOB_counts, num_records))
    similarity_df['AgeSimilarity']= df['DOB'].apply(lambda x: age_similarity_score(dob, x))
    similarity_df[['strAddressSimilarity', 'jcdAddressSimilarity']] = df['Address'].apply(lambda x: address_str_similarity_score(address, x))
    similarity_df['cityAddressMatch'] = df['CityName'].apply(lambda x: location_matching(city_name, x))
    similarity_df[['cityAddressRarity1', 'cityAddressProb1']] = count_likelihood2(city_name.lower(), city_address_counts, num_records)
    similarity_df[['cityAddressRarity2', 'cityAddressProb2']] = df['CityName'].str.lower().apply(lambda x: count_likelihood2(x, city_address_counts, num_records))
    similarity_df['countryAddressMatch'] = df['Country of Address'].apply(lambda x: location_matching(country.lower(), x))
    similarity_df[['countryAddressRarity1', 'countryAddressProb1']] = count_likelihood2(country.lower(), country_address_counts, num_records)
    similarity_df[['countryAddressRarity2', 'countryAddressProb2']] = df['Country of Address'].str.lower().apply(lambda x: count_likelihood2(x, country_address_counts, num_records))
    similarity_df['sexMatch'] = df['Sex'].str.lower().apply(lambda x: location_matching(sex.lower(), x))
    similarity_df[['sexRarity1', 'sexProb1']] = count_likelihood2(sex.lower(), gender_counts, num_records)
    similarity_df[['sexRarity2', 'sexProb2']] = df['Sex'].str.lower().apply(lambda x: count_likelihood2(x, gender_counts, num_records))
    similarity_df['natMatch'] = df['Nationality'].str.lower().apply(lambda x: location_matching(nationality.lower(), x))
    similarity_df[['natRarity1', 'natProb1']] = count_likelihood2(nationality.lower(), nationality_counts, num_records)
    similarity_df[['natRarity2', 'natProb2']] = df['Nationality'].str.lower().apply(lambda x: count_likelihood2(x, nationality_counts, num_records))
    similarity_df['originAirportMatch'] = df['OriginIATA'].str.lower().apply(lambda x: location_matching(iata_o.lower(), x))
    similarity_df[['originAirportRarity1', 'originAirportProb1']] = count_likelihood2(iata_o.lower(), origin_airport_counts, num_records)
    similarity_df[['originAirportRarity2', 'originAirportProb2']] = df['OriginIATA'].str.lower().apply(lambda x: count_likelihood2(x, origin_airport_counts, num_records))
    similarity_df['destinationAirportMatch'] = df['DestinationIATA'].str.lower().apply(lambda x: location_matching(iata_d.lower(), x))
    similarity_df[['destinationAirportRarity1', 'destinationAirportProb1']] = count_likelihood2(iata_o.lower(), origin_airport_counts, num_records)
    similarity_df[['destinationAirportRarity2', 'destinationAirportProb2']] = df['DestinationIATA'].str.lower().apply(lambda x: count_likelihood2(x, destination_airport_counts, num_records))
    similarity_df['originCityMatch'] = df['OriginCity'].str.lower().apply(lambda x: location_matching(city_org.lower(), x))
    similarity_df[['originCityRarity1', 'originCityProb1']] = count_likelihood2(city_org.lower(), origin_city_counts, num_records)
    similarity_df[['originCityRarity2', 'originCityProb2']] = df['OriginCity'].str.lower().apply(lambda x: count_likelihood2(x, origin_city_counts, num_records))
    similarity_df['destinationCityMatch'] = df['DestinationCity'].str.lower().apply(lambda x: location_matching(city_dest.lower(), x))
    similarity_df[['destinationCityRarity1', 'destinationCityProb1']] = count_likelihood2(city_dest.lower(), destination_city_counts, num_records)
    similarity_df[['destinationCityRarity2', 'destinationCityProb2']] = df['DestinationCity'].str.lower().apply(lambda x: count_likelihood2(x, destination_city_counts, num_records))
    similarity_df['originCountryMatch'] = df['OriginCountry'].str.lower().apply(lambda x: location_matching(ctry_org.lower(), x))
    similarity_df[['originCountryRarity1', 'originCountryProb1']] = count_likelihood2(ctry_org.lower(), origin_country_counts, num_records)
    similarity_df[['originCountryRarity2', 'originCountryProb2']] = df['OriginCountry'].str.lower().apply(lambda x: count_likelihood2(x, origin_country_counts, num_records))
    similarity_df['destinationCountryMatch'] = df['DestinationCountry'].str.lower().apply(lambda x: location_matching(ctry_dest.lower(), x))
    similarity_df[['destinationCountryRarity1', 'destinationCountryProb1']] = count_likelihood2(ctry_dest.lower(), destination_country_counts, num_records)
    similarity_df[['destinationCountryRarity2', 'destinationCountryProb2']] = df['DestinationCountry'].str.lower().apply(lambda x: count_likelihood2(x, destination_country_counts, num_records))
    similarity_df[['originSimilarity', 'originExpScore']] = df.apply(lambda row: location_similarity_score(lon_o, lat_o, row['OriginLon'], row['OriginLat'], max_distance), axis=1, result_type='expand')
    similarity_df[['destinationSimilarity', 'destinationExpScore']] = df.apply(lambda row: location_similarity_score(lon_d, lat_d, row['DestinationLon'], row['DestinationLat'], max_distance), axis=1, result_type='expand')
    similarity_df.reset_index(inplace=True)
    similarity_df.rename(columns={'index': 'unique_id'}, inplace=True)

    test = similarity_df.select_dtypes(exclude=['object', 'string']).drop(columns=['Class', 'Mark', 'DOBSimilarity', 'strAddressSimilarity', 'unique_id'], errors='ignore')
    model = joblib.load(model_path)
    predictions = model.predict(test)
    df['predictions'] = predictions
    result_df = pd.merge(df, similarity_df, on='unique_id', how='inner')
    nameThreshold = float(nameThreshold) if nameThreshold else 0
    ageThreshold = float(ageThreshold) if ageThreshold else 0
    locationThreshold = float(locationThreshold) if locationThreshold else 0

    filtered_result_df = result_df[(result_df['FNSimilarity'] >= nameThreshold) &
                        (result_df['SNSimilarity'] >= nameThreshold) &
                        (result_df['AgeSimilarity'] >= ageThreshold)
                        ]
    # filtered_result_df.to_csv('test/filtered_resilt_df.csv')
    filtered_result_df.sort_values(by = ['predictions'], ascending = False, inplace = True)
    return filtered_result_df

def parse_xml(file_path):
    airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance

    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []
    # Fetch the IATA codes
    origin_code = root.find('.//FlightLeg/DepartureAirport').get('LocationCode') if root.find('.//FlightLeg/DepartureAirport') is not None else None
    destination_code = root.find('.//FlightLeg/ArrivalAirport').get('LocationCode') if root.find('.//FlightLeg/ArrivalAirport') is not None else None

    # Use LocDataAccess to get lat/lon for origin and destination
    origin_lon, origin_lat = airport_data_access.get_airport_lon_lat_by_iata(origin_code) if origin_code else (None, None)
    destination_lon, destination_lat = airport_data_access.get_airport_lon_lat_by_iata(destination_code) if destination_code else (None, None)

    for pnr in root.findall('.//PNR'):
        bookID = pnr.find('.//BookingRefID').get('ID') if pnr.find('.//BookingRefID') is not None else 'Unknown'
        for passenger in pnr.findall('.//Passenger'):
            firstname = passenger.find('.//GivenName').text.strip()
            surname = passenger.find('.//Surname').text.strip()
            name = passenger.find('.//GivenName').text.strip() + ' ' + passenger.find('.//Surname').text.strip()
            travel_doc_nbr = passenger.find('.//DOC_SSR/DOCO').get('TravelDocNbr') if passenger.find('.//DOC_SSR/DOCO') is not None else 'Unknown'
            place_of_issue = passenger.find('.//DOC_SSR/DOCO').get('PlaceOfIssue') if passenger.find('.//DOC_SSR/DOCO') is not None else 'Unknown'
            date_of_birth = passenger.find('.//DOC_SSR/DOCS').get('DateOfBirth') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            nationality = passenger.find('.//DOC_SSR/DOCS').get('PaxNationality') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            sex = passenger.find('.//DOC_SSR/DOCS').get('Gender') if passenger.find('.//DOC_SSR/DOCS') is not None else 'Unknown'
            city_name = passenger.find('.//DOC_SSR/DOCA').get('CityName') if passenger.find('.//DOC_SSR/DOCA') is not None else None
            address = passenger.find('.//DOC_SSR/DOCA').get('Address') if passenger.find('.//DOC_SSR/DOCA') is not None else None
            
            
            
            # Get lat/lon for the city
            city_lat, city_lon = airport_data_access.get_airport_lon_lat_by_city(city_name) if city_name else (None, None)
            city_org = airport_data_access.get_city_by_airport_iata(origin_code) if origin_code else (None)
            city_dest = airport_data_access.get_city_by_airport_iata(destination_code) if destination_code else (None)
            ctry_org = airport_data_access.get_country_by_airport_iata(origin_code) if origin_code else (None)
            ctry_dest = airport_data_access.get_country_by_airport_iata(destination_code) if destination_code else (None)
            country_of_address = airport_data_access.get_country_by_city(city_name) if city_name else (None)

            # Append data including lat/lon for origin, destination, and city
            data.append((file_path, bookID, firstname, surname, name, travel_doc_nbr, place_of_issue, origin_code, city_org, ctry_org, origin_lat, origin_lon, destination_code, city_dest, ctry_dest, destination_lat, destination_lon, date_of_birth, city_name, city_lat, city_lon, address,  country_of_address, nationality, sex))
    columns = ['FilePath', 'BookingID', 'Firstname', 'Surname', 'Name', 'Travel Doc Number', 'Place of Issue', 'OriginIATA', 'OriginCity', 'OriginCountry', 'OriginLat', 'OriginLon', 'DestinationIATA', 'DestinationCity', 'DestinationCountry', 'DestinationLat', 'DestinationLon', 'DOB', 'CityName', 'CityLat', 'CityLon', 'Address', 'Country of Address', 'Nationality', 'Sex']
    df = pd.DataFrame(data, columns=columns)
    # df.to_csv('parsedXML.csv', index = False)
    return df



# Example usage
# user_query = 'Chris James'
# directory = 'XMLs'
# data, no_similar = find_similar_passengers(user_query, directory)
# print(data)
# print(no_similar)
