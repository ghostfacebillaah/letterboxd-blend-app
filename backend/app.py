from flask import Flask, jsonify, request
from utils import calculate_blend_percentage, find_top_rated_common_films, scrape_profile_avatar, scrape_movie_poster, get_watchlist_party_results
from flask_cors import CORS
import numpy as np
import json

app = Flask(__name__)
CORS(app)  # To allow cross-origin requests from React frontend

@app.route('/api/calculate_blend', methods=['POST'])
def calculate_blend():
    """API endpoint to calculate blend percentage between two users."""
    data = request.get_json()
    username1 = data.get('username1')
    username2 = data.get('username2')

    if not username1 or not username2:
        return jsonify({"error": "Usernames are required"}), 400

    try:
        blend_percentage = calculate_blend_percentage(username1, username2)
        return jsonify({"blend_percentage": blend_percentage})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/profile_avatars', methods=['POST'])
def profile_avatars():
    """API endpoint to get profile avatars for users."""
    data = request.get_json()
    username1 = data.get('username1')
    username2 = data.get('username2')

    if not username1 or not username2:
        return jsonify({"error": "Usernames are required"}), 400

    try:
        avatar1 = scrape_profile_avatar(username1)
        avatar2 = scrape_profile_avatar(username2)
        return jsonify({"avatar1": avatar1, "avatar2": avatar2})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/top_common_films', methods=['POST'])
def top_common_films():
    """API endpoint to get the top common films between two users."""
    data = request.get_json()
    username1 = data.get('username1')
    username2 = data.get('username2')
    top_n = data.get('top_n', 4)

    if not username1 or not username2:
        return jsonify({"error": "Usernames are required"}), 400

    try:
        top_common_films, _ = find_top_rated_common_films(username1, username2, top_n=top_n)
        return jsonify({"top_common_films": top_common_films})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/scrape_poster', methods=['POST'])
def scrape_poster():
    data = request.json
    film_url = data.get('film_url')

    if not film_url:
        return jsonify({"error": "film_url is required"}), 400

    try:
        image_url = scrape_movie_poster(film_url)
        return jsonify({"image_url": image_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/watchlist-party', methods=['POST'])
def watchlist_party():
    data = request.json
    usernames = data.get('usernames', [])
    genre = data.get('genre')
    director = data.get('director')
    decade = data.get('decade')
    min_runtime = data.get('min_runtime')
    max_runtime = data.get('max_runtime')

    # Debugging: Check received filters
    print(f"Received filters - Genre: {genre}, Director: {director}, Decade: {decade}, Min Runtime: {min_runtime}, Max Runtime: {max_runtime}")

    results = get_watchlist_party_results(
        usernames, genre, director, decade, min_runtime, max_runtime
    )

    # Debugging: Check results after filtering
    print(f"Filtered movies count: {len(results)}")

    # Convert NaN to None before returning JSON
    # safe_results = json.loads(json.dumps(results, default=lambda x: None if x != x else x))
    # Convert NaN to None before returning JSON
    def replace_nan(obj):
        if isinstance(obj, float) and np.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: replace_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_nan(i) for i in obj]
        return obj

    safe_results = replace_nan(results)
    return jsonify({'common_films': safe_results})


@app.route('/health')
def health_check():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
