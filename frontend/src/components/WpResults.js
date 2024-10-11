import React from 'react';
import { useLocation } from 'react-router-dom';
// import '../styles/Wlp.css';  Adjust the path to match the file location


const WpResults = () => {
    const location = useLocation();
    const { usernames } = location.state || { usernames: [] }; // Get the usernames from navigation state

    return (
        <div>
            <h1>Watchlist Party Results</h1>
            <ul>
                {usernames.map((username, index) => (
                    <li key={index}>{username}</li>
                ))}
            </ul>
        </div>
    );
};

export default WpResults;
