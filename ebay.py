import time
import random

from ssl import Options
from urllib.parse import urlencode
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def human_delay(a=1.5, b=3.5): # delay to mimic human behavior
    time.sleep(random.uniform(a, b))

def get_driver(): # setup selenium webdriver
    options = Options()
    # options.add_argument("--headless=new")  
    driver = webdriver.Chrome(options=options)
    return driver

def open_ebay(query:str): # open ebay and search for query
    driver = get_driver()
    driver.get("https://www.ebay.com/")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "gh-ac")))

    driver.find_element(By.ID, 'gh-ac').send_keys(query)
    human_delay()
    driver.find_element(By.ID, 'gh-search-btn').click()

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".srp-results.srp-list.clearfix")))
    return driver

def get_page(driver, query: str, page: Optional[int] = 1, max_item: Optional[int] = 60) -> int: # construct url for specific page and max items
    payload: dict[str, str] = {
        '_nkw': query,
        '_sacat': '0',
        '_from': 'R40',
        '_ipg': max_item,
        '_pgn': page,
        'rt': 'nc'
    }
    if page >= 5:
        payload['rt'] = 'nc'
    try:
        if page >= 5:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".srp-river")))
    except TimeoutException:
        print("Timeout: hasil produk tidak ditemukan")
    return f"https://www.ebay.com/sch/i.html?{urlencode(payload)}"

def parse(driver)-> List[Dict]: # parse the product list from the page
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".srp-results")))
    except TimeoutException:
        print("Timeout: hasil produk tidak ditemukan")
        return []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_list = []
    products = soup.find("ul", attrs={"class":"srp-results srp-list clearfix"}).find_all('div', attrs={"class":"su-card-container su-card-container--horizontal"})
    for product in products:
        title = product.find("div", attrs={"class":"s-card__title"})

        link = product.find_all('a')
        for tautan in link:
            urls = tautan.get('href')

        price = product.find("div", attrs={"class":"s-card__attribute-row"})
        prices = price.text if price else ""
        data_dict = ({
            "Title": title.text if title else "",
            "Link": urls,
            "Price": prices,
        })
        product_list.append(data_dict)   
    return product_list

def scrape_detail(driver, url) -> Dict: # scrape product detail from product page
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tabs__content")))
    except TimeoutException:
        print(f"Timeout: detail produk tidak ditemukan di {url}")
        return {}
    
    human_delay(3, 7)

    spesific_dict = {}
    item_number = None
    # item specifics
    try:
        spesific = driver.find_element(By.CSS_SELECTOR, ".tabs__content .ux-layout-section-module-evo").text
        lines = spesific.split("\n")
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                if lines[i].lower() == "item specifics":
                    continue
                spesific_dict[lines[i].strip()] = lines[i+1].strip()
    except:
        pass
    # item number
    try:
        item_number = driver.find_element(By.CSS_SELECTOR, ".tabs__content .ux-textspans.ux-textspans--BOLD").text
    except:
        pass

    return {**spesific_dict, "Item Number": item_number}

def main(): # main function to run the scraper
    query = "smartwatch"
    driver = open_ebay(query=query)

    total_products = 0
    page = 1

    while True:
        url = get_page(driver, query, page, max_item=60)
        print(f"Scraping page {page}: {url}")
        driver.get(url)

        product = parse(driver)
        if not product:
            print(f"Tidak ada produk di page {page}, scraping selesai.")
            break
        print(f"Catch {len(product)} product in page {page}")
        total_products += len(product)

        for product in product:
            title = product["Title"].lower()
            url = product["Link"]

            if "smart" in title and "watch" in title:
                print(f"{product['Title']} | {product['Price']}")
                detail = scrape_detail(driver, url)
                print(detail)
            else:
                print(f"Lewati: {product['Title']}")
            print("="*40)

        page += 1
        human_delay(3, 7)
    print(f"Total products so far: {total_products}")

if __name__ == "__main__":
    main()


