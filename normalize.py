from urllib.parse import urljoin, urldefrag


def normalize_url(url, base_url):
    """Normalize URLs by removing fragments and resolving relative URLs."""
    url = urljoin(base_url, url)
    url, _ = urldefrag(url)
    return url
