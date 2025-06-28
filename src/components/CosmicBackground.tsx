import React from 'react';

const CosmicBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 z-0">
      {/* Nebula Background */}
      <div className="absolute inset-0 nebula-background"></div>
      
      {/* Animated Stars */}
      <div className="absolute inset-0">
        {Array.from({ length: 100 }).map((_, i) => (
          <div
            key={i}
            className="star"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 10}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}
          />
        ))}
      </div>
      
      {/* Floating Particles */}
      <div className="absolute inset-0">
        {Array.from({ length: 30 }).map((_, i) => (
          <div
            key={i}
            className="cosmic-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 15}s`,
              animationDuration: `${8 + Math.random() * 12}s`
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default CosmicBackground;