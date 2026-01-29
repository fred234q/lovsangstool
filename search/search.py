SELENIUM_ENABLED = True

from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from thefuzz import process
import asyncio
from playwright.sync_api import sync_playwright

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
    # Add headers to avoid getting flagged
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.get(
        f"https://lovsang.dk/sange_xhr.php?sEcho=5&iColumns=1&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&sSearch_0={query} __lang__&bRegex_0=false&bSearchable_0=true&sSearch=&bRegex=false&order_by=title&order_direction=ASC&_=1750808394764",
        headers=headers
        )

    request_data = r.json()["aaData"]

    html_data = ""
    for request_data_point in request_data:
        html_data += f"{request_data_point[0]}\n"

    soup = BeautifulSoup(html_data, "html.parser")

    results = soup.find_all("div")

    songs = []
    for result in results:
        title = result["title"]
        id = result["ref"]
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

    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.get(base_url, headers=headers)


    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="entry-title")

    songs = []
    for result in results:
        title = result.a.get_text()
        url = result.a["href"]

        song = {"title": title, "url": url, "source": "TFK Media"}
        songs.append(song)

    return songs

def scrape_worshiptogether(query):
    session = HTMLSession()
    r = session.get(f"https://www.worshiptogether.com/search-results/#?cludoquery={query}&cludoCategory=Songs&cludopage=1&cludoinputtype=standard")
    asyncio.set_event_loop(asyncio.new_event_loop())
    r.html.render(sleep=1, timeout=20)
    results_div = r.html.find('#search-results', first=True)
    soup = BeautifulSoup(results_div.html, "html.parser")

    results = soup.find_all(class_="search-results-item")
    
    songs = []
    for result in results:
        title = result.a["title"]
        url = result.a["href"]

        song = {"title": title, "url": url, "source": "Worship Togther"}
        songs.append(song)
    
    return songs


def metasearch(query):
    songs = scrape_worshiptoday(query) + scrape_lovsang(query) + scrape_nodebasen(query) + scrape_tfkmedia(query) + scrape_stillestunder()
    # if SELENIUM_ENABLED:
    #     songs += scrape_worshiptogether(query)
    song_titles = [song["title"] for song in songs]
    scores = process.extract(query, song_titles, limit=len(song_titles))

    results = []
    for title, score in scores:
        for song in songs:
            if song in results:
                continue
            if song["title"] == title:
                song["score"] = score
                results.append(song)
    
    return results

# Scrapes all songs from all sites
def scrape_all():
    # Headers used by some requests when necessary
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    # Scrape WorshipToday
    r = requests.get("https://worshiptoday.dk/lovsange")
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all(class_="col-md-3")
    
    songs = []
    for result in results:

        song_details = result.a.find(class_="thumbnail").ul.find_all("li")
        title = song_details[0].get_text()
        path = result.a["href"]
        url = f"https://worshiptoday.dk{path}"

        song = {"title": title, "url": url, "source": "WorshipToday"}
        songs.append(song)

    # Scrape lovsang.dk
    index = 0
    while True:
        r = requests.get(
            f"https://lovsang.dk/sange_xhr.php?sEcho=6&iColumns=1&sColumns=&iDisplayStart={index}&iDisplayLength=10&mDataProp_0=0&sSearch_0=du sagde __lang__&bRegex_0=false&bSearchable_0=true&sSearch=&bRegex=false&order_by=title&order_direction=ASC&_=1762644971686",
            headers=headers
            )
        
        request_data = r.json()["aaData"]

        html_data = ""
        for request_data_point in request_data:
            html_data += f"{request_data_point[0]}\n"

        soup = BeautifulSoup(html_data, "html.parser")

        results = soup.find_all("div")

        if len(results) == 0:
            break

        for result in results:
            title = result["title"]
            id = result["ref"]
            url = f"https://lovsang.dk/song/view.php?song_id={id}"

            song = {"title": title, "url": url, "source": "lovsang.dk"}
            songs.append(song)
        
        index += 10

    # Scrape Stille Stunder
    songs += scrape_stillestunder()

    # Scrape Nodebasen
    page = 1
    while True:
        base_url = f"https://nodebasen.dk/page/{page}/?id=169&post_type=product"

        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.find_all("h3", class_="t-entry-title h3 font-weight-500 title-scale")
        # Remove duplicates
        results = results[:len(results) // 2]

        if len(results) == 0:
            break

        for result in results:
            title = result.a.get_text()
            url = result.a["href"]

            song = {"title": title, "url": url, "source": "nodebasen.dk"}
            songs.append(song)
        
        page += 1

    # Scrape TFK Media
    total_categories = 16
    for i in range(0, total_categories):
        page = 1
        while True:
            base_url = f"https://tfkmedia.dk/?paged={page}&cat={i}"

            r = requests.get(base_url, headers=headers)


            soup = BeautifulSoup(r.text, "html.parser")

            results = soup.find_all(class_="entry-title")

            if len(results) == 0:
                break

            for result in results:
                title = result.a.get_text()
                url = result.a["href"]

                song = {"title": title, "url": url, "source": "TFK Media"}
                songs.append(song)
            
            page += 1
    
    # Scrape Worship Together
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            f"https://www.worshiptogether.com/search-results/#?cludoquery=Songs&cludoCategory=Songs&cludopage=1"
        )
        i = 0
        while True:
            i += 1
            print(i)

            page.wait_for_selector(".search-results-item", timeout=10000)

            soup = BeautifulSoup(page.content(), "html.parser")
            results = soup.select(".search-results-item")

            if not results:
                break

            for result in results:
                a = result.find("a")
                print(a["title"])
                songs.append({
                    "title": a["title"],
                    "url": a["href"],
                    "source": "Worship Together",
                })

            # Try to go to next page
            next_button = page.query_selector("li.next")

            if not next_button or "disabled" in next_button.get_attribute("class"):
                break

            next_button.click()

            # IMPORTANT: wait for NEW results, not the same DOM
            page.wait_for_function(
                "document.querySelectorAll('.search-results-item').length > 0"
            )

        browser.close()

    # Return songs
    return songs