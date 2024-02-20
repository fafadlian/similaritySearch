# Similarity Search WebApp

## Description
The Similarity Search WebApp is a Python-Flask-based web application designed to perform advanced similarity searches across PNR data. Utilizing a combination of algorithms for distance and age similarity, it offers users the ability to find a person from a watchlist.

## Installation
To run this application, ensure you have Docker installed on your machine.

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Build the Docker image: (docker build -t similaritysearch .)
4. Run the Docker container: (docker run -p 5000:5000 similaritysearch)


## Usage
After starting the application, navigate to `http://localhost:5000` in your web browser to access the web interface. Enter your search parameters to begin finding similarities in your data.

## Query/Test Cases
All test case initiated by submitting the PNR Timeframe Parameter (Arrival Date From and Arrival Date To). We're going to use 1 January 2019 to 30 November 2019

1. Test case A
| Parameter          | Descripotion                                  | Example Values |
|--------------------|-----------------------------------------------|----------------|
| First Name         | The first name of the individual to search    | Jamie          |
| Surname            | The surname of the individual to search       | Smith          |
| Estimated age      | The estimated age of the individual to search | 52             |
| Origin IATA        | 3-letter IATA code for origin airport         | AUH            |
| Destination IATA   | 3-letter IATA code for destination airport    | RTM            |
| City Address       | Name of the city on the person's address      | Abu Dhabi      |
| Name Threshold     | Threshold for thhe name similarity (0 to 100) | 70             |
| Age Threshold      | Threshold for age similarity (0 to 100)       | 20             |
| Location Threshold | Threshold for location (0 to 100)             | 95             |

This test case will try to searchy Jaime Smith that travels from Dubai(DXB) to Amsterdam(AMS) with address in Dubai. We use slightly different values in the query for the purpose of showing how the 'fuzzy' similarity search works.

1. Test case B
We're looking someone with the name of Mike Smith, the approximate age is 55 to 60, travels from somewhere in london to CDG Paris. He lives in London.
Note: You can choose from one of the airport in london (STN, LTN, LGW, LHR).
Clue: Since the name of "Mike" often the short version of "Michael", we can use a lower name threshold (60). 
Since we have an almost complete information of his locations, we can use a higher threshold value (99)
We have the estimated age, we can try to use 80 for the age threshold.

Feel free to adjust the thresholds and see how the threshold affect the output.



## Features
- **Data Similarity Searches**: Perform searches based on multiple similarity criteria.
- **Adjustable Sensitivity (Threshold)**: Utilizes custom threshold for the similarity score
- **Interactive Web Interface**: Easy-to-use web interface for all user interactions.

## Contributing
Contributions to the Similarity Search WebApp are welcome. Please submit pull requests or open issues to suggest changes or add new features.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For support or inquiries, please contact via [GitHub issues](https://github.com/fafadlian).


