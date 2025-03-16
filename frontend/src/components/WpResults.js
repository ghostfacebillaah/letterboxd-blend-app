import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/Lf.css';

function WpResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const usernames = location.state?.usernames || [];
  const [commonFilms, setCommonFilms] = useState(location.state?.commonFilms || []);
  const [displayedMovies, setDisplayedMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFirstRender, setIsFirstRender] = useState(true);
  const [initialMovies, setInitialMovies] = useState(null); // Store the first selection
  const initialMoviesRef = useRef(null); // Store initial selection without re-rendering

  useEffect(() => {
    if (commonFilms.length > 0) {
      pickInitialMovies(commonFilms);
    }
    else {
      setLoading(false); // Stop loading if there are no common films
    }
  }, [commonFilms]);
  

  const pickInitialMovies = async (films) => {
    if (films.length === 0 || initialMoviesRef.current) return; // Stop re-selection
  
    setLoading(true);
  
    let selectedMovies = [...films].sort(() => 0.5 - Math.random()).slice(0, 5);
    initialMoviesRef.current = selectedMovies; // Store the initial selection
  
    try {
      const moviesWithPosters = await fetchPosters(selectedMovies);
  
      setTimeout(() => {
        setDisplayedMovies(moviesWithPosters);
        setLoading(false);
        setIsFirstRender(false);
      }, 100);
    } catch (error) {
      console.error("Error fetching posters:", error);
      
      setTimeout(() => {
        setDisplayedMovies(selectedMovies);
        setLoading(false);
        setIsFirstRender(false);
      }, 100);
    }
  };


  const shuffleMovies = async () => {
    if (commonFilms.length === 0) return;
  
    setLoading(true); 
  
    let shuffled = [...commonFilms].sort(() => 0.5 - Math.random()).slice(0, 5);
  
    setDisplayedMovies(shuffled.map(movie => ({ ...movie, poster: '/assets/images/placeholder.png' })));
  
    try {
      const moviesWithPosters = await fetchPosters(shuffled);
  
      setTimeout(() => {
        setDisplayedMovies(moviesWithPosters);
        setLoading(false);
      }, 100);
    } catch (error) {
      console.error("Error fetching posters:", error);
      
      setTimeout(() => {
        setDisplayedMovies(shuffled); 
        setLoading(false);
      }, 100);
    }
  };
  
  const fetchPosters = async (movies) => {
    return await Promise.all(movies.map(async (film) => {
      try {
        const posterResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scrape_poster`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ film_url: `https://letterboxd.com${film.link}` }),
        });

        const posterData = await posterResponse.json();
        return { ...film, image_url: posterData.image_url || 'No image found' };
      } catch (error) {
        console.error(`Error fetching poster for ${film.title}`, error);
        return { ...film, image_url: 'No image found' };
      }
    }));
  };
  
  return (
    <div className="result-container">
      {loading ? (
        <div className="spinner-container">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <style>
              {`.spinner_d9Sa{transform-origin:center}.spinner_qQQY{animation:spinner_ZpfF 9s linear infinite}.spinner_pote{animation:spinner_ZpfF .75s linear infinite}@keyframes spinner_ZpfF{100%{transform:rotate(360deg)}}`}
            </style>
            <path fill="#FFFFFF" d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,20a9,9,0,1,1,9-9A9,9,0,0,1,12,21Z" />
            <rect
              fill="#FFFFFF"
              className="spinner_d9Sa spinner_qQQY"
              x="11"
              y="6"
              rx="1"
              width="2"
              height="7"
            />
            <rect
              fill="#FFFFFF"
              className="spinner_d9Sa spinner_pote"
              x="11"
              y="11"
              rx="1"
              width="2"
              height="9"
            />
          </svg>
        </div>
      ) : (
        <>
          <h1>Watchlist Party Results</h1>
          <div className="poster-grid">
            {displayedMovies.length > 0 ? (
              displayedMovies.map((film, index) => (
                <div className="poster-item" key={index}>
                  <a href={`https://letterboxd.com${film.link}`} target="_blank" rel="noopener noreferrer">
                    <img 
                      src={film.image_url} 
                      alt={`${film.title_x} (${film.year}) poster`} 
                      loading="lazy" 
                      onError={(e) => { e.target.onerror = null; e.target.src = 'fallback-image-url.jpg'; }}
                    />
                  </a>
                  <div className="poster-overlay">
                  <h4>
                    {film.title_y ? film.title_y.replace(/['[\]]/g, '') : "Untitled Movie"} <br />
                    Genre: {film.genres ? film.genres.replace(/['[\]]/g, '') : "Unknown"} <br />
                    Director: {film.directors ? film.directors.replace(/['[\]]/g, '') : "Unknown"} <br />
                    Runtime: {film.runtime ? `${film.runtime} mins` : "N/A"} <br />
                    Avg. Rating: {film.avg_rating ? film.avg_rating : "Not Rated"}                                 
                  </h4>
                  </div>
                </div>
              ))
            ) : (
              <p>No common films found.</p>
            )}
          </div>
          <div className="button-container">
            <button className="btnwp" onClick={() => navigate('/watchlistparty')}>Reset filters</button>
            <button className="btnhwp" onClick={() => navigate('/')}>Back to Home</button>
            {commonFilms.length > 5 && (
              <button className="btnsh" onClick={() => shuffleMovies(commonFilms)}>Shuffle</button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default WpResults;
