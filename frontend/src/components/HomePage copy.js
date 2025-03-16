import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/App.css'; // Adjust the path to match the file location

function HomePage({ setUsernames }) {
  const [username1, setUsername1] = useState('');
  const [username2, setUsername2] = useState('');
  const navigate = useNavigate(); // Use navigate for navigation

  const handleSubmit = (e) => {
    e.preventDefault();
    setUsernames({ username1, username2 });
    navigate('/result', { state: { username1, username2 } }); // Pass usernames to result page
  };

  const handleWatchlist = (e) => {
    e.preventDefault();
    navigate('/watchlistparty'); // Navigate to WatchlistParty page
  };

  return (
    <div className="home-container">
      <h1 className="title">Letterboxd Blend</h1>
      <form onSubmit={handleSubmit} className="home-form">
        <div className="textbox-container floating-label">
          <input
            type="text"
            value={username1}
            onChange={(e) => setUsername1(e.target.value)}
            placeholder=" "
            required
            className="input-box"
          />
          <label>Username 1</label>
        </div>
        <div className="textbox-container floating-label">
          <input
            type="text"
            value={username2}
            onChange={(e) => setUsername2(e.target.value)}
            placeholder=" "
            required
            className="input-box"
          />
          <label>Username 2</label>
        </div>
        <button type="submit" className="submit-button">
          Blend
        </button>
        {/* Change type to button and add onClick handler */}
        <button type="button" className="watchlist-button" onClick={handleWatchlist}>
          Watchlist Party
        </button>
      </form>
    </div>
  );
}

export default HomePage;
