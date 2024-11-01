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

def get_longest_page(log_file_path):
    """
    Finds the URL with the most words in its content from a Worker.log file.

    Parameters:
    log_file_path (str): The path to the Worker.log file.

    Returns:
    tuple: A tuple containing the URL with the most words and the word count.
    """
    url_pattern = re.compile(r'Downloaded (https?://[^\s,]+)')
    max_word_count = 0
    longest_page_url = None

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = url_pattern.search(line)
            if match:
                url = match.group(1)
                
                # Fetch the page content
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        # Parse HTML content and remove tags
                        soup = BeautifulSoup(response.content, 'html.parser')
                        for script_or_style in soup(['script', 'style']):
                            script_or_style.decompose()  # Remove scripts and styles
                        
                        text_content = soup.get_text(separator=' ', strip=True)
                        words = text_content.split()  # Split text by whitespace to count words
                        word_count = len(words)
                        
                        # Track the URL with the highest word count
                        if word_count > max_word_count:
                            max_word_count = word_count
                            longest_page_url = url

                except requests.RequestException as e:
                    print(f"Error fetching {url}: {e}")

    return longest_page_url, max_word_count

# results.py
if __name__ == "__main__":
    unique_page_count = count_unique_pages('/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log')
    print(f"Number of unique pages: {unique_page_count}")
    longest_page_url, max_word_count = get_longest_page('/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log')
    print(f"The longest page is: {longest_page_url} with {max_word_count} words")
