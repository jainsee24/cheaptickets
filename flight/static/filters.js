document.addEventListener('DOMContentLoaded', () => {
    const filters = document.querySelectorAll('.filters input[type="checkbox"]');
    const sortSelect = document.getElementById('sort');
    const flightsList = document.getElementById('flights-list');

    const stopsFilter = document.getElementById('filter-stops');
    const airlinesFilter = document.getElementById('filter-airlines');

    const stops = new Set();
    const airlines = new Set();

    [...flightsList.children].forEach(flight => {
        stops.add(flight.dataset.stops);
        airlines.add(flight.dataset.airlines);
    });

    stops.forEach(stop => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" name="stops" value="${stop}"> ${stop} Stops`;
        stopsFilter.appendChild(label);
        stopsFilter.appendChild(document.createElement('br'));
    });

    airlines.forEach(airline => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" name="airlines" value="${airline}"> ${airline}`;
        airlinesFilter.appendChild(label);
        airlinesFilter.appendChild(document.createElement('br'));
    });

    filters.forEach(filter => {
        filter.addEventListener('change', () => {
            applyFilters();
        });
    });

    sortSelect.addEventListener('change', () => {
        applyFilters();
    });

    function applyFilters() {
        const activeFilters = {
            stops: [],
            airlines: [],
            travel_baggage: []
        };

        filters.forEach(filter => {
            if (filter.checked) {
                if (filter.name === 'stops') {
                    activeFilters.stops.push(filter.value);
                } else if (filter.name === 'airlines') {
                    activeFilters.airlines.push(filter.value);
                } else if (filter.name === 'travel_baggage') {
                    activeFilters.travel_baggage.push(filter.value);
                }
            }
        });

        const sortedFlights = [...flightsList.children].sort((a, b) => {
            if (sortSelect.value === 'price') {
                return parseFloat(a.querySelector('.flight-price span').textContent.replace(/[^0-9.-]+/g, "")) - 
                       parseFloat(b.querySelector('.flight-price span').textContent.replace(/[^0-9.-]+/g, ""));
            } else if (sortSelect.value === 'duration') {
                return parseInt(a.querySelector('.flight-time span:last-child').textContent.split('h')[0]) - 
                       parseInt(b.querySelector('.flight-time span:last-child').textContent.split('h')[0]);
            } else {
                return 0; // Default sorting (recommended)
            }
        });

        flightsList.innerHTML = '';

        sortedFlights.forEach(flight => {
            const stops = flight.dataset.stops;
            const airline = flight.dataset.airlines.toLowerCase();

            if ((activeFilters.stops.length === 0 || activeFilters.stops.includes(stops)) &&
                (activeFilters.airlines.length === 0 || activeFilters.airlines.some(a => airline.includes(a))) &&
                (activeFilters.travel_baggage.length === 0 || activeFilters.travel_baggage.includes('seat_choice'))) {
                flightsList.appendChild(flight);
            }
        });
    }
});
