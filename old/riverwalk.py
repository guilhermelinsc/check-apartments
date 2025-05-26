from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

URL = "https://cortland.com/apartments/cortland-lakecrest/available-apartments/?floorplan=8119"
CHECK_INTERVAL = 86400  # Every 24 hours

def check_availability():
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        )

        driver = webdriver.Chrome(options=options)
        driver.get(URL)

        # Wait until apartment count is present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "filter-results-count"))
        )

        # Get apartment count
        count_element = driver.find_element(By.ID, "filter-results-count")
        count = count_element.text.strip()
        print(f"[{datetime.now()}] Available apartments: {count}")

        # Wait until apartment list loads
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "apartments__card-link"))
        )

        apartment_links = driver.find_elements(By.CLASS_NAME, "apartments__card-link")
        apartment_numbers = [
            link.text.strip() for link in apartment_links if link.text.strip().startswith("Apt #")
        ]

        print(f"Found {len(apartment_numbers)} available units")
        print("Available Units:")
        for number in apartment_numbers:
            print(f" - {number}")

        return int(count)

    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        return None

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)
