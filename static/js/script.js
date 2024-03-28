document.addEventListener('DOMContentLoaded', function () {

    //Navigation
    setupNavigation();

    //Populating dropdowns
    populateNationalityDropdown();

    //Highlighting Section
     // Identify the current section here. This is a placeholder example.
     var currentSection = "similaritySearchSection"; // Change this based on actual logic or URL

     // Remove 'active' class from all nav links first
     document.querySelectorAll('.nav-link').forEach(function(link) {
         link.classList.remove('active');
     });
 
     // Add 'active' class to the current section's nav link
     if (currentSection === "similaritySearchSection") {
         document.querySelector('a[href="#similaritySearchSection"]').classList.add('active');
     } else if (currentSection === "anomalyDetectionSection") {
         document.querySelector('a[href="#anomalyDetectionSection"]').classList.add('active');
     }
     // Extend with more else-if blocks for additional sections as needed

    var lastParam = {};

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

        lastParam = data;

        // Handle the server response
        // ...
    });

    var lastSearchQuery = {};

    // Handle Similarity Search Form Submission
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        var firstname = document.getElementById('firstname').value;
        var surname = document.getElementById('surname').value;
        var dob = document.getElementById('dob').value;
        var name = firstname + ' ' + surname;
        var iata_o = document.getElementById('iata_o').value;
        var iata_d = document.getElementById('iata_d').value;
        var city_name = document.getElementById('city_name').value;
        var address = document.getElementById('address').value;
        var sex = document.getElementById('sex').value;
        var nationality = document.getElementById('nationality').value;
        var nameThreshold = document.getElementById('nameThreshold').value;
        var ageThreshold = document.getElementById('ageThreshold').value;
        var locationThreshold = document.getElementById('locationThreshold').value;

        var query = {
            firstname: firstname,
            surname: surname,
            dob: dob,
            iata_o: iata_o,
            iata_d: iata_d,
            city_name: city_name,
            address: address,
            sex: sex,
            nationality: nationality,
            name: name,
            nameThreshold: nameThreshold,
            ageThreshold: ageThreshold,
            locationThreshold: locationThreshold
        };

        lastSearchQuery = query;

            // Print the threshold values to the console
        // console.log("Name Threshold: ", nameThreshold);
        // console.log("Age Threshold: ", ageThreshold);
        // console.log("Location Threshold: ", locationThreshold);
    
        sendRequest('/perform_similarity_search', { query: query }, function(response) {
            console.log("Response data:", response)
            if (response && response.data) {
                console.log("Search successful:", response.message);
                displayResults(response);
            } else {
                console.error('Error in search:', response ? response.message : "No response from server");
            }

            
        });
    });


    //Handle result file download
    // document.getElementById('downloadCsv').addEventListener('click', function() {
    //     var data = globalResponseData;
    //     var csvContent = "data:text/csv;charset=utf-8,";
    
    //     // Adjusted header to match the new structure
    //     csvContent += "FilePath,Booking ID,Full Name,Origin IATA,Origin Lat,Origin Lon,Destination IATA,Destination Lat,Destination Lon,DOB,City Name,City Lat,City Lon,Nationality,Sex,Name Similarity,Origin Distance, Destination Distance, City Distance, Age Similarity, Compound Similarity\n";
    
    //     // Adjust the rows to include all values in the correct order
    //     data.forEach(function(item) {
    //         // Construct the row string based on the item structure; adjust the indexes as necessary
    //         var row = `${item[0]},${item[1]},${item[2]},${item[3]},${item[4]},${item[5]},${item[6]},${item[7]},${item[8]},${item[9]},${item[10]},${item[11]},${item[12]},${item[13]},${item[14]},${item[15]},${item[16]},${item[17]},${item[18]},${item[19]},${item[20]}\n`;
    //         csvContent += row;
    //     });
    //     var fileName = `similar_passengers_${lastSearchQuery.firstName}_${lastSearchQuery.surname}_${lastSearchQuery.iata_o}_${lastSearchQuery.iata_d}`.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '') + '.csv';
    
    //     var encodedUri = encodeURI(csvContent);
    //     var link = document.createElement("a");
    //     link.setAttribute("href", encodedUri);
    //     link.setAttribute("download", fileName);
    //     document.body.appendChild(link); // Required for FF
    
    //     link.click(); // This will download the data file
    // });
    document.getElementById('downloadCsv').addEventListener('click', function() {
        var data = globalResponseData;
        var csvContent = "data:text/csv;charset=utf-8,";
    
        // Define headers based on your JSON object keys
        var headers = ["FilePath", "Booking ID", "Full Name", "Origin IATA", "Origin Lat", "Origin Lon", "Destination IATA", "Destination Lat", "Destination Lon", "DOB", "City Name", "City Lat", "City Lon", "Nationality", "Sex", "Name Similarity", "Origin Distance", "Destination Distance", "City Distance", "Age Similarity", "Compound Similarity"];
        csvContent += headers.join(",") + "\n";
    
        // Iterate through each object in the data array and create a row for each
        data.forEach(function(item) {
            var row = headers.map(header => item[header]).join(",");
            csvContent += row + "\n";
        });
    
        var fileName = `similar_passengers_${new Date().toISOString()}.csv`;
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
    });
    

    // document.getElementById('downloadJson').addEventListener('click', function() {
    //     var now = new Date();
    //     var dateTimeString = now.toISOString().replace(/[^0-9]/g, ''); // Creates a string in the format 'YYYYMMDDTHHMMSS'
    //     var flightParam = lastParam;
    //     var searchQuery = lastSearchQuery;
    //     var data = globalResponseData;
    //     var jsonData = {
    //         "PNR_Timeframe": {
    //             "arrivalDateFrom": flightParam.arrivalDateFrom, // Example data, replace with actual data
    //             "arrivalDateTo": flightParam.arrivalDateTo,
    //         },
    //         "searchedIndividual": {
    //             "FirstName": searchQuery.firstName,
    //             "Surname": searchQuery.surname,
    //             "EstAge":searchQuery.age,
    //             "originIATA":searchQuery.iata_o,
    //             "destinationIATA":searchQuery.iata_d,
    //             "cityAddress":searchQuery.city_name
    //         },
    //         "thresholds":{
    //             "nameSimilarityThreshold": searchQuery.nameThreshold,
    //             "ageSimilarityThreshold": searchQuery.ageThreshold,
    //             "location Similarity Threshold": searchQuery.locationThreshold,
    //         },
    //         "results":{},
    //     };
    
    //        // Iterate over each item in the data array and convert it to a JSON object
    //     data.forEach(function(item, index) {
    //         var resultID = "resultID" + index; // Construct the result ID
    //         jsonData.results[resultID] = { // Use the result ID as a key
    //             "similarityScores": {
    //                 "compoundSimilarity": item[20],
    //                 "nameSimilarity": item[15],
    //                 "ageSimilarity": item[19],
    //                 "originSimilarity": item[16],
    //                 "destinationSimilarity": item[17],
    //                 "cityDistanceSimilarity": item[18],
    //             },
    //             "bookInfo": {
    //                 "FilePath": item[0],
    //                 "bookingID": item[1],
    //                 "originIATA": item[3],
    //                 "originLat": item[4],
    //                 "originLon": item[5],
    //                 "destinationIATA": item[6],
    //                 "destinationLat": item[7],
    //                 "destinationLon": item[8],
    //             },
    //             "passengerInfo": {
    //                 "fullName": item[2],
    //                 "DOB": item[9],
    //                 "Nationality": item[13],
    //                 "Sex": item[14],
    //             }
    //         };
    //     });

        
    
    //     // Convert the structured data to a JSON string
    //     var jsonString = JSON.stringify(jsonData, null, 2); // Beautify the JSON output

        
    //     // Generate a file name based on last search query
    //     // var fileName = `similar_passengers_${lastSearchQuery.firstName}_${lastSearchQuery.surname}_${lastSearchQuery.iata_o}_${lastSearchQuery.iata_d}`.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '') + '.json';
        
    //     //Generate a file name based on current date time
        
    //     var fileName = `similar_passengers_${dateTimeString}.json`;

    //     // Create a blob with JSON content
    //     var blob = new Blob([jsonString], {type: "application/json"});
    //     var url = URL.createObjectURL(blob);
        
    //     // Create a link and trigger the download
    //     var link = document.createElement("a");
    //     link.setAttribute("href", url);
    //     link.setAttribute("download", fileName);
    //     document.body.appendChild(link); // Required for FF
        
    //     link.click(); // This will download the data file
        
    //     // Optionally, remove the link after downloading
    //     document.body.removeChild(link);
    // });

    document.getElementById('downloadJson').addEventListener('click', function() {
        var dateTimeString = new Date().toISOString().replace(/[^0-9]/g, '');
        var searchQuery = lastSearchQuery;
        var data = globalResponseData; // Assuming this is an array of objects
        var jsonData = {
            "PNR_Timeframe": {
                "arrivalDateFrom": searchQuery.arrivalDateFrom,
                "arrivalDateTo": searchQuery.arrivalDateTo,
            },
            "searchedIndividual": {
                "FirstName": searchQuery.firstName,
                "Surname": searchQuery.surname,
                "EstAge": searchQuery.age,
                "originIATA": searchQuery.iata_o,
                "destinationIATA": searchQuery.iata_d,
                "cityAddress": searchQuery.city_name
            },
            "thresholds": {
                "nameSimilarityThreshold": searchQuery.nameThreshold,
                "ageSimilarityThreshold": searchQuery.ageThreshold,
                "location Similarity Threshold": searchQuery.locationThreshold,
            },
            "results": data // Assuming data is structured as needed
        };
    
        var jsonString = JSON.stringify(jsonData, null, 2);
        var fileName = `similar_passengers_${dateTimeString}.json`;
        var blob = new Blob([jsonString], {type: "application/json"});
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
    
    
    

    // Function to send AJAX request to the server
    function sendRequest(url, data, callback) {
        // Show the loading indicator before sending the request
        document.getElementById('loadingIndicator').style.display = 'flex';
        
        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
    
        xhr.onload = function () {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    // After processing the response, hide the loading indicator
                    callback(response, () => {
                        document.getElementById('loadingIndicator').style.display = 'none';
                    });
                } catch (error) {
                    console.error("Parsing error:", error);
                    document.getElementById('loadingIndicator').style.display = 'none'; // Hide on error
                }
            } else {
                console.error("Request failed with status:", xhr.status);
                document.getElementById('loadingIndicator').style.display = 'none'; // Hide on request failure
            }
        };
    
        xhr.onerror = function() {
            console.error("Request failed due to a network error");
            document.getElementById('loadingIndicator').style.display = 'none'; // Hide on network error
        };
    
        xhr.send(JSON.stringify(data));
    }

    
    
    
    
    
    // Function to handle displaying the count
    function displayFlightIdCount(fileName) {
        // Modified to include the hideLoadingIndicator function
        sendRequest('/count_unique_flight_ids', {fileName: fileName}, function(response, hideLoadingIndicator) {
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
    
            // Hide the loading indicator after processing the response
            hideLoadingIndicator();
        });
    }
    


    var globalResponseData = [];  // Global variable to store the response data

    // Old Version
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
    //     var headers = ["File Path", "Booking ID", "Full Name", "Origin IATA", "Origin Lat", "Origin Lon", "Destination IATA", "Destination Lat", "Destination Lon", "DOB", "City Name", "City Lat", "City Lon", "Nationality", "Sex", "Name Similarity Score", "Origin Similarity", "Destination Similarity", "Address Similarity", "Age Similariity", "Compund Similarity Score"];
    //     var headers = ["File Path", "Full Name", "DOB", "City Name", "Nationality"];
    //     headers.forEach(headerText => {
    //         var header = document.createElement("th");
    //         header.textContent = headerText;
    //         headerRow.appendChild(header);
    //     });
    
    //     // Add table body
    //     var tbody = table.createTBody();
    //     response.data.forEach(item => {
    //         var row = tbody.insertRow();
    
    //         // Assuming the order of values in 'item' matches the columns
    //         item.forEach((value, index) => {
    //             var cell = row.insertCell();
    //             cell.textContent = value; // This will set each value in the order they appear in 'item'
    //         });
    //     });
    
    //     resultsDiv.appendChild(table);
    // }

    function displayResults(response) {
        console.log("Response data:", response);
        var resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = ''; // Clear previous results
    
        if (response.data && response.data.length > 0) {
            // Create a table
            var table = document.createElement('table');
            table.className = 'table table-striped'; // Assuming Bootstrap
    
            // Create header
            var thead = document.createElement('thead');
            var tr = document.createElement('tr');
            Object.keys(response.data[0]).forEach(function(key) {
                var th = document.createElement('th');
                th.textContent = key.replace(/([A-Z])/g, ' $1').trim(); // Add space before capital letters and trim
                tr.appendChild(th);
            });
            thead.appendChild(tr);
            table.appendChild(thead);
    
            // Create body
            var tbody = document.createElement('tbody');
            response.data.forEach(function(item) {
                var tr = document.createElement('tr');
                Object.values(item).forEach(function(value) {
                    var td = document.createElement('td');
                    td.textContent = value;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
    
            resultsDiv.appendChild(table);
        } else {
            resultsDiv.textContent = 'No similar passengers found.';
        }

        // Hide the loading indicator after processing the response
        hideLoadingIndicator();
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

    function populateNationalityDropdown() {
        const nationalitySelect = document.getElementById('nationality');
        const csvPath = '/static/data/geoCrosswalk/GeoCrossWalkMed.csv'; // Adjust based on your setup
    
        Papa.parse(csvPath, {
            download: true,
            header: true,
            complete: function(results) {
                let nationalities = results.data;
                
                // Sort nationalities by countryName alphabetically
                nationalities = nationalities.sort((a, b) => a.countryName.localeCompare(b.countryName));
    
                const addedNationalities = new Set(); // To track already added nationalities
    
                nationalities.forEach(nationality => {
                    const countryName = nationality.countryName.trim();
                    const hhIso = nationality.HH_ISO.trim();
    
                    if (countryName && hhIso && !addedNationalities.has(hhIso)) {
                        const option = document.createElement('option');
                        option.value = hhIso;
                        option.textContent = countryName;
                        nationalitySelect.appendChild(option);
    
                        addedNationalities.add(hhIso);
                    }
                });
    
                // Initialize Select2 with search and limited scroll
                $(nationalitySelect).select2({
                    width: '100%', // Adjust width to fit your layout
                    dropdownAutoWidth: true
                });
            }
        });
    }
    
    



    
    
    



    // Add more functions as needed
    // ...
});
