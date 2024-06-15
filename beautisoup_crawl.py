import os
import csv
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

visited_urls = set()


def fetch_page(url):
    """Fetches the content of a URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def normalize_url(url, base_url):
    """Normalize URLs by removing fragments and resolving relative URLs."""
    url = urljoin(base_url, url)
    url, _ = urldefrag(url)
    return url


def create_directory_structure(url, base_dir):
    """Creates a directory structure based on the URL."""
    parsed_url = urlparse(url)
    path = os.path.join(base_dir, parsed_url.netloc, parsed_url.path.lstrip("/"))
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download_image(image_url, page_url, save_dir, csv_writer):
    """Downloads an image from the given URL and saves it to the specified directory."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Create directory structure based on page URL
        image_save_dir = create_directory_structure(page_url, save_dir)
        image_name = os.path.join(image_save_dir, image_url.split('/')[-1])
        with open(image_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {image_url}")
        csv_writer.writerow([image_url, image_name, page_url])

    except requests.RequestException as e:
        print(f"Failed to download image {image_url}: {e}")


def scrape_site(start_url, save_dir, csv_file, max_workers=7):
    queue = deque([start_url])  # queue to manage URLs for BFS

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['image_url', 'local_path', 'page_url'])

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(fetch_page, start_url): start_url}

            while queue or future_to_url:
                while queue:
                    url = queue.popleft()
                    normalized_url = normalize_url(url, start_url)
                    if normalized_url in visited_urls:
                        continue
                    visited_urls.add(normalized_url)
                    future_to_url[executor.submit(fetch_page, normalized_url)] = normalized_url

                for future in as_completed(future_to_url):
                    page_url = future_to_url.pop(future)
                    soup = future.result()
                    if soup is None:
                        continue
                    print(f"Scraping: {page_url}")

                    # Find all image tags on the page
                    for img in soup.find_all('img', src=True):
                        img_url = normalize_url(img['src'], page_url)
                        executor.submit(download_image, img_url, page_url, save_dir, csv_writer)

                    # Find all links on the page
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        normalized_href = normalize_url(href, start_url)
                        if start_url in normalized_href and normalized_href not in visited_urls:
                            queue.append(normalized_href)


def main(start_url):
    save_dir = 'images'
    csv_file = 'image_data.csv'
    scrape_site(start_url, save_dir, csv_file)


if __name__ == '__main__':
    main('https://www.glamira.com')
