import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "../styles/App.css";

const WatchlistParty = () => {
    const [movies, setMovies] = useState([""]);
    const [loading, setLoading] = useState(false); // Loading state
    const navigate = useNavigate();

    const addTextbox = () => {
        setMovies([...movies, ""]);
    };

    const removeTextbox = (index) => {
        if (movies.length > 1) {
            setMovies(movies.filter((_, i) => i !== index));
        }
    };

    const handleInputChange = (index, value) => {
        const newMovies = [...movies];
        newMovies[index] = value;
        setMovies(newMovies);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const runtimeMin = document.getElementById("runtime-min").value || null;
        const runtimeMax = document.getElementById("runtime-max").value || null;
        const genre = document.getElementById("genre").value || null;
        const decade = document.getElementById("decade").value || null;
        const director = document.getElementById("director").value.trim() || null;
    
        const requestBody = {
            usernames: movies,
            min_runtime: document.getElementById("runtime-min").value || null,
            max_runtime: document.getElementById("runtime-max").value || null,
            genre: document.getElementById("genre").value || null,
            decade: document.getElementById("decade").value || null,
            director: document.getElementById("director").value.trim() || null,
        };
    
        console.log("Sending request to backend from watchlistpartyjs:", requestBody); // Debugging

        // Navigate immediately to WpResults with a loading state
        /*navigate("/wpresults", { 
            state: { 
                usernames: movies, 
                commonFilms: [], // Empty initially
                filters: { runtimeMin, runtimeMax, genre, decade, director },
                loading: true  // Ensure loading is true initially
            } 
        });*/
    
        try {
            const response = await fetch("http://localhost:5000/api/watchlist-party", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody),
            });
    
            const data = await response.json();
            console.log("Received response to watchlistpartyjs:", data); // Debugging
    
            setLoading(false);
            navigate("/wpresults", { 
                state: { 
                    replace: true, // Ensures it updates rather than pushing a new history entry
                    usernames: movies, 
                    commonFilms: data.common_films, // Ensure this key matches the backend response
                    filters: { runtimeMin, runtimeMax, genre, decade, director },
                    loading: false  // Ensure loading is true initially
                } 
            });            
        } catch (error) {
            console.error("Error fetching watchlist results:", error);
        }
    };
    

    return (
        <div className="watchlist-container">
            <h1 className="title">Watchlist Party</h1>
            <form id="watchlist-form" onSubmit={handleSubmit}>
                <div id="textbox-group">
                    {movies.map((movie, index) => (
                        <div key={index} className="textbox-container floating-label">
                            <input
                                type="text"
                                className="input-box movie-input"
                                placeholder=" "
                                value={movie}
                                onChange={(e) => handleInputChange(index, e.target.value)}
                                required
                            />
                            <label>Username {index + 1}</label>
                            <button type="button" className="icon-button add-btn" onClick={addTextbox}>+</button>
                            <button type="button" className="icon-button remove-btn" onClick={() => removeTextbox(index)}>−</button>
                        </div>
                    ))}
                </div>

                {/* Filters */}
                <div className="filters">
                    <div className="filter-group">
                        <label>Runtime (in minutes)</label>
                        <input type="number" id="runtime-min" placeholder="Min" />
                        <input type="number" id="runtime-max" placeholder="Max" />
                    </div>
                    <div className="filter-group">
                        <label>Genre</label>
                        <select id="genre">
                            <option value="">Any</option>
                            <option value="Action">Action</option>
                            <option value="Adventure">Adventure</option>
                            <option value="Animation">Animation</option>
                            <option value="Comedy">Comedy</option>
                            <option value="Crime">Crime</option>
                            <option value="Drama">Drama</option>
                            <option value="Documentary">Documentary</option>
                            <option value="Family">Family</option>
                            <option value="Fantasy">Fantasy</option>
                            <option value="History">History</option>
                            <option value="Horror">Horror</option>
                            <option value="Music">Music</option>
                            <option value="Mystery">Mystery</option>
                            <option value="Romance">Romance</option>
                            <option value="Science Fiction">Science Fiction</option>
                            <option value="Thriller">Thriller</option>
                            <option value="TV Movie">TV Movie</option>
                            <option value="War">War</option>
                            <option value="Western">Western</option>
                        </select>
                    </div>
                    <div className="filter-group">
                        <label>Decade</label>
                        <select id="decade">
                            <option value="">Any</option>
                            <option value="2020s">2020s</option>
                            <option value="2010s">2010s</option>
                            <option value="2000s">2000s</option>
                            <option value="1990s">1990s</option>
                            <option value="1980s">1980s</option>
                            <option value="1970s">1970s</option>
                            <option value="1960s">1960s</option>
                            <option value="1950s">1950s</option>
                            <option value="1940s">1940s</option>
                            <option value="1930s">1930s</option>
                            <option value="1920s">1920s</option>
                            <option value="1910s">1910s</option>
                            <option value="1900s">1900s</option>
                            <option value="1890s">1890s</option>
                            <option value="1880s">1880s</option>
                            <option value="1870s">1870s</option>
                        </select>
                    </div>
                    <div className="filter-group">
                        <label>Director</label>
                        <input type="text" id="director" placeholder="Director's Name" />
                    </div>
                </div>

                {/* Submit Button */}
                <button type="submit" className="wp-button" disabled={loading}>
                    {loading ? (
                        <svg
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <style>
                                {`.spinner_d9Sa{transform-origin:center}.spinner_qQQY{animation:spinner_ZpfF 9s linear infinite}.spinner_pote{animation:spinner_ZpfF .75s linear infinite}@keyframes spinner_ZpfF{100%{transform:rotate(360deg)}}`}
                            </style>
                            <path fill="#FFFFFF" d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,20a9,9,0,1,1,9-9A9,9,0,0,1,12,21Z" />
                            <rect fill="#FFFFFF" className="spinner_d9Sa spinner_qQQY" x="11" y="6" rx="1" width="2" height="7" />
                            <rect fill="#FFFFFF" className="spinner_d9Sa spinner_pote" x="11" y="11" rx="1" width="2" height="9" />
                        </svg>
                    ) : (
                        "Find Movies"
                    )}
                </button>
                <button className="btnhwp" onClick={() => navigate('/')}>Back to Home</button>
            </form>
        </div>
    );
};

export default WatchlistParty;