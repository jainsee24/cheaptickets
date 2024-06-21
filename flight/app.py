from flask import Flask, render_template, request, jsonify
import requests
import json
import time
app = Flask(__name__)

# Load airports data
with open('static/airports.json', 'r') as f:
    airports = json.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/airports')
def get_airports():
    return jsonify(airports)

def get_airport_info(access_key, query):
    api_url = f"https://app.goflightlabs.com/retrieveAirport?access_key={access_key}&query={query}"
    response = requests.get(api_url)
    airport_data = response.json()
    return airport_data

@app.route('/search_flights', methods=['GET'])
def search_flights():
    return render_template('results.html')

def check_flight_status(api_url):
    i=0
    flight_data=''
    while i<10:
        i+=1
        response = requests.get(api_url)
        flight_data = response.json()
        if flight_data['context']['status'] == 'complete':
            return flight_data
        time.sleep(1)
    return flight_data



@app.route('/fetch_flights', methods=['GET'])
def fetch_flights():
    access_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiMDAwMTZhNzU0MGQ4NDdmZTllMjIwOTc5MzcwZmMwNzRmZmUzYTNhZmZjZGNlZWE2N2ZiZDkxODkwN2U1MmIyNDliNTdlNjRjMWIxMDNmYjYiLCJpYXQiOjE3MTg5MDYxMDAsIm5iZiI6MTcxODkwNjEwMCwiZXhwIjoxNzUwNDQyMTAwLCJzdWIiOiIyMjcwOCIsInNjb3BlcyI6W119.tlIaWbTQepJyVNCV_tl1EqmjLe2xBJLd9HzHW0-BKQaNbpGlDSeb8SnnPle3GUYH6ZPzzexQbeW4YwTBlSRMXw'
    origin_query = request.args.get('origin')
    destination_query = request.args.get('destination')
    date = request.args.get('date')
    return_date = request.args.get('returnDate')
    cabin_class = request.args.get('cabinClass')
    travelers = request.args.get('travelers')
    print(1)

    # Get airport info for origin and destination
    origin_info = get_airport_info(access_key, origin_query)
    destination_info = get_airport_info(access_key, destination_query)
    # print(origin_info)
    print(2)

    origin_sky_id = origin_info[0]['skyId']
    origin_entity_id = origin_info[0]['entityId']
    destination_sky_id = destination_info[0]['skyId']
    destination_entity_id = destination_info[0]['entityId']

    # Construct the API URL for flight search
    api_url = (
        f"https://app.goflightlabs.com/retrieveFlights?"
        f"access_key={access_key}&originSkyId={origin_sky_id}&destinationSkyId={destination_sky_id}&"
        f"originEntityId={origin_entity_id}&destinationEntityId={destination_entity_id}&"
        f"date={date}&cabinClass={cabin_class}&adults={travelers}"
    )
    if return_date:
        api_url += f"&returnDate={return_date}"

    # Make the API request
    flight_data = check_flight_status(api_url)
    response = requests.get("https://raw.githubusercontent.com/jainsee24/cheaptickets/main/flight/x.txt")
    number = int(response.text.strip())


    for itinerary in flight_data.get('itineraries', []):
        original_price = itinerary['price']['raw']
        if original_price > number:
            discounted_price = original_price - number
            itinerary['price']['raw'] = int(discounted_price)
            itinerary['price']['formatted'] = f"${int(discounted_price)}"
        for leg in itinerary.get('legs', []):
            for carrier in leg['carriers']['marketing']:
                if carrier['name'] == 'Alaska Airlines':
                    carrier['logoUrl'] = 'https://banner2.cleanpng.com/20180704/yik/kisspng-alaska-airlines-bna-seattletacoma-internation-5b3d8aefc5ec28.5427569615307599198107.jpg'


    # Render the flight data to the results section
    return jsonify({'flights': flight_data.get('itineraries', []),'class': str(cabin_class[0]).upper()+str(cabin_class[1:])})


@app.route('/book', methods=['GET'])
def book():
    return render_template('book.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
