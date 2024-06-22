from flask import Flask, render_template, request, jsonify
import requests
import json
import time
app = Flask(__name__)


CLIENT_ID = 'JzX4vpbG1UbHIRoaNC81ZPqvK9I1Snvb'
CLIENT_SECRET = 'XpzUanVp7Va4yY2p'
ACCESS_TOKEN_URL = 'https://test.api.amadeus.com/v1/security/oauth2/token'
FLIGHT_OFFERS_URL = 'https://test.api.amadeus.com/v2/shopping/flight-offers'

access_token = 'yLLeXvN90GAZ9c46nxL3GS2PPqB1'
token_expiry = 0


def get_new_access_token():
    global access_token, token_expiry
    response = requests.post(ACCESS_TOKEN_URL, data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        token_expiry = token_info['expires_in']
    else:
        raise Exception('Failed to get access token')


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
    while i<5:
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
    origin_sky_id = origin_info[0]['skyId']
    origin_entity_id = origin_info[0]['entityId']
    destination_sky_id = destination_info[0]['skyId']
    destination_entity_id = destination_info[0]['entityId']

    for i in destination_info:
        if i['skyId']==destination_query:
            destination_entity_id = i['entityId']
    for i in origin_info:
        if i['skyId']==origin_query:
            origin_entity_id = i['entityId']
    

    # Construct the API URL for flight search
    api_url = (
        f"https://app.goflightlabs.com/retrieveFlights?"
        f"access_key={access_key}&originSkyId={origin_sky_id}&destinationSkyId={destination_sky_id}&"
        f"originEntityId={origin_entity_id}&destinationEntityId={destination_entity_id}&"
        f"date={date}&cabinClass={cabin_class}&adults={travelers}"
    )
    if return_date:
        api_url += f"&returnDate={return_date}"
    print(api_url)

    # Make the API request
    flight_data = check_flight_status(api_url)
    response = requests.get("https://raw.githubusercontent.com/jainsee24/cheaptickets/main/flight/x.txt")
    number = int(response.text.strip())


    for itinerary in flight_data.get('itineraries', []):
        original_price = itinerary['price']['raw']
        discounted_price = original_price * (1-number/100)
        itinerary['price']['raw'] = int(discounted_price)
        itinerary['price']['formatted'] = f"${int(discounted_price)}"
        for leg in itinerary.get('legs', []):
            for carrier in leg['carriers']['marketing']:
                if carrier['name'] == 'Alaska Airlines':
                    carrier['logoUrl'] = 'https://banner2.cleanpng.com/20180704/yik/kisspng-alaska-airlines-bna-seattletacoma-internation-5b3d8aefc5ec28.5427569615307599198107.jpg'

    print(flight_data)
    # Render the flight data to the results section
    return jsonify({'flights': flight_data.get('itineraries', []),'classs': str(cabin_class[0]).upper()+str(cabin_class[1:])})


@app.route('/fetch_flights1', methods=['GET'])
def fetch_flights1():
    global access_token, token_expiry

    if token_expiry <= 0:
        get_new_access_token()

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    if request.args.get('returnDate'):

        params = {
            'originLocationCode': request.args.get('origin'),
            'destinationLocationCode': request.args.get('destination'),
            'departureDate': request.args.get('date'),
            'returnDate': request.args.get('returnDate'),
            'travelClass': 'ECONOMY',
            'adults': request.args.get('travelers')
        }
    else:
        params = {
            'originLocationCode': request.args.get('origin'),
            'destinationLocationCode': request.args.get('destination'),
            'departureDate': request.args.get('date'),
            'travelClass': 'ECONOMY',
            'adults': request.args.get('travelers')
        }

    response = requests.get(FLIGHT_OFFERS_URL, headers=headers, params=params)
    if response.status_code == 401:
        # Token expired or invalid, refresh token and retry
        get_new_access_token()
        headers['Authorization'] = f'Bearer {access_token}'
        response = requests.get(FLIGHT_OFFERS_URL, headers=headers, params=params)

    print(response.json())
    if response.status_code == 200:
        flight_data = response.json()
        formatted_flights = convert_api_format(flight_data)
        formatted_flights_dict = json.loads(formatted_flights)

        return jsonify({'flights': formatted_flights_dict.get('itineraries', [])})
    else:
        return jsonify({'error': 'Failed to fetch flight offers'}), response.status_code

@app.route('/book', methods=['GET'])
def book():
    return render_template('book.html')

import re


import json

def parse_duration(duration):
    # This function parses ISO 8601 duration format like "PT4H20M" into minutes
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration)
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes

