import React, { useState, useEffect } from 'react';
import LogoWithFluidSwirl from './LogoWithFluidSwirl';
import ArtDecoColumns from './ArtDecoColumns';
import { ChevronDown, Play, Sparkles, Zap, User } from 'lucide-react';
import { supabase } from '../lib/supabase';
import AuthModal from './auth/AuthModal';

const taglines = [
  "Conscious Creation",
  "Reality Reimagined", 
  "Vision Unleashed",
  "Dream Directed"
];

const HeroSection: React.FC = () => {
  const [dreamPrompt, setDreamPrompt] = useState('');
  const [currentTagline, setCurrentTagline] = useState(0);
  const [dreamResult, setDreamResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPopup, setShowPopup] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    // Check authentication status
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTagline((prev: number) => (prev + 1) % taglines.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStartDreaming = () => {
    if (user) {
      // User is logged in, proceed with dream creation or go to profile
      window.location.href = '/profile';
    } else {
      // User not logged in, open auth modal
      setIsAuthModalOpen(true);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthModalOpen(false);
    // Refresh the page to update user state
    window.location.reload();
  };

  const handleDreamSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dreamPrompt.trim()) return;
    
    // Check if user is authenticated
    if (!user) {
      setIsAuthModalOpen(true);
      return;
    }

    setLoading(true);
    setError(null);
    setDreamResult(null);
    setShowPopup(true);
    try {
      const response = await fetch("http://localhost:8000/api/dream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: dreamPrompt }),
      });
      if (!response.ok) throw new Error("Failed to generate dream.");
      const data = await response.json();
      setDreamResult(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <section className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="container mx-auto px-6">
          {/* Art Deco Columns */}
          <ArtDecoColumns />
          
          {/* Main Content */}
          <div className="text-center space-y-8 max-w-5xl mx-auto">
            {/* Logo with Fluid Swirl - Replacing Marble Bust */}
            <div className="relative mb-16">
              <LogoWithFluidSwirl size="large" className="mx-auto" />
            </div>

            {/* Headlines */}
            <div className="space-y-6">
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-cinzel font-bold text-stardust-silver leading-tight">
                <span className="text-brass">
                  DREAM
                </span>
                <br />
                <span className="text-stardust-silver">
                  VISIONS
                </span>
              </h1>
              
              {/* Dynamic Tagline */}
              <div className="h-16 flex items-center justify-center">
                <h2 className="text-2xl md:text-3xl font-cinzel font-semibold text-brass transition-all duration-500 transform">
                  {taglines[currentTagline]}
                </h2>
              </div>
              
              <p className="text-xl md:text-2xl text-stardust-silver/80 font-inter font-light leading-relaxed max-w-4xl mx-auto">
                Where AI agents craft dynamic interactive narratives that respond to your every choice.
                <br className="hidden md:block" />
                Experience stories that evolve, adapt, and surprise at every turn.
              </p>
            </div>

            {/* Dream Input */}
            <div className="max-w-2xl mx-auto space-y-6">
              {user ? (
                <form onSubmit={handleDreamSubmit} className="space-y-4">
                  <div className="relative">
                    <input
                      type="text"
                      value={dreamPrompt}
                      onChange={(e) => setDreamPrompt(e.target.value)}
                      placeholder="What would you like to dream about? (e.g., rescue a princess from a castle)"
                      className="w-full px-6 py-4 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none backdrop-blur-md"
                    />
                    <Sparkles className="absolute right-4 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                  </div>
                  <button 
                    type="submit"
                    className="marble-button-large group w-full"
                    disabled={!dreamPrompt.trim() || loading}
                  >
                    <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300 flex items-center justify-center space-x-2">
                      <Play className="w-5 h-5" />
                      <span>{loading ? "Generating..." : "Begin Your Dream"}</span>
                    </span>
                  </button>
                </form>
              ) : (
                <div className="space-y-4">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Sign in to start dreaming..."
                      className="w-full px-6 py-4 bg-black-marble/30 border-2 border-brass/20 rounded-lg text-stardust-silver/50 placeholder-stardust-silver/30 font-inter cursor-not-allowed"
                      disabled
                    />
                    <User className="absolute right-4 top-1/2 transform -translate-y-1/2 text-brass/50 w-5 h-5" />
                  </div>
                  <button 
                    onClick={handleStartDreaming}
                    className="marble-button-large group w-full"
                  >
                    <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300 flex items-center justify-center space-x-2">
                      <Play className="w-5 h-5" />
                      <span>Sign In to Start Dreaming</span>
                    </span>
                  </button>
                </div>
              )}

              {loading && <div className="text-brass mt-4">Generating your dream...</div>}
              {error && <div className="text-red-500 mt-4">{error}</div>}
              {dreamResult && (
                <div className="dream-result mt-8 p-6 rounded-lg bg-black-marble/70 border border-brass/30">
                  <h2 className="text-3xl font-cinzel font-bold text-brass mb-2">{dreamResult.dream_name}</h2>
                  <p className="text-lg text-stardust-silver/80 mb-2"><strong>Prompt:</strong> {dreamResult.story_prompt}</p>
                  <p className="text-lg text-stardust-silver/80 mb-2"><strong>Goal:</strong> {dreamResult.initial_goal}</p>
                  <p className="text-stardust-silver/90 mt-4">{dreamResult.pitch}</p>
                  <p className="text-xs text-stardust-silver/50 mt-2">IMN file: {dreamResult.imn_filename}</p>
                </div>
              )}
              {showPopup && (
                <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-60">
                  <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
                    {loading && (
                      <>
                        <div className="mb-4 animate-spin mx-auto w-12 h-12 border-4 border-brass border-t-transparent rounded-full"></div>
                        <h2 className="text-2xl font-bold text-brass mb-2">Generating your dream...</h2>
                        <p className="text-black-marble">Please wait while your dream is being created.</p>
                      </>
                    )}
                    {error && !loading && (
                      <>
                        <h2 className="text-2xl font-bold text-red-600 mb-2">Error</h2>
                        <p className="text-black-marble mb-4">{error}</p>
                        <button
                          className="marble-button-large mt-2"
                          onClick={() => setShowPopup(false)}
                        >
                          Close
                        </button>
                      </>
                    )}
                    {dreamResult && !loading && !error && (
                      <>
                        <h2 className="text-2xl font-bold text-brass mb-4">Dream Created!</h2>
                        <p className="text-lg text-black-marble mb-2">Your dream title:</p>
                        <div className="text-xl font-cinzel text-brass mb-4">{dreamResult.dream_name}</div>
                        <button
                          className="marble-button-large mt-2"
                          onClick={() => setShowPopup(false)}
                        >
                          Close
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Feature Highlights with Taglines */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="glass-card p-6 group hover:border-brass/40 transition-all duration-300">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-brass to-yellow-400 rounded-full flex items-center justify-center">
                    <Zap className="w-6 h-6 text-black-marble" />
                  </div>
                </div>
                <h3 className="text-brass font-cinzel font-semibold text-lg mb-2">Conscious Creation</h3>
                <p className="text-stardust-silver/70 font-inter text-sm">Take control of your narrative destiny. Every choice you make consciously shapes the story's evolution.</p>
              </div>
              <div className="glass-card p-6 group hover:border-stardust-silver/40 transition-all duration-300">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-stardust-silver to-gray-400 rounded-full flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-black-marble" />
                  </div>
                </div>
                <h3 className="text-stardust-silver font-cinzel font-semibold text-lg mb-2">Reality Reimagined</h3>
                <p className="text-stardust-silver/70 font-inter text-sm">Transform the impossible into the inevitable. Watch as AI agents reshape reality according to your vision.</p>
              </div>
              <div className="glass-card p-6 group hover:border-brass/40 transition-all duration-300">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-brass to-yellow-400 rounded-full flex items-center justify-center">
                    <Play className="w-6 h-6 text-black-marble" />
                  </div>
                </div>
                <h3 className="text-brass font-cinzel font-semibold text-lg mb-2">Vision Unleashed</h3>
                <p className="text-stardust-silver/70 font-inter text-sm">Break free from linear storytelling. Experience narratives that adapt, surprise, and evolve with unlimited potential.</p>
              </div>
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
            <div className="animate-bounce">
              <ChevronDown className="text-brass w-8 h-8" />
            </div>
          </div>
        </div>
      </section>

      {/* Auth Modal */}
      <AuthModal 
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
};

export default HeroSection;