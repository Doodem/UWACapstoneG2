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

LOG_FILENAME = 'error_logs.txt'
logging.basicConfig(filename=LOG_FILENAME)

BUTTON_LOCATORS  = {
    "Download Now": By.LINK_TEXT,
    "Download for Information Only": By.XPATH,
    "Download Documents": By.XPATH
}

CUSTOM_USER_AGENT  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"

def batch_request_tenders(max_workers, batch_size, batch_interval, tender_dict, path):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        total_batches = len(tender_dict) // batch_size + (1 if len(tender_dict) % batch_size > 0 else 0)
        
        with tqdm(total=total_batches, desc="Downloading Batches", colour='green') as pbar:
            for i in range(0, len(tender_dict), batch_size):
                batch_tenders = list(tender_dict.items())[i:i+batch_size]
                futures = []
                
                for ref, link in batch_tenders:
                    future = executor.submit(download_tender, link, ref, path)
                    futures.append(future)
      
                pbar.update(1)
                
                if batch_interval > 0 and i + batch_size < len(tender_dict):
                    time.sleep(batch_interval)

def log_error(ref, e):
    error_message = f"Error: {ref}, {e}"
    logging.error(error_message)
    
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
    
    wait = WebDriverWait(driver, 10)
    buttons = ["Download Now", "Download for Information Only", "Download Documents"]
    for button in buttons:
        click_button(driver, wait, button, ref)
            
    # Wait for downloads to complete
    time.sleep(20)
    driver.quit()

def open_link(driver, link, ref):
    while True:
        try:
            driver.get(link)
        except Exception as e:
            log_error(ref, e)
            driver.quit()
            break
        return
    
def click_button(driver, wait, button_text, ref):
    
    locator = BUTTON_LOCATORS[button_text]
    if locator == "xpath":
        button_text = f"//input[@value='{button_text}']"
    
    while True:
        try:
            button = wait.until(EC.element_to_be_clickable((locator, button_text)))
            button.click()
        except Exception as e:
            log_error(ref, e)
            driver.quit()
            break
        return

def log_error(ref, e):
    error_message = f"Error: {ref}, {e}"
    logging.error(error_message)
    
def main():
    parser = argparse.ArgumentParser(description="Download Tenders")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of worker threads")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of requests per batch")
    parser.add_argument("--batch_interval", type=int, default=10, help="Time inbetween batch requests")
    parser.add_argument("--path", type=str, default="./downloads", help="Path to save downloaded files")
    parser.add_argument("--file", type=str, help="File to read from")
    args = parser.parse_args()

    Tenders = pd.read_excel(args.file)
    CleanTenders = Tenders[["Reference Number", "TenderLink"]].dropna(subset=["TenderLink"]).drop_duplicates()
    TenderDict = dict(zip(CleanTenders["Reference Number"], CleanTenders["TenderLink"]))
    ProTenders = {key: value for key, value in TenderDict.items() if "qas" not in value}

    batch_request_tenders(args.max_workers, args.batch_size, args.batch_interval, ProTenders, args.path)

if __name__ == "__main__":
    main()
    
# how to run
# python downloadtenders.py --max_workers 10 --batch_size 5 --batch_interval 10 --path /path/to/save/downloads --file /path/to/data/file
# /home/ucc/doodem/Documents/git/UWACapstoneG2/data/UpdatedTenders.xlsx