def convert_api_format(source_data):
    converted_data = {
        "context": {
            "status": "incomplete",
            "sessionId": "generated_session_id",
            "totalResults": source_data["meta"]["count"]
        },
        "itineraries": []
    }
    
    for offer in source_data["data"]:
        itinerary = {
            "id": offer["id"],
            "price": {
                "raw": float(offer["price"]["total"]),
                "formatted": "${:.2f}".format(float(offer["price"]["total"])),
                "pricingOptionId": "generated_pricing_option_id"
            },
            "legs": []
        }
        
        for itinerary_data in offer["itineraries"]:
            for segment in itinerary_data["segments"]:
                leg = {
                    "id": f"{segment['departure']['iataCode']}-{segment['arrival']['iataCode']}-{segment['departure']['at']}",
                    "origin": {
                        "id": segment["departure"]["iataCode"],
                        "entityId": "generated_entity_id",
                        "name": "Generated Airport Name",
                        "displayCode": segment["departure"]["iataCode"],
                        "city": "Generated City",
                        "country": "Generated Country",
                        "isHighlighted": False
                    },
                    "destination": {
                        "id": segment["arrival"]["iataCode"],
                        "entityId": "generated_entity_id",
                        "name": "Generated Airport Name",
                        "displayCode": segment["arrival"]["iataCode"],
                        "city": "Generated City",
                        "country": "Generated Country",
                        "isHighlighted": False
                    },
                    "durationInMinutes": parse_duration(segment["duration"]),
                    "stopCount": segment["numberOfStops"],
                    "isSmallestStops": False,
                    "departure": segment["departure"]["at"],
                    "arrival": segment["arrival"]["at"],
                    "timeDeltaInDays": 0,
                    "carriers": {
                        "marketing": [
                            {
                                "id": "generated_carrier_id",
                                "logoUrl": "https://logos.skyscnr.com/images/airlines/favicon/UA.png",
                                "name": segment["carrierCode"]
                            }
                        ],
                        "operationType": "fully_operated"
                    },
                    "segments": [
                        {
                            "id": f"{segment['departure']['iataCode']}-{segment['arrival']['iataCode']}-{segment['departure']['at']}",
                            "origin": {
                                "flightPlaceId": segment["departure"]["iataCode"],
                                "displayCode": segment["departure"]["iataCode"],
                                "parent": {
                                    "flightPlaceId": "generated_parent_id",
                                    "displayCode": segment["departure"]["iataCode"],
                                    "name": "Generated City",
                                    "type": "City"
                                },
                                "name": "Generated Airport Name",
                                "type": "Airport",
                                "country": "Generated Country"
                            },
                            "destination": {
                                "flightPlaceId": segment["arrival"]["iataCode"],
                                "displayCode": segment["arrival"]["iataCode"],
                                "parent": {
                                    "flightPlaceId": "generated_parent_id",
                                    "displayCode": segment["arrival"]["iataCode"],
                                    "name": "Generated City",
                                    "type": "City"
                                },
                                "name": "Generated Airport Name",
                                "type": "Airport",
                                "country": "Generated Country"
                            },
                            "departure": segment["departure"]["at"],
                            "arrival": segment["arrival"]["at"],
                            "durationInMinutes": parse_duration(segment["duration"]),
                            "flightNumber": segment["number"],
                            "marketingCarrier": {
                                "id": "generated_carrier_id",
                                "name": segment["carrierCode"],
                                "alternateId": segment["carrierCode"],
                                "allianceId": 0,
                                "displayCode": ""
                            },
                            "operatingCarrier": {
                                "id": "generated_carrier_id",
                                "name": segment["carrierCode"],
                                "alternateId": segment["carrierCode"],
                                "allianceId": 0,
                                "displayCode": ""
                            }
                        }
                    ]
                }
                itinerary["legs"].append(leg)
        
        itinerary["isSelfTransfer"] = False
        itinerary["isProtectedSelfTransfer"] = False
        itinerary["farePolicy"] = {
            "isChangeAllowed": False,
            "isPartiallyChangeable": False,
            "isCancellationAllowed": False,
            "isPartiallyRefundable": False
        }
        itinerary["fareAttributes"] = []
        itinerary["isMashUp"] = False
        itinerary["hasFlexibleOptions"] = False
        itinerary["score"] = 0.999
        
        converted_data["itineraries"].append(itinerary)
    
    return json.dumps(converted_data, indent=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)


