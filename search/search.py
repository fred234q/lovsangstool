from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests
import time

query = input("Query: ")

def scrape_worshiptoday(query):
    base_url = "https://worshiptoday.dk/soeg"
    params = {"q": query}

    r = requests.get(base_url, params=params)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="search-result")

    if not results:
        return
    
    for result in results:
        title = result.find("h3", class_="results-topic")
        result.title = title
        link = title.a["href"]
        result.link = "https://worshiptoday.dk" + link
    
    return results

def scrape_lovsang(query):
    url = "https://lovsang.dk/sange.php?all"

    # https://stackoverflow.com/a/60627463
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Close pop-ups
    driver.find_element(By.CSS_SELECTOR, "button.fc-button").click()
    driver.find_element(By.CSS_SELECTOR, "button.button").click()
    
    # Input search query in input field
    input_field = driver.find_element(By.ID, "title_filter")
    input_field.send_keys(query)
    # Wait for search results to update
    time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()

    results = soup.find_all(class_="songinfo")

    for result in results:
        result.title = result.span.get_text()
        id = result.parent["ref"]
        result.link = "https://lovsang.dk/song/view.php?song_id=" + id