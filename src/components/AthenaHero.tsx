import React from 'react';
import { motion } from 'framer-motion';

const AthenaHero: React.FC = () => {
  return (
    <div className="relative z-20 flex items-center justify-center min-h-screen">
      {/* Art Deco Frame */}
      <div className="absolute inset-8 border-4 border-brass/40 rounded-lg">
        {/* Corner decorations with ziggurat steps */}
        <div className="absolute -top-4 -left-4">
          <div className="w-16 h-16 border-l-4 border-t-4 border-brass relative">
            <div className="absolute -top-2 -left-2 w-8 h-8 border-l-2 border-t-2 border-brass/60"></div>
            <div className="absolute -top-1 -left-1 w-4 h-4 border-l-1 border-t-1 border-brass/40"></div>
          </div>
        </div>
        <div className="absolute -top-4 -right-4">
          <div className="w-16 h-16 border-r-4 border-t-4 border-brass relative">
            <div className="absolute -top-2 -right-2 w-8 h-8 border-r-2 border-t-2 border-brass/60"></div>
            <div className="absolute -top-1 -right-1 w-4 h-4 border-r-1 border-t-1 border-brass/40"></div>
          </div>
        </div>
        <div className="absolute -bottom-4 -left-4">
          <div className="w-16 h-16 border-l-4 border-b-4 border-brass relative">
            <div className="absolute -bottom-2 -left-2 w-8 h-8 border-l-2 border-b-2 border-brass/60"></div>
            <div className="absolute -bottom-1 -left-1 w-4 h-4 border-l-1 border-b-1 border-brass/40"></div>
          </div>
        </div>
        <div className="absolute -bottom-4 -right-4">
          <div className="w-16 h-16 border-r-4 border-b-4 border-brass relative">
            <div className="absolute -bottom-2 -right-2 w-8 h-8 border-r-2 border-b-2 border-brass/60"></div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 border-r-1 border-b-1 border-brass/40"></div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="relative z-30 flex items-center justify-between w-full max-w-7xl mx-auto px-12">
        
        {/* Left Side - Athena Bust */}
        <motion.div
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 2, ease: "easeOut" }}
          className="relative"
        >
          {/* Marble Base with Art Deco Pattern */}
          <div className="relative">
            {/* Base platform */}
            <motion.div
              className="w-96 h-32 bg-gradient-to-t from-marble-black via-marble-medium to-marble-light rounded-lg shadow-2xl relative overflow-hidden"
              animate={{
                boxShadow: [
                  "0 20px 60px rgba(0,0,0,0.8), 0 0 40px rgba(207,181,59,0.2)",
                  "0 25px 80px rgba(0,0,0,0.9), 0 0 60px rgba(207,181,59,0.4)",
                  "0 20px 60px rgba(0,0,0,0.8), 0 0 40px rgba(207,181,59,0.2)"
                ]
              }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              {/* Art Deco sunburst pattern */}
              <div className="absolute inset-0 opacity-30">
                {[...Array(12)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute top-1/2 left-1/2 w-1 h-16 bg-gradient-to-t from-transparent to-brass origin-bottom"
                    style={{
                      transform: `translate(-50%, -100%) rotate(${i * 30}deg)`,
                    }}
                  />
                ))}
              </div>
              
              {/* Brass inlay lines */}
              <div className="absolute inset-4 border-2 border-brass/40 rounded">
                <div className="absolute inset-2 border border-brass/20 rounded"></div>
              </div>
            </motion.div>

            {/* Athena Bust */}
            <motion.div
              className="absolute -top-20 left-1/2 transform -translate-x-1/2"
              animate={{
                y: [0, -10, 0],
              }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            >
              {/* Cosmic Mind Opening Effect */}
              <div className="relative">
                {/* Bust silhouette */}
                <div className="w-48 h-64 bg-gradient-to-b from-platinum via-chrome to-marble-light rounded-t-full relative shadow-2xl">
                  {/* Face details */}
                  <div className="absolute top-16 left-1/2 transform -translate-x-1/2">
                    {/* Eyes */}
                    <div className="flex space-x-8 mb-4">
                      <div className="w-3 h-2 bg-marble-black rounded-full"></div>
                      <div className="w-3 h-2 bg-marble-black rounded-full"></div>
                    </div>
                    {/* Nose */}
                    <div className="w-2 h-6 bg-gradient-to-b from-chrome to-marble-medium mx-auto mb-2 rounded"></div>
                    {/* Mouth */}
                    <div className="w-6 h-1 bg-marble-black rounded-full mx-auto"></div>
                  </div>

                  {/* Hair/Crown area */}
                  <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 w-32 h-16 bg-gradient-to-b from-chrome to-platinum rounded-t-full"></div>

                  {/* Cosmic Mind Opening */}
                  <motion.div
                    className="absolute -top-12 left-1/2 transform -translate-x-1/2 w-40 h-20 overflow-hidden"
                    animate={{
                      scale: [1, 1.1, 1],
                      opacity: [0.8, 1, 0.8],
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    {/* Cosmic swirl */}
                    <div className="w-full h-full bg-gradient-to-r from-electric-blue via-nebula-pink to-deep-purple rounded-full opacity-80 blur-sm"></div>
                    
                    {/* Inner cosmic energy */}
                    <motion.div
                      className="absolute inset-2 bg-gradient-to-r from-nebula-pink via-electric-blue to-deep-purple rounded-full"
                      animate={{
                        rotate: [0, 360],
                      }}
                      transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                    />
                    
                    {/* Cosmic particles */}
                    {[...Array(20)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="absolute w-1 h-1 bg-stardust-silver rounded-full"
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
                          delay: Math.random() * 2,
                        }}
                      />
                    ))}
                  </motion.div>

                  {/* Draped clothing */}
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 w-56 h-20 bg-gradient-to-b from-platinum to-chrome rounded-b-lg shadow-lg">
                    {/* Fabric folds */}
                    <div className="absolute inset-0 opacity-30">
                      {[...Array(6)].map((_, i) => (
                        <div
                          key={i}
                          className="absolute w-1 h-full bg-gradient-to-b from-transparent to-marble-black"
                          style={{ left: `${15 + i * 12}%` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Cosmic aura */}
                <motion.div
                  className="absolute inset-0 -m-8 rounded-full"
                  animate={{
                    background: [
                      'radial-gradient(circle, rgba(207,181,59,0.2) 0%, rgba(42,10,76,0.1) 50%, transparent 100%)',
                      'radial-gradient(circle, rgba(0,102,204,0.2) 0%, rgba(255,105,180,0.1) 50%, transparent 100%)',
                      'radial-gradient(circle, rgba(207,181,59,0.2) 0%, rgba(42,10,76,0.1) 50%, transparent 100%)'
                    ]
                  }}
                  transition={{ duration: 6, repeat: Infinity }}
                />
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Right Side - Three Art Deco Columns */}
        <motion.div
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 2, delay: 0.5, ease: "easeOut" }}
          className="flex space-x-8"
        >
          {[...Array(3)].map((_, index) => (
            <motion.div
              key={index}
              className="relative"
              animate={{
                y: [0, -5, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                delay: index * 0.5,
                ease: "easeInOut"
              }}
            >
              {/* Column */}
              <div className="w-20 h-96 bg-gradient-to-b from-platinum via-chrome to-marble-light rounded-lg shadow-2xl relative overflow-hidden">
                {/* Fluted details */}
                {[...Array(8)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute w-1 h-full bg-gradient-to-b from-transparent via-marble-black/20 to-transparent"
                    style={{ left: `${10 + i * 10}%` }}
                  />
                ))}

                {/* Brass accents */}
                <div className="absolute top-4 left-2 right-2 h-2 bg-gradient-to-r from-brass-dark via-brass to-brass-light rounded-full shadow-lg"></div>
                <div className="absolute bottom-4 left-2 right-2 h-2 bg-gradient-to-r from-brass-dark via-brass to-brass-light rounded-full shadow-lg"></div>
                
                {/* Middle accent band */}
                <div className="absolute top-1/2 transform -translate-y-1/2 left-1 right-1 h-4 bg-gradient-to-r from-brass-dark via-brass to-brass-light rounded shadow-lg">
                  {/* Art Deco pattern */}
                  <div className="absolute inset-1 flex justify-center items-center">
                    <div className="w-2 h-2 bg-marble-black transform rotate-45"></div>
                  </div>
                </div>
              </div>

              {/* Corinthian Capital */}
              <div className="absolute -top-8 -left-4 w-28 h-16 bg-gradient-to-b from-brass-light via-brass to-brass-dark rounded-lg shadow-xl">
                {/* Acanthus leaves pattern */}
                <div className="absolute inset-2 opacity-60">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-3 h-8 bg-gradient-to-t from-marble-black to-transparent rounded-full"
                      style={{
                        left: `${10 + i * 12}%`,
                        top: '20%',
                        transform: `rotate(${(i - 2.5) * 15}deg)`,
                      }}
                    />
                  ))}
                </div>
                
                {/* Volutes (scrolls) */}
                <div className="absolute -top-2 left-2 w-4 h-4 border-2 border-marble-black rounded-full"></div>
                <div className="absolute -top-2 right-2 w-4 h-4 border-2 border-marble-black rounded-full"></div>
              </div>

              {/* Base */}
              <div className="absolute -bottom-4 -left-2 w-24 h-8 bg-gradient-to-b from-marble-light to-marble-black rounded shadow-xl">
                <div className="absolute inset-1 border border-brass/40 rounded"></div>
              </div>

              {/* Cosmic lighting effect */}
              <motion.div
                className="absolute inset-0 -m-2 rounded-lg pointer-events-none"
                animate={{
                  boxShadow: [
                    `0 0 20px rgba(${index === 0 ? '207,181,59' : index === 1 ? '0,102,204' : '255,105,180'}, 0.3)`,
                    `0 0 40px rgba(${index === 0 ? '207,181,59' : index === 1 ? '0,102,204' : '255,105,180'}, 0.6)`,
                    `0 0 20px rgba(${index === 0 ? '207,181,59' : index === 1 ? '0,102,204' : '255,105,180'}, 0.3)`
                  ]
                }}
                transition={{ duration: 3, repeat: Infinity, delay: index * 0.7 }}
              />
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Floating Art Deco Elements */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-4 h-4 bg-gradient-to-br from-brass to-brass-dark transform rotate-45"
          style={{
            left: `${10 + Math.random() * 80}%`,
            top: `${10 + Math.random() * 80}%`,
          }}
          animate={{
            opacity: [0.3, 0.8, 0.3],
            scale: [1, 1.2, 1],
            rotate: [45, 90, 45],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            delay: i * 0.5,
          }}
        />
      ))}
    </div>
  );
};

export default AthenaHero;