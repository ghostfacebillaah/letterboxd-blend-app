import time
import pandas as pd
from scipy.stats import spearmanr
from collections import Counter
import random
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Constants
LOCAL_DB_PATH = 'mother22.csv'
DOMAIN = "https://letterboxd.com"

#HEADERS = {
#    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                  "AppleWebKit/537.36 (KHTML, like Gecko) "
#                  "Chrome/115.0.0.0 Safari/537.36"
#}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)

def transform_ratings(r):
    stars = {
        "★": 1, "★★": 2, "★★★": 3, "★★★★": 4, "★★★★★": 5,
        "½": 0.5, "★½": 1.5, "★★½": 2.5, "★★★½": 3.5, "★★★★½": 4.5
    }
    return stars.get(r, None)

def scrape_diary(username):
    movies_dict = {
        'id': [], 'title': [], 'rating': [], 'date': [], 'link': []
    }

    base_url = f"{DOMAIN}/{username}/films/diary/"
    first_page = fetch_url(base_url)
    if not first_page:
        print(f"Failed to load diary for {username}")
        return pd.DataFrame(movies_dict)

    soup = BeautifulSoup(first_page.content, 'html.parser')

    # Find number of pages
    li_pagination = soup.find_all("li", class_="paginate-page")
    pages = int(li_pagination[-1].get_text()) if li_pagination else 1

    for i in range(1, pages + 1):
        url = f"{DOMAIN}/{username}/films/diary/page/{i}/"
        response = fetch_url(url)
        if not response:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        diary_entries = soup.find_all("tr", class_="diary-entry-row")

        for entry in diary_entries:
            title_tag = entry.find("h3", class_="headline-3 prettify").find("a")
            if not title_tag:
                continue

            movie_id = entry.get("data-object-id", "").split(":")[-1]
            title = title_tag.text.strip()
            link = entry.find("td", class_="td-actions")["data-film-link"].strip()

            date_link_tag = entry.find("td", class_="td-day").find("a", href=True)
            diary_date = date_link_tag["href"].split("/for/")[-1].strip() if date_link_tag else "Unknown"

            rating_tag = entry.find("td", class_="td-rating")
            rating = None
            if rating_tag and rating_tag.find("span", class_="rating"):
                rating_text = rating_tag.find("span", class_="rating").text.strip()
                rating = transform_ratings(rating_text)

            movies_dict['id'].append(movie_id)
            movies_dict['title'].append(title)
            movies_dict['rating'].append(rating)
            movies_dict['date'].append(diary_date)
            movies_dict['link'].append(link)

        time.sleep(0.2)  # avoid hammering the site

    print(f" Scraped {len(movies_dict['title'])} diary entries for {username}")
    return pd.DataFrame(movies_dict)


def fetch_url(url, max_retries=3, timeout=10):
    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(url, headers= HEADERS, timeout=timeout)
            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                return None
        except Exception as e:
            print(f"Error: {e} on {url}")
        time.sleep(0.5)
    return None

def parse_movies(soup):
    ul = soup.find("ul", class_="poster-list")
    if not ul:
        return []

    movies = []
    for li in ul.find_all("li"):
        try:
            div = li.find("div")
            film_id = div['data-film-id']
            title = li.find('img')['alt']
            rating_str = li.find('p', class_="poster-viewingdata").get_text(strip=True)
            rating = transform_ratings(rating_str)
            liked = li.find('span', class_='like') is not None
            link = div['data-target-link']
            movies.append((film_id, title, rating, liked, link))
        except Exception:
            continue
    return movies
    
def scrape_films(username):
    movies_dict = {'id': [], 'title': [], 'rating': [], 'liked': [], 'link': []}
    base_url = f"{DOMAIN}/{username}/films/"
    first_response = fetch_url(base_url)

    if not first_response:
        print(f"Failed to load profile for {username}")
        return pd.DataFrame(movies_dict)

    soup = BeautifulSoup(first_response.content, 'html.parser')
    movies = parse_movies(soup)

    try:
        last_page = int(soup.select("li.paginate-page")[-1].get_text(strip=True))
    except:
        last_page = 1

    for page in range(2, last_page + 1):
        url = f"{base_url}page/{page}/"
        response = fetch_url(url)
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            movies.extend(parse_movies(soup))
        time.sleep(0.3)

    for film_id, title, rating, liked, link in movies:
        movies_dict['id'].append(film_id)
        movies_dict['title'].append(title)
        movies_dict['rating'].append(rating)
        movies_dict['liked'].append(liked)
        movies_dict['link'].append(link)

    return pd.DataFrame(movies_dict)


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
    #new code
    weights = [1.5, 2, 2, 1, 1, 1.25, 1.5, 0.85, 0.8, 1, 1.5, 1.25]  # Adjust weights as needed

    # Calculate total weighted Jaccard similarity
    total_weighted_jaccard = compare_attributes(merged_user1, merged_user2, attributes, weights)
    #new code
    total_weighted_jaccard /= sum(weights)
    total_weighted_jaccard = min(total_weighted_jaccard, 1) 

    # Find common movies
    common_movies = pd.merge(df_user1, df_user2, on='link', suffixes=('_user1', '_user2'))

    # Calculate proportion of common films
    total_movies = len(set(df_user1['link']).union(set(df_user2 ['link'])))
    proportion_common = len(common_movies) / total_movies if total_movies > 0 else 0
    #new code
    proportion_common = min(proportion_common, 1)

    # Filter out unrated movies for Spearman's calculation
    common_rated_movies = common_movies.dropna(subset=['rating_user1', 'rating_user2'])

    # Calculate Spearman's rank correlation coefficient for ratings
    if len(common_rated_movies) > 1:
        spearman_corr = spearmanr(common_rated_movies['rating_user1'], common_rated_movies['rating_user2']).correlation
        spearman_normalized = min((spearman_corr + 1) / 2, 1)  # Ensure Spearman does not exceed 1
    else:
        spearman_normalized = 0

    # Compute blend percentage
    #blend_percentage = (0.09 * proportion_common) + (0.9 * spearman_normalized) + (0.01 * total_weighted_jaccard)
    blend_percentage = (0.2 * proportion_common) + (0.9 * spearman_normalized) + (0.15 * total_weighted_jaccard)
    blend_percentage = min(blend_percentage, 1)

    # Round off the blend percentage to the nearest whole number
    return round(blend_percentage * 100)


