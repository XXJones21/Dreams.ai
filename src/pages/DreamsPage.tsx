import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Sparkles, Terminal, Crown } from 'lucide-react';

const DreamsPage: React.FC = () => {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [promptIndex, setPromptIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);

  const examplePrompts = [
    'explore a haunted hospital',
    'slay the dragon',
    'escape from a space station',
    'solve a murder mystery',
    'survive a zombie apocalypse',
    'discover ancient treasures',
    'infiltrate a corporate conspiracy',
    'command a starship fleet'
  ];

  const dreamExamples = [
    {
      id: 1,
      title: 'Corporate Conspiracy',
      image: 'https://images.pexels.com/photos/2041627/pexels-photo-2041627.jpeg',
      description: 'Infiltrate the marble towers of power',
      category: 'Thriller'
    },
    {
      id: 2,
      title: 'Cosmic Dragon',
      image: 'https://images.pexels.com/photos/1205301/pexels-photo-1205301.jpeg',
      description: 'Face the stellar beast in nebula realms',
      category: 'Fantasy'
    },
    {
      id: 3,
      title: 'Space Station Omega',
      image: 'https://images.pexels.com/photos/2159/flight-sky-earth-space.jpg',
      description: 'Escape through the cosmic void',
      category: 'Sci-Fi'
    },
    {
      id: 4,
      title: 'Wall Street Phantom',
      image: 'https://images.pexels.com/photos/2041396/pexels-photo-2041396.jpeg',
      description: 'Uncover secrets in golden towers',
      category: 'Mystery'
    },
    {
      id: 5,
      title: 'Nebula Kingdom',
      image: 'https://images.pexels.com/photos/1205301/pexels-photo-1205301.jpeg',
      description: 'Rule among the stars',
      category: 'Adventure'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setPromptIndex((prev) => (prev + 1) % examplePrompts.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleDreamSubmit = () => {
    if (currentPrompt.trim()) {
      console.log('Starting dream:', currentPrompt);
      // Here we would integrate with the agent system
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Corporate Cosmic Background */}
      <div className="absolute inset-0">
        {/* Marble texture base */}
        <div className="absolute inset-0 bg-marble-texture opacity-90"></div>
        
        {/* Floating geometric elements */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-gold rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [1, 1.5, 1],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>

        {/* Art Deco geometric patterns */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
          <div className="absolute top-20 left-20 w-32 h-32 border-2 border-gold transform rotate-45"></div>
          <div className="absolute top-40 right-32 w-24 h-24 border border-brass transform rotate-12"></div>
          <div className="absolute bottom-32 left-1/4 w-40 h-40 border border-gold transform -rotate-30"></div>
          <div className="absolute bottom-20 right-20 w-28 h-28 border-2 border-brass transform rotate-60"></div>
        </div>

        {/* Nebula effects */}
        <div className="absolute inset-0 bg-nebula-gradient opacity-20"></div>
        
        {/* Corporate scan lines */}
        <div className="absolute inset-0 corporate-scan-line"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="text-center mb-16"
        >
          {/* Corporate Crown Icon */}
          <motion.div
            className="flex justify-center mb-8"
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            <Crown className="w-16 h-16 text-gold drop-shadow-lg" />
          </motion.div>

          <h1 className="text-6xl md:text-8xl font-luxury font-bold mb-6 wall-street-text">
            What will you
          </h1>
          <h1 className="text-6xl md:text-8xl font-luxury font-bold mb-8 wall-street-text">
            DREAM?
          </h1>
          
          <motion.p
            className="text-xl md:text-2xl text-platinum/80 font-corporate tracking-wide max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 1 }}
          >
            Enter the realm where <span className="text-gold font-bold">corporate power</span> meets <span className="text-nebula-purple font-bold">cosmic infinity</span>
          </motion.p>
        </motion.div>

        {/* Dream Examples Carousel */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="w-full max-w-6xl mb-12"
        >
          <div className="flex overflow-x-auto space-x-6 pb-4 scrollbar-hide">
            {dreamExamples.map((dream, index) => (
              <motion.div
                key={dream.id}
                className="flex-shrink-0 w-80 marble-surface rounded-lg overflow-hidden art-deco-corner group cursor-pointer"
                whileHover={{ scale: 1.05, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={dream.image}
                    alt={dream.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-marble-black via-transparent to-transparent"></div>
                  <div className="absolute top-4 right-4 brass-accent px-3 py-1 rounded-full">
                    <span className="text-marble-black font-corporate font-bold text-sm">{dream.category}</span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-corporate font-bold text-gold mb-2">{dream.title}</h3>
                  <p className="text-platinum/70 font-modern">{dream.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Dream Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="w-full max-w-2xl"
        >
          <div className="marble-surface rounded-lg p-8 art-deco-corner relative">
            {/* Terminal header */}
            <div className="flex items-center mb-6 pb-4 border-b border-gold/30">
              <Terminal className="w-6 h-6 text-terminal-green mr-3" />
              <span className="terminal-glow font-terminal text-lg">DREAM_INTERFACE_v2.0</span>
              <div className="ml-auto flex space-x-2">
                <div className="w-3 h-3 rounded-full bg-terminal-red"></div>
                <div className="w-3 h-3 rounded-full bg-terminal-amber"></div>
                <div className="w-3 h-3 rounded-full bg-terminal-green"></div>
              </div>
            </div>

            <div className="relative">
              <textarea
                value={currentPrompt}
                onChange={(e) => setCurrentPrompt(e.target.value)}
                placeholder="Describe your dream..."
                className="w-full h-32 bg-marble-dark border-2 border-gold/30 rounded-lg p-4 text-platinum placeholder-platinum/50 font-corporate text-lg resize-none focus:border-gold focus:outline-none focus:ring-2 focus:ring-gold/20 transition-all duration-300"
              />
              
              {/* Animated example prompt */}
              {!currentPrompt && (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={promptIndex}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.5 }}
                    className="absolute left-4 top-4 text-xl text-gold/60 pointer-events-none font-terminal italic"
                  >
                    {examplePrompts[promptIndex]}
                  </motion.div>
                </AnimatePresence>
              )}
            </div>

            <motion.button
              onClick={handleDreamSubmit}
              className="w-full mt-6 trump-tower-gold text-marble-black font-corporate font-bold text-xl py-4 rounded-lg wall-street-shadow transition-all duration-300 hover:scale-105 active:scale-95"
              whileHover={{ boxShadow: "0 0 30px rgba(255, 215, 0, 0.5)" }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center justify-center space-x-3">
                <Sparkles className="w-6 h-6" />
                <span>INITIATE DREAM SEQUENCE</span>
                <Sparkles className="w-6 h-6" />
              </div>
            </motion.button>
          </div>
        </motion.div>

        {/* Corporate Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 1 }}
          className="mt-16 text-center"
        >
          <p className="text-platinum/60 font-terminal text-sm tracking-wider">
            POWERED BY ARTIFICIAL INTELLIGENCE • SECURED BY BLOCKCHAIN • INSPIRED BY INFINITY
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default DreamsPage;