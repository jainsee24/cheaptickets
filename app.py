from flask import Flask, render_template, request, jsonify, redirect
import requests
import json
import time

from datetime import datetime, timedelta
import random
from flask import send_from_directory


app = Flask(__name__)

@app.before_request
def before_request():
    if not request.is_secure and not app.debug:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


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
@app.route('/flight')
def home1():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
    return flight_data



@app.route('/fetch_flights', methods=['GET'])
def fetch_flights():
    access_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiYmMwNzA2NWIxZTIzZjU4NzU0N2I2M2Y1NjM5Njc4ZGU0MzNlMzkxYzYwNGMwYzAxNmM0ZjEwOWFkYmU5OWJkNTUyYjdmNzMxODZlMzA1NDAiLCJpYXQiOjE3MjA5NTAxMTgsIm5iZiI6MTcyMDk1MDExOCwiZXhwIjoxNzUyNDg2MTE4LCJzdWIiOiIyMjgyNSIsInNjb3BlcyI6W119.uN3amniKbYUyVtnts-2-P4TFmdNGmcjXavGeeOVnC8u6yp19HG1RIz545Pd-CV_ZwSjTRrx9mKLbepzQRaPzcA'
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
    number = 60#int(response.text.strip())


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
    additional_flight = {
        'id': 'custom-1',
        'price': {'raw': 1507, 'formatted': '$1507'},
        'legs': [
            {
                'id': 'custom-leg-1',
                'origin': {'name': 'San Francisco International Airport', 'displayCode': 'SFO', 'city': 'San Francisco', 'country': 'United States'},
                'destination': {'name': 'Heathrow Airport', 'displayCode': 'LHR', 'city': 'London', 'country': 'United Kingdom'},
                'departure': '2024-11-14T15:45:00',
                'arrival': '2024-11-15T10:00:00',
                'durationInMinutes': 615,
                'carriers': {'marketing': [{'name': 'Virgin Atlantic', 'logoUrl': 'data:image/png;base64,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'}]},
                'segments': [
                    {
                        'origin': {'flightPlaceId': 'SFO', 'displayCode': 'SFO', 'name': 'San Francisco International', 'type': 'Airport'},
                        'destination': {'flightPlaceId': 'LHR', 'displayCode': 'LHR', 'name': 'Heathrow Airport', 'type': 'Airport'},
                        'departure': '2024-11-14T15:45:00',
                        'arrival': '2024-11-15T10:00:00',
                        'durationInMinutes': 615,
                        'flightNumber': 'VS 20',
                        'marketingCarrier': {'name': 'Virgin Atlantic', 'alternateId': 'VS', 'displayCode': 'VS'},
                        'aircraft': {'code': '787', 'name': '787 (widebody)'},
                        'cabinClass': 'Upper Class'
                    }
                ]
            },
            {
                'id': 'custom-leg-2',
                'origin': {'name': 'Heathrow Airport', 'displayCode': 'LHR', 'city': 'London', 'country': 'United Kingdom'},
                'destination': {'name': 'Kempegowda Intl Airport', 'displayCode': 'BLR', 'city': 'Bengaluru', 'country': 'India'},
                'departure': '2024-11-15T11:05:00',
                'arrival': '2024-11-16T02:35:00',
                'durationInMinutes': 600,
                'carriers': {'marketing': [{'name': 'Virgin Atlantic', 'logoUrl': 'data:image/png;base64,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'}]},
                'segments': [
                    {
                        'origin': {'flightPlaceId': 'LHR', 'displayCode': 'LHR', 'name': 'Heathrow Airport', 'type': 'Airport'},
                        'destination': {'flightPlaceId': 'BLR', 'displayCode': 'BLR', 'name': 'Kempegowda Intl Airport', 'type': 'Airport'},
                        'departure': '2024-11-15T11:05:00',
                        'arrival': '2024-11-16T02:35:00',
                        'durationInMinutes': 600,
                        'flightNumber': 'VS 316',
                        'marketingCarrier': {'name': 'Virgin Atlantic', 'alternateId': 'VS', 'displayCode': 'VS'},
                        'aircraft': {'code': '787', 'name': '787 (widebody)'},
                        'cabinClass': 'Upper Class'
                    }
                ]
            }
        ],
        'isSelfTransfer': False,
        'isProtectedSelfTransfer': True
    }
    
    flight_data['itineraries'].append(additional_flight)
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

