import React, { useState } from 'react';
import MarbleBust from './MarbleBust';
import ArtDecoColumns from './ArtDecoColumns';
import { ChevronDown, Play, Sparkles } from 'lucide-react';

const HeroSection: React.FC = () => {
  const [dreamPrompt, setDreamPrompt] = useState('');

  const handleDreamSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (dreamPrompt.trim()) {
      // This would trigger the agent workflow
      console.log('Starting dream:', dreamPrompt);
    }
  };

  return (
    <section className="relative z-10 min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-6">
        {/* Art Deco Columns */}
        <ArtDecoColumns />
        
        {/* Main Content */}
        <div className="text-center space-y-8 max-w-5xl mx-auto">
          {/* Marble Bust */}
          <div className="relative mb-16">
            <MarbleBust />
          </div>

          {/* Headlines */}
          <div className="space-y-6">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-cinzel font-bold text-stardust-silver leading-tight">
              <span className="bg-gradient-to-r from-brass via-stardust-silver to-brass bg-clip-text text-transparent">
                DREAMS
              </span>
              <br />
              <span className="text-stardust-silver">
                COME ALIVE
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-stardust-silver/80 font-inter font-light leading-relaxed max-w-4xl mx-auto">
              Where AI agents craft dynamic interactive narratives that respond to your every choice.
              <br className="hidden md:block" />
              Experience stories that evolve, adapt, and surprise at every turn.
            </p>
          </div>

          {/* Dream Input */}
          <div className="max-w-2xl mx-auto space-y-6">
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
                disabled={!dreamPrompt.trim()}
              >
                <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300 flex items-center justify-center space-x-2">
                  <Play className="w-5 h-5" />
                  <span>Begin Your Dream</span>
                </span>
              </button>
            </form>
          </div>

          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            <div className="glass-card p-6">
              <h3 className="text-brass font-cinzel font-semibold text-lg mb-2">AI Agent Network</h3>
              <p className="text-stardust-silver/70 font-inter text-sm">Carthir, Narnion, and Cenedril work together to craft your perfect narrative experience.</p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-brass font-cinzel font-semibold text-lg mb-2">Dynamic Storytelling</h3>
              <p className="text-stardust-silver/70 font-inter text-sm">Every choice matters. Watch as your decisions reshape the story in real-time.</p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-brass font-cinzel font-semibold text-lg mb-2">Visual Narratives</h3>
              <p className="text-stardust-silver/70 font-inter text-sm">Experience your dreams through cinematic visuals that adapt to your journey.</p>
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
  );
};

export default HeroSection;