# from flask import Flask, Response
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import requests

# app = Flask(__name__)

# def get_website_content(url):
#     # Set up Chrome options
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Run headless Chrome
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")  # Ensure sufficient resolution

#     # Set up Chrome driver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
#     # Open the website
#     driver.get(url)
    
#     # Wait for the page to load completely
#     try:
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )
#     except Exception as e:
#         print("Error loading page:", e)
#         driver.quit()
#         return None, []

#     # Get the HTML content
#     html_content = driver.page_source
    
#     # Get all CSS links
#     css_links = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
#     css_files = []
#     for link in css_links:
#         href = link.get_attribute("href")
#         if href:
#             try:
#                 css_content = requests.get(href).text
#                 css_files.append(css_content)
#             except Exception as e:
#                 print(f"Error fetching CSS file {href}: {e}")

#     # Close the driver
#     driver.quit()
    
#     return html_content, css_files

# @app.route('/scrape', methods=['GET'])
# def scrape():
#     url = "https://edreams.net/"
#     html_content, css_files = get_website_content(url)
#     if html_content:
#         # Inject CSS into HTML
#         css_injection = "<style>" + "\n".join(css_files) + "</style>"
#         injected_html = html_content.replace("</head>", css_injection + "</head>")
#         return Response(injected_html, mimetype='text/html')
#     else:
#         return Response("Error loading page", status=500)

# if __name__ == '__main__':
#     app.run(debug=True)


import requests

def get_airport_info(access_key, query):
    try:
        api_url = f"https://app.goflightlabs.com/retrieveAirport?access_key={access_key}&query={query}"
        response = requests.get(api_url)
        response.raise_for_status()
        airport_data = response.json()
        if not airport_data:  # Check if the response is empty
            print(f"No airport data found for {query}")
            return None
        return airport_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching airport info for {query}: {e}")
        return None

def fetch_flights(access_key, origin, destinations, date, return_date=None, cabin_class='first', travelers=1):
    all_flights = []

    for destination in destinations:
        # Get airport info for origin and destination
        origin_info = get_airport_info(access_key, origin)
        destination_info = get_airport_info(access_key, destination)

        if origin_info is None or destination_info is None:
            continue

        if not origin_info or not destination_info:
            print(f"Skipping {destination} due to missing airport info")
            continue

        origin_sky_id = origin_info[0]['skyId']
        origin_entity_id = origin_info[0]['entityId']
        destination_sky_id = destination_info[0]['skyId']
        destination_entity_id = destination_info[0]['entityId']

        for i in destination_info:
            if i['skyId'] == destination:
                destination_entity_id = i['entityId']
        for i in origin_info:
            if i['skyId'] == origin:
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
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            flights = response.json()
            if 'itineraries' in flights:
                all_flights.extend(flights['itineraries'])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching flights from {origin} to {destination}: {e}")
            continue

    return all_flights

def filter_and_sort_flights(flights):
    # Modify this logic to fit your requirement better
    flights_with_criteria = [
        flight for flight in flights if any(segment['destination']['displayCode'] == 'MUC' for leg in flight['legs'] for segment in leg['segments'])
    ]
    flights_with_criteria_sorted = sorted(flights_with_criteria, key=lambda x: x['price']['raw'])
    return flights_with_criteria_sorted[:5]

if __name__ == "__main__":
    access_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiMGQ5MjNkYTBhY2MzNWJhMjhlZmQ5NjUwNDJlMWI3NTdhMzIwMDI4NzNiZDk0ZGJlODYxZDEyMjA1N2EzYzRiOTMwZTE5ZmQzZmVlMGJiNDkiLCJpYXQiOjE3MjI0ODcyOTMsIm5iZiI6MTcyMjQ4NzI5MywiZXhwIjoxNzU0MDIzMjkzLCJzdWIiOiIyMjkyMyIsInNjb3BlcyI6W119.C1earFApGOKC6nW3WU-hX6odbYtB6EBVO5LMRHAD5iFBCZpwDChDhyaTvxk0Mu7rEex-HD33w3mTBoP9i2I0Xg'
    origin = 'SAN'
    top_20_europe_airports = [
        'LHR', 'CDG', 'FRA', 'AMS', 'MUC', 'BCN', 'MAD', 'FCO', 'DUB', 'ZRH',
        'VIE', 'CPH', 'OSL', 'BRU', 'HEL', 'ARN', 'TXL', 'GVA', 'IST', 'LGW'
    ]

    # For testing, limit to the top 1 airport

    date = '2024-10-15'
    return_date = None  # Use None for no return date

    flights = fetch_flights(access_key, origin, top_20_europe_airports, date, return_date)

    top_5_flights = filter_and_sort_flights(flights)

    for flight in top_5_flights:
        print(f"Flight from {flight['legs'][0]['origin']['displayCode']} to {flight['legs'][0]['destination']['displayCode']}")
        print(f"Price: {flight['price']['formatted']}")
        layovers = [segment['destination']['displayCode'] for leg in flight['legs'] for segment in leg['segments']]
        print(f"Layovers: {layovers}")
        print("\n")
