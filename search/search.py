from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

query = input("Query: ")

def scrape_worshiptoday(query):
    base_url = "https://worshiptoday.dk/soeg"
    params = {"q": query}

    r = requests.get(base_url, params=params)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="search-result")

    if not results:
        print("No results.")
        return
    
    songs = []
    for result in results:
        header = result.find("h3", class_="results-topic")
        title = header.get_text()
        path = header.a["href"]
        url = f"https://worshiptoday.dk{path}"
        
        song = {"title": title, "url": url}
        songs.append(song)
    
    return songs

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

    songs = []
    for result in results:
        title = result.span.get_text()
        id = result.parent["ref"]
        url = f"https://lovsang.dk/song/view.php?song_id={id}"

        song = {"title": title, "url": url}
        songs.append(song)
    
    return songs

def metasearch(query):
    songs = scrape_worshiptoday(query) + scrape_lovsang(query)
    song_titles = [song["title"] for song in songs]
    scores = process.extract(query, song_titles, limit=5)

    results = []
    for title, score in scores:
        for song in songs:
            if song["title"] == title:
                song["score"] = score
                results.append(song)
                break
    
    return results