import re
import requests
from requests.exceptions import SSLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import Counter

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

# List of English stop words (loaded from the ranks.nl website)
STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
])

def extract_urls_with_status_200(log_file_path):
    """Extract URLs with status 200 from the Worker.log file, filtering out non-text files and specific problematic URLs."""
    urls = []
    with open(log_file_path, 'r') as file:
        for line in file:
            match = re.search(r'Downloaded (\S+), status <200>', line)
            if match:
                url = match.group(1)

                # Skip non-text files based on their extensions
                if not re.search(r'\.(mpg|mp4|avi|mov|mkv|ogg|ogv|pdf|png|jpg|jpeg|gif|bmp|wav|mp3|zip|rar|gz|exe|dmg|iso)$', url.lower()):
                    urls.append(url)
                else:
                    print(f"Skipping non-text file: {url}")
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

def get_words_from_url(url):
    """Download content of a URL, extract words, and filter out stop words."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Split text into words and filter out stop words
        words = re.findall(r'\b\w+\b', text.lower())  # Convert to lowercase and extract words
        return [word for word in words if word not in STOP_WORDS]
    except SSLError:
        print(f"SSL error for {url}. Skipping.")
        return []
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return []

def find_most_common_words(log_file_path, top_n=50):
    """Find the most common words across all pages, excluding stop words."""
    urls = extract_urls_with_status_200(log_file_path)
    word_counter = Counter()

    for url in urls:
        words = get_words_from_url(url)
        word_counter.update(words)

        # Print intermediate results for top N most common words so far
        most_common_words = word_counter.most_common(top_n)
        print(f"Current top {top_n} most common words after processing {url}:")
        for word, count in most_common_words:
            print(f"{word}: {count}")
        print("\n" + "-"*50 + "\n")

    # Final top 50 most common words
    print("Final top 50 most common words across all pages:")
    for word, count in most_common_words:
        print(f"{word}: {count}")

    return most_common_words

if __name__ == "__main__":
    unique_page_count = count_unique_pages('/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log')
    print(f"Number of unique pages: {unique_page_count}")
    log_file_path = '/home/ajguerr4/spacetime-crawler4py/Logs/Worker.log'
    #find_longest_page(log_file_path)
    find_most_common_words(log_file_path)