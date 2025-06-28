import React from 'react';

const ArtDecoColumns: React.FC = () => {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Left Column */}
      <div className="art-deco-column left-column">
        <div className="column-shaft">
          <div className="brass-inlay"></div>
          <div className="geometric-pattern pattern-1"></div>
        </div>
        <div className="column-capital">
          <div className="capital-ornament"></div>
        </div>
      </div>

      {/* Center Column */}
      <div className="art-deco-column center-column">
        <div className="column-shaft">
          <div className="brass-inlay"></div>
          <div className="geometric-pattern pattern-2"></div>
        </div>
        <div className="column-capital">
          <div className="capital-ornament"></div>
        </div>
      </div>

      {/* Right Column */}
      <div className="art-deco-column right-column">
        <div className="column-shaft">
          <div className="brass-inlay"></div>
          <div className="geometric-pattern pattern-3"></div>
        </div>
        <div className="column-capital">
          <div className="capital-ornament"></div>
        </div>
      </div>

      {/* Connecting Architectural Elements */}
      <div className="architectural-frame">
        <div className="top-beam"></div>
        <div className="corner-ornament top-left"></div>
        <div className="corner-ornament top-right"></div>
        <div className="corner-ornament bottom-left"></div>
        <div className="corner-ornament bottom-right"></div>
      </div>
    </div>
  );
};

export default ArtDecoColumns;