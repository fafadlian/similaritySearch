from data_loader import load_json_data
from similarity_search import perform_similarity_search, find_similar_passengers, parse_xml
from api_client import fetch_pnr_data, save_json, count_unique_flight_ids
from flask import Flask, request, jsonify, render_template
from loc_access import LocDataAccess
from datetime import datetime
import pandas as pd
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
        access_token = os.getenv('eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIzZTU0MTg3NC1iYTNiLTQ5M2EtOGZkYy0xYjgwMGI5YWMxMjYiLCJpYXQiOjE3MDkyODcyNzQsImV4cCI6MTcxMTkxNjMzMH0.WzkMxcwGcjP-fapVl3vQSIoJfI38BBU_guBNqAxhcNae99Y833Bl9OMZftbV3oG4QacgSDX58X_44i8HLvn8cw')
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
    
    # Now you can use airport_data_access to get airport data
    # Example: lon, lat = airport_data_access.get_airport_lon_lat_by_iata(iata_code)
    
    query_data = request.json.get('query', {})
    
    # Now you can safely access the nested data
    firstname = query_data.get('firstName')  # Now this correctly uses .get() on the nested dictionary
    surname = query_data.get('surname')
    age = query_data.get('age')
    iata_o = query_data.get('iata_o')
    iata_d = query_data.get('iata_d')
    city_name = query_data.get('city_name')
    name = query_data.get('name') 
    nameThreshold = query_data.get('nameThreshold')
    ageThreshold = query_data.get('ageThreshold')
    locationThreshold = query_data.get('locationThreshold')
    if age is not None:
        try:
            age = int(age)
        except ValueError:
            return jsonify({'error': 'Invalid age value'}), 400
    else:
    # Handle cases where age is not provided or is None
        pass

    # Pass the airport data access instance to your service function if needed
    print("Threshold: ", name, nameThreshold, ageThreshold, locationThreshold)
    data, no_similar = find_similar_passengers(airport_data_access, firstname, surname, name, age, iata_o, iata_d, city_name, xml_dir, nameThreshold, ageThreshold, locationThreshold)
    response = {
        'data': data,
        'no_similar' : no_similar
    }
    return jsonify(response)

if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=True, port=5001)
    #change debug=True for debug
