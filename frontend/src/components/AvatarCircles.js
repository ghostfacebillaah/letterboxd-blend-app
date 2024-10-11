// AvatarCircles.js
import React from 'react';

const AvatarCircles = ({ username1, username2, avatars }) => {
  return (
    <div c  ssName="circles-container">
      <a href={`https://letterboxd.com/${username1}`} target="_blank" rel="noopener noreferrer">
        <div className="circle circle1" style={{ backgroundImage: `url(${avatars.avatar1})` }}></div>
      </a>
      <a href={`https://letterboxd.com/${username2}`} target="_blank" rel="noopener noreferrer">
        <div className="circle circle2" style={{ backgroundImage: `url(${avatars.avatar2})` }}></div>
      </a>
    </div>
  );
};

export default AvatarCircles;
