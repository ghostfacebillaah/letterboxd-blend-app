import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ResultPage from './components/ResultPage';
import LovedFilms from './components/LovedFilms';
import WatchlistParty from './components/WatchlistParty';
import WpResults from './components/WpResults';

function App() {
  const [usernames, setUsernames] = useState({ username1: '', username2: '' });

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={<HomePage setUsernames={setUsernames} />}
        />
        <Route
          path="/result"
          element={<ResultPage usernames={usernames} />}
        />
        <Route
          path="/lovedfilms"
          element={<LovedFilms usernames={usernames} />}
        />
        {/* 
        <Route
          path="/watchlistparty"
          element={<WatchlistParty />}
        />
        <Route
          path="/WpResults"
          element={<WpResults />}
        /> 
        */}
      </Routes>
    </Router>
  );
}

export default App;
