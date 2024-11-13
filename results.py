import re
import requests
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


# results.py
if __name__ == "__main__":
    unique_page_count = count_unique_pages('/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log')
    print(f"Number of unique pages: {unique_page_count}")