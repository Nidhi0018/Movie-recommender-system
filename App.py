import streamlit as st
import pickle
import pandas as pd
import requests

# ✅ Secure: read your API key from Streamlit Secrets
tmdb_api_key = st.secrets["TMDB_API_KEY"]  # ✅ This is your ONLY key now!

# ✅ Reuse session
session = requests.Session()

# ----------------------------------
# 🧩 Fetch details by TMDB ID
# ----------------------------------
def fetch_movie_details(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=en-US'
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        poster_url = "https://via.placeholder.com/300x450?text=No+Poster"
        overview = "No overview available."
        rating = "N/A"

        if 'poster_path' in data and data['poster_path']:
            poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

        if 'overview' in data and data['overview']:
            overview = data['overview']

        if 'vote_average' in data and data['vote_average']:
            rating = round(data['vote_average'], 1)

        return poster_url, overview, rating

    except Exception as e:
        print(f"[ERROR] Fetching details for TMDB ID {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Error", "No overview available.", "N/A"

# ----------------------------------
# 🧩 Fallback: Fetch by title
# ----------------------------------
def fetch_movie_details_by_title(title):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}'
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            result = data['results'][0]
            poster_url = "https://via.placeholder.com/300x450?text=No+Poster"
            overview = result.get('overview', "No overview available.")
            rating = round(result.get('vote_average', 0), 1)

            if result['poster_path']:
                poster_url = "https://image.tmdb.org/t/p/w500/" + result['poster_path']

            return poster_url, overview, rating

        else:
            return "https://via.placeholder.com/300x450?text=No+Poster", "No overview available.", "N/A"

    except Exception as e:
        print(f"[ERROR] Fetching details for title {title}: {e}")
        return "https://via.placeholder.com/300x450?text=Error", "No overview available.", "N/A"
