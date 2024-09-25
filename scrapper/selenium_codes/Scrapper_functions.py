import random
import time
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options


def get_chrome_options():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')  # This option is not necessary for Firefox but can be left for compatibility
    options.add_argument('--incognito')
    options.add_argument('--disable-infobars')  # Not applicable to Firefox
    return options

def scrape_prices_from_dawa(urls):
    price_Dawa = []
    max_retries = 2  # Maximum retries for stale elements

    # Initialize WebDriver
    options = get_chrome_options()
    service = Service()  # Using the default service; specify the path if necessary
    driver = webdriver.Firefox(service=service, options=options)
    print("ChromeDriver initialized successfully.")
    
    # Iterate over the URLs
    for url in urls:
        retries = 0
        while retries <= max_retries:
            try:
                print(f"Fetching URL: {url}")
                driver.get(url)
                
                # Wait for the page to load and the price element to be present
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="maincontent"]/div[2]/div[1]/div/div[3]/div[3]/div[3]')))
                
                # Locate and process the price element
                i = driver.find_elements(By.XPATH, '//*[@id="maincontent"]/div[2]/div[1]/div/div[3]/div[3]/div[3]')[0]
                price_text = i.text
                price_text_raw = price_text.replace(" SAR", "")
                price_text, sep, price_before = price_text_raw.partition(' ')
                print(price_text)
                price_text = float(price_text)
                price_Dawa.append(price_text)
                break  # Break out of the retry loop on success
            
            except StaleElementReferenceException:
                retries += 1
                if retries > max_retries:
                    price_Dawa.append(None)
                    print(f"Stale element encountered for link: {url}. Max retries reached. Skipping...")
                else:
                    print(f"Stale element encountered for link: {url}. Retrying ({retries}/{max_retries})...")
            
            except NoSuchElementException:
                price_Dawa.append(None)
                print(f"No such element found for link: {url}")
                break  # No need to retry if element doesn't exist
            
            except Exception as e:
                price_Dawa.append(None)
                print(f"Error occurred: {e}")
                break  # No need to retry if another exception occurs
        
        # Add a random delay between requests
        time.sleep(random.uniform(1, 3))
    
    driver.quit()
    return price_Dawa

def scrape_prices_from_nahdi(urls):
    price_Nahdi = []
    max_retries = 2  # Maximum retries for stale elements

    # Initialize WebDriver
    options = get_chrome_options()
    service = Service()  # Using the default service; specify the path if necessary
    driver = webdriver.Firefox(service=service, options=options)
    print("ChromeDriver initialized successfully.")
    
    # Iterate over the URLs
    for url in urls:
        retries = 0
        while retries <= max_retries:
            try:
                print(f"Fetching URL: {url}")
                driver.get(url)
                
                # Wait for the page to load and the price element to be present
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'price')))
                
                # Locate and process the price element
                i = driver.find_elements(By.CLASS_NAME, 'price')[0]
                price_text = i.text
                price_text = price_text.replace(" SAR", "")
                print(price_text)
                price_text = float(price_text)
                price_Nahdi.append(price_text)
                break  # Break out of the retry loop on success
            
            except StaleElementReferenceException:
                # Handle stale element reference, and retry
                retries += 1
                if retries > max_retries:
                    price_Nahdi.append(None)
                    print(f"Stale element encountered for link: {url}. Max retries reached. Skipping...")
                else:
                    print(f"Stale element encountered for link: {url}. Retrying ({retries}/{max_retries})...")
            
            except NoSuchElementException:
                # Handle no such element exception
                price_Nahdi.append(None)
                print(f"No such element found for link: {url}")
                break  # No need to retry if element doesn't exist
            
            except Exception as e:
                # Handle any other exceptions
                price_Nahdi.append(None)
                print(f"Error occurred: {e}")
                break  # No need to retry if another exception occurs
        
        # Add a random delay between requests
        time.sleep(random.uniform(1, 3))
    
    driver.quit()
    return price_Nahdi

def scrape_prices_from_amazon(urls):
    price_Amazon = []
    Ship_Amazon = []
    Sold_Amazon = []
    max_retries = 2  # Maximum retries for stale elements

    # Initialize WebDriver
    options = get_chrome_options()
    service = Service()  # Using the default service; specify the path if necessary
    driver = webdriver.Firefox(service=service, options=options)
    print("ChromeDriver initialized successfully.")
    
    # Iterate over the URLs
    for url in urls:
        retries = 0
        while retries <= max_retries:
            try:
                print(f"Fetching URL: {url}")
                driver.get(url)
                
                # Wait for the page to load and the price element to be present
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'reinventPricePriceToPayMargin')))
                
                # Scraping logic
                if len(driver.find_elements(By.CLASS_NAME, 'reinventPricePriceToPayMargin')) > 0:
                    price_text = driver.find_element(By.CLASS_NAME, 'reinventPricePriceToPayMargin').text
                    price_text = price_text.replace("\n", ".")
                    price_text = price_text.replace("ريال", "").strip()
                    print(f"Price: {price_text}")
                    
                    ship_elements = driver.find_elements(By.CLASS_NAME, 'offer-display-feature-text-message')
                    ship_text = ship_elements[0].get_attribute("textContent") if len(ship_elements) > 0 else None
                    sold_text = ship_elements[1].get_attribute("textContent") if len(ship_elements) > 1 else None
                    
                    print(f"Shipping: {ship_text}")
                    print(f"Sold By: {sold_text}")
                    
                    price_Amazon.append(price_text)
                    Ship_Amazon.append(ship_text)
                    Sold_Amazon.append(sold_text)
                else:
                    price_Amazon.append(None)
                    Ship_Amazon.append(None)
                    Sold_Amazon.append(None)
                    print("Price not found, setting all values to None.")
                    
                break  # Break out of the retry loop on success
            
            except StaleElementReferenceException:
                retries += 1
                if retries > max_retries:
                    price_Amazon.append(None)
                    Ship_Amazon.append(None)
                    Sold_Amazon.append(None)
                    print(f"Stale element encountered for link: {url}. Max retries reached. Skipping...")
                else:
                    print(f"Stale element encountered for link: {url}. Retrying ({retries}/{max_retries})...")
            
            except NoSuchElementException:
                price_Amazon.append(None)
                Ship_Amazon.append(None)
                Sold_Amazon.append(None)
                print(f"No such element found for link: {url}")
                break  # No need to retry if element doesn't exist
            
            except Exception as e:
                price_Amazon.append(None)
                Ship_Amazon.append(None)
                Sold_Amazon.append(None)
                print(f"Error occurred: {e}")
                break  # No need to retry if another exception occurs
        
        # Add a random delay between requests
        time.sleep(random.uniform(1, 3))
    
    driver.quit()
    return price_Amazon, Ship_Amazon, Sold_Amazon