@app.route('/search_cars', methods=['GET'])
def search_cars():
    pick_up_location = request.args.get('pickUpLocation')
    drop_off_location = request.args.get('dropOffLocation')
    pick_up_date = request.args.get('pickUpDate')
    drop_off_date = request.args.get('dropOffDate')

    # Check if dates are provided
    if not pick_up_date or not drop_off_date:
        return "Please provide both pick-up and drop-off dates", 400

    # Convert dates to datetime objects
    pick_up_date_obj = datetime.strptime(pick_up_date, '%Y-%m-%d')
    drop_off_date_obj = datetime.strptime(drop_off_date, '%Y-%m-%d')

    # Calculate the number of days
    days = (drop_off_date_obj - pick_up_date_obj).days

    car_types = [
        'Compact', 'Truck', 'Luxury', 'Convertible', 'Electric', 'SUV', 
        'Van', 'Hybrid', 'Economy', 'Full-size', 'Midsize', 'Mini', 
        'Premium', 'Standard', 'Mid-size', 'Mystery'
    ]

    car_types_name = [
        'Ford Focus', 'Chevy Colorado', 'Chrysler 300', 'Ford Mustang', 'Telsa Model 3', 'Chevrolet Equinox', 
        'Nissan Pathfinder', 'BMW X3', 'Chevrolet Spark', 'Nissan Pathfinder', 'GMC Yukon', 'Mitsuibuishi Mirage', 
        'Nissan Maxima', 'Volkswagen Jetta', 'Mazda 3', 'Mystery'
    ]
    

    car_companies = [
        'Thrifty', 'Sixt', 'National', 'Hertz', 'Fox', 'Enterprise', 
        'Dollar', 'Budget', 'Avis', 'Alamo'
    ]

    car_results = []
    i=-1
    for car_type in car_types:
        i+=1
        for car_company in car_companies:
            price_per_day = random.randint(2, 6)
            cancellation_deadline = pick_up_date_obj - timedelta(days=3)
            company_logo = f"/static/images/{car_company.lower()}.png"
            image = f"/static/images/{car_type.lower()}.png"

            car_results.append({
                "type": car_type,
                "company": car_company,
                "model": car_types_name[i],
                "passengers": 5,
                "bags": 3,
                "transmission": "Automatic",
                "image": image,
                "pricePerDay": price_per_day,
                "days": days,
                "companyLogo": company_logo,
                "pickupLocation": pick_up_location,
                "cancellationDeadline": cancellation_deadline.strftime('%Y-%m-%d')
            })
    import numpy as np
    np.random.shuffle(car_results)
    return render_template('car-result.html', cars=car_results)


@app.route('/car-book')
def car_book():
    type = request.args.get('type')
    model = request.args.get('model')
    company = request.args.get('company')
    price_per_day = request.args.get('pricePerDay')
    days = request.args.get('days')
    pickup_location = request.args.get('pickupLocation')
    cancellation_deadline = request.args.get('cancellationDeadline')
    image = request.args.get('image')
    company_logo = request.args.get('companyLogo')

    car_details = {
        'type': type,
        'model': model,
        'company': company,
        'price_per_day': price_per_day,
        'days': days,
        'pickup_location': pickup_location,
        'cancellation_deadline': cancellation_deadline,
        'image': image,
        'company_logo': company_logo
    }

    return render_template('car-book.html', car_details=car_details)

# @app.errorhandler(404)
# def not_found(e):
#     return render_template('index.html'), 404

# @app.errorhandler(405)
# def method_not_allowed(e):
#     return render_template('index.html'), 405

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)


