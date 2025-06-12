from bs4 import BeautifulSoup
from selenium import webdriver
import os
import pathlib
import requests

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

scrape_worshiptoday(query)