import re
import hashlib
import secrets
import string
import requests

URL_REGEX = re.compile(
    r'^(?:http|https)://'  # enforce scheme
    r'(?:[^\s/$.?#].[^\s]*)$',  # general URL characters
    re.IGNORECASE
)

def is_valid_url_format(url: str) -> bool:
    """Basic format validation using regex."""
    return bool(URL_REGEX.match(url.strip()))

def is_url_reachable(url: str, timeout: int = 5) -> bool:
    """Check if the URL responds with a non-error status."""
    try:
        # HEAD first; some servers may not support HEAD—fallback to GET
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        if resp.status_code < 400:
            return True
        # Fallback GET if HEAD not reliable
        resp = requests.get(url, allow_redirects=True, timeout=timeout)
        return resp.status_code < 400
    except requests.RequestException:
        return False

def canonicalize_url(url: str) -> str:
    """Ensure scheme and strip whitespace."""
    url = url.strip()
    # If user forgot scheme, you could optionally add it—here we enforce explicit scheme
    return url

def md5_short_code(source: str, length: int = 6) -> str:
    """Generate a deterministic short code from MD5 hash."""
    digest = hashlib.md5(source.encode("utf-8")).hexdigest()
    return digest[:length]

def random_short_code(length: int = 6) -> str:
    """Generate a random short code to avoid collisions."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))