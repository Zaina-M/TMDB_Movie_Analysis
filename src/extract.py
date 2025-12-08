import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found. Did you set it in .env?")

movie_ids = [
    0, 299534, 19995, 140607, 299536, 597, 135397, 420818,
    24428, 168259, 99861, 284054, 12445, 181808, 330457,
    351286, 109445, 321612, 260513
]

def fetch_movies(ids=movie_ids):
    
    wanted_movies = []
    for movie_id in ids:
        if movie_id == 0:
            continue

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=credits&api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            wanted_movies.append(response.json())
        else:
            print(f"Failed to fetch movie {movie_id}: {response.status_code}")
    return wanted_movies
