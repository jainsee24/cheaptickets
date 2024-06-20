from flask import Flask, Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

app = Flask(__name__)

def get_website_content(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")  # Ensure sufficient resolution

    # Set up Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the website
    driver.get(url)
    
    # Wait for the page to load completely
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print("Error loading page:", e)
        driver.quit()
        return None, []

    # Get the HTML content
    html_content = driver.page_source
    
    # Get all CSS links
    css_links = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
    css_files = []
    for link in css_links:
        href = link.get_attribute("href")
        if href:
            try:
                css_content = requests.get(href).text
                css_files.append(css_content)
            except Exception as e:
                print(f"Error fetching CSS file {href}: {e}")

    # Close the driver
    driver.quit()
    
    return html_content, css_files

@app.route('/scrape', methods=['GET'])
def scrape():
    url = "https://edreams.net/"
    html_content, css_files = get_website_content(url)
    if html_content:
        # Inject CSS into HTML
        css_injection = "<style>" + "\n".join(css_files) + "</style>"
        injected_html = html_content.replace("</head>", css_injection + "</head>")
        return Response(injected_html, mimetype='text/html')
    else:
        return Response("Error loading page", status=500)

if __name__ == '__main__':
    app.run(debug=True)
