import React from 'react';
import CosmicNebulaBackground from './components/CosmicNebulaBackground';
import AthenaHero from './components/AthenaHero';
import LuxuryNavigation from './components/LuxuryNavigation';
import InteractiveCTA from './components/InteractiveCTA';

function App() {
  return (
    <div className="min-h-screen bg-marble-black overflow-hidden">
      {/* WebGL Cosmic Background */}
      <CosmicNebulaBackground />
      
      {/* Navigation */}
      <LuxuryNavigation />
      
      {/* Main Hero Section */}
      <AthenaHero />
      
      {/* Interactive CTA */}
      <InteractiveCTA />
      
      {/* Luxury scan line effect */}
      <div className="fixed bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-brass to-transparent opacity-60"></div>
    </div>
  );
}

export default App;