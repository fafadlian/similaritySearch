from data_loader import load_json_data
from similarity_search import perform_similarity_search, find_similar_passengers, parse_xml
from api_client import fetch_pnr_data, save_json, count_unique_flight_ids
from flask import Flask, request, jsonify, render_template
from loc_access import LocDataAccess
from datetime import datetime
import pandas as pd
import numpy as np
from flask_talisman import Talisman
import os

app = Flask(__name__)

df_airports = pd.read_csv('data/geoCrosswalk/GeoCrossWalkMed.csv')
df_airports.set_index('IATA', inplace=True)
xml_dir = "XMLs"

@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the submission of the date range
@app.route('/submit_param', methods=['POST'])
def submit_param():
    try:
        data = request.json
        print("Received data:", data)  # Debugging line
        arrival_date_from = data.get('arrivalDateFrom')
        arrival_date_to = data.get('arrivalDateTo')
        flight_number = data.get('flightNbr')

        api_url = 'https://tenacity-rmt.eurodyn.com/api/datalist/flights'
        access_token = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhMGI4M2U5OS1mZWE2LTRjMzItYjNlNi1iOWE0ODhlZjE3YjIiLCJpYXQiOjE3MDkyODg4NDksImV4cCI6MTcxMTkxNzkwNX0.O0n_a_ICZFYtaT6zK3fmKlrpmJV8FqbwSSeYSI8KJ5RFh5f5NR-usxzfnoh9yvtd7iwfK1ym6UjYKtf5TDQQiQ'
        params = {
            'ft_flight_leg_arrival_date_time_from': arrival_date_from,
            'ft_flight_leg_arrival_date_time_to': arrival_date_to,
            'ft_flight_leg_flight_number': flight_number
            # ... other parameters ...
        }
        print("Params:, ", params)

        pnr_data = fetch_pnr_data(api_url, access_token, params)
        print('PNR data received:', pnr_data)
        if pnr_data:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f'pnr_data_{timestamp}.json'
            save_json(pnr_data, 'jsonData', file_name)
            return jsonify({'message': 'Data fetched and saved', 'fileName': file_name})
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500
    except Exception as e:
        print(f"Error in submit_param: {e}")  # Debugging line
        app.logger.error(f"Error in submit_param: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/count_unique_flight_ids', methods=['POST'])
def count_flight_ids():
    try:
        file_name = request.json.get('fileName')
        if not file_name:
            return jsonify({'error': 'No file name provided'}), 400

        file_path = f'jsonData/{file_name}'
        count = count_unique_flight_ids(file_path)

        return jsonify({'unique_flight_id_count': count})
    except Exception as e:
        return jsonify({'error': f'Error processing the file: {str(e)}'}), 500



@app.route('/perform_similarity_search', methods=['POST'])
def handle_similarity_search():
    airport_data_access = LocDataAccess.get_instance()
    similar_passengers = pd.DataFrame()
    
    # Now you can use airport_data_access to get airport data
    # Example: lon, lat = airport_data_access.get_airport_lon_lat_by_iata(iata_code)
    
    query_data = request.json.get('query', {})
    
    # Now you can safely access the nested data
    firstname = query_data.get('firstname')  # Now this correctly uses .get() on the nested dictionary
    surname = query_data.get('surname')
    dob = query_data.get('dob')
    iata_o = query_data.get('iata_o')
    iata_d = query_data.get('iata_d')
    city_name = query_data.get('city_name')
    name = query_data.get('name')
    address = query_data.get('address')
    sex = query_data.get('sex')
    nationality = query_data.get('nationality')
    nameThreshold = query_data.get('nameThreshold')
    ageThreshold = query_data.get('ageThreshold')
    locationThreshold = query_data.get('locationThreshold')


    # Pass the airport data access instance to your service function if needed
    print("Threshold: ", name, nameThreshold, ageThreshold, locationThreshold)
    # Your existing code to find similar passengers
    similar_passengers = find_similar_passengers(airport_data_access, firstname, surname, name, dob, iata_o, iata_d, city_name, address, sex, nationality, xml_dir, nameThreshold, ageThreshold, locationThreshold)

    # Replace np.inf and -np.inf with np.nan in the DataFrame, then convert to a dictionary for JSON response
    similar_passengers.replace([np.inf, -np.inf], np.nan, inplace=True)
    similar_passengers_json = similar_passengers.where(pd.notnull(similar_passengers), None).to_dict(orient='records')
    similar_passengers_json = similar_passengers.to_dict(orient='records')
    response_data = {
    'data': similar_passengers_json,
    'message': 'Similar passengers found successfully'
    }
    # Creating the JSON response with Flask's jsonify
    response = jsonify(response_data)
    return response

if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=True, port=5002)
    #change debug=True for debug
