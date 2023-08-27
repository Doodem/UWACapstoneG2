#!/usr/bin/env python

import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from tqdm import tqdm
import argparse

# generate mock data set to test
ref_nums = [str(i) for i in range(100)]
links = ["http://localhost:8000/" + str(i) for i in ref_nums]
Tenders = pd.DataFrame({"Reference Number": ref_nums, "TenderLink": links})

CleanTenders = Tenders[["Reference Number", "TenderLink"]].dropna(subset=["TenderLink"]).drop_duplicates()
TenderDict = dict(zip(CleanTenders["Reference Number"], CleanTenders["TenderLink"]))
ProTenders = {key: value for key, value in TenderDict.items() if "qas" not in value}

LOG_FILENAME = 'error_logs.txt'
logging.basicConfig(filename=LOG_FILENAME)

BUTTON_LOCATORS  = {
    "Download Now": By.LINK_TEXT,
    "Download for Information Only": By.XPATH,
    "Download Documents": By.XPATH
}

CUSTOM_USER_AGENT  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"

def download_multiple_tenders(max_workers, tender_dict, path):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []        
        for ref, link in tender_dict.items():
            future = executor.submit(download_tender, link, ref, path)
            futures.append(future)
            
        with tqdm(total=len(futures), desc="Downloading Tenders", colour='green') as pbar:
            for future in futures:
                future.result()
                pbar.update(1)
    
def download_tender(link, ref, path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={CUSTOM_USER_AGENT }")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"download.default_directory": path}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    open_link(driver, link, ref)
    
    # wait for button to be clickable
    wait = WebDriverWait(driver, 10)

    buttons = ["Download Now", "Download for Information Only", "Download Documents"]
    for button in buttons:
        if not click_button(driver, wait, button, ref):
            driver.quit()
            break
        
    # Wait for downloads to complete
    time.sleep(15)
    driver.quit()

def open_link(driver, link, ref):
    while True:
        try:
            driver.get(link)
        except Exception as e:
            error_message = f"Error: {ref}, {e}"
            logging.error(error_message)
            driver.quit()
            break
        return
    
def click_button(driver, wait, button_text, ref):
    
    locator = BUTTON_LOCATORS[button_text]
    if locator == "xpath":
        button_text = f"//input[@value='{button_text}']"
    
    try:
        button = wait.until(EC.element_to_be_clickable((locator, button_text)))
        button.click()
    except Exception as e:
        error_message = f"Error: {ref}, {e}"
        logging.error(error_message)
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Download Tenders")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of worker threads")
    parser.add_argument("--path", type=str, default="./downloads", help="Path to save downloaded files")
    args = parser.parse_args()

    download_multiple_tenders(args.max_workers, ProTenders, args.path)

if __name__ == "__main__":
    main()
    
# how to run
# python downloadtenders.py --max_workers 10 --path /path/to/save/downloads
