# Letterboxd Blend

**Letterboxd Blend** is a web app that calculates the similarity ("blend percentage") between two Letterboxd users based on their movie ratings and preferences. It also showcases the top four films both users have rated highly in common, and helps groups discover movies they all want to watch by finding overlaps in their watchlists with customizable filters.

### Features:
- **Blend Percentage Calculation**: Analyzes and quantifies how similar two users’ movie tastes are by combining multiple metrics. It uses Spearman's rank correlation to measure the strength and direction of association between the users' ratings for commonly watched films. In addition, it applies Jaccard similarity to compare various categorical attributes such as genres, directors, themes, countries, and more. This multi-dimensional approach, including the consideration of the proportion of common movies between both users, ensures that both rating behavior and broader cinematic preferences are captured, resulting in a nuanced and accurate "blend percentage."
  
![Screenshot (1040)](https://github.com/user-attachments/assets/c6f5fb41-465d-4493-9821-199d2d8402f7)


- **Top Common Films**: Showcases four standout films that both users have rated highly, complete with posters and direct links to their Letterboxd pages. Films watched on the same date are given priority, adding an extra layer of shared experience to the selection.

![Screenshot (1043)](https://github.com/user-attachments/assets/abb8b244-9a91-4175-aa03-2833f6235bd1)


  - **Watchlist Party**: Allows multiple users to input their Letterboxd watchlists and analyzes their watchlists to suggest five films most likely to appeal to the whole group. 
  
![Screenshot (1045)](https://github.com/user-attachments/assets/8e22f531-a283-4910-b80c-f368b2214299)

  Includes advanced filters for runtime, genre, decade, and directors, helping groups find common movies to watch together and a shuffle option, which lets users explore different combinations—perfect for when no one can decide what to watch.

![Screenshot (1053)](https://github.com/user-attachments/assets/5eb6737f-4726-46b2-87e4-248162998361)
<p align="center"><i><small> RIP, Mr Lynch. </small></i></p>



- **Interactive UI**: The app features a clean, intuitive React-based interface which balances minimalism with interactivity, ensuring effortless discovery of shared tastes and enabling user(s) to make group movie decisions in a visually appealing, responsive environment. On the main blend page, users can enter two Letterboxd usernames into prominently placed input fields centered on the screen. Upon submission, the app fetches and displays the blend percentage. From this page, the user(s) can proceed to see their top four common films ahead. Each film is presented with its poster image, and clicking on it would open the movie’s Letterboxd page in a new tab for quick exploration. An overlay displays the name and respective ratings of both users.
  For the watchlist overlap (group viewing) feature, the UI provides a dynamic form where multiple usernames can be added or removed using plus and minus buttons, allowing flexible input. Users can apply a variety of filters—including runtime ranges, genres, decades, and specific directors—to narrow down the selection based on group preferences. After submitting the usernames, the app displays the list of overlapping watchlist films, presented as a grid of clickable posters. A shuffle button lets users randomly reorder the filtered watchlist, helping break indecision by surfacing unexpected movie options. An overlay panel on these movies posters displays detailed information about the film—such as title, year, genres, runtime, director(s), and synopsis—without leaving the page. Clicking on these posters also includes direct links to the movie’s Letterboxd page, enhancing user engagement and exploration.



### Technical Overview:
- **Frontend**: Built with React, offering a smooth and minimalistic user experience.
- **Backend**: The backend is built on a Flask-based API, which enables all data processing logic. When a user inputs Letterboxd usernames, the backend initiates web scraping routines using libraries like requests and BeautifulSoup to fetch publicly available profile data in real time. This includes the list of films watched or rated, ratings given, watch (diary) dates, and watchlist entries. Once the raw data is scraped, it is parsed and normalized — for example, extracting consistent movie IDs or URLs to allow accurate matching between users. The backend then leverages statistical methods and similarity algorithms.
For the top common films, the backend filters and ranks movies that appear in both users’ profiles, giving priority to those with high ratings and shared watch dates. Poster URLs and direct Letterboxd links are fetched or constructed for seamless frontend display.
The watchlist overlap feature performs set intersections on multiple users’ watchlists and applies filtering criteria such as genre, runtime, decade, and director. Efficient data structures like sets and dictionaries are employed to optimize performance, especially when handling multiple users or large watchlists.
The Flask API exposes well-structured JSON endpoints consumed by the React frontend, ensuring fast and reliable communication between client and server. Error handling and validation mechanisms are in place to manage invalid usernames or network issues gracefully.

  

### Future Plans:
- **Recommendations**: Introduce Machine Learning-based movie recommendations based on common preferences.
- **Enhanced UI/UX**: Improve the design and aesthetics.

### How to Run:
1. Clone the repository.
2. Install dependencies for both the backend and frontend.
3. Run the Flask backend (python app.py) and React frontend (npm start) to use the app locally.

---
