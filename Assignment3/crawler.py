#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: crawler.py
# SPECIFICATION: This program is a web crawler that retrieves HTML pages from a website and stores them in a MongoDB database. The crawler will stop when it finds a target page.
# TIME SPENT: 4.5 hours
#-----------------------------------------------------------*/
import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pymongo
from collections import deque

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawler_db"]
collection = db["pages"]

# Global Variables
START_URL = "https://www.cpp.edu/sci/computer-science/"
TARGET_HEADING = '<h1 class="cpp-h1">Permanent Faculty</h1>'
TARGET_URL = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"

# Frontier Class
class Frontier:
    def __init__(self):
        self.queue = deque([START_URL])
        self.visited = set()

    def nextURL(self):
        return self.queue.popleft()

    def addURL(self, url):
        if url not in self.visited:
            self.queue.append(url)

    def done(self):
        return len(self.queue) == 0

    def mark_visited(self, url):
        self.visited.add(url)

# Function to retrieve HTML
def retrieveHTML(url):
    try:
        with urllib.request.urlopen(url) as response:
            if 'html' in response.info().get_content_type():
                return response.read()
    except Exception as e:
        print(f"Failed to retrieve {url}: {e}")
    return None

# Function to store HTML in MongoDB
def storePage(url, html):
    collection.insert_one({"url": url, "html": html})

# Function to parse HTML and extract links
def parse(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        if is_valid_url(full_url):
            links.add(full_url)
    return links

# Function to check if the target page is found
def is_target_page(html):
    return TARGET_HEADING in str(html)

# Function to check if a URL is valid
def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and url.endswith(('.html', '.shtml'))

# Crawler Procedure
def crawlerThread(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        if url in frontier.visited:
            continue
        frontier.mark_visited(url)

        html = retrieveHTML(url)
        if html is None:
            continue
        
        storePage(url, html)

        # Check if the target page is found
        if is_target_page(html):
            print(f"Target page found at: {url}")
            return

        # Extract and add new URLs to the frontier
        new_urls = parse(html, url)
        for new_url in new_urls:
            frontier.addURL(new_url)

    print("Target page not found.")

# Main Execution
if __name__ == "__main__":
    frontier = Frontier()
    crawlerThread(frontier)
