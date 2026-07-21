import time
import random
import logging
from functools import wraps
import requests

logger = logging.getLogger(__name__)

def with_resilience(max_retries: int = 3, base_delay: float = 1.0):
    """
    Exponential backoff with jitter decorator.
    Catches transient network errors and 5xx HTTP errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    if retries >= max_retries:
                        logger.error(f"Max retries reached due to network error: {e}")
                        raise
                    delay = base_delay * (2 ** retries) + random.uniform(0, 1)
                    logger.warning(f"Transient network error: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    retries += 1
                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code >= 500:
                        if retries >= max_retries:
                            logger.error(f"Max retries reached due to 5xx error: {e}")
                            raise
                        delay = base_delay * (2 ** retries) + random.uniform(0, 1)
                        logger.warning(f"Transient 5xx error: {e}. Retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        retries += 1
                    else:
                        # Re-raise 4xx errors immediately (e.g. 401, 404), they are not transient
                        raise
                except Exception:
                    # Non-transient or unknown exception, re-raise immediately
                    raise
        return wrapper
    return decorator
