import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // Import useNavigate
import '../styles/App.css';

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate(); // Get the navigate function for navigation
  const { username1, username2 } = location.state || { username1: '', username2: '' };
  const [loadingMessage, setLoadingMessage] = useState('Calculating...');
  const [blendPercentage, setBlendPercentage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [avatars, setAvatars] = useState({ avatar1: '', avatar2: '' });
  const [quote, setQuote] = useState('');

  useEffect(() => {
    const fetchResults = async () => {
      try {
        // Fetch blend percentage
        const responseBlend = await fetch('${process.env.REACT_APP_BACKEND_URL}/api/calculate_blend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username1, username2 }),
        });
        const blendData = await responseBlend.json();
        setBlendPercentage(blendData.blend_percentage);

        // Fetch profile avatars
        const responseAvatars = await fetch('${process.env.REACT_APP_BACKEND_URL}/api/profile_avatars', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username1, username2 }),
        });
        const avatarData = await responseAvatars.json();
        setAvatars({ avatar1: avatarData.avatar1, avatar2: avatarData.avatar2 });

        setLoading(false);
      } catch (error) {
        setLoadingMessage('Error fetching results');
        console.error(error);
      }
    };

    fetchResults();
  }, [username1, username2]);

  useEffect(() => {
    // Function to provide quotes based on blend percentage
    const getQuote = (percentage) => {
      if (percentage < 10) return `"Sometimes, the most unexpected encounters lead to the most profound friendships." – Three Colors: Red (1994, dir. Krzysztof Kieślowski)`;
      if (percentage < 20) return `"It’s not the kind of people we meet that matters, but the kind of friendships we make." – The Trouble with Harry (1955, dir. Alfred Hitchcock)`;
      if (percentage < 30) return `"The most profound connections are often found in the unspoken moments of understanding between friends." – Charulata (1964, dir. Satyajit Ray)`;
      if (percentage < 40) return `"In the midst of chaos, we find the true strength of our connections with others." – Ran (1985, dir. Akira Kurosawa)`;
      if (percentage < 50) return `"We are all islands, and it’s through others that we discover our own shores." – Solaris (1972, dir. Andrei Tarkovsky)`;
      if (percentage < 60) return `"In the end, we are all strangers, but in our hearts, we are familiar." – Pierrot le Fou (1965, dir. Jean-Luc Godard)`;
      if (percentage < 70) return `"The closest people are the ones who understand the depths of your silence." – Autumn Sonata (1978, dir. Ingmar Bergman)`;
      if (percentage < 80) return `"Sometimes the strongest connections are the ones we never speak of." – In the Mood for Love (2000, dir. Wong Kar-wai)`;
      if (percentage < 90) return `"C'est comme si j'avais rencontré une part de moi-même. (It’s as if I met a part of myself)" – Portrait of a Lady on Fire (2019, dir. Céline Sciamma)`;
      return `"I would rather share one lifetime with you than face all the ages of this world alone." – The Lord of the Rings: The Fellowship of the Ring (2001, dir. Peter Jackson)`;
    };  

    setQuote(getQuote(blendPercentage));
  }, [blendPercentage]);

  return (
    <div className="result-container">
      {loading ? (
        <div className="spinner-container">
          {/* Loading spinner */}
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
          <div className="circles-container">
           <a href={`https://letterboxd.com/${username1}`} target="_blank" rel="noopener noreferrer">
            <div className="circle circle1" style={{ backgroundImage: `url(${avatars.avatar1 || 'default-avatar-url'})` }}></div>
           </a>
           <a href={`https://letterboxd.com/${username2}`} target="_blank" rel="noopener noreferrer">
            <div className="circle circle2" style={{ backgroundImage: `url(${avatars.avatar2 || 'default-avatar-url'})` }}></div>
           </a>
          </div>
          <div className="progress-text">
            Your taste match is {blendPercentage}%
          </div>
          <div className="quote-text">
            {quote}
          </div>
          <div className="button-container">
            <button className="btn1" onClick={() => navigate('/')}>
              Back to Home
            </button>
            <button className="btn2" onClick={() => navigate('/lovedfilms', { state: { username1, username2 } })}>
              See your Four Favourites
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default ResultPage;
