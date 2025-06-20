from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests
import time
from fuzzywuzzy import process
from django.core.files import File
from django.core.files.storage import default_storage
import os
from django.conf import settings
from pychordpro import Song

def scrape_worshiptoday(query):
    base_url = "https://worshiptoday.dk/soeg"
    params = {"q": query}

    r = requests.get(base_url, params=params)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="search-result")
    
    songs = []
    for result in results:
        header = result.find("h3", class_="results-topic")
        title = header.get_text()
        path = header.a["href"]
        url = f"https://worshiptoday.dk{path}"
        
        song = {"title": title, "url": url, "source": "WorshipToday"}
        songs.append(song)
    
    return songs

def scrape_lovsang(query):
    base_url = "https://lovsang.dk/sange.php?all"

    # https://stackoverflow.com/a/60627463
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

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

        song = {"title": title, "url": url, "source": "lovsang.dk"}
        songs.append(song)
    
    return songs

def scrape_stillestunder():
    base_url = "https://www.stillestunder.com/tekst-og-akkorder"

    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="sqs-block html-block sqs-block-html")
    results = results[1:len(results) - 1]
    
    urls = soup.find_all(class_="sqs-block-button-element--medium sqs-button-element--primary sqs-block-button-element")

    songs = []
    for result, url in zip(results, urls):
        title = result.div.div.h1.get_text()
        path = url["href"]
        if not path:
            continue
        song_url = f"https://www.stillestunder.com{path}"
        song = {"title": title, "url": song_url, "source": "Stille Stunder"}
        songs.append(song)
    
    return songs

def scrape_nodebasen(query):
    base_url = f"https://nodebasen.dk/?s={query}&id=169&post_type=product"

    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all("h3", class_="t-entry-title h3 font-weight-500 title-scale")
    # Remove duplicates
    results = results[:len(results) // 2]

    songs = []
    for result in results:
        title = result.a.get_text()
        url = result.a["href"]

        song = {"title": title, "url": url, "source": "nodebasen.dk"}
        songs.append(song)

    return songs

def scrape_tfkmedia(query):
    base_url = f"https://tfkmedia.dk/?s={query}"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()

    results = soup.find_all(class_="entry-title")

    songs = []
    for result in results:
        title = result.a.get_text()
        url = result.a["href"]

        song = {"title": title, "url": url, "source": "TFK Media"}
        songs.append(song)

    return songs

def metasearch(query):
    songs = scrape_worshiptoday(query) + scrape_lovsang(query) + scrape_stillestunder() + scrape_nodebasen(query) + scrape_tfkmedia(query)
    song_titles = [song["title"] for song in songs]
    scores = process.extract(query, song_titles, limit=10)

    results = []
    for title, score in scores:
        for song in songs:
            if song in results:
                continue
            if song["title"] == title:
                song["score"] = score
                results.append(song)
    
    return results

def scrape_song(song):
    source = song["source"]
    url = song["url"]

    if source == "Worship Today":
        url_cutoff = len("https://worshiptoday.dk/lovsange/")
        path = url[url_cutoff:len(url) - 1]
        chordpro_url = f"https://worshiptoday.dk/lovsange/download/{path}.cho"

        r = requests.get(chordpro_url)
        filename = f"{path}.chordpro"
        with open(filename, "wb") as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        
        song = Song(filename=filename, notes="")
        song.lyrics_only()
        song.encoding("utf-8")
        song.compile()
        


# scrape_song({"source": "Worship Today", "url": "https://worshiptoday.dk/lovsange/aere-vaere-du-guds-lam-david-skarsholm/"})
        