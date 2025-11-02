# main.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time, random

def scrape_uber_data():
    print("🚀 Starting Uber scraper...")

    # --- Step 1: Launch undetected Chrome ---
    driver = uc.Chrome()
    driver.get('https://www.uber.com/global/en/price-estimate/')
    driver.refresh()
    time.sleep(5)

    # --- Step 2: Log in to Uber using Google ---
    try:
        login_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Log in')]")
        login_button.click()
        time.sleep(3)

        google_button = driver.find_element(By.XPATH, "//*[@id='google-login-btn']/div/div[2]/div/div[2]/p")
        google_button.click()
        time.sleep(3)

        print("Clicked 'Continue with Google'...")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        email_field = driver.find_element(By.ID, 'identifierId')
        email_field.send_keys('muralboss@gmail.com')
        time.sleep(2)
        driver.find_element(By.ID, 'identifierNext').click()
        time.sleep(3)

        password_field = driver.find_element(By.NAME, 'Passwd')
        password_field.send_keys('murali1994')
        time.sleep(2)
        driver.find_element(By.ID, 'passwordNext').click()
        time.sleep(10)

        driver.switch_to.window(driver.window_handles[0])
        print('✅ Logged in successfully! Page title:', driver.title)
    except Exception as e:
        print("⚠️ Login failed:", e)
        driver.quit()
        return

    wait = WebDriverWait(driver, 25)  # increased to handle delays

    # --- Step 3: Define locations ---
    locations = [
        "kempegowda international airport bengaluru",
        "Jayanagar",
        "Whitefield",
        "Indira Nagar",
        "Hebbal"
    ]

    # --- Step 4: Generate all source-destination pairs ---
    all_pairs = [(src, dest) for src in locations for dest in locations if src != dest]
    random.shuffle(all_pairs)
    print(f"🔁 Total routes to scrape: {len(all_pairs)}")

    # --- Step 5: Initialize results list ---
    records = []

    # --- Step 6: Scrape each pair ---
    for i, (source, destination) in enumerate(all_pairs, start=1):
        print(f"\n🛣️ Route {i}: {source} → {destination}")

        try:
            # Enter Pickup
            pickup_label = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(., 'Pickup location')]")
            ))
            pickup_input = pickup_label.find_element(By.XPATH, ".//following::input[1]")
            pickup_input.send_keys(source)
            time.sleep(2)
            pickup_input.send_keys(Keys.RETURN)

            # Enter Dropoff
            drop_label = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(., 'Dropoff location')]")
            ))
            drop_input = drop_label.find_element(By.XPATH, ".//following::input[1]")
            drop_input.send_keys(destination)
            time.sleep(3)
            drop_input.send_keys(Keys.RETURN)
            time.sleep(2)

            # Click 'See prices'
            see_prices_btn = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "See prices"))
            )
            see_prices_btn.click()
            print("Clicked 'See prices'... waiting for results.")

            # --- Smart wait for rides ---
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Uber Go') or contains(text(), 'Go Non AC')]")
                    )
                )
            except:
                print(f"⚠️ Rides not loaded for {source} → {destination}. Skipping...")
                driver.back()
                continue

            time.sleep(4)  # let rides stabilize

            # --- Extract rides info ---
            ride_elements = driver.find_elements(
                By.XPATH, "//*[contains(text(), 'Uber Go') or contains(text(), 'Go Non AC')]/ancestor::div[3]"
            )

            for ride in ride_elements:
                full_text = ride.text.split('\n')

                car_name = next((x for x in full_text if 'Uber Go' in x or 'Go Non AC' in x), 'N/A')
                price = next((x for x in full_text if '₹' in x), 'N/A')
                eta = next((x for x in full_text if 'away' in x), 'N/A')
                duration = next((x for x in full_text if re.match(r'\d{2}:\d{2}', x)), 'N/A')

                records.append({
                    "Source": source,
                    "Destination": destination,
                    "Car_Type": car_name,
                    "ETA": eta,
                    "Trip_Duration": duration,
                    "Price": price,
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            print(f"✅ Scraped {len(ride_elements)} rides for this route.")
            driver.back()
            time.sleep(5)

        except Exception as e:
            print(f"❌ Error on {source} → {destination}: {e}")
            continue

    # --- Step 7: Save data ---
    if records:
        df = pd.DataFrame(records)
        # --- Save everything into one master CSV ---
        csv_file = "uber_price_data_master.csv"

        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_existing, df], ignore_index=True)
            df_combined.to_csv(csv_file, index=False)
            print(f"✅ Appended {len(df)} new records to master file: {csv_file}")
        else:
            df.to_csv(csv_file, index=False)
            print(f"🆕 Created new master file: {csv_file} with {len(df)} records")

        print("💾 All data saved to single master file successfully.")
    else:
        print("⚠️ No data collected this run.")

    # --- Step 8: Close driver ---
    driver.quit()
    print("✅ Browser closed. Scraping completed.")


# main function to call the scrape_uber_data function
def main():
    scrape_uber_data()  # call the function

# run the main function if the script is run directly 
if __name__ == "__main__":
    main()






