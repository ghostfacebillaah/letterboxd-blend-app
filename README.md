# Letterboxd Blend

**Letterboxd Blend** is a web app that calculates the similarity ("blend percentage") between two Letterboxd users based on their movie ratings and preferences. The app also showcases the top four films that both users have rated highly in common.

### Features:
- **Blend Percentage Calculation**: Compares two users’ movie tastes using a combination of Spearman's rank correlation for ratings and Jaccard similarity for various attributes like genres, directors, and more.
  
  ![image](https://github.com/user-attachments/assets/a31af927-a87b-4f38-914c-0c4971e5327f)


- **Top Common Films**: Displays the top four movies that the users have both rated highly, along with their posters and links to the movies' Letterboxd pages.
  
  ![image](https://github.com/user-attachments/assets/4b394ae0-c303-408c-ad82-11cbe5ab9d4c)

  
- **Interactive UI**: A user-friendly interface where two usernames can be entered, and the results are displayed in an engaging way.

### Technical Overview:
- **Frontend**: Built with React, offering a smooth and minimalistic user experience.
- **Backend**: A Flask-based API that handles scraping Letterboxd data, calculating blend percentages, and serving the results to the frontend.
- **Blend Formula**: 
  1. Proportion of common films.
  2. Spearman's rank correlation for movie ratings.
  3. Jaccard similarity for attributes such as genres, directors, themes, countries, and more.
  

### Future Plans:
- **Recommendations**: Introduce machine learning-based movie recommendations based on common preferences.
- **Watchlist Party**: Watchlist overlap of two or more users, filtering and sorting.
- **Enhanced UI/UX**: Improve the design and aesthetics.

### How to Run:
1. Clone the repository.
2. Install dependencies for both the backend and frontend.
3. Run the Flask backend and React frontend to use the app locally.

---
