import React from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import CosmicBackground from './components/CosmicBackground';
import AgentShowcase from './components/AgentShowcase';
import DreamCarousel from './components/DreamCarousel';

function App() {
  return (
    <div className="min-h-screen bg-black-marble overflow-hidden">
      <CosmicBackground />
      <Header />
      <HeroSection />
      <DreamCarousel />
      <AgentShowcase />
    </div>
  );
}

export default App;