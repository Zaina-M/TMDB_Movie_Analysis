import os
import time
import logging
import json
from typing import List, Dict, Optional

import requests
import pandas as pd
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------
# Environment & Config
# -------------------------
load_dotenv()


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")



if not API_KEY:
    raise RuntimeError("API_KEY not found in environment variables")
MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397, 420818,
    24428, 168259, 99861, 284054, 12445, 181808, 330457,
    351286, 109445, 321612, 260513
]

REQUEST_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5  # exponential backoff base


# -------------------------
# Logging (FILE ONLY)
# -------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "fetch_movies.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("tmdb_fetcher")


# -------------------------
# HTTP Session with Retries
# -------------------------
def create_session() -> requests.Session:
    """
    Create a requests session with retry strategy.
    """
    retry_strategy = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=RETRY_BACKOFF,
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# -------------------------
# Fetch Single Movie
# -------------------------
def fetch_movie(
    session: requests.Session,
    movie_id: int
) -> Optional[Dict]:
    """
    Fetch a single movie from TMDb.
    Returns None for invalid or failed IDs.
    """
    if movie_id <= 0:
        logger.warning(f"Skipping invalid movie_id: {movie_id}")
        return None

    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY, "append_to_response": "credits"}

    try:
        response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)

        if response.status_code == 404:
            logger.warning(f"Movie not found (404): {movie_id}")
            return None

        if response.status_code != 200:
            logger.error(
                f"Failed to fetch movie_id={movie_id} "
                f"status={response.status_code}"
            )
            return None

        data = response.json()

        logger.info(f"Successfully fetched movie_id={movie_id}")
        return {
            "movie_id": data.get("id"),
            "title": data.get("title"),
            "tagline": data.get("tagline"),
            "overview": data.get("overview"),
            "poster_path": data.get("poster_path"),
            "release_date": data.get("release_date"),
            "runtime": data.get("runtime"),
            "budget": data.get("budget"),
            "revenue": data.get("revenue"),
            "popularity": data.get("popularity"),
            "vote_average": data.get("vote_average"),
            "vote_count": data.get("vote_count"),
            "original_language": data.get("original_language"),
            "belongs_to_collection": data.get("belongs_to_collection"),
            "genres": data.get("genres"),
            "production_companies": data.get("production_companies"),
            "production_countries": data.get("production_countries"),
            "spoken_languages": data.get("spoken_languages"),
            "credits": data.get("credits")
        }

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching movie_id={movie_id}")
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request error for movie_id={movie_id}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error for movie_id={movie_id}: {e}")

    return None


# -------------------------
# Fetch All Movies
# -------------------------
def fetch_movies(movie_ids: List[int]) -> pd.DataFrame:
    """
    Fetch multiple movies (including full credits)
    and return as Pandas DataFrame.
    """
    session = create_session()
    results = []

    for movie_id in movie_ids:
        movie = fetch_movie(session, movie_id)
        if movie:
            results.append(movie)

        time.sleep(0.2)

    wanted_movie = pd.DataFrame(results)

    logger.info(
        f"Fetch completed | requested={len(movie_ids)} "
        f"successful={len(wanted_movie)}"
    )

    return wanted_movie


# -------------------------
# Main Execution
# -------------------------
if __name__ == "__main__":
    df_movies = fetch_movies(MOVIE_IDS)

    # Example: persist downstream
    df_movies.to_json("movies_raw.json", orient="records", indent=4)

    logger.info("Movie data saved to movies_raw.json")