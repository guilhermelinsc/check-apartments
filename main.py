from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.cloud import storage
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json


URL = "https://cortland.com/apartments/cortland-lakecrest/available-apartments/?floorplan=8119"
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BLOB_NAME = "last_apartments.json"

app = Flask(__name__)

def fetch_available_apartments():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    )
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "apartments__card-link"))
    )

    apartment_links = driver.find_elements(By.CLASS_NAME, "apartments__card-link")
    apartment_numbers = [
        link.text.strip().replace("Apt #", "") for link in apartment_links if link.text.strip().startswith("Apt #")
    ]

    driver.quit()
    return apartment_numbers

def get_previous_apartments():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "modular-rex-454820-v2")
    client = storage.Client(project=project_id)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)

    if blob.exists():
        data = blob.download_as_text()
        return json.loads(data)
    return []

def save_current_apartments(apartment_list):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    blob.upload_from_string(json.dumps(apartment_list))

def notify_user(new_apartments):
    # Replace with email/webhook integration if desired
    print(f"🟢 New apartments found: {new_apartments}")

@app.route("/", methods=["GET"])
def check():
    current = fetch_available_apartments()
    previous = get_previous_apartments()

    new_apartments = list(set(current) - set(previous))

    if new_apartments:
        notify_user(new_apartments)
        save_current_apartments(current)

    florida_time = datetime.now(ZoneInfo("America/New_York"))
    formatted_time = florida_time.strftime("%B %d, %Y %I:%M %p %Z")

    return jsonify({
        "timestamp": formatted_time,
        "found": len(current),
        "new_apartments": new_apartments,
        "all_apartments": current
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))