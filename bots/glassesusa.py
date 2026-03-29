# Libraries Used
import csv
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Helper function to clean price text
def clean_price(price_text):
    if not price_text:
        return None

    cleaned = (
        price_text.replace("$", "")
        .replace("C$", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


# Helper function to split combined title into brand and product name
def split_brand_and_product(full_title):
    if not full_title:
        return None, None

    parts = full_title.strip().split(maxsplit=1)

    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[1]


# Step 1 - Configuration and Setup
# Setup Selenium WebDriver
print("Setting up webdriver...")
chrome_option = Options()

# Keep headless OFF for debugging GlassesUSA
# chrome_option.add_argument('--headless=new')

chrome_option.add_argument('--disable-gpu')
chrome_option.add_argument('--window-size=1920,1080')
chrome_option.add_argument('--no-sandbox')
chrome_option.add_argument('--disable-dev-shm-usage')
chrome_option.add_argument('--log-level=3')
chrome_option.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)

print("WebDriver Configuration Done..")

# Install the chrome driver
print("Installing Chrome Web Driver")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "https://www.glassesusa.com/eyeglasses-collection"
print(f"Visiting {url} page")
driver.get(url)

# Wait for page body, scroll to trigger lazy loading,
# then wait for productTitle elements to appear
try:
    print("Waiting for page body to load...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    print("Page body loaded.")
    time.sleep(5)

    print("Scrolling to trigger lazy loading...")
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(15):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scroll {i + 1} completed")
        time.sleep(3)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            print("No more new content loaded.")
            break

        last_height = new_height

    print("Waiting extra time after scrolling...")
    time.sleep(5)

    print("Done...Proceed to parse the data")

except Exception as e:
    print(f"Error waiting for {url}: {e}")

    with open("glassesusa_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print("Saved debug HTML as glassesusa_debug.html")
    driver.quit()
    raise
html = driver.page_source

print("Contains productTitle:", 'data-test-name="productTitle"' in html)
print("Contains regularPrice:", 'data-test-name="regularPrice"' in html)
print("Contains lazyload-wrapper:", 'lazyload-wrapper' in html)

# Data Parsing and Extraction
# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, 'html.parser')

products = []

print("Extracting product data...")
product_tiles = page.find_all("div", class_="lazyload-wrapper")
print(f"Found {len(product_tiles)} product tiles.")

for tile in product_tiles:
    title_tag = tile.find("a", attrs={"data-test-name": "productTitle"})
    price_tag = tile.find("span", attrs={"data-test-name": "regularPrice"})

    full_title = title_tag.get_text(strip=True) if title_tag else None
    current_price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

    brand, product_name = split_brand_and_product(full_title)

    if full_title and current_price is not None:
        products.append({
            "Vendor": "GlassesUSA",
            "Brand": brand,
            "Product_Name": product_name,
            "Former_Price": None,
            "Current_Price": current_price
        })

print(f"Extracted {len(products)} products.")

for product in products[:5]:
    print(product)

# Step 3 - Data Storage
if products:
    column_names = products[0].keys()

    with open("./extracted_data/glassesusa-data.csv", mode="w", newline="", encoding="utf-8") as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=column_names)
        dict_writer.writeheader()
        dict_writer.writerows(products)

    print(f"Saved {len(products)} records to CSV.")

    with open("./extracted_data/glassesusa-data.json", mode="w", encoding="utf-8") as json_file:
        json.dump(products, json_file, indent=4)

    print(f"Saved {len(products)} records to JSON.")
else:
    print("No products were extracted, so no files were created.")

# close the browser
driver.quit()
print("Closed")