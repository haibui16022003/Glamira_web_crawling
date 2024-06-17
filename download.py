import os
import requests
from urllib.parse import urlparse

downloaded_images = set()


def download_image(image_url, page_url, save_dir, csv_writer):
    """Downloads an image from the given URL and saves it to the specified directory."""
    if image_url in downloaded_images:
        return

    if image_url.lower().endswith(('.svg', '.gif')):
        return

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
        downloaded_images.add(image_url)

    except requests.RequestException as e:
        print(f"Failed to download image {image_url}: {e}")


def create_directory_structure(url, base_dir):
    """Creates a directory structure based on the URL."""
    parsed_url = urlparse(url)
    path = os.path.join(base_dir, parsed_url.netloc, parsed_url.path.lstrip("/"))
    if not os.path.exists(path):
        os.makedirs(path)
    return path
