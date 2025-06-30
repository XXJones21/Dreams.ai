import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './components/auth/AuthProvider';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import CosmicBackground from './components/CosmicBackground';
import AgentShowcase from './components/AgentShowcase';
import DreamCarousel from './components/DreamCarousel';
import ProfilePage from './components/profile/ProfilePage';
import FeedPage from './pages/FeedPage';
import AuthTest from './components/auth/AuthTest';
import DreamDetailPage from "./pages/DreamDetailPage";
import { supabase } from './lib/supabase';

function SupabaseTest() {
  useEffect(() => {
    async function test() {
      console.log('VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL);
      console.log('VITE_SUPABASE_ANON_KEY:', import.meta.env.VITE_SUPABASE_ANON_KEY);
      try {
        const { data, error } = await supabase.from('profiles').select('*').limit(1);
        if (error) {
          console.error('Supabase test error:', error);
        } else {
          console.log('Supabase test data:', data);
        }
      } catch (err) {
        console.error('Supabase test exception:', err);
      }
    }
    test();
  }, []);
  return null;
}

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
    <>
      <SupabaseTest />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } 
            />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/dreams" element={<FeedPage />} />
            <Route path="/dreams/:dreamId" element={<DreamDetailPage />} />
            <Route path="/auth/test" element={<AuthTest />} />
            {/* Catch all route */}
            <Route path="*" element={<HomePage />} />
          </Routes>
        </Router>
      </AuthProvider>
    </>
  );
}

export default App;