import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/Lf.css';

function TopCommonFilmsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { username1, username2 } = location.state || { username1: '', username2: '' };
  const [loadingMessage, setLoadingMessage] = useState('Fetching top films...');
  const [topCommonFilms, setTopCommonFilms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log(username1, username2);

    // Check if usernames are missing, set a loading message and stop the API call
    if (!username1 || !username2) {
      setLoadingMessage('Usernames are missing');
      setLoading(false);
      return;
    }

    const fetchTopCommonFilms = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/top_common_films', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username1, username2, top_n: 4 }),
        });

        const data = await response.json();
        console.log(data);

        if (response.ok) {
          // Get the common films data
          const filmsWithPosters = await Promise.all(data.top_common_films.map(async (film) => {
            const posterResponse = await fetch('http://localhost:5000/api/scrape_poster', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ film_url: `https://letterboxd.com${film.link}` }),  // Assuming `film.link` is available
            });

            const posterData = await posterResponse.json();
            return {
              ...film,
              image_url: posterData.image_url || 'No image found',
            };
          }));

          setTopCommonFilms(filmsWithPosters);
          setLoading(false);
        } else {
          setLoadingMessage(`Error: ${data.error}`);
          setLoading(false);
        }
      } catch (error) {
        setLoadingMessage('Error fetching top films');
        console.error(error);
        setLoading(false);
      }
    };

    fetchTopCommonFilms();
  }, [username1, username2]);

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
          <h1>{username1} and {username2}'s Favourite Four</h1>
          <div className="poster-grid">
            {topCommonFilms.length > 0 ? (
              topCommonFilms.map((film, index) => (
                <div className="poster-item" key={index}>
                  <a href={`https://letterboxd.com${film.link}`} target="_blank" rel="noopener noreferrer">
                    <img 
                      src={film.image_url} 
                      alt={`${film.title} (${film.year}) poster`} 
                      loading="lazy" // Implementing lazy loading
                      onError={(e) => { e.target.onerror = null; e.target.src = 'fallback-image-url.jpg'; }} // Fallback image in case of error
                    />
                  </a>
                  <div className="poster-overlay">
                    <h4>{film.title}</h4>
                    <p>{username1}'s rating: {film.rating_user1 ? film.rating_user1.toFixed(1) : 'N/A'}</p>
                    <p>{username2}'s rating: {film.rating_user2 ? film.rating_user2.toFixed(1) : 'N/A'}</p>
                  </div>
                </div>
              ))
            ) : (
              <p>No common films found.</p>
            )}
          </div>
          <div className="button-container">
            <button className="btn3" onClick={() => navigate('/')}>
              Back to Home
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default TopCommonFilmsPage;
