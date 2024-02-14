# Similarity Search WebApp

## Description
The Similarity Search WebApp is a Python-Flask-based web application designed to perform advanced similarity searches across PNR data. Utilizing a combination of algorithms for distance and age similarity, it offers users the ability to find a person from a watchlist.

## Installation
To run this application, ensure you have Docker installed on your machine.

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Build the Docker image:
	docker build -t similaritysearch .
4. Run the Docker container:
	docker run -p 5000:5000 similaritysearch


## Usage
After starting the application, navigate to `http://localhost:5000` in your web browser to access the web interface. Enter your search parameters to begin finding similarities in your data.

## Features
- **Data Similarity Searches**: Perform searches based on multiple similarity criteria.
- **Adjustable Sensitivity (Threshold**: Utilizes custom threshold for the similarity score
- **Interactive Web Interface**: Easy-to-use web interface for all user interactions.

## Contributing
Contributions to the Similarity Search WebApp are welcome. Please submit pull requests or open issues to suggest changes or add new features.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For support or inquiries, please contact via [GitHub issues](https://github.com/fafadlian).


