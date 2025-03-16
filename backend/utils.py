import pandas as pd
from scipy.stats import spearmanr
from collections import Counter
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Constants
LOCAL_DB_PATH = 'mother22.csv'
DOMAIN = "https://letterboxd.com"

def transform_ratings(some_str):
    """
    Transforms raw star rating into float value
    :param: some_str: actual star rating
    :rtype: returns the float representation of the given star(s)
    """
    stars = {
        "★": 1,
        "★★": 2,
        "★★★": 3,
        "★★★★": 4,
        "★★★★★": 5,
        "½": 0.5,
        "★½": 1.5,
        "★★½": 2.5,
        "★★★½": 3.5,
        "★★★★½": 4.5
    }
    try:
        return stars[some_str]
    except:
        return -1
    

def scrape_diary(username):
    movies_dict = {
        'id': [], 'title': [], 'rating': [], 'date': [], 'link': []
    }
    url = f"{DOMAIN}/{username}/films/diary/"
    url_page = requests.get(url)
    soup = BeautifulSoup(url_page.content, 'html.parser')

    # Check number of pages
    li_pagination = soup.findAll("li", {"class": "paginate-page"})
    pages = int(li_pagination[-1].find('a').get_text().strip()) if li_pagination else 1

    for i in range(pages):
        url = f"{DOMAIN}/{username}/films/diary/page/{i + 1}" if pages > 1 else f"{DOMAIN}/{username}/films/diary/"
        url_page = requests.get(url)
        soup = BeautifulSoup(url_page.content, 'html.parser')
        
        diary_entries = soup.find_all("tr", class_="diary-entry-row")
        if not diary_entries:
            break

        for entry in diary_entries:
            title_tag = entry.find("td", class_="td-film-details").find("a")
            if not title_tag:
                continue  # Skip this entry if the title tag is missing

            movie_id = entry["data-object-id"].split(":")[-1]
            title = title_tag.text.strip()
            link = entry.find("td", class_="td-actions")["data-film-link"].strip()
        
            date_tag = entry.find("td", class_="td-day").find("a")
            if date_tag and "films/diary/for/" in date_tag["href"]:
                diary_date = date_tag["href"].split("/for/")[-1].strip("/")  # Extract full date (YYYY/MM/DD)
            else:
                diary_date = "Unknown"
        
            rating_tag = entry.find("td", class_="td-rating")
            rating = None
            if rating_tag:
                star_tag = rating_tag.find("span", class_="rating")
                if star_tag:
                    rating = transform_ratings(star_tag.text.strip())
                    
            movies_dict['id'].append(movie_id)
            movies_dict['title'].append(title)
            movies_dict['rating'].append(rating)
            movies_dict['date'].append(diary_date)
            movies_dict['link'].append(link)

    df_diary = pd.DataFrame(movies_dict)
    return df_diary

def scrape_films(username):
    movies_dict = {
        'id': [], 'title': [], 'rating': [], 'liked': [], 'link': []
    }
    url = DOMAIN + "/" + username + "/films/"
    url_page = requests.get(url)
    soup = BeautifulSoup(url_page.content, 'html.parser')
    
    # check number of pages
    li_pagination = soup.findAll("li", {"class": "paginate-page"})
    if len(li_pagination) == 0:
        ul = soup.find("ul", {"class": "poster-list"})
        if ul:
            movies = ul.find_all("li")
            for movie in movies:
                movies_dict['id'].append(movie.find('div')['data-film-id'])
                movies_dict['title'].append(movie.find('img')['alt'])
                rating_str = movie.find('p', {"class": "poster-viewingdata"}).get_text().strip()
                rating = transform_ratings(rating_str)
                movies_dict['rating'].append(rating if rating != -1 else None)
                movies_dict['liked'].append(movie.find('span', {'class': 'like'}) != None)
                movies_dict['link'].append(movie.find('div')['data-target-link'])
    else:
        for i in range(int(li_pagination[-1].find('a').get_text().strip())):
            url = DOMAIN + "/" + username + "/films/page/" + str(i + 1)
            url_page = requests.get(url)
            soup = BeautifulSoup(url_page.content, 'html.parser')
            ul = soup.find("ul", {"class": "poster-list"})
            if ul:
                movies = ul.find_all("li")
                for movie in movies:
                    movies_dict['id'].append(movie.find('div')['data-film-id'])
                    movies_dict['title'].append(movie.find('img')['alt'])
                    rating_str = movie.find('p', {"class": "poster-viewingdata"}).get_text().strip()
                    rating = transform_ratings(rating_str)
                    movies_dict['rating'].append(rating if rating != -1 else None)
                    movies_dict['liked'].append(movie.find('span', {'class': 'like'}) != None)
                    movies_dict['link'].append(movie.find('div')['data-target-link'])

    df_film = pd.DataFrame(movies_dict)
    return df_film

