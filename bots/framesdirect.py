# Step 1 - Initial Setup

# Libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Setup WebDriver
print("Setting up webdriver...")

chrome_option = Options()
chrome_option.add_argument("--headless")
chrome_option.add_argument("--disable-gpu")
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)

print("WebDriver Configuration Done..")

# Install Chrome driver
print("Installing Chrome Web Driver")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_option)

print("Driver ready")

# Target URL
url = "https://www.framesdirect.com/eyeglasses/"
print(f"Visiting {url}")

driver.get(url)

# Wait for page to load (IMPORTANT)
try:
    print("Waiting for product tiles to load...")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "prod-holder"))
    )

    print("Page loaded successfully. Ready for scraping.")

except Exception as e:
    print(f"Error loading page: {e}")
    driver.quit()
    raise


# Step 1 - Initial Setup
# Step 2 - Data Extraction

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


def clean_price(price_text):
    if not price_text:
        return None

    cleaned = (
        price_text.replace("$", "")
        .replace(",", "")
        .replace("As low as", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


print("Setting up webdriver...")

chrome_option = Options()
chrome_option.add_argument("--headless")
chrome_option.add_argument("--disable-gpu")
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)

print("WebDriver Configuration Done..")

print("Installing Chrome Web Driver")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_option)

print("Driver ready")

url = "https://www.framesdirect.com/eyeglasses/"
print(f"Visiting {url}")
driver.get(url)

try:
    print("Waiting for product tiles to load...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "prod-holder"))
    )
    print("Page loaded successfully. Ready for scraping.")
except Exception as e:
    print(f"Error loading page: {e}")
    driver.quit()
    raise

print("Parsing page source...")
content = driver.page_source
page = BeautifulSoup(content, "html.parser")

products = []

print("Extracting product data...")
product_tiles = page.find_all("div", class_="prod-holder")
print(f"Found {len(product_tiles)} product tiles.")

for tile in product_tiles:
    brand_tag = tile.find("div", class_="catalog-name")
    name_tag = tile.find("div", class_="product_name")
    former_price_tag = tile.find("div", class_="prod-catalog-retail-price")
    current_price_tag = tile.find("div", class_="prod-aslowas")

    brand = brand_tag.get_text(strip=True) if brand_tag else None
    product_name = name_tag.get_text(strip=True) if name_tag else None
    former_price = clean_price(former_price_tag.get_text(strip=True)) if former_price_tag else None
    current_price = clean_price(current_price_tag.get_text(strip=True)) if current_price_tag else None

    print("---- PRODUCT DEBUG ----")
    print("Brand:", brand)
    print("Product Name:", product_name)
    print("Former Price:", former_price)
    print("Current Price:", current_price)

    if brand and product_name and current_price is not None:
        products.append({
            "Vendor": "FramesDirect",
            "Brand": brand,
            "Product_Name": product_name,
            "Former_Price": former_price,
            "Current_Price": current_price
        })

print(f"Extracted {len(products)} products.")

for product in products[:5]:
    print(product)

# Step 3 - Data Storage



if products:
    column_names = products[0].keys()

    with open("./extracted_data/framesdirect-data.csv", mode="w", newline="", encoding="utf-8") as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=column_names)
        dict_writer.writeheader()
        dict_writer.writerows(products)

    print(f"Saved {len(products)} records to CSV.")

    with open("./extracted_data/framesdirect-data.json", mode="w", encoding="utf-8") as json_file:
        json.dump(products, json_file, indent=4)

    print(f"Saved {len(products)} records to JSON.")
else:
    print("No products were extracted, so no files were created.")

driver.quit()
print("End of Step 3")