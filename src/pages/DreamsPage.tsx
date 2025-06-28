import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Terminal, Crown, Zap, Play, ChevronRight } from 'lucide-react';
import WebGLBackground from '../components/WebGLBackground';
import InteractiveButton from '../components/InteractiveButton';
import FluidMenu from '../components/FluidMenu';
import CorporateCard from '../components/CorporateCard';

const DreamsPage: React.FC = () => {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [promptIndex, setPromptIndex] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const examplePrompts = [
    'infiltrate a corporate conspiracy...',
    'command a stellar empire...',
    'escape from a space station...',
    'solve a murder in the clouds...',
    'survive a digital apocalypse...',
    'discover ancient alien tech...',
    'rule from a marble throne...',
    'navigate quantum realities...'
  ];

  const dreamExamples = [
    {
      id: 1,
      title: 'Corporate Conspiracy',
      image: 'https://images.pexels.com/photos/2041627/pexels-photo-2041627.jpeg',
      description: 'Infiltrate the marble towers of power and uncover secrets that could topple empires',
      category: 'Thriller'
    },
    {
      id: 2,
      title: 'Cosmic Dragon',
      image: 'https://images.pexels.com/photos/1205301/pexels-photo-1205301.jpeg',
      description: 'Face the stellar beast in nebula realms where physics bend to will',
      category: 'Fantasy'
    },
    {
      id: 3,
      title: 'Space Station Omega',
      image: 'https://images.pexels.com/photos/2159/flight-sky-earth-space.jpg',
      description: 'Escape through the cosmic void as reality fragments around you',
      category: 'Sci-Fi'
    },
    {
      id: 4,
      title: 'Wall Street Phantom',
      image: 'https://images.pexels.com/photos/2041396/pexels-photo-2041396.jpeg',
      description: 'Uncover supernatural secrets in golden towers of infinite wealth',
      category: 'Mystery'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setPromptIndex((prev) => (prev + 1) % examplePrompts.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleDreamSubmit = () => {
    if (currentPrompt.trim()) {
      console.log('Starting dream:', currentPrompt);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-marble-black via-marble-dark to-marble-black">
      {/* WebGL Background */}
      <WebGLBackground />

      {/* Luxury Art Deco Border Frame */}
      <div className="fixed inset-0 pointer-events-none z-10">
        <div className="absolute inset-4 border-4 border-gold/30 rounded-lg">
          {/* Corner decorations */}
          <div className="absolute -top-2 -left-2 w-8 h-8 border-l-4 border-t-4 border-gold"></div>
          <div className="absolute -top-2 -right-2 w-8 h-8 border-r-4 border-t-4 border-gold"></div>
          <div className="absolute -bottom-2 -left-2 w-8 h-8 border-l-4 border-b-4 border-gold"></div>
          <div className="absolute -bottom-2 -right-2 w-8 h-8 border-r-4 border-b-4 border-gold"></div>
        </div>
      </div>

      {/* Premium cursor follower */}
      <motion.div
        className="fixed w-6 h-6 pointer-events-none z-50 mix-blend-screen"
        style={{
          left: mousePosition.x - 12,
          top: mousePosition.y - 12,
        }}
        animate={{
          scale: isHovered ? 2 : 1,
          opacity: isHovered ? 0.8 : 0.4,
        }}
      >
        <div className="w-full h-full bg-gradient-to-br from-gold via-brass to-gold rounded-full blur-sm"></div>
        <div className="absolute inset-2 bg-gold rounded-full"></div>
      </motion.div>

      {/* Navigation */}
      <div className="absolute top-8 left-8 z-40">
        <FluidMenu />
      </div>

      {/* Main Content Container */}
      <div className="relative z-30 min-h-screen flex flex-col">
        
        {/* Hero Section */}
        <div className="flex-1 flex flex-col items-center justify-center px-8 py-20">
          
          {/* Luxury Header */}
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className="text-center mb-16 relative"
          >
            {/* Art Deco Crown with Cosmic Aura */}
            <motion.div
              className="flex justify-center mb-12 relative"
              animate={{ 
                rotate: [0, 2, -2, 0],
              }}
              transition={{ duration: 8, repeat: Infinity }}
            >
              <div className="relative">
                {/* Cosmic aura */}
                <motion.div
                  className="absolute inset-0 w-32 h-32 -m-6"
                  animate={{
                    background: [
                      'radial-gradient(circle, rgba(255,215,0,0.3) 0%, rgba(74,20,140,0.2) 50%, transparent 100%)',
                      'radial-gradient(circle, rgba(74,20,140,0.3) 0%, rgba(255,215,0,0.2) 50%, transparent 100%)',
                      'radial-gradient(circle, rgba(255,215,0,0.3) 0%, rgba(74,20,140,0.2) 50%, transparent 100%)'
                    ]
                  }}
                  transition={{ duration: 4, repeat: Infinity }}
                />
                
                {/* Main crown */}
                <div className="relative w-20 h-20 bg-gradient-to-br from-gold via-brass to-gold rounded-lg flex items-center justify-center shadow-2xl">
                  <Crown className="w-12 h-12 text-marble-black" />
                  
                  {/* Luxury shine effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-lg"
                    animate={{
                      x: ['-100%', '100%'],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                  />
                </div>

                {/* Orbiting luxury particles */}
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 bg-gradient-to-br from-gold to-brass rounded-full shadow-lg"
                    style={{
                      left: '50%',
                      top: '50%',
                    }}
                    animate={{
                      rotate: [0, 360],
                      x: Math.cos((i / 8) * Math.PI * 2) * 60,
                      y: Math.sin((i / 8) * Math.PI * 2) * 60,
                    }}
                    transition={{
                      duration: 12,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            </motion.div>

            {/* Luxury Typography */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 1.2 }}
              className="relative"
            >
              <h1 className="text-8xl md:text-9xl font-luxury font-bold mb-4 relative">
                <span className="bg-gradient-to-r from-gold via-brass to-gold bg-clip-text text-transparent drop-shadow-2xl">
                  What will you
                </span>
              </h1>
              
              <h1 className="text-8xl md:text-9xl font-luxury font-bold mb-8 relative">
                <span className="bg-gradient-to-r from-gold via-brass to-gold bg-clip-text text-transparent drop-shadow-2xl">
                  DREAM?
                </span>
                
                {/* Lightning accent */}
                <motion.div
                  className="absolute -top-4 -right-8"
                  animate={{
                    opacity: [0, 1, 0],
                    scale: [0.8, 1.2, 0.8],
                    rotate: [0, 10, -10, 0],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    delay: 2,
                  }}
                >
                  <Zap className="w-16 h-16 text-terminal-green drop-shadow-lg" />
                </motion.div>
              </h1>

              {/* Luxury subtitle */}
              <motion.p
                className="text-2xl md:text-3xl text-platinum font-corporate tracking-wide max-w-5xl mx-auto leading-relaxed"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1, duration: 1 }}
              >
                Enter the realm where{' '}
                <span className="text-gold font-bold">corporate power</span>{' '}
                meets{' '}
                <span className="text-nebula-purple font-bold">cosmic infinity</span>
              </motion.p>
            </motion.div>
          </motion.div>

          {/* Premium Dream Examples */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5, duration: 1 }}
            className="w-full max-w-7xl mb-16"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {dreamExamples.map((dream, index) => (
                <motion.div
                  key={dream.id}
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.7 + index * 0.1 }}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                >
                  <CorporateCard
                    title={dream.title}
                    description={dream.description}
                    image={dream.image}
                    category={dream.category}
                    onClick={() => console.log('Selected dream:', dream.title)}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Luxury Dream Input Terminal */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2, duration: 1 }}
            className="w-full max-w-4xl"
          >
            <div className="relative">
              {/* Art Deco frame */}
              <div className="absolute -inset-4 bg-gradient-to-r from-gold/20 via-brass/30 to-gold/20 rounded-2xl blur-xl"></div>
              
              <div className="relative bg-gradient-to-br from-marble-black via-marble-dark to-marble-black rounded-2xl border-2 border-gold/40 p-12 shadow-2xl">
                
                {/* Luxury terminal header */}
                <div className="flex items-center justify-between mb-10 pb-8 border-b-2 border-gold/30">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-gold to-brass rounded-lg flex items-center justify-center shadow-lg">
                      <Terminal className="w-6 h-6 text-marble-black" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-corporate font-bold text-gold tracking-wider">
                        DREAM INTERFACE
                      </h3>
                      <p className="text-platinum/70 font-terminal text-sm tracking-wider">
                        NEURAL LINK v3.0 • QUANTUM ENCRYPTED
                      </p>
                    </div>
                  </div>
                  
                  {/* Status indicators */}
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-terminal-green rounded-full animate-pulse shadow-lg"></div>
                      <span className="font-terminal text-terminal-green text-sm font-bold">ONLINE</span>
                    </div>
                    <div className="flex space-x-1">
                      {[...Array(4)].map((_, i) => (
                        <motion.div
                          key={i}
                          className="w-1 h-6 bg-gold/60 rounded-full"
                          animate={{
                            scaleY: [0.3, 1, 0.3],
                            opacity: [0.3, 1, 0.3],
                          }}
                          transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Input area */}
                <div className="relative">
                  <textarea
                    value={currentPrompt}
                    onChange={(e) => setCurrentPrompt(e.target.value)}
                    placeholder=""
                    className="w-full h-48 bg-gradient-to-br from-marble-dark/90 to-marble-black/90 border-2 border-brass/40 rounded-xl p-8 text-platinum placeholder-platinum/50 font-corporate text-xl resize-none focus:border-gold focus:outline-none focus:ring-4 focus:ring-gold/20 transition-all duration-500 backdrop-blur-sm shadow-inner"
                  />
                  
                  {/* Animated placeholder */}
                  {!currentPrompt && (
                    <AnimatePresence mode="wait">
                      <motion.div
                        key={promptIndex}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 1 }}
                        className="absolute left-8 top-8 text-2xl text-gold/60 pointer-events-none font-terminal italic"
                      >
                        {examplePrompts[promptIndex]}
                      </motion.div>
                    </AnimatePresence>
                  )}

                  {/* Luxury scan line */}
                  <motion.div
                    className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-terminal-green to-transparent rounded-full"
                    animate={{
                      x: ['-100%', '100%'],
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                  />
                </div>

                {/* Luxury action button */}
                <div className="mt-10">
                  <motion.button
                    onClick={handleDreamSubmit}
                    className="w-full bg-gradient-to-r from-gold via-brass to-gold text-marble-black font-corporate font-bold text-2xl py-6 rounded-xl shadow-2xl relative overflow-hidden group"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                  >
                    {/* Button shine effect */}
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                      animate={{
                        x: ['-100%', '100%'],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'linear',
                      }}
                    />
                    
                    <div className="relative flex items-center justify-center space-x-4">
                      <Play className="w-8 h-8" />
                      <span>INITIATE DREAM SEQUENCE</span>
                      <ChevronRight className="w-8 h-8" />
                    </div>
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Luxury Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.5, duration: 1 }}
          className="relative z-30 py-12 border-t border-gold/20"
        >
          <div className="max-w-7xl mx-auto px-8">
            <div className="flex items-center justify-center space-x-12 text-platinum/60 font-terminal text-sm tracking-wider">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-terminal-green rounded-full animate-pulse"></div>
                <span>POWERED BY ARTIFICIAL INTELLIGENCE</span>
              </div>
              <div className="w-px h-6 bg-gold/30"></div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gold rounded-full animate-pulse delay-300"></div>
                <span>SECURED BY QUANTUM ENCRYPTION</span>
              </div>
              <div className="w-px h-6 bg-gold/30"></div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-nebula-purple rounded-full animate-pulse delay-500"></div>
                <span>INSPIRED BY INFINITY</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DreamsPage;