def load_local_database():
    """Load the local movie database."""
    return pd.read_csv(LOCAL_DB_PATH)

def merge_with_local_db(df_user, local_db):
    """Merge scraped films with the local database to get attributes."""
    merged_df = pd.merge(df_user, local_db, on='link', how='left')
    return merged_df

def calculate_jaccard_similarity(counter1, counter2):
    """Calculate the Jaccard similarity between two counters."""
    intersection = sum((counter1 & counter2).values())
    union = sum((counter1 | counter2).values())
    return intersection / union if union > 0 else 0

def compare_attributes(df_user1, df_user2, attributes, weights):
    """Compare attributes between two users using weighted Jaccard similarity."""
    total_weighted_jaccard = 0

    for attr, weight in zip(attributes, weights):
        # Create counters for each attribute
        counter_user1 = Counter(df_user1[attr].dropna().str.split(', ').sum())
        counter_user2 = Counter(df_user2[attr].dropna().str.split(', ').sum())
        
        # Calculate Jaccard similarity
        jaccard_similarity = calculate_jaccard_similarity(counter_user1, counter_user2)
        weighted_jaccard = jaccard_similarity * weight
        total_weighted_jaccard += weighted_jaccard
        
    return total_weighted_jaccard

def calculate_blend_percentage(user1, user2):
    """Calculate the blend percentage between two users."""
    # Scrape films
    df_user1 = scrape_films(user1)
    df_user2 = scrape_films(user2)

    # Load local database
    local_db = load_local_database()

    # Merge scraped films with local database
    merged_user1 = merge_with_local_db(df_user1, local_db)
    merged_user2 = merge_with_local_db(df_user2, local_db)

    # Define attributes for Jaccard similarity calculation and their weights
    attributes = ['decade', 'directors', 'genres', 'themes', 'studios', 'countries', 
                  'language', 'cinematographer', 'composers', 'cast', 'popularity_class', 'duration_class']
    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Adjust weights as needed

    # Calculate total weighted Jaccard similarity
    total_weighted_jaccard = compare_attributes(merged_user1, merged_user2, attributes, weights)

    # Find common movies
    common_movies = pd.merge(df_user1, df_user2, on='link', suffixes=('_user1', '_user2'))

    # Calculate proportion of common films
    total_movies = len(set(df_user1['link']).union(set(df_user2 ['link'])))
    proportion_common = len(common_movies) / total_movies if total_movies > 0 else 0

    # Filter out unrated movies for Spearman's calculation
    common_rated_movies = common_movies.dropna(subset=['rating_user1', 'rating_user2'])

    # Calculate Spearman's rank correlation coefficient for ratings
    if len(common_rated_movies) > 1:
        spearman_corr = spearmanr(common_rated_movies['rating_user1'], common_rated_movies['rating_user2']).correlation
        spearman_normalized = (spearman_corr + 1) / 2
    else:
        spearman_normalized = 0

    # Compute blend percentage
    blend_percentage = (0.09 * proportion_common) + (0.9 * spearman_normalized) + (0.01 * total_weighted_jaccard)

    # Round off the blend percentage to the nearest whole number
    return round(blend_percentage * 100)


def find_top_rated_common_films(username1, username2, top_n=4):
    # Scrape diary entries for both users
    df_diary1 = scrape_diary(username1)
    df_diary2 = scrape_diary(username2)
    
    # Check if 'date' column exists in both DataFrames
    if 'date' in df_diary1.columns and 'date' in df_diary2.columns:
        # Merge DataFrames on 'title' and 'date'
        common_films = pd.merge(df_diary1, df_diary2, on=['title', 'date'], suffixes=('_user1', '_user2'))
    else:
        common_films = pd.DataFrame()  # Empty DataFrame to avoid errors in case 'date' column is missing

    # Number of common films found in the diary
    n_common_films = len(common_films)
    
    # If we have fewer common films than needed, scrape the films page
    if n_common_films < top_n:
        df_films1 = scrape_films(username1)
        df_films2 = scrape_films(username2)
        
        # Merge DataFrames on 'title'
        additional_common_films = pd.merge(df_films1, df_films2, on='title', suffixes=('_user1', '_user2'))
        
        if not additional_common_films.empty:
            # Convert ratings to numeric values if they are not already
            additional_common_films['rating_user1'] = pd.to_numeric(additional_common_films['rating_user1'], errors='coerce')
            additional_common_films['rating_user2'] = pd.to_numeric(additional_common_films['rating_user2'], errors='coerce')
            
            # Exclude already found common films
            additional_common_films = additional_common_films[~additional_common_films['title'].isin(common_films['title'])]

            # Add link for films
            additional_common_films['link'] = additional_common_films['link_user1']
            
            # Calculate the sum of ratings for sorting
            additional_common_films['sum_ratings'] = additional_common_films['rating_user1'] + additional_common_films['rating_user2']
            
            # Select top (top_n - n_common_films) additional films based on sum of ratings
            additional_common_films = additional_common_films.nlargest(top_n - n_common_films, 'sum_ratings')
            
            # Concatenate the additional films to the common films
            common_films = pd.concat([common_films, additional_common_films])
    
    # Ensure we have at most top_n films
    if len(common_films) > top_n:
        # Calculate the sum of ratings for sorting
        common_films['sum_ratings'] = common_films['rating_user1'] + common_films['rating_user2']
        
        # Select top top_n films based on sum of ratings
        common_films = common_films.nlargest(top_n, 'sum_ratings')

        #link = f"/film/{link.split("/film/", 1)[-1]}"

    if common_films.empty:
        return None, None
    
    # Convert the DataFrame to a JSON-serializable format
    common_films_json = common_films[['title', 'rating_user1', 'rating_user2', 'link_user1']].rename(columns={'link_user1': 'link'}).to_dict(orient='records')

    return common_films_json, common_films

def scrape_profile_avatar(username):
    url = f"https://letterboxd.com/{username}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Adjusted to target the 'avatar' span
    avatar_span = soup.find("span", class_="avatar -a500 -borderless -large")
    if avatar_span:
        img_tag = avatar_span.find("img")
        if img_tag:
            return img_tag['src']
    return None

def scrape_movie_poster(film_url):
    # Send a GET request to fetch the HTML content
    response = requests.get(film_url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <script> tag containing JSON-LD data
    script_tag = soup.find('script', {'type': 'application/ld+json'})

    if script_tag:
        # Clean the script content by removing any CDATA comments
        script_content = script_tag.string.strip().replace('/* <![CDATA[ */', '').replace('/* ]]> */', '')

        try:
            # Load the content of the script as JSON
            json_data = json.loads(script_content)

            # Extract the image URL from the JSON data
            image_url = json_data.get('image', 'No image found')
            return image_url

        except json.JSONDecodeError as e:
            raise ValueError("Error decoding JSON: " + str(e))
    else:
        raise ValueError("Could not find the JSON-LD script tag.")

def fetch_page(session, url):
    """Fetches a webpage using a shared session."""
    response = session.get(url)
    return response.content if response.status_code == 200 else None

def get_total_pages(session, username):
    """Retrieves the total number of pages in a user's watchlist."""
    url = f"{DOMAIN}/{username}/watchlist/"
    soup = BeautifulSoup(fetch_page(session, url), 'html.parser')
    pagination = soup.find_all("li", class_="paginate-page")
    return int(pagination[-1].find('a').text.strip()) if pagination else 1

def parse_watchlist_page(content):
    """Parses a single watchlist page and extracts movie data."""
    soup = BeautifulSoup(content, 'html.parser')
    ul = soup.find("ul", class_="poster-list")
    
    if not ul:
        return []

    movies = []
    for movie in ul.find_all("li"):
        movies.append({
            "id": movie.find("div")["data-film-id"],
            "title": movie.find("img")["alt"],
            "link": movie.find("div")["data-target-link"]
        })
    
    return movies

def scrape_watchlist(username):
    """Scrapes the watchlist of a given Letterboxd user with optimized requests."""
    with requests.Session() as session:
        total_pages = get_total_pages(session, username)
        urls = [f"{DOMAIN}/{username}/watchlist/page/{i}/" for i in range(1, total_pages + 1)]

        movies = []
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda url: fetch_page(session, url), urls)
            for content in results:
                if content:
                    movies.extend(parse_watchlist_page(content))

    return pd.DataFrame(movies)

