import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md  # Convert HTML to Markdown
from tqdm import tqdm

# Constants
CONTROL_FILE = "control_index.json"
# Array of URLs to avoid crawling
SKIP_URLS = {"https://faker.readthedocs.io/en/master/genindex.html"}

# Custom headers to mimic a real browser, this will avoid being blocked.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}


def clear_terminal():
    """
    Helps visibility on the terminal, to avoid clutter CLI outputs.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def print_control_status(control_index):
    """Gives status of the scraper in real-time"""
    clear_terminal()
    header = "=== Scraper Control Status ==="
    print(header)
    for i, (page, status) in enumerate(control_index.items(), 1):
        print(f"{i:3}. {page} : {status}")
    print("=" * len(header))
    print()  # Blank line


def generate_filename(url):
    """ Generate a safe filename from the URL path"""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "index"
    return path + ".md"


def crawl_index(url, domain, visited):
    """Recursively crawl the website to collect page URLs."""
    if url in visited:
        return set()
    visited.add(url)
    urls = set()
    if url not in SKIP_URLS:
        urls.add(url)
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return urls
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return urls

    soup = BeautifulSoup(response.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        link = a['href']
        abs_link = urljoin(url, link)
        # Only consider links within the same domain and skip if in SKIP_URLS
        if domain in urlparse(abs_link).netloc and abs_link not in SKIP_URLS:
            urls |= crawl_index(abs_link, domain, visited)
    return urls


def create_control_index(base_url, domain):
    print("Creating control index. This may take a while...")
    visited = set()
    all_urls = crawl_index(base_url, domain, visited)
    control_index = {url: "PENDING" for url in all_urls}
    with open(CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(control_index, f, indent=4)
    return control_index


def load_control_index():
    if os.path.exists(CONTROL_FILE):
        with open(CONTROL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def update_control_index(control_index):
    with open(CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(control_index, f, indent=4)


def create_control_index_from_genindex(index_url, domain):
    print("Creating control index from genindex page...")
    try:
        response = requests.get(index_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to retrieve index page: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error retrieving index page: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    urls = set()
    for a in soup.find_all('a', href=True):
        link = a['href']
        abs_link = urljoin(index_url, link)
        if domain in urlparse(abs_link).netloc:
            if abs_link == index_url:
                continue
            urls.add(abs_link)
    control_index = {url: "PENDING" for url in urls}
    with open(CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(control_index, f, indent=4)
    return control_index


def scrape_page(url, output_folder, control_index):
    # Skip if already processed
    if control_index.get(url) == "DONE":
        return
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}: {response.status_code}")
            return
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return

    # Convert the page HTML to Markdown
    markdown_content = md(response.text)
    filename = generate_filename(url)
    file_path = os.path.join(output_folder, filename)

    # Write only if file doesn't exist or is not marked DONE
    if not os.path.exists(file_path) or control_index.get(url) != "DONE":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"## Documentation from {url}\n\n")
            f.write(markdown_content)

    # Mark the page as DONE and update the control file
    control_index[url] = "DONE"
    update_control_index(control_index)


if __name__ == "__main__":
    # TODO: make it as a parameter for user's input
    base_url = "https://faker.readthedocs.io/en/master/providers.html"
    genindex_url = "https://faker.readthedocs.io/en/master/genindex.html"
    domain = "faker.readthedocs.io"

    # Create output folder with a datetime stamp (e.g., faker_20230331_235959)
    folder_name = "faker_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(folder_name, exist_ok=True)

    # Load or create the control index using the genindex page
    control_index = load_control_index()
    if not control_index:
        control_index = create_control_index_from_genindex(genindex_url, domain)

    # Remove any SKIP_URLS from the control index if present
    for skip_url in SKIP_URLS:
        control_index.pop(skip_url, None)
    update_control_index(control_index)

    print_control_status(control_index)

    # Process pages that are still pending
    pending_urls = [url for url, status in control_index.items() if status != "DONE"]
    for url in tqdm(pending_urls, desc="Scraping pages"):
        scrape_page(url, folder_name, control_index)
        print_control_status(control_index)
        time.sleep(0.5)  # Polite delay

    print(f"Scraping complete. Markdown files saved in folder '{folder_name}'.")
