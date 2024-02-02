import os
import requests
import json
from datetime import datetime

def fetch_pnr_data(api_url, access_token, params):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(api_url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        # Log error and/or retry request as needed
        # print("Error in fetch_pnr_data")
        return None
    
def count_unique_flight_ids(file_path):
    directory = "XMLs"
    try:
        with open(file_path, 'r') as file:
            json_data = file.read()
        data = json.loads(json_data)

        # Extract flight_id values
        flight_ids = [item['flight_id'] for item in data]

        # Count unique IDs
        unique_flight_ids = set(flight_ids)
        for flight_id in unique_flight_ids:
            save_xml_data_for_flight_id(flight_id, directory)
        return len(unique_flight_ids)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return 0
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
    
def save_xml_data_for_flight_id(flight_id, directory):
    url = f"https://tenacity-rmt.eurodyn.com/api/pnr-notification/xml/by-id?id={flight_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        file_path = f"{directory}/flight_id_{flight_id}.xml"
        with open(file_path, 'w') as file:
            file.write(response.text)
            print(f"Data for flight ID {flight_id} saved to {file_path}")
    else:
        print(f"Failed to retrieve data for flight ID {flight_id}: {response.status_code}")

# Example usage


def save_json(data, folder_name, file_name):
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)