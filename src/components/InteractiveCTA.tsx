import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, ChevronRight, Sparkles } from 'lucide-react';

const InteractiveCTA: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 z-40">
      <motion.button
        className="relative group px-12 py-6 bg-gradient-to-r from-marble-black via-marble-medium to-marble-black border-2 border-brass/60 rounded-lg shadow-2xl overflow-hidden"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        whileHover={{ scale: 1.05, y: -5 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            "0 12px 40px rgba(0,0,0,0.8), 0 0 30px rgba(207,181,59,0.3)",
            "0 16px 50px rgba(0,0,0,0.9), 0 0 40px rgba(207,181,59,0.5)",
            "0 12px 40px rgba(0,0,0,0.8), 0 0 30px rgba(207,181,59,0.3)"
          ]
        }}
        transition={{ duration: 4, repeat: Infinity }}
      >
        {/* Marble texture overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-marble-black/90 via-marble-medium/90 to-marble-black/90"></div>
        
        {/* Brass shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-brass/30 to-transparent"
          animate={{
            x: ['-100%', '100%'],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Content */}
        <div className="relative flex items-center space-x-4">
          {/* Icon */}
          <motion.div
            className="w-8 h-8 bg-gradient-to-br from-brass-light to-brass-dark rounded-full flex items-center justify-center"
            animate={{
              rotate: isHovered ? 360 : 0,
            }}
            transition={{ duration: 0.8 }}
          >
            <Play className="w-4 h-4 text-marble-black ml-0.5" />
          </motion.div>

          {/* Text */}
          <span className="text-xl font-bold text-brass font-serif tracking-wider">
            ENTER THE DREAM
          </span>

          {/* Arrow */}
          <motion.div
            animate={{
              x: isHovered ? 8 : 0,
            }}
            transition={{ duration: 0.3 }}
          >
            <ChevronRight className="w-6 h-6 text-brass" />
          </motion.div>
        </div>

        {/* Floating particles */}
        {isHovered && (
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(12)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-brass rounded-full"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                  y: [0, -20, -40],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: Math.random() * 1.5,
                }}
              />
            ))}
          </div>
        )}

        {/* Art Deco corner accents */}
        <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2 border-brass/60"></div>
        <div className="absolute top-2 right-2 w-4 h-4 border-r-2 border-t-2 border-brass/60"></div>
        <div className="absolute bottom-2 left-2 w-4 h-4 border-l-2 border-b-2 border-brass/60"></div>
        <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2 border-brass/60"></div>

        {/* Status indicator */}
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-electric-blue rounded-full animate-pulse shadow-lg">
          <div className="absolute inset-1 bg-stardust-silver rounded-full"></div>
        </div>
      </motion.button>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
        className="text-center mt-4 text-stardust-silver/70 font-mono text-sm tracking-wider"
      >
        NEURAL INTERFACE • QUANTUM ENCRYPTED • AI POWERED
      </motion.p>
    </div>
  );
};

export default InteractiveCTA;