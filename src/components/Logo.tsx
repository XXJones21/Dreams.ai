import React from 'react';
import { motion } from 'framer-motion';

const Logo: React.FC = () => {
  return (
    <motion.div
      className="flex items-center space-x-4"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* The Thinker Statue with Corporate Marble Texture */}
      <div className="relative">
        <motion.div
          className="w-12 h-12 marble-surface rounded-lg flex items-center justify-center art-deco-corner"
          animate={{ 
            boxShadow: [
              "0 0 20px rgba(255, 215, 0, 0.3)",
              "0 0 40px rgba(255, 215, 0, 0.5)",
              "0 0 20px rgba(255, 215, 0, 0.3)"
            ]
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {/* Simplified Thinker representation */}
          <div className="w-8 h-8 bg-gradient-to-br from-platinum to-chrome rounded-full relative">
            {/* Head with cosmic vapor effect */}
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-nebula-purple rounded-full opacity-70 animate-pulse"></div>
            <div className="absolute -top-2 right-0 w-2 h-2 bg-nebula-blue rounded-full opacity-50 animate-pulse delay-300"></div>
            <div className="absolute -top-1 right-1 w-1 h-1 bg-gold rounded-full animate-pulse delay-500"></div>
          </div>
        </motion.div>
        
        {/* Cosmic vapor clouds */}
        <motion.div
          className="absolute -top-2 -right-2 w-6 h-6"
          animate={{ 
            rotate: [0, 360],
            scale: [1, 1.2, 1]
          }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          <div className="w-full h-full bg-gradient-to-r from-nebula-purple via-nebula-blue to-nebula-pink rounded-full opacity-30 blur-sm"></div>
        </motion.div>
      </div>

      {/* Dreams.ai Typography */}
      <div className="flex flex-col">
        <motion.h1
          className="text-2xl font-corporate font-bold wall-street-text leading-none"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          Dreams
        </motion.h1>
        <motion.div
          className="flex items-center space-x-1"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          <span className="text-lg font-corporate font-bold text-gold">.ai</span>
          <motion.div
            className="w-2 h-2 bg-terminal-green rounded-full"
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Logo;