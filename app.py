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

# Load airports data
with open('static/cities.json', 'r') as f:
    cities = json.load(f)



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

@app.route('/cities')
def get_cities():
    return jsonify(cities)


def get_airport_info(access_key, query):
    api_url = f"https://app.goflightlabs.com/retrieveAirport?access_key={access_key}&query={query}"
    response = requests.get(api_url)
    airport_data = response.json()
    return airport_data

@app.route('/search_flights', methods=['GET'])
def search_flights():
    return render_template('results.html')

def check_flight_status(api_url):
    i = 0
    flight_data = ''
    while i < 10:
        i += 1
        response = requests.get(api_url)
        flight_data1 = response.json()
        if flight_data1['context']['status'] == 'complete':
            return flight_data1
        if flight_data == '':
            flight_data = flight_data1
        elif len(flight_data.get('itineraries', [])) < len(flight_data1.get('itineraries', [])):
            flight_data = flight_data1
    return flight_data

@app.route('/fetch_flights', methods=['GET'])
def fetch_flights():
    access_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiNGY3N2M0Y2M2NjBjYmVlZjQzYTg1ZDY5YjQ1OTUwNDVlYWExMGMyNDYzYzBkYWQ0OWFiZWZkNGVkMTBjYzdkZWZiZjZlOTJhZDc4MDgwMTgiLCJpYXQiOjE3MjMwMDkzNjUsIm5iZiI6MTcyMzAwOTM2NSwiZXhwIjoxNzU0NTQ1MzY1LCJzdWIiOiIyMjk0MiIsInNjb3BlcyI6W119.nmZm8nXiHkzILtd-P-JRma9f76hStUmTNuh7-tSQcHjjHxt6lpJoRh8w7OSsx6pmiQNTnTMBFYwxfIrK_MugSQ'
    origin_query = request.args.get('origin')
    destination_query = request.args.get('destination')
    date = request.args.get('date')
    return_date = request.args.get('returnDate')
    cabin_class = request.args.get('cabinClass')
    travelers = request.args.get('travelers')

    # Get airport info for origin and destination
    origin_info = get_airport_info(access_key, origin_query)
    destination_info = get_airport_info(access_key, destination_query)

    origin_sky_id = origin_info[0]['skyId']
    origin_entity_id = origin_info[0]['entityId']
    destination_sky_id = destination_info[0]['skyId']
    destination_entity_id = destination_info[0]['entityId']

    for i in destination_info:
        if i['skyId'] == destination_query:
            destination_entity_id = i['entityId']
    for i in origin_info:
        if i['skyId'] == origin_query:
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

    # Make the API request
    flight_data = check_flight_status(api_url)
    response = requests.get("https://raw.githubusercontent.com/jainsee24/TravelFlight/main/flight/x.txt")
    number = 75  # int(response.text.strip())

    for itinerary in flight_data.get('itineraries', []):
        original_price = itinerary['price']['raw']
        discounted_price = original_price * (1 - number / 100)
        itinerary['price']['raw'] = int(discounted_price)
        itinerary['price']['formatted'] = f"${int(discounted_price)}"
        for leg in itinerary.get('legs', []):
            for carrier in leg['carriers']['marketing']:
                if carrier['name'] == 'Alaska Airlines':
                    carrier['logoUrl'] = 'https://banner2.cleanpng.com/20180704/yik/kisspng-alaska-airlines-bna-seattletacoma-internation-5b3d8aefc5ec28.5427569615307599198107.jpg'

    new_itinerary = {
        'id': 'SAN-LAX-16082024',
        'price': {'raw': 87, 'formatted': '$87', 'pricingOptionId': 'NewEntry456'},
        'legs': [{
            'id': 'SAN-LAX-16082024',
            'origin': {'id': 'SAN', 'entityId': '12345678', 'name': 'San Diego International Airport', 'displayCode': 'SAN', 'city': 'San Diego', 'country': 'United States', 'isHighlighted': False},
            'destination': {'id': 'LAX', 'entityId': '87654321', 'name': 'Los Angeles International Airport', 'displayCode': 'LAX', 'city': 'Los Angeles', 'country': 'United States', 'isHighlighted': False},
            'durationInMinutes': 172,
            'stopCount': 1,
            'isSmallestStops': False,
            'departure': '2024-08-16T16:43:00',
            'arrival': '2024-08-16T20:24:00',
            'timeDeltaInDays': 0,
            'carriers': {
                'marketing': [{'id': -56789, 'logoUrl': 'https://banner2.cleanpng.com/20180704/yik/kisspng-alaska-airlines-bna-seattletacoma-internation-5b3d8aefc5ec28.5427569615307599198107.jpg', 'name': 'Alaska Airlines'}],
                'operating': [{'id': -56789, 'name': 'Alaska Airlines'}],
                'operationType': 'fully_operated'
            },
            'segments': [
                {'id': 'SAN-SJC-16082024-16112024--56789', 'origin': {'flightPlaceId': 'SAN', 'displayCode': 'SAN', 'name': 'San Diego International Airport', 'type': 'Airport', 'country': 'United States'}, 'destination': {'flightPlaceId': 'SJC', 'displayCode': 'SJC', 'name': 'Norman Y. Mineta International', 'type': 'Airport', 'country': 'United States'}, 'departure': '2024-08-16T16:43:00', 'arrival': '2024-08-16T18:11:00', 'durationInMinutes': 88, 'flightNumber': '3384', 'marketingCarrier': {'id': -56789, 'name': 'Alaska Airlines', 'alternateId': 'AS', 'allianceId': 0, 'displayCode': ''}, 'operatingCarrier': {'id': -56789, 'name': 'Alaska Airlines', 'alternateId': 'AS', 'allianceId': 0, 'displayCode': ''}},
                {'id': 'SJC-LAX-16082024-16242024--56789', 'origin': {'flightPlaceId': 'SJC', 'displayCode': 'SJC', 'name': 'Norman Y. Mineta International', 'type': 'Airport', 'country': 'United States'}, 'destination': {'flightPlaceId': 'LAX', 'displayCode': 'LAX', 'name': 'Los Angeles International Airport', 'type': 'Airport', 'country': 'United States'}, 'departure': '2024-08-16T19:00:00', 'arrival': '2024-08-16T20:24:00', 'durationInMinutes': 84, 'flightNumber': '3387', 'marketingCarrier': {'id': -56789, 'name': 'Alaska Airlines', 'alternateId': 'AS', 'allianceId': 0, 'displayCode': ''}, 'operatingCarrier': {'id': -56789, 'name': 'Alaska Airlines', 'alternateId': 'AS', 'allianceId': 0, 'displayCode': ''}}
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

    flight_data['itineraries'].append(new_itinerary)

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
        'Nissan Van', 'BMW X3', 'Chevrolet Spark', 'Chevrolet Malibu', 'GMC Yukon', 'Mitsuibuishi Mirage', 
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
    'Full-size': 7,
    'Midsize': 3,
    'Mini': 2,
    'Premium': 5,
    'Standard': 3,
    'Mid-size': 3,
    'Mystery': 2
}
    car_companies_taxes = {
    'Thrifty': 0.10,
    'Sixt': 0.12,
    'National': 0.15,
    'Hertz': 0.13,
    'Fox': 0.11,
    'Enterprise': 0.14,
    'Dollar': 0.09,
    'Budget': 0.10,
    'Avis': 0.13,
    'Alamo': 0.12
}

    car_results = []
    i=-1
    for car_type in car_types:
        i+=1
        for car_company in car_companies:
            price_per_day = car_type_prices.get(car_type, 3)
            tax_rate = car_companies_taxes.get(car_company, 0.10)
            price_per_day = round(price_per_day * (1 + tax_rate), 2)
            cancellation_deadline = pick_up_date_obj - timedelta(days=0)
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
                "pricePerDay": price_per_day*2,
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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime


top_100_airports = [
    "ATL", "DFW", "DEN", "ORD", "LAX", "JFK", "LAS", "MCO", "MIA", "CLT",
    "SEA", "PHX", "EWR", "SFO", "IAH", "BOS", "FLL", "MSP", "LGA", "DTW",
    "PHL", "SLC", "DCA", "SAN", "BWI", "TPA", "AUS", "IAD", "BNA", "MDW", 
    "HNL", "STL", "DAL", "HOU", "RDU", "MCI", "MKE", "SNA", "OAK", "SMF",
    "SJC", "CLE", "SJU", "SAT", "RSW", "IND", "PIT", "CVG", "CMH", "MSY",
    "RNO", "JAX", "ABQ", "OGG", "ONT", "BUF", "ANC", "PDX", "BOI", "BUR",
    "LIH", "BHM", "PBI", "LGB", "TUL", "OMA", "OKC", "TUS", "RIC", "PVD",
    "CHS", "GRR", "ALB", "SAV", "ELP", "HSV", "GSP", "SYR", "BTV", "PWM",
    "FAT", "ICT", "DAY", "BDL", "LIT", "COS", "PSP", "ROA", "MYR", "CRW",
    "LEX", "TYS", "ECP", "FAR", "MOB"
]

top_100_eur = [
    "AMS", "ATH", "BCN", "BRU", "BUD", "CPH", "DUB", "DUS", "FCO", "FRA",
    "GVA", "HAM", "HEL", "IST", "LGW", "LHR", "LIN", "LIS", "LYS", "MAD",
    "MAN", "MUC", "MXP", "NCE", "OSL", "OTP", "PMI", "PRG", "RIX", "SVO",
    "ARN", "TXL", "VIE", "WAW", "ZRH", "BFS", "BHD", "BHX", "BRS", "EDI",
    "GLA", "LTN", "NCL", "STN", "BGO", "SVG", "TRD", "OSD", "ARN", "GOT",
    "MMX", "BMA", "NYO", "VST", "BLL", "AAL", "KRP", "TLL", "RIX", "VNO",
    "MSQ", "GDN", "KRK", "KTW", "POZ", "WRO", "SZZ", "ZAG", "DBV", "SPU",
    "PUY", "RJK", "SJJ", "SKP", "TIA", "PRN", "SOF", "VAR", "BOJ", "OTP",
    "CLJ", "TSR", "LCA", "PFO", "MLA", "SKG", "ATH", "HER", "CHQ", "RHO",
    "CFU", "JTR", "KLX", "VOL", "SMI", "JSI", "KGS", "PVK"
]


top_50_airports_india = [
    "DEL",  # Indira Gandhi International Airport, Delhi
    "BOM",  # Chhatrapati Shivaji Maharaj International Airport, Mumbai
    "BLR",  # Kempegowda International Airport, Bengaluru
    "MAA",  # Chennai International Airport, Chennai
    "HYD",  # Rajiv Gandhi International Airport, Hyderabad
    "CCU",  # Netaji Subhas Chandra Bose International Airport, Kolkata
    "AMD",  # Sardar Vallabhbhai Patel International Airport, Ahmedabad
    "GOI",  # Goa International Airport, Goa
    "COK",  # Cochin International Airport, Kochi
    "PNQ",  # Pune International Airport, Pune
    "TRV",  # Trivandrum International Airport, Thiruvananthapuram
    "JAI",  # Jaipur International Airport, Jaipur
    "LKO",  # Chaudhary Charan Singh International Airport, Lucknow
    "BBI",  # Biju Patnaik International Airport, Bhubaneswar
    "IXC",  # Chandigarh International Airport, Chandigarh
    "VGA",  # Vijayawada International Airport, Vijayawada
    "PAT",  # Jay Prakash Narayan International Airport, Patna
    "NAG",  # Dr. Babasaheb Ambedkar International Airport, Nagpur
    "GWL",  # Gwalior Airport, Gwalior
    "BHO",  # Raja Bhoj International Airport, Bhopal
    "IXJ",  # Jammu Airport, Jammu
    "SXR",  # Sheikh ul-Alam International Airport, Srinagar
    "IXL",  # Kushok Bakula Rimpochee Airport, Leh
    "UDR",  # Maharana Pratap Airport, Udaipur
    "IXU",  # Aurangabad Airport, Aurangabad
    "HBX",  # Hubli Airport, Hubli
    "VNS",  # Lal Bahadur Shastri Airport, Varanasi
    "BDQ",  # Vadodara Airport, Vadodara
    "IXB",  # Bagdogra Airport, Bagdogra
    "IXE",  # Mangalore International Airport, Mangalore
    "ATQ",  # Sri Guru Ram Dass Jee International Airport, Amritsar
    "JDH",  # Jodhpur Airport, Jodhpur
    "GAU",  # Lokpriya Gopinath Bordoloi International Airport, Guwahati
    "DIB",  # Dibrugarh Airport, Dibrugarh
    "DMU",  # Dimapur Airport, Dimapur
    "SHL",  # Shillong Airport, Shillong
    "IMF",  # Imphal International Airport, Imphal
    "IXR",  # Birsa Munda Airport, Ranchi
    "RPR",  # Swami Vivekananda Airport, Raipur
    "JLR",  # Jabalpur Airport, Jabalpur
    "STV",  # Surat Airport, Surat
    "UDR",  # Maharana Pratap Airport, Udaipur
    "TIR",  # Tirupati Airport, Tirupati
    "BBI",  # Biju Patnaik International Airport, Bhubaneswar
    "CJB",  # Coimbatore International Airport, Coimbatore
    "IXM",  # Madurai Airport, Madurai
    "TRZ",  # Tiruchirappalli International Airport, Tiruchirappalli
    "IXA",  # Maharaja Bir Bikram Airport, Agartala
    "AJL",  # Lengpui Airport, Aizawl
    "CCJ",
    "IDR",  # Calicut International Airport, Kozhikode
]

@app.route('/skip')
def skip_home():
    return render_template('skip.html')

@app.route('/search', methods=['POST'])
def search():
    from_cities = request.form['from'].split(',')
    from_city = from_cities[0]
    to_cities = request.form['to'].split(',')
    to_city = to_cities[0]
    depart_date = request.form['depart_date']

    filtered_results = []

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Path to Chrome and ChromeDriver
    chrome_path = "/app/.chrome-for-testing/chrome-linux64/chrome"
    chromedriver_path = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(f"https://skiplagged.com/flights/{from_city}/{to_city}/{depart_date}")

    fetch_scripts = []

    for from_city1 in from_cities:
        for hub_city in top_100_airports:
            if hub_city == from_city1:
                continue

            # Create a fetch script for each API call
            script = f"""
            fetch("https://skiplagged.com/api/search.php?from={from_city1}&to={hub_city}&depart={depart_date}&return=&format=v3&counts%5Badults%5D=1&counts%5Bchildren%5D=0", {{
                "headers": {{
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "en-US,en;q=0.9",
                    "priority": "u=1, i",
                    "sec-ch-ua": "\\"Not/A)Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"126\\", \\"Google Chrome\\";v=\\"126\\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\\"macOS\\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-requested-with": "XMLHttpRequest"
                }},
                "referrer": "https://skiplagged.com/flights/{from_city1}/{hub_city}/{depart_date}",
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": null,
                "method": "GET",
                "mode": "cors",
                "credentials": "include"
            }}).then(response => response.json())
            """
            fetch_scripts.append(script)

    # Combine all fetch scripts into one to execute in parallel
    combined_script = f"""
    Promise.all([{','.join(fetch_scripts)}]).then(results => {{
        return results.map(result => {{
            return result.json();
        }});
    }});
    """
    # Execute the combined script
    results = driver.execute_script(combined_script)

    for result in results:
        if not result:
            continue
        
        itineraries = result.get('itineraries', {}).get('outbound', [])
        flights = result.get('flights', {})
        
        for itinerary in itineraries:
            try:
                itinerary_data = json.loads(itinerary['data'].split('|')[1])
                flight_key = itinerary_data['key']
                flight_data = flights.get(flight_key, {})
                
                if not flight_data:
                    continue
                
                segments = flight_data.get('segments', [])
                if any(segment['arrival']['airport'] in to_cities for segment in segments) or segments[-1]['arrival']['airport'] == to_city:
                    layover_times = []
                    total_layover_time = 0
                    for i in range(1, len(segments)):
                        departure_time = datetime.fromisoformat(segments[i]['departure']['time'])
                        arrival_time = datetime.fromisoformat(segments[i-1]['arrival']['time'])
                        layover_duration = (departure_time - arrival_time) if departure_time and arrival_time else "N/A"
                        layover_times.append(str(layover_duration))
                        if layover_duration != "N/A":
                            total_layover_time += layover_duration.total_seconds()
                    
                    total_travel_time = arrival_time - departure_time
                    total_travel_seconds = total_travel_time.total_seconds()
                    total_travel_hours = total_travel_seconds // 3600
                    total_travel_minutes = (total_travel_seconds % 3600) // 60

                    filtered_result = {
                    'airline': segments[0]['airline'],
                    'flight_number': segments[0]['flight_number'],
                    'cost': itinerary_data['cost'],
                    'departure': segments[0]['departure']['time'],
                    'arrival': segments[-1]['arrival']['time'],
                    'segments': segments,
                    'layover_times': layover_times,
                    'total_layover_time': total_layover_time,
                    'total_travel_time': f"{int(total_travel_hours)}h {int(total_travel_minutes)}m"
                }

                    filtered_results.append(filtered_result)
            except (json.JSONDecodeError, KeyError):
                continue  # Skip this itinerary if there's an error

    # Close the browser
    driver.quit()

    # Sort results by cost
    filtered_results.sort(key=lambda x: x['cost'])
    return render_template('skip_results.html', results=filtered_results, from_city=from_city, to_city=to_city, depart_date=depart_date)

@app.route('/search_stays')
def search_stays():
    airport = request.args.get('airport')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    num_rooms = request.args.get('num_rooms', 1)
    num_adults = request.args.get('num_adults', 1)
    num_children = request.args.get('num_children', 0)

    api_url = f"https://skiplagged.com/api/hotel_search.php?airport={airport}&checkin={checkin}&checkout={checkout}&num_rooms={num_rooms}&num_adults={num_adults}&num_children={num_children}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(api_url, headers=headers)
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        data = {"error": "Invalid response from the hotel API"}
    
    return render_template(
        'hotels.html',
        data=data,
        airport=airport,
        checkin=checkin,
        checkout=checkout,
        num_rooms=num_rooms,
        num_adults=num_adults,
        num_children=num_children
    )

@app.route('/show_available_room')
def show_available_room():
    hotel_id = request.args.get('hotel_id')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    num_rooms = request.args.get('num_rooms')
    num_adults = request.args.get('num_adults')
    num_children = request.args.get('num_children')

    url = f"https://skiplagged.com/api/hotel_detail.php?hotel_id={hotel_id}&checkin={checkin}&checkout={checkout}&num_rooms={num_rooms}&numAdults={num_adults}&numChildren={num_children}&live=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url,headers=headers)
    data = response.json()

    return render_template('show_available_room.html', hotel=data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
