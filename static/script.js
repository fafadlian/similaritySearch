document.addEventListener('DOMContentLoaded', function () {

    // Handle Date Range Form Submission
    document.getElementById('paramForm').addEventListener('submit', function (event) {
        event.preventDefault();
        var arrivalDateFrom = document.getElementById('arrivalDateFrom').value;
        var arrivalDateTo = document.getElementById('arrivalDateTo').value;
        var flightNbr = document.getElementById('flightNbr').value;

        var data = {
            arrivalDateFrom: arrivalDateFrom,
            arrivalDateTo: arrivalDateTo,
            flightNbr: flightNbr
        };

        sendRequest('/submit_param', data, function(response) {
            // Handle the response here
            console.log(response.message);
            // You can update the HTML to display the response message
            if (response.fileName) {
                displayFlightIdCount(response.fileName);
            } else {
                console.error('Error:', response.message || 'No file name returned');
            }
        });

        // Handle the server response
        // ...
    });


    // Handle Similarity Search Form Submission
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
    
        var firstName = document.getElementById('firstName').value;
        var surname = document.getElementById('surname').value;
        var age = document.getElementById('age').value;
        var name = firstName + ' ' + surname;
        var iata_o = document.getElementById('iata_o').value;
        var iata_d = document.getElementById('iata_d').value;
        var city_name = document.getElementById('city_name').value;

        var query = {
            firstName: firstName,
            surname: surname,
            age: age,
            iata_o: iata_o,
            iata_d: iata_d,
            city_name: city_name,
            // name: name
        };
    
        sendRequest('/perform_similarity_search', { query: query }, function(response) {
            displayResults(response);
        });
    });


    //Handle result file download
    document.getElementById('downloadCsv').addEventListener('click', function() {
        var data = globalResponseData;
        var csvContent = "data:text/csv;charset=utf-8,";
    
        // Add header
        csvContent += "Similarity Score,Full Name,PNR File,Booking ID,DOB, Nationality\n";
    
        // Add rows
        data.forEach(function(item) {
            var row = `${item[5]},${item[1]},${item[0]},${item[2]},${item[3]},${item[4]}\n`;
            csvContent += row;
        });
    
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "similar_passengers.csv");
        document.body.appendChild(link); // Required for FF
    
        link.click(); // This will download the data file
    });
    

    // Function to send AJAX request to the server
    function sendRequest(url, data, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                callback(response);
            } else {
                console.error('Error in request:', xhr.responseText);
                // Invoke callback with error information
                callback({ error: 'Error processing request', details: xhr.responseText });
            }
        };
        xhr.send(JSON.stringify(data));
    }
    
    // Function to handle displaying the count
    function displayFlightIdCount(fileName) {
        sendRequest('/count_unique_flight_ids', {fileName: fileName}, function(response) {
            if (response.unique_flight_id_count !== undefined) {
                // Display the count to the user
                document.getElementById('uniqueFlightIds').innerHTML = 
                `<h3>Unique Flight IDs: ${response.unique_flight_id_count}</h3>`;
            } else {
                // Handle errors
                console.error('Error counting flight IDs', response.details || '');
                document.getElementById('uniqueFlightIds').innerHTML = 
                `<h3>Error in counting flight IDs: ${response.details || 'Unknown error'}</h3>`;
            }
        });
    }


    var globalResponseData = [];  // Global variable to store the response data

    function displayResults(response) {
        globalResponseData = response.data;
        var resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = ''; // Clear previous results
    
        // Create a table
        var table = document.createElement('table');
        table.className = 'table'; // If you're using Bootstrap or similar CSS framework
    
        // Add table header
        var thead = table.createTHead();
        var headerRow = thead.insertRow();
        var headers = ["Similarity Score", "Full Name", "PNR", "Booking ID", "DOB", "Nationality"];
        headers.forEach(headerText => {
            var header = document.createElement("th");
            header.textContent = headerText;
            headerRow.appendChild(header);
        });
    
        // Add table body
        var tbody = table.createTBody();
        response.data.forEach(item => {
            var row = tbody.insertRow();

            var scoreCell = row.insertCell();
            scoreCell.textContent = item[5]; // Similarity Score

            var nameCell = row.insertCell();
            nameCell.textContent = item[1]; // Full Name
    
            var fileCell = row.insertCell();
            fileCell.textContent = item[0]; // File
    
            var bookingIDCell = row.insertCell();
            bookingIDCell.textContent = item[2]; // Booking ID

            var DOBCell = row.insertCell();
            DOBCell.textContent = item[3]; // DOB

            var natCell = row.insertCell();
            natCell.textContent = item[4]; // Nationality
    
            
        });
    
        resultsDiv.appendChild(table);
    }
    
    



    // Add more functions as needed
    // ...
});
