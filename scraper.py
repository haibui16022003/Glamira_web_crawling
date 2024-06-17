import csv
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from fetch import fetch_page
from normalize import normalize_url
from download import download_image, downloaded_images

visited_urls = set()


def scrape_site(start_url, save_dir, csv_file, max_workers=5):
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
                        if img_url not in downloaded_images:
                            executor.submit(download_image, img_url, page_url, save_dir, csv_writer)

                    # Find all links on the page
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        normalized_href = normalize_url(href, start_url)
                        parsed_href = urlparse(normalized_href)
                        # Follow the link that started by the start url
                        if parsed_href.netloc == urlparse(start_url).netloc and normalized_href not in visited_urls:
                            queue.append(normalized_href)
