import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import CosmicBackground from './components/CosmicBackground';
import AgentShowcase from './components/AgentShowcase';
import DreamCarousel from './components/DreamCarousel';
import ProfilePage from './components/profile/ProfilePage';
import FeedPage from './pages/FeedPage';

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
        <Route path="/feed" element={<FeedPage />} />
        <Route path="/dreams" element={<FeedPage />} />
        {/* Catch all route */}
        <Route path="*" element={<HomePage />} />
      </Routes>
    </Router>
  );
}

export default App;