document.addEventListener('DOMContentLoaded', function () {

    //Navigation
    setupNavigation();

    //Populating dropdowns
    populateNationalityDropdown();

    const displayedColumns = ['predictions', 'Name', 'DOB', 'Sex', 'Nationality','Travel Doc Number', 'BookingID', 'FilePath']; // Directly displayed columns
    const hoverColumns = ['FNSimilarity','SNSimilarity','AgeSimilarity', 'DOBSimilarity', 'strAddressSimilarity', 'natMatch', 'sexMatch', 'originSimilarity', 'destinationSimilarity', 'predictions']; // Columns to display on hover
    var globalResponseData = [];  // Global variable to store the response data


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
        console.log("Query is There")
        sendRequest('/perform_similarity_search', { query: query }, function(response) {
            console.log("sendRequest is Running")
            console.log("Response data:", response)
            if (response && response.data) {
                console.log("Search successful:", response.message);
                displayResults(response);
            } else {
                console.error('Error in search:', response ? response.message : "No response from server");
            }

            
        });
        console.log("sendRequest finished")
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
        console.log("Print globalResponseData", globalResponseData)
        console.log("Print data", data)
        var jsonData = {
            "PNR_Timeframe": {
                "arrivalDateFrom": searchQuery.arrivalDateFrom,
                "arrivalDateTo": searchQuery.arrivalDateTo,
            },
            "searchedIndividual": {
                "FirstName": searchQuery.firstname,
                "Surname": searchQuery.surname,
                "DOB": searchQuery.dob,
                "originIATA": searchQuery.iata_o,
                "destinationIATA": searchQuery.iata_d,
                "cityAddress": searchQuery.city_name,
                "Address": searchQuery.address,
                "Nationality": searchQuery.nationality,
                "Sex":searchQuery.sex
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
            console.log("XHR Load Event Triggered");
            console.log("XHR onload triggered", xhr.status);
            console.log("Raw response text:", xhr.responseText);
            if (xhr.status === 200) {
                try {
                    var response = preprocessAndParseJSON(xhr.responseText);
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

    function displayResults(response) {
        console.log("Response data:", response.data);
        globalResponseData = response.data;
        var resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = ''; // Clear previous results
    
        if (response.data && response.data.length > 0) {
            var table = document.createElement('table');
            table.className = 'table table-striped';
    
            // Header for displayed columns
            var thead = document.createElement('thead');
            var headerRow = document.createElement('tr');
            displayedColumns.forEach(columnName => {
                var th = document.createElement('th');
                th.textContent = columnName;
                headerRow.appendChild(th);
            });
    
            // Header cell for "Actions"
            var actionTh = document.createElement('th');
            actionTh.textContent = "Actions";
            headerRow.appendChild(actionTh);
            thead.appendChild(headerRow);
            table.appendChild(thead);
    
            // Body with clickable details
            var tbody = document.createElement('tbody');
            response.data.forEach((item, index) => {
                var row = document.createElement('tr');
                displayedColumns.forEach(columnName => {
                    var td = document.createElement('td');
                    td.textContent = item[columnName];
                    row.appendChild(td);
                });
    
                // Cell with a "View More" button to toggle additional details
                var toggleDetailsTd = document.createElement('td');
                var toggleDetailsBtn = document.createElement('button');
                toggleDetailsBtn.textContent = "View More";
                toggleDetailsBtn.className = 'btn btn-info btn-sm';
                toggleDetailsBtn.onclick = function() {
                    var detailsRow = document.getElementById(`details-${index}`);
                    detailsRow.style.display = detailsRow.style.display === 'none' ? '' : 'none';
                };
                toggleDetailsTd.appendChild(toggleDetailsBtn);
                row.appendChild(toggleDetailsTd);
                tbody.appendChild(row);
    
                // Create a hidden row for additional details
                var detailsRow = document.createElement('tr');
                detailsRow.style.display = 'none'; // Initially hidden
                detailsRow.id = `details-${index}`;
    
                var detailsCell = document.createElement('td');
                detailsCell.colSpan = displayedColumns.length + 1;
    
                var miniTable = document.createElement('table');
                miniTable.className = 'table table-hover'; // Bootstrap styles
    
                var miniThead = document.createElement('thead');
                var miniHeaderRow = document.createElement('tr');
                hoverColumns.forEach(columnName => {
                    var miniTh = document.createElement('th');
                    miniTh.textContent = columnName;
                    miniHeaderRow.appendChild(miniTh);
                });
                miniThead.appendChild(miniHeaderRow);
                miniTable.appendChild(miniThead);
    
                var miniTbody = document.createElement('tbody');
                var miniBodyRow = document.createElement('tr');
                hoverColumns.forEach(columnName => {
                    var miniTd = document.createElement('td');
                    miniTd.textContent = item[columnName];
                    miniBodyRow.appendChild(miniTd);
                });
                miniTbody.appendChild(miniBodyRow);
                miniTable.appendChild(miniTbody);
    
                detailsCell.appendChild(miniTable);
                detailsRow.appendChild(detailsCell);
    
                tbody.appendChild(detailsRow); // Append the details row right after the main row
            });
            table.appendChild(tbody);
            resultsDiv.appendChild(table);
        } else {
            resultsDiv.textContent = 'No similar passengers found.';
        }
    
        // Function to hide the loading indicator (if applicable)
        hideLoadingIndicator(); // Ensure this function is defined elsewhere or remove this line if not needed
    }
    
    
    
    

    function safeJSONParse(text) {
        return JSON.parse(text, (key, value) => {
            if (typeof value === 'string' && value === 'NaN') return NaN;
            return value;
        });
    }

    function preprocessAndParseJSON(responseText) {
        // Replace occurrences of NaN with null in the response text
        // Ensure the replacement is safe and won't affect actual string values that might coincidentally contain "NaN"
        const safeResponseText = responseText.replace(/:\s*NaN\b/g, ": null");
        
        // Now parse the modified response text as JSON
        return JSON.parse(safeResponseText);
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
