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
    while i<10:
        i+=1
        response = requests.get(api_url)
        flight_data1 = response.json()
        if flight_data1['context']['status'] == 'complete':
            return flight_data1
        if flight_data=='':
            flight_data=flight_data1
        elif len(flight_data.get('itineraries', []))<len(flight_data1.get('itineraries', [])):
            flight_data=flight_data1
    return flight_data



@app.route('/fetch_flights', methods=['GET'])
def fetch_flights():
    access_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiMDM5MzNiN2YwYWFhZGMwMTUzOWMyMDI4OGFmZGY1MTk2M2MxNWVkMTAyYTBmMzExZTc5Zjg5M2ExZjEwMTMyYzI1YWJjNWYwZjZkODY0YmYiLCJpYXQiOjE3MjE2OTQwNjYsIm5iZiI6MTcyMTY5NDA2NiwiZXhwIjoxNzUzMjMwMDY2LCJzdWIiOiIyMjg2OCIsInNjb3BlcyI6W119.n1yJG4jMe7ANpmAbPed6Y_VcvgS5BgnuQLRvBIDpP_EYg1luEQ-D9JuXhryZOeV7_lSvl7XraGWURn1IEwDpQQ'
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
    response = requests.get("https://raw.githubusercontent.com/jainsee24/TravelFlight/main/flight/x.txt")
    number = 70#int(response.text.strip())


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
    new_itinerary = {
    'id': '10617-2408161552--32573-2-10037-2408162337',
    'price': {'raw': 136, 'formatted': '$136', 'pricingOptionId': 'NewEntry123'},
    'legs': [{
        'id': '10617-2408161552--32573-2-10037-2408162337',
        'origin': {'id': 'CMI', 'entityId': '95674194', 'name': 'University of Illinois Airport', 'displayCode': 'CMI', 'city': 'Champaign', 'country': 'United States', 'isHighlighted': False},
        'destination': {'id': 'BNA', 'entityId': '95673724', 'name': 'Nashville', 'displayCode': 'BNA', 'city': 'Nashville', 'country': 'United States', 'isHighlighted': False},
        'durationInMinutes': 441,
        'stopCount': 2,
        'isSmallestStops': False,
        'departure': '2024-08-16T15:52:00',
        'arrival': '2024-08-16T23:37:00',
        'timeDeltaInDays': 0,
        'carriers': {
            'marketing': [{'id': -32573, 'logoUrl': 'https://logos.skyscnr.com/images/airlines/favicon/AA.png', 'name': 'American Airlines'}],
            'operating': [{'id': -32573, 'name': 'American Airlines'}],
            'operationType': 'partially_operated'
        },
        'segments': [
            {'id': '10617-10037-2408161552-2408161805--32573', 'origin': {'flightPlaceId': 'CMI', 'displayCode': 'CMI', 'name': 'University of Illinois Airport', 'type': 'Airport', 'country': 'United States'}, 'destination': {'flightPlaceId': 'DFW', 'displayCode': 'DFW', 'name': 'Dallas/Ft. Worth International Airport', 'type': 'Airport', 'country': 'United States'}, 'departure': '2024-08-16T15:52:00', 'arrival': '2024-08-16T18:05:00', 'durationInMinutes': 133, 'flightNumber': '3700', 'marketingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}, 'operatingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}},
            {'id': '10037-10602-2408161855-2408162235--32573', 'origin': {'flightPlaceId': 'DFW', 'displayCode': 'DFW', 'name': 'Dallas/Ft. Worth International Airport', 'type': 'Airport', 'country': 'United States'}, 'destination': {'flightPlaceId': 'CLT', 'displayCode': 'CLT', 'name': 'Douglas International Airport', 'type': 'Airport', 'country': 'United States'}, 'departure': '2024-08-16T18:55:00', 'arrival': '2024-08-16T22:35:00', 'durationInMinutes': 160, 'flightNumber': '522', 'marketingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}, 'operatingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}},
            {'id': '10602-10037-2408162316-2408162337--32573', 'origin': {'flightPlaceId': 'CLT', 'displayCode': 'CLT', 'name': 'Douglas International Airport', 'type': 'Airport', 'country': 'United States'}, 'destination': {'flightPlaceId': 'BNA', 'displayCode': 'BNA', 'name': 'Nashville International Airport', 'type': 'Airport', 'country': 'United States'}, 'departure': '2024-08-16T23:16:00', 'arrival': '2024-08-16T23:37:00', 'durationInMinutes': 81, 'flightNumber': '526', 'marketingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}, 'operatingCarrier': {'id': -32573, 'name': 'American Airlines', 'alternateId': 'AA', 'allianceId': 0, 'displayCode': ''}}
        ]
    }],
    'isSelfTransfer': False,
    'isProtectedSelfTransfer': False,
    'farePolicy': {'isChangeAllowed': False, 'isPartiallyChangeable': False, 'isCancellationAllowed': False, 'isPartiallyRefundable': False},
    'fareAttributes': [],
    'tags': [],
    'isMashUp': False,
    'hasFlexibleOptions': False,
    'score': 0.0
    }

    # flight_data['itineraries'].append(new_itinerary)
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

    car_type_prices = {
    'Compact': 2,
    'Truck': 4,
    'Luxury': 6,
    'Convertible': 5,
    'Electric': 4,
    'SUV': 5,
    'Van': 3,
    'Hybrid': 4,
    'Economy': 2,
    'Full-size': 4,
    'Midsize': 3,
    'Mini': 2,
    'Premium': 5,
    'Standard': 3,
    'Mid-size': 3,
    'Mystery': 2
}

    car_results = []
    i=-1
    for car_type in car_types:
        i+=1
        for car_company in car_companies:
            price_per_day = car_type_prices.get(car_type, 3)  
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


