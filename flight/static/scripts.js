document.addEventListener('DOMContentLoaded', function() {
    $.getJSON('/airports', function(data) {
        const airports = data;
        $("#from-airport, #to-airport").autocomplete({
            source: function(request, response) {
                const results = $.map(airports, function(airport) {
                    const airportName = airport.name + " (" + airport.code + ")";
                    if (airportName.toLowerCase().indexOf(request.term.toLowerCase()) !== -1) {
                        return {
                            label: airportName,
                            value: airport.code
                        };
                    }
                });
                response(results);
            },
            minLength: 2
        });
    });
});

function toggleDateInputs() {
    const tripType = document.querySelector('input[name="tripType"]:checked').value;
    const returnDate = document.getElementById('return-date');
    if (tripType === 'oneWay') {
        returnDate.style.display = 'none';
    } else {
        returnDate.style.display = 'block';
    }
}

function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(tabId).style.display = 'block';
    
    const tabButtons = document.querySelectorAll('.tab');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`button[onclick="showTab('${tabId}')"]`).classList.add('active');
}
