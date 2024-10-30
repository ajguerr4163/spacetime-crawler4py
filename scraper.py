import re
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup

def scraper(url, resp):
    """
    Extracts links from a page response and returns only valid URLs.

    Parameters:
    url (str): The URL of the page.
    resp (Response): The response object containing page data.

    Returns:
    list of str: List of valid URLs extracted from the page.
    """
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """
    Extracts and returns a list of hyperlinks from the content of the response.

    Parameters:
    url (str): The URL that was used to get the page.
    resp (Response): The response object containing status, content, and metadata.

    Returns:
    list of str: List of hyperlinks found on the page.
    """
    links = []

    # Process only if the response is valid and the status code is 200
    if resp.status != 200:
        return links  # Return an empty list if the page could not be retrieved successfully

    # Check if there is content in the response
    if not resp.raw_response or not resp.raw_response.content:
        return links  # Return an empty list if no content is available

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # Extract all anchor tags and their href attributes
    for anchor in soup.find_all('a', href=True):
        # Use urljoin to form absolute URLs from relative paths
        link = urljoin(url, anchor['href'])
        links.append(link)

    return links

def is_valid(url):
    """
    Decides whether to crawl this URL or not. Returns True if the URL is within specified domains and paths.

    Parameters:
    url (str): The URL to check.

    Returns:
    bool: True if the URL is valid for crawling; False otherwise.
    """
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Immediately return False if there is a fragment
        if parsed.fragment:
            return False

        # Scheme check: Only allow http and https
        if parsed.scheme not in {"http", "https"}:
            return False

        # File extension check: Skip non-crawlable file types
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False

        # Only allow URLs from the specified subdomains of uci.edu
        allowed_domains = {
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu",
            "today.uci.edu"
        }
        if not any(parsed.netloc.endswith(domain) for domain in allowed_domains):
            return False

        # Path restriction for today.uci.edu
        if parsed.netloc == "today.uci.edu" and not parsed.path.startswith("/department/information_computer_sciences"):
            return False

        return True

    except TypeError:
        print("TypeError for ", url)
        raise
