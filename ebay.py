import time
import random
import pandas as pd

from urllib.parse import urlencode
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def human_delay(a=1.5, b=3.5): # delay to mimic human behavior
    time.sleep(random.uniform(a, b))

def get_driver(): # setup selenium webdriver
    options = Options()
    options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument("--disable-blink-features=AutomationControlled")  
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def open_ebay(query:str): # open ebay and search for query
    driver = get_driver()
    driver.get("https://www.ebay.com/")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "gh-ac")))

    driver.find_element(By.ID, "gh-ac").send_keys(query)
    human_delay(2, 5)
    driver.find_element(By.ID, "gh-search-btn").click()

    return driver

def get_page(query: str, page: Optional[int] = 1, max_item: Optional[int] = 60) -> int: # construct url for specific page and max items
    payload: dict[str, str] = {
        '_nkw': query,
        '_sacat': '0',
        '_from': 'R40',
        '_ipg': max_item,
        '_pgn': page,
        'rt': 'nc'
    }
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

def paginate(driver, pages_to_scrape) -> Optional[str]: # get next page url
    if pages_to_scrape < 166:  # max 10.000 (60*166)
            for i in range(1, pages_to_scrape+1):
                print(f"Scraping page {i}...")
                if i == 1:
                    try:
                        next_page = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "pagination__item")))
                        next_page = next_page.get_attribute("href")
                        driver.get(next_page) 
                    except:
                        pass
                else:
                    try:
                        next_page = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "pagination__item")))
                        next_page = next_page[1] if len(next_page) > 1 else next_page[0]
                        next_page = next_page.get_attribute("href")
                        driver.get(next_page) 
                    except:
                        pass  
            return next_page

def main():
    query = "smartwatch"
    total_products = 0
    page = 1
    results = []

    while True:
        # Buka driver baru untuk setiap page
        driver = open_ebay(query=query)
        url = get_page(query, page, max_item=60)
        print(f"Scraping page {page}: {url}")
        driver.get(url)

        product_list = parse(driver)

        if not product_list:
            print(f"Tidak ada produk di page {page}, scraping selesai.")
            break

        print(f"Catch {len(product_list)} product in page {page}")
        total_products += len(product_list)

        for product in product_list:
            title = product["Title"].lower()
            url = product["Link"]

            if "smart" in title and "watch" in title:
                detail_driver = get_driver()
                detail = scrape_detail(detail_driver, url)

                # Gabungkan semua info jadi satu dict
                item = {
                    "Title": product["Title"],
                    "Price": product["Price"],
                    "Link": url,
                    "Detail": detail
                }
                results.append(item)

                # Print hasil
                print(f"Title  : {item['Title']}")
                print(f"Price  : {item['Price']}")
                print(f"Link   : {item['Link']}")
                print(f"Detail : {item['Detail']}")
                print("=" * 50)
            else:
                print(f"Lewati: {product['Title']}")

            human_delay(2, 5)

        page += 1
        human_delay(3, 7)

    print(f"Total products scraped: {len(results)}")
    return results

if __name__ == "__main__":
    data = main()
    df = pd.DataFrame(data)
    df.to_excel('ebay.xlsx', index=False)
    print("✅ Excel file saved: ebay.xlsx")


