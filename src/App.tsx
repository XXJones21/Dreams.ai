import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import CosmicBackground from './components/CosmicBackground';
import AgentShowcase from './components/AgentShowcase';
import DreamCarousel from './components/DreamCarousel';
import ProfilePage from './components/profile/ProfilePage';

function HomePage() {
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

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Router>
  );
}

export default App;