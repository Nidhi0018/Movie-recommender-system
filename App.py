import streamlit as st
import pickle
import pandas as pd
import requests

# ✅ Your TMDB API Key
TMDB_API_KEY = "6ff01690190842fad959ba9b5a7a7a69"

# ✅ Reuse session
session = requests.Session()

# ----------------------------------
# 🧩 Fetch details by TMDB ID
# ----------------------------------
def fetch_movie_details(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US'
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
    url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}'
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

# ----------------------------------
# 📊 Load data
# ----------------------------------
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_list = movies['title'].values

# ----------------------------------
# 🧩 Recommend
# ----------------------------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list_idx = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_overviews = []
    recommended_ratings = []

    for i in movies_list_idx:
        title = movies.iloc[i[0]].title

        if 'movie_id' in movies.columns:
            movie_id = movies.iloc[i[0]].movie_id
            poster, overview, rating = fetch_movie_details(movie_id)
        else:
            poster, overview, rating = fetch_movie_details_by_title(title)

        recommended_movies.append(title)
        recommended_posters.append(poster)
        recommended_overviews.append(overview)
        recommended_ratings.append(rating)

    return recommended_movies, recommended_posters, recommended_overviews, recommended_ratings

# ----------------------------------
# 🎨 Custom CSS styling
# ----------------------------------
custom_css = """
<style>
h1 {
    color: #FF4B4B;
}

.stImage img {
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.selected-movie {
    text-align: center;
    margin-bottom: 3rem;
}

.selected-movie-title {
    font-weight: 900;
    font-size: 2rem;
    color: #FF4B4B;
    margin-top: 1rem;
}

.selected-movie-overview {
    font-size: 1rem;
    color: #DDDDDD;
    margin-top: 0.5rem;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

.movie-card {
    background: #1c1c1c;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    text-align: center;
}

.movie-title {
    font-weight: 700;
    font-size: 1.1rem;
    color: #FFFFFF;
    margin-top: 0.5rem;
}

.movie-rating {
    font-size: 1rem;
    color: #F39C12;
}

.movie-overview {
    font-size: 0.85rem;
    color: #BBBBBB;
    margin-top: 0.3rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----------------------------------
# 🎬 Streamlit App
# ----------------------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

st.title('🎬 Movie Recommender System')
st.write("✨ Find movies similar to your favorite ones with beautiful posters, short overviews, and ratings!")

selected_movie = st.selectbox(
    "🎥 Pick a movie you love:",
    movies_list
)

if st.button('🔍 Recommend'):
    # Show selected movie details nicely
    if 'movie_id' in movies.columns:
        selected_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
        poster, overview, rating = fetch_movie_details(selected_id)
    else:
        poster, overview, rating = fetch_movie_details_by_title(selected_movie)

    st.markdown("<div class='selected-movie'>", unsafe_allow_html=True)
    st.image(poster, width=300)
    st.markdown(f"<div class='selected-movie-title'>{selected_movie}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='selected-movie-overview'>{overview}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Show recommendations
    names, posters, overviews, ratings = recommend(selected_movie)

    st.subheader(f"✨ Movies similar to **{selected_movie}**")
    cols = st.columns(5)
    for col, name, poster, overview, rating in zip(cols, names, posters, overviews, ratings):
        with col:
            st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
            st.image(poster, use_container_width=True)
            st.markdown(f"<div class='movie-title'>{name}</div>", unsafe_allow_html=True)

            try:
                stars = '⭐' * int(round(float(rating)/2))
            except:
                stars = "No rating"

            st.markdown(f"<div class='movie-rating'>{stars} ({rating}/10)</div>", unsafe_allow_html=True)

            clipped = overview[:100] + "..." if len(overview) > 100 else overview
            st.markdown(f"<div class='movie-overview'>{clipped}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
