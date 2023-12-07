// query.js

function addAmenity() {
    var amenitySelect = document.getElementById("amenity");
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");

    for (var i = 0; i < amenitySelect.options.length; i++) {
        var option = amenitySelect.options[i];
        if (option.selected) {
            // Check if the option is already in the selected amenities list
            if (!selectedAmenitiesSelect.options.namedItem(option.value)) {
                var newOption = document.createElement("option");
                newOption.value = option.value;
                newOption.text = option.text;
                selectedAmenitiesSelect.add(newOption);
            }
        }
    }

    // Nachdem die Amenities hinzugefügt wurden, aktualisiere die SQL-Abfrage
    updateSQLQuery();
}


function removeAmenity() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");

    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        var option = selectedAmenitiesSelect.options[i];
        if (option.selected) {
            selectedAmenitiesSelect.remove(i);
            i--; // Adjust index after removal
        }
    }

    // Nachdem die Amenities entfernt wurden, aktualisiere die SQL-Abfrage
    updateSQLQuery();
}


function removeAllAmenities() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    selectedAmenitiesSelect.innerHTML = "";

    // Nachdem die Amenities entfernt wurden, aktualisiere die SQL-Abfrage
    updateSQLQuery();

    // Setze das sqlQuery-Feld auf einen leeren String
    $("#sqlQuery").val("");
}


function runQuery() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    var selectedAmenities = [];
    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        selectedAmenities.push(selectedAmenitiesSelect.options[i].value);
    }

    // Send selected amenities to the server using AJAX
    $.ajax({
        type: "POST",
        url: "/result",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({ selectedAmenities: selectedAmenities }),
        success: function (response) {
            // Call function to display results directly in the DOM
            displayQueryResultsInDOM(response);
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
}

function displayQueryResultsInDOM(results) {
    // Clear existing rows
    var queryResultsTable = document.getElementById("queryResults");
    queryResultsTable.innerHTML = "";

    // Create header row
    var headerRow = document.createElement("tr");
    var headerTitles = ["OSM ID", "Building", "Housename", "Name", "Way Area", "Way"];
    for (var i = 0; i < headerTitles.length; i++) {
        var th = document.createElement("th");
        th.appendChild(document.createTextNode(headerTitles[i]));
        headerRow.appendChild(th);
    }
    queryResultsTable.appendChild(headerRow);

    // Create data rows
    for (var j = 0; j < results.length; j++) {
        var dataRow = document.createElement("tr");
        for (var k = 0; k < results[j].length; k++) {
            var td = document.createElement("td");
            td.appendChild(document.createTextNode(results[j][k]));
            dataRow.appendChild(td);
        }
        queryResultsTable.appendChild(dataRow);
    }
}


function updateSQLQuery() {
    // Get the selected amenities
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    var selectedAmenities = [];
    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        selectedAmenities.push(selectedAmenitiesSelect.options[i].value);
    }

    // Build the SQL query with OR conditions for selected amenities
    var query = "SELECT osm_id, building, 'addr:housename', name, ST_Area(way) AS way_area, way FROM planet_osm_polygon";

    // Check if there are selected amenities to filter
    if (selectedAmenities.length > 0) {
        query += " WHERE amenity IN (";
        query += selectedAmenities.map(function (amenity) { return "'" + amenity + "'"; }).join(", ");
        query += ")";
    }

    query += ";";

    // Display the SQL query in the textarea
    $("#sqlQuery").val(query);
}


// Event listener for the "Run Query" button
document.getElementById("runQueryButton").addEventListener("click", function () {
    runQuery();
});