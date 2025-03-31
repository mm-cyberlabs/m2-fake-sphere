import os
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md  # Convert HTML to Markdown
from tqdm import tqdm  # Progress bar library

# Global dictionary to hold page URLs and their status (PENDING/DONE)
pages_status = {}


def clear_terminal():
    # Clear the terminal output based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')


def print_pages_status():
    # Clear terminal before printing updated status
    clear_terminal()
    header = "=== Scraper Status ==="
    print(header)
    for i, (page, status) in enumerate(pages_status.items(), 1):
        print(f"{i:3}. {page} : {status}")
    print("=" * len(header))
    print()  # Blank line


visited = set()  # Track visited URLs to avoid repeats
pbar = tqdm(desc='Pages scraped', unit='page')  # Initialize progress bar

# Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}


def scrape(url, domain):
    # Add URL to the tracking dictionary if new
    if url not in pages_status:
        pages_status[url] = "PENDING"
        print_pages_status()  # Display updated statuses
    if url in visited:
        return
    visited.add(url)
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}: Status code {response.status_code}")
            return
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return

    pbar.update(1)  # Update progress bar

    # Convert the full HTML response to Markdown
    markdown_content = md(response.text)

    # Append the Markdown content to the output file
    with open("documentation.md", "a", encoding="utf-8") as f:
        f.write(f"## Documentation from {url}\n\n")
        f.write(markdown_content)
        f.write("\n\n---\n\n")

    # Recursively scrape internal links within the same domain
    soup = BeautifulSoup(response.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        link = a['href']
        abs_link = urljoin(url, link)
        if domain in urlparse(abs_link).netloc:
            scrape(abs_link, domain)
            time.sleep(0.5)  # Polite delay between requests

    pages_status[url] = "DONE"
    print_pages_status()  # Refresh status display
    return


if __name__ == "__main__":
    base_url = "https://faker.readthedocs.io/en/master/providers.html"
    domain = "faker.readthedocs.io"

    # Overwrite the Markdown output file at the start
    with open("documentation.md", "w", encoding="utf-8") as f:
        pass

    scrape(base_url, domain)
    pbar.close()  # Close the progress bar
    print("Full documentation saved to documentation.md")
