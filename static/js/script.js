document.addEventListener('DOMContentLoaded', function () {

    //Navigation
    setupNavigation();

    //Highlighting Section



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

    var lastSearchQuery = {};

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
            name: name
        };

        lastSearchQuery = query;
    
        sendRequest('/perform_similarity_search', { query: query }, function(response) {
            displayResults(response);
        });
    });


    //Handle result file download
    document.getElementById('downloadCsv').addEventListener('click', function() {
        var data = globalResponseData;
        var csvContent = "data:text/csv;charset=utf-8,";
    
        // Adjusted header to match the new structure
        csvContent += "FilePath,Booking ID,Full Name,Origin IATA,Origin Lat,Origin Lon,Destination IATA,Destination Lat,Destination Lon,DOB,City Name,City Lat,City Lon,Nationality,Sex,Name Similarity,Origin Distance, Destination Distance, City Distance, Age Similarity, Compound Similarity\n";
    
        // Adjust the rows to include all values in the correct order
        data.forEach(function(item) {
            // Construct the row string based on the item structure; adjust the indexes as necessary
            var row = `${item[0]},${item[1]},${item[2]},${item[3]},${item[4]},${item[5]},${item[6]},${item[7]},${item[8]},${item[9]},${item[10]},${item[11]},${item[12]},${item[13]},${item[14]},${item[15]},${item[16]},${item[17]},${item[18]},${item[19]},${item[20]}\n`;
            csvContent += row;
        });
        var fileName = `similar_passengers_${lastSearchQuery.firstName}_${lastSearchQuery.surname}_${lastSearchQuery.iata_o}_${lastSearchQuery.iata_d}`.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '') + '.csv';
    
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", fileName);
        document.body.appendChild(link); // Required for FF
    
        link.click(); // This will download the data file
    });
    

    // Function to send AJAX request to the server
    function sendRequest(url, data, callback) {
        // Show the loading indicator before sending the request
        document.getElementById('loadingIndicator').style.display = 'flex';
    
        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            // Hide the loading indicator once the request is complete
            document.getElementById('loadingIndicator').style.display = 'none';
    
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                callback(response);
            } else {
                console.error('Error in request:', xhr.responseText);
                // Invoke callback with error information, still hide the loading indicator
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

    // function displayResults(response) {
    //     globalResponseData = response.data;
    //     var resultsDiv = document.getElementById('searchResults');
    //     resultsDiv.innerHTML = ''; // Clear previous results
    
    //     // Create a table
    //     var table = document.createElement('table');
    //     table.className = 'table'; // If you're using Bootstrap or similar CSS framework
    
    //     // Add table header
    //     var thead = table.createTHead();
    //     var headerRow = thead.insertRow();
    //     var headers = ["Similarity Score", "Full Name", "PNR", "Booking ID", "DOB", "Nationality"];
    //     headers.forEach(headerText => {
    //         var header = document.createElement("th");
    //         header.textContent = headerText;
    //         headerRow.appendChild(header);
    //     });
    
    //     // Add table body
    //     var tbody = table.createTBody();
    //     response.data.forEach(item => {
    //         var row = tbody.insertRow();

    //         var scoreCell = row.insertCell();
    //         scoreCell.textContent = item[5]; // Similarity Score

    //         var nameCell = row.insertCell();
    //         nameCell.textContent = item[1]; // Full Name
    
    //         var fileCell = row.insertCell();
    //         fileCell.textContent = item[0]; // File
    
    //         var bookingIDCell = row.insertCell();
    //         bookingIDCell.textContent = item[2]; // Booking ID

    //         var DOBCell = row.insertCell();
    //         DOBCell.textContent = item[3]; // DOB

    //         var natCell = row.insertCell();
    //         natCell.textContent = item[4]; // Nationality
    
            
    //     });
    
    //     resultsDiv.appendChild(table);
    // }

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
        var headers = ["File Path", "Booking ID", "Full Name", "Origin IATA", "Origin Lat", "Origin Lon", "Destination IATA", "Destination Lat", "Destination Lon", "DOB", "City Name", "City Lat", "City Lon", "Nationality", "Sex", "Name Similarity Score", "Origin Similarity", "Destination Similarity", "Address Similarity", "Age Similariity", "Compund Similarity Score"];
        headers.forEach(headerText => {
            var header = document.createElement("th");
            header.textContent = headerText;
            headerRow.appendChild(header);
        });
    
        // Add table body
        var tbody = table.createTBody();
        response.data.forEach(item => {
            var row = tbody.insertRow();
    
            // Assuming the order of values in 'item' matches the columns
            item.forEach((value, index) => {
                var cell = row.insertCell();
                cell.textContent = value; // This will set each value in the order they appear in 'item'
            });
        });
    
        resultsDiv.appendChild(table);
    }

    function setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link-container .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent the default anchor behavior
                
                // Remove 'active' class from all nav links
                navLinks.forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add 'active' class to the clicked link
                this.classList.add('active');
                
                // Hide all sections initially
                const sections = document.querySelectorAll('main > section');
                sections.forEach(section => {
                    section.style.display = 'none'; // Hide all sections
                });
                
                // Extract the target section ID from the href and show the targeted section only
                const targetSectionId = this.getAttribute('href').substring(1); // Remove the '#' from the href value
                const targetSection = document.getElementById(targetSectionId);
                if (targetSection) {
                    targetSection.style.display = 'block'; // Make the target section visible
                }
            });
        });
    }
    
    
    
    



    // Add more functions as needed
    // ...
});