def find_top_rated_common_films(username1, username2, top_n=4):
    # STEP 1: Scrape diaries
    df_diary1 = scrape_diary(username1)
    df_diary2 = scrape_diary(username2)

    # Save diaries for debugging
    df_diary1.to_csv(f'diary_{username1}.csv', index=False)
    df_diary2.to_csv(f'diary_{username2}.csv', index=False)

    # STEP 2: Find common diary entries (same title + date, many-to-many)
    common_diary = df_diary1.merge(df_diary2, on=['title', 'date'], how='inner', suffixes=('_user1', '_user2'))

    if not common_diary.empty:
        # Convert ratings to numeric
        common_diary['rating_user1'] = pd.to_numeric(common_diary['rating_user1'], errors='coerce')
        common_diary['rating_user2'] = pd.to_numeric(common_diary['rating_user2'], errors='coerce')
        common_diary['sum_ratings'] = common_diary['rating_user1'] + common_diary['rating_user2']

        # Sort by combined rating
        common_diary = common_diary.sort_values(by='sum_ratings', ascending=False)

        print("\n Top-rated common diary films (watched on same date):")
        for _, row in common_diary.iterrows():
            print(f"• '{row['title']}' on {row['date']} – {row['rating_user1']} + {row['rating_user2']} = {row['sum_ratings']}")
    else:
        print("\n No common diary entries with same date found.")

    top_diary = common_diary.head(top_n)
    remaining_slots = top_n - len(top_diary)

    # STEP 3: If fewer than top_n, fill with films from /films/
    additional_common = pd.DataFrame()
    if remaining_slots > 0:
        df_films1 = scrape_films(username1)
        df_films2 = scrape_films(username2)

        # Merge on title
        common_films = pd.merge(df_films1, df_films2, on='title', suffixes=('_user1', '_user2'))

        if not common_films.empty:
            # Exclude diary matches
            already_seen_titles = set(common_diary['title'])
            common_films = common_films[~common_films['title'].isin(already_seen_titles)]

            # Calculate combined ratings
            common_films['rating_user1'] = pd.to_numeric(common_films['rating_user1'], errors='coerce')
            common_films['rating_user2'] = pd.to_numeric(common_films['rating_user2'], errors='coerce')
            common_films['sum_ratings'] = common_films['rating_user1'] + common_films['rating_user2']

            # Sort and take top needed
            common_films = common_films.sort_values(by='sum_ratings', ascending=False)
            additional_common = common_films.head(remaining_slots)

            print(f"\n Additional common films from /films/ page (excluding diary):")
            for _, row in additional_common.iterrows():
                print(f"• '{row['title']}' – {row['rating_user1']} + {row['rating_user2']} = {row['sum_ratings']}")
        else:
            print("\n No additional common films found on /films/ page.")

    # Combine final result
    final_top = pd.concat([top_diary, additional_common], ignore_index=True)
    final_top = final_top.head(top_n)

    if not final_top.empty:
        final_top.to_csv("common_films.csv", index=False)
        print(f"\n Final top {top_n} common films saved to 'common_films.csv'.")
        return final_top, pd.concat([common_diary, additional_common], ignore_index=True)
    else:
        print("\n No common films found at all.")
        return None, None

def scrape_profile_avatar(username):
    url = f"https://letterboxd.com/{username}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    avatar_span = soup.find("span", class_="avatar -a500 -borderless -large")
    if avatar_span:
        img_tag = avatar_span.find("img")
        if img_tag and img_tag.get('src', '').startswith('http'):
            return img_tag['src']
    return None

def scrape_movie_poster(film_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36'
    }

    try:
        # Send a GET request to fetch the HTML content
        response = requests.get(film_url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch page, status code: {response.status_code}")
        
        html_content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the <script> tag containing JSON-LD data
        script_tag = soup.find('script', {'type': 'application/ld+json'})

        if script_tag:
            # Clean the script content by removing any CDATA comments
            script_content = script_tag.string.strip().replace('/* <![CDATA[ */', '').replace('/* ]]> */', '')

            # Load the content of the script as JSON
            json_data = json.loads(script_content)

            # Extract the image URL from the JSON data
            return json_data.get('image', 'No image found')
        else:
            raise ValueError("Could not find the JSON-LD script tag.")
    
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}")
    except Exception as e:
        raise RuntimeError(f"Error fetching poster: {e}")


def fetch_page(session, url, max_retries=3, timeout=10):
    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(random.uniform(1.5, 3.5))  # randomized delay
            response = session.get(url, headers=HEADERS, timeout=timeout)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"[fetch_page] 404 Not Found: {url}")
                return None
            else:
                print(f"[fetch_page] Attempt {attempt}: Failed to fetch {url} - Status code: {response.status_code}")
        except Exception as e:
            print(f"[fetch_page] Attempt {attempt}: Exception while fetching {url}: {e}")
        time.sleep(0.5)  # delay before retry
    return None


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
