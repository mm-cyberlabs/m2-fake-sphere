import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md  # Convert HTML to Markdown
from tqdm import tqdm
import re  # For cleaning markdown content

# Constants
CONTROL_FILE = "control_index.json"
SKIP_URLS = {"https://faker.readthedocs.io/en/master/genindex.html"}

# Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}


def clean_markdown(md_text):
    """
    Clean markdown content by removing header blocks, table of contents,
    footer lines, specific navigation elements, and extraneous characters like '¶'.
    """
    # Remove header blocks (lines starting with '#' at the beginning)
    md_text = re.sub(r'^(?:#.*\n)+\n', '', md_text)
    # Remove sections containing "Table of Contents" or "Navigation"
    md_text = re.sub(r'(?im)^.*(Table of Contents|Navigation).*\n(?:.*\n)+?(?=\n)', '', md_text)
    # Remove footer lines that might start with ©
    md_text = re.sub(r'(?im)^©.*\n', '', md_text)

    # Remove specific navigation elements
    navigation_patterns = [
        r'^(Previous topic\s*$)',
        r'^(Locale en_NZ\s*$)',
        r'^(Next topic\s*$)',
        r'^(Locale en_PK\s*$)',
        r'^(This Page\s*$)',
        r'^(Show Source\s*$)',
        r'^(Quick search\s*$)',
        r'^(Created using Sphinx.*$)',
    ]
    for pattern in navigation_patterns:
        md_text = re.sub(pattern, '', md_text, flags=re.MULTILINE)

    # Remove extraneous pilcrow characters '¶'
    md_text = md_text.replace("¶", "")

    return md_text


def generate_filename(url):
    """Generate a safe filename from the URL path."""
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
        if domain in urlparse(abs_link).netloc and abs_link != index_url:
            urls.add(abs_link)
    control_index = {url: "PENDING" for url in urls}
    with open(CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(control_index, f, indent=4)
    return control_index


def scrape_page(url, output_folder, control_index):
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

    # Convert HTML to Markdown and clean the content
    markdown_content = md(response.text)
    markdown_content = clean_markdown(markdown_content)

    filename = generate_filename(url)
    file_path = os.path.join(output_folder, filename)

    if not os.path.exists(file_path) or control_index.get(url) != "DONE":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"## Documentation from {url}\n\n")
            f.write(markdown_content)

    control_index[url] = "DONE"
    update_control_index(control_index)


if __name__ == "__main__":
    base_url = "https://faker.readthedocs.io/en/master/providers.html"
    genindex_url = "https://faker.readthedocs.io/en/master/genindex.html"
    domain = "faker.readthedocs.io"

    folder_name = "faker_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(folder_name, exist_ok=True)

    control_index = load_control_index()
    if not control_index:
        control_index = create_control_index_from_genindex(genindex_url, domain)

    for skip_url in SKIP_URLS:
        control_index.pop(skip_url, None)
    update_control_index(control_index)

    # Only the tqdm progress bar is shown
    pending_urls = [url for url, status in control_index.items() if status != "DONE"]
    for url in tqdm(pending_urls, desc="Scraping pages"):
        scrape_page(url, folder_name, control_index)
        time.sleep(0.5)  # Polite delay

    print(f"Scraping complete. Markdown files saved in folder '{folder_name}'.")
