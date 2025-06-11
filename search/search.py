import requests
from bs4 import BeautifulSoup

query = input("Query: ")

def scrape_worshiptoday(query):
    base_url = "https://worshiptoday.dk/soeg"
    params = {'q': query}

    try:
        # Send HTTP request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result items
        results = soup.find_all('div', class_='list-group-item search-result results-entry')
        
        if not results:
            print("No results found.")
            return
        
        # Process and display each result
        for i, result in enumerate(results, 1):
            # Extract title and URL
            title_tag = result.find('h3', class_='results-topic').find('a')
            title = title_tag.get_text(strip=True)
            url = title_tag['href']
            
            # Extract emneord (tags)
            emneord = []
            emneord_container = result.find('b', class_='emneord')
            if emneord_container:
                for a_tag in emneord_container.find_next_siblings('a'):
                    emneord.append(a_tag.get_text(strip=True))
            
            # Extract score if available
            score = result.get('data-document-score', 'N/A')
            
            # Print formatted result
            print(f"\nResult {i}:")
            print(f"Title: {title}")
            print(f"URL: https://worshiptoday.dk{url}")
            print(f"Score: {score}")
            if emneord:
                print("Tags:", ", ".join(emneord))
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")

scrape_worshiptoday(query)