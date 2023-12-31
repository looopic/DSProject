
// Function to add a new amenity to the list of selected amenities
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
    updateSQLQuery();
}

// Function to remove an amenity from the list of selected amenities
function removeAmenity() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");

    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        var option = selectedAmenitiesSelect.options[i];
        if (option.selected) {
            selectedAmenitiesSelect.remove(i);
            i--;
        }
    }
    updateSQLQuery();
}

// Function to remove all amenities from the list of selected amenities
function removeAllAmenities() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    selectedAmenitiesSelect.innerHTML = "";
    updateSQLQuery();
    $("#sqlQuery").val("");
}

// Function to update the SQL query
function updateSQLQuery() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    var selectedAmenities = [];
    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        selectedAmenities.push(selectedAmenitiesSelect.options[i].value);
    }
    var query = "SELECT osm_id, building, 'addr:housename', name, ST_Area(way) AS way_area, way FROM planet_osm_polygon";
    if (selectedAmenities.length > 0) {
        query += " WHERE amenity IN (";
        query += selectedAmenities.map(function (amenity) { return "'" + amenity + "'"; }).join(", ");
        query += ")";
    }
    query += ";";
    $("#sqlQuery").val(query);
}

// Function to run the query against the database
function runQuery() {
    var selectedAmenitiesSelect = document.getElementById("selectedAmenities");
    var selectedAmenities = [];
    for (var i = 0; i < selectedAmenitiesSelect.options.length; i++) {
        selectedAmenities.push(selectedAmenitiesSelect.options[i].value);
    }
    $.ajax({
        type: "POST",
        url: "/result",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({ selectedAmenities: selectedAmenities }),
        success: function (response) {
            displayQueryResultsInDOM(response);
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
}

// Function to display the query results
function displayQueryResultsInDOM(results) {
    var queryResultsTable = document.getElementById("queryResults");
    queryResultsTable.innerHTML = "";
    var headerRow = document.createElement("tr");
    var headerTitles = ["OSM ID", "Building", "Housename", "Name", "Way Area", "Way"];
    for (var i = 0; i < headerTitles.length; i++) {
        var th = document.createElement("th");
        th.appendChild(document.createTextNode(headerTitles[i]));
        headerRow.appendChild(th);
    }
    queryResultsTable.appendChild(headerRow);
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

// Function to display the query results
function displayGenericQueryResultsInDOM(results) {
    var queryResultsTable = document.getElementById("queryResults");
    queryResultsTable.innerHTML = "";
    if (results.length === 0) {
        return;
    }
    var headerTitles = ["osm_id", "building", "historic", "man_made", "ST_Area", "way"];
    var headerRow = document.createElement("tr");

    for (var i = 0; i < headerTitles.length; i++) {
        var th = document.createElement("th");
        th.appendChild(document.createTextNode(headerTitles[i]));
        headerRow.appendChild(th);
    }
    queryResultsTable.appendChild(headerRow);
    for (var i = 0; i < results.length; i++) {
        var dataRow = document.createElement("tr");
        for (var key in results[i]) {
            if (results[i].hasOwnProperty(key)) {
                var td = document.createElement("td");
                td.appendChild(document.createTextNode(results[i][key]));
                dataRow.appendChild(td);
            }
        }
        queryResultsTable.appendChild(dataRow);
    }
}

// Function to run the predefined query against the database
function runPredefinedQuery() {
    var selectedQuery = document.getElementById("predefinedQuery").value;
    var predefinedQuery = getPredefinedQuery(selectedQuery);

    $.ajax({
        type: "POST",
        url: "/predefined_query",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({ selectedQuery: selectedQuery }),
        success: function (response) {
            displayGenericQueryResultsInDOM(response);
            document.getElementById("selectedQueryDisplay").value = predefinedQuery;
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
}

// Function to update the predefined query display based on the selected value
function updatePredefinedQuery() {
    var selectedQuery = document.getElementById("predefinedQuery").value;
    var predefinedQuery = getPredefinedQuery(selectedQuery);
    document.getElementById("selectedQueryDisplay").value = predefinedQuery;
}

// Function to get the predefined query
function getPredefinedQuery(selectedQuery) {
    switch (selectedQuery) {
        case "historicalChimneys":
            return "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE historic = 'industrial' AND man_made = 'chimney';";
        case "commercialBuildings":
            return "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE man_made = 'works' AND building IS NOT NULL AND historic IS NULL;";
        case "schools":
            return "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE amenity = 'school';";
        default:
            return "";
    }
}
document.getElementById("runQueryButton").addEventListener("click", function () {
    runQuery();
});
document.getElementById("runPredefinedQueryButton").addEventListener("click", function () {
    runPredefinedQuery();
});
$("#predefinedQuery").change(function () {
    updatePredefinedQuery();
});
