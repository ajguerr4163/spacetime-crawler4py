import re
import requests
from requests.exceptions import SSLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def count_unique_pages(log_file_path):
    """
    Counts the number of unique pages from a Worker.log file, based on URL uniqueness (ignoring fragments).

    Parameters:
    log_file_path (str): The path to the Worker.log file.

    Returns:
    int: The number of unique pages.
    """
    unique_urls = set()
    url_pattern = re.compile(r'Downloaded (https?://[^\s,]+)')

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = url_pattern.search(line)
            if match:
                url = match.group(1)
                # Parse URL and remove fragment
                parsed_url = urlparse(url)
                defragmented_url = parsed_url._replace(fragment="").geturl()
                unique_urls.add(defragmented_url)

    return len(unique_urls)

def extract_urls_with_status_200(log_file_path):
    """Extract URLs with status 200 from the Worker.log file."""
    urls = []
    with open(log_file_path, 'r') as file:
        for line in file:
            match = re.search(r'Downloaded (\S+), status <200>', line)
            if match:
                url = match.group(1)
                urls.append(url)
    return urls

def count_words_in_url(url):
    """Download content of a URL and count the number of words (excluding HTML markup)."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Count words in text
        words = text.split()
        return len(words)
    except SSLError:
        print(f"SSL error for {url}. Skipping.")
        return 0
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return 0

def find_longest_page(log_file_path):
    """Find the URL with the longest page in terms of word count."""
    urls = extract_urls_with_status_200(log_file_path)
    longest_url = None
    max_word_count = 0

    for url in urls:
        word_count = count_words_in_url(url)
        print(f"{url}: {word_count} words")
        
        if word_count > max_word_count:
            max_word_count = word_count
            longest_url = url

    print(f"The longest page is {longest_url} with {max_word_count} words.")
    return longest_url


# results.py
if __name__ == "__main__":
    unique_page_count = count_unique_pages('/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log')
    print(f"Number of unique pages: {unique_page_count}")
    log_file_path = '/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log'
    find_longest_page(log_file_path)