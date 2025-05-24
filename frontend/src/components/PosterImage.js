import React, { useState } from 'react';

const PosterImage = ({ src, alt }) => {
  const [loaded, setLoaded] = useState(false);
  const fallback = '/fallback.jpg';

  return (
    <img
      src={src || fallback}
      alt={alt}
      className={`poster ${loaded ? 'poster-loaded' : ''}`}
      loading="lazy"
      onLoad={() => setLoaded(true)}
      onError={(e) => {
        e.target.onerror = null;
        e.target.src = fallback;
        setLoaded(true);
      }}
    />
  );
};

export default PosterImage;
