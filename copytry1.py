import os
import requests
from bs4 import BeautifulSoup
import cloudscraper
from urllib.parse import urljoin
from googletrans import Translator
import time

# Function to create chunks of text for translation
def create_chunks(corpus):
    chunks = [corpus[i:i + 5000] for i in range(0, len(corpus), 5000)]
    return chunks

# Set target language
target_lang = 'hi'

# Target URL
target_url = "https://www.classcentral.com/"

# Create scraper object
scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

# Scrape the main page
html_main = scraper.get(target_url).content

# Create BeautifulSoup object for the main page
soup_main = BeautifulSoup(html_main, 'html.parser')

# Modify links on the main page to use absolute URLs
for link in soup_main.find_all('a'):
    if link.has_attr('href'):
        link['href'] = urljoin(target_url, link['href'])

# Find all links on the main page
links_main = soup_main.find_all('a')

# Create an empty list to store the URLs of the pages to scrape
urls = [target_url]

# Iterate through the links and extract the href attribute
for link in links_main:
    href = link.get('href')
    if href is not None and target_url in href:
        urls.append(href)

# Translate and save the pages
for url in urls:
    # Set filename
    if url == target_url:
        filename = "index.html"
    else:
        filename = url.strip('/').split('/')[-1] + ".html"

    # Check if file already exists
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Skipping translation...")
        continue

    # Get HTML content
    html = scraper.get(url).content

    # Create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    # Modify links to use absolute URLs
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            link['href'] = urljoin(url, link['href'])

    # Translate text content
    translator = Translator()
    for tag in soup.find_all(True):
        if tag.string is not None and tag.name != 'style':
            text = tag.string.strip()
            original_chunks = create_chunks(text)
            results_list = []
            for i in original_chunks:
                r = translator.translate(i, dest=target_lang, src='en',)
                time.sleep(1)
                results_list.append(r.text)
            translated_text = "".join(results_list)
            tag.string.replace_with(translated_text)
            tag.contents[0].replace_with(translated_text)

    # Save translated HTML content
    with open(filename, 'w') as f:
        f.write(soup.prettify())

    print(f"Translated and saved {filename}")
