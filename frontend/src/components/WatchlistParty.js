import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// import '../styles/Wlp.css'; Adjust the path to match the file location

const WatchlistParty = () => {
    const [usernames, setUsernames] = useState(['']); // Initial input box for usernames
    const navigate = useNavigate();

    const addInputBox = () => {
        setUsernames([...usernames, '']); // Add new empty input box
    };

    const removeInputBox = (index) => {
        const updatedUsernames = usernames.filter((_, i) => i !== index); // Remove the selected input box
        setUsernames(updatedUsernames);
    };

    const handleChange = (index, value) => {
        const updatedUsernames = usernames.map((username, i) => (i === index ? value : username));
        setUsernames(updatedUsernames);
    };

    const goToResultPage = () => {
        navigate('/wpresults', { state: { usernames } }); // Pass the array of usernames
    };

    return (
        <div className="home-container">
            <h1 className="title">Watchlist Party</h1>
            <form className="home-form">
                {usernames.map((username, index) => (
                    <div className="input-box-container" key={index}>
                        <button type="button" className="remove-button" onClick={() => removeInputBox(index)}>-</button>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => handleChange(index, e.target.value)}
                            placeholder={`Username ${index + 1}`}
                            required
                            className="input-box"
                        />
                        <button type="button" className="add-button" onClick={addInputBox}>+</button>
                    </div>
                ))}
                <br />
                <button type="button" className="submit-button" onClick={goToResultPage}>
                    Go to Result Page
                </button>
            </form>
        </div>
    );
};

export default WatchlistParty;