def find_common_watchlist(usernames):
    """Finds the intersection of watchlists among multiple users."""
    watchlists = [scrape_watchlist(user) for user in usernames]
    
    # Remove empty watchlists
    watchlists = [wl for wl in watchlists if not wl.empty]
    
    if not watchlists:
        return pd.DataFrame()
    
    common_movies = watchlists[0]
    for wl in watchlists[1:]:
        common_movies = pd.merge(common_movies, wl, on=["id", "title", "link"])
        if common_movies.empty:
            return pd.DataFrame()

    return common_movies

def merge_with_local_dbw(common_watchlist, local_db_path=LOCAL_DB_PATH):
    """Merges the common watchlist with the local movie database, reading only required columns."""
    if common_watchlist.empty:
        return pd.DataFrame()
    
    local_db = pd.read_csv(local_db_path, usecols=["link", "title", "avg_rating", "genres", "directors", "decade", "runtime"])
    merged_df = pd.merge(common_watchlist, local_db, on="link", how="left")  # Merge using Letterboxd link

    # Rename title column explicitly if needed
    #if "title_x" in merged_df.columns:
     #   merged_df.rename(columns={"title_x": "title"}, inplace=True)
    #merged_df.to_csv("testos.csv", index=False)

    return merged_df

def filter_common_movies(merged_df, genre=None, director=None, decade=None, min_runtime=None, max_runtime=None):
    """Filters the merged database by genre, director, decade, and runtime range."""
    if merged_df.empty:
        return pd.DataFrame()
    
    # Convert runtime to numeric and drop NaNs
    merged_df["runtime"] = pd.to_numeric(merged_df["runtime"], errors="coerce")
    merged_df = merged_df.dropna(subset=["runtime"])

    # Apply filters selectively
    if genre:
        merged_df = merged_df[merged_df["genres"].str.contains(genre, case=False, na=False)]
    if director:
        merged_df = merged_df[merged_df["directors"].str.contains(director, case=False, na=False)]
    if decade:
        merged_df = merged_df[merged_df["decade"].astype(str).str.startswith(str(decade))]
    if min_runtime is not None and max_runtime is not None:
        merged_df = merged_df[(merged_df["runtime"] >= int(min_runtime)) & (merged_df["runtime"] <= int(max_runtime))]

    return merged_df

def get_watchlist_party_results(usernames, genre=None, director=None, decade=None, min_runtime=None, max_runtime=None):
    """Main function to get the final watchlist party recommendations."""
    common_watchlist = find_common_watchlist(usernames)
    
    if common_watchlist.empty:
        return []
    
    detailed_common_watchlist = merge_with_local_dbw(common_watchlist)
    filtered_movies = filter_common_movies(
        detailed_common_watchlist, 
        genre=genre, 
        director=director, 
        decade=decade, 
        min_runtime=min_runtime, 
        max_runtime=max_runtime
    )

    if filtered_movies.empty:
        return []
    
    return filtered_movies.to_dict(orient="records")
