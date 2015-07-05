$(document).ready(function() {
	// selects the searchbar when the page loads
	$('#searchbar-text-field').focus();

    var timeoutID;
    var waitTime = 1000;
    var urlNotInDatabaseException = "URL not in database. Please wait.";

    function displayResponse(response) {
        console.log("Displaying Response: " +response.toString());
        var resultsHTML = '<p class="col-12" id="results-header">Results for <span id="results-title">' +response.product_name +'</span>:</p>' +'<ul class="row" id="results-list">';
        for (var i = 0; i < response.key_points.length; i++)
        {
            if (response.key_points[i] !== "")
                response.key_points[i] = $.trim(response.key_points[i]);
                resultsHTML += '<li class="key-point col-8">' + response.key_points[i] + "</li>";
        }
        resultsHTML += "</ul>";

        $('#results').html(resultsHTML);
    }

    function displayError(error) {
        console.log("Displaying error: " +error.toString());
        var displayedError = error.exception;

        var resultsHTML = '<p class="col-12" id="results-header">Error: <span id="exception">' +displayedError +'</span></p>';
        $('#results').html(resultsHTML);
    }

    var userSearch;

    function waitForServerResponse(json_input) {
        $.ajax({
            type: searchForm.attr('method'),
            url: "/wait",
            data: json_input,
            dataType: "json",
            success: function (response) {
                console.log(response);

                // If user requested a different url during ajax call
                if (response.url !== userSearch) {
                    console.log("User query changed. Was '" + response.url + "', now '" + userSearch + "'");
                    return;
                }

                if (!response.exception) {
                    console.log("url now found in database");
                    displayResponse(response);
                } else {
                    displayError(response);
                    if (response.exception === urlNotInDatabaseException) {
                        waitTime = waitTime * 2;
                        if (waitTime < 64000) {
                            // make another ajax request to wait until url is added to database
                            timeoutID = window.setTimeout(function() { waitForServerResponse(json_input); }, waitTime);
                        }
                        else {
                            response.exception = "Maximum wait time exceeded";
                            displayError(response);
                        }
                    }
                }

            },
            error: function(response) {
                console.log("error while waiting for url to enter database");
                console.log(response);
            }
        });
    }

	var searchForm = $('#search-form');
    searchForm.submit(function (ev) {
    	// when the user submits the form get the user input and submit it to the server with ajax
    	userSearch = $("#searchbar-text-field").val();
    	var userInputObject = new Object();
    	userInputObject.userInput = userSearch;
    	var json_input = JSON.stringify(userInputObject);
    	console.log("Submitting: " + json_input);

        $.ajax({
            type: searchForm.attr('method'),
            url: "/ajax/getkeypoints/",
            data: json_input,
            dataType: "json",
            success: function (response) {
                // Runs when the ajax call completes successfully
                console.log("success");
                console.log(response);

                // If user requested a different url during ajax call
                if (response.url !== userSearch) {
                    console.log("User query changed. Was '" + response.url + "', now '" + userSearch + "'");
                    return;
                }

				if (!response.exception) {
                    console.log("no exception occurred");
					// creates a string of HTML code that will be inserted into the page to give the user their results
                    displayResponse(response);
				} else { 
                    console.log("exception occurred");
                    // exception occurred
                    displayError(response);

                    if (response.exception === urlNotInDatabaseException) {
                        // make another ajax request to wait until url is added to database
                        timeoutID = window.setTimeout(function() { waitForServerResponse(json_input); }, waitTime);
                    }
				}
            },
            error: function (response) {
            	// Runs if the ajax call fails
            	console.log('Error in submitting request to server');
                console.log(response);
            }
        });
		// prevents the form from submitting
        ev.preventDefault();
    });
});
