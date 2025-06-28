import React from 'react';

const MarbleBust: React.FC = () => {
  return (
    <div className="relative w-80 h-80 mx-auto marble-bust-container">
      {/* Marble Base */}
      <div className="marble-base">
        <div className="marble-texture"></div>
        <div className="brass-trim"></div>
      </div>
      
      {/* Bust Silhouette */}
      <div className="bust-silhouette">
        {/* Marble texture overlay */}
        <div className="marble-bust-texture"></div>
        
        {/* Cosmic Head Effect */}
        <div className="cosmic-head">
          <div className="nebula-swirl"></div>
          <div className="cosmic-particles">
            {Array.from({ length: 20 }).map((_, i) => (
              <div
                key={i}
                className="particle"
                style={{
                  left: `${20 + Math.random() * 60}%`,
                  top: `${20 + Math.random() * 60}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  animationDuration: `${2 + Math.random() * 2}s`
                }}
              />
            ))}
          </div>
        </div>
        
        {/* Art Deco Geometric Overlay */}
        <div className="geometric-overlay">
          <div className="zigzag-pattern"></div>
          <div className="sunburst-pattern"></div>
        </div>
      </div>
      
      {/* Ambient Lighting */}
      <div className="ambient-light"></div>
    </div>
  );
};

export default MarbleBust;