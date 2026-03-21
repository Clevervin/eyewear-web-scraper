# Libraries Used
import csv 
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Step 1 - Configuration and Setup
# Setup Selenium WebDriver
print("Setting up webdriver...")
chrome_option = Options()
chrome_option.add_argument('--headless')
chrome_option.add_argument('--disable-gpu')
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36")
# This is specifically for Mac OS, Uncomment the below line and comment the above line if you are running on Mac OS
# chrome_option.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36 ")
print("WebDriver Configuration Done..")

# Install the chrome driver (This is a one time thing)
print("Installing Chrome Web Driver")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "The_Sites_URL"
print(f"Visting {url} page")
driver.get(url)

# Further instruction to wait for JS to load the products via the body tag
try:
    print("Waiting for product tiles to load")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'site_element_body'))
    )
    print("Done...Proceed to parse the data")
except (TimeoutError, Exception) as e:
    print(f"Error waiting for {url}: {e}")
    driver.quit()
    print("Closed")

# Data Parsing and Extraction
# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, 'html.parser')

# THIS IS WHERE YOU COME IN - Modify this part to extract the data (Brand Name, Product Name, Former and Current Price)

# temporary storage for the extracted data
products = []


# Step 3 - Data Storage: store the extracted data in CSV and JSON formats
# Save to CSV file
column_name = products[0].keys() # get the column names
with open('./extracted_data/websitename-data.csv', mode='w', newline='', encoding='utf-8') as csv_file: # open up the file with context manager
    dict_writer = csv.DictWriter(csv_file, fieldnames=column_name)
    dict_writer.writeheader()
    dict_writer.writerows(products)
print(f"Saved {len(products)} records to CSV in the extracted data folder.")

# Save to JSON file
with open("./extracted_data/websitename-data.json", mode='w') as json_file:
    json.dump(products, json_file, indent=4)
print(f"Saved {len(products)} records to JSON in the extracted data folder.")

# close the browser
driver.quit()
print("End of Web Extraction")