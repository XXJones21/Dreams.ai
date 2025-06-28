import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Crown, Sparkles, Terminal, Building2 } from 'lucide-react';

const LuxuryNavigation: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { label: 'DREAMS', icon: Sparkles, href: '#dreams' },
    { label: 'GALLERY', icon: Building2, href: '#gallery' },
    { label: 'TERMINAL', icon: Terminal, href: '#terminal' },
    { label: 'EXECUTIVE', icon: Crown, href: '#executive' },
  ];

  return (
    <>
      {/* Menu Toggle Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-8 left-8 z-50 w-16 h-16 bg-gradient-to-br from-marble-black via-marble-medium to-marble-black border-2 border-brass/60 rounded-lg shadow-2xl flex items-center justify-center group"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            "0 8px 32px rgba(0,0,0,0.8), 0 0 20px rgba(207,181,59,0.3)",
            "0 12px 40px rgba(0,0,0,0.9), 0 0 30px rgba(207,181,59,0.5)",
            "0 8px 32px rgba(0,0,0,0.8), 0 0 20px rgba(207,181,59,0.3)"
          ]
        }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <X className="w-8 h-8 text-brass group-hover:text-brass-light transition-colors" />
            </motion.div>
          ) : (
            <motion.div
              key="menu"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Menu className="w-8 h-8 text-brass group-hover:text-brass-light transition-colors" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Art Deco corner accents */}
        <div className="absolute -top-1 -left-1 w-4 h-4 border-l-2 border-t-2 border-brass/80"></div>
        <div className="absolute -bottom-1 -right-1 w-4 h-4 border-r-2 border-b-2 border-brass/80"></div>
      </motion.button>

      {/* Sliding Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-marble-black/80 backdrop-blur-sm"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu Panel */}
            <motion.div
              initial={{ x: -400, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -400, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed left-0 top-0 bottom-0 z-50 w-80 bg-gradient-to-b from-marble-black via-marble-medium to-marble-black border-r-4 border-brass/40 shadow-2xl"
            >
              {/* Art Deco Header */}
              <div className="p-8 border-b-2 border-brass/30">
                <motion.div
                  initial={{ y: -20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="flex items-center space-x-4"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-brass-light via-brass to-brass-dark rounded-lg flex items-center justify-center shadow-lg">
                    <Crown className="w-6 h-6 text-marble-black" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-brass font-serif">Dreams.ai</h2>
                    <p className="text-stardust-silver/70 text-sm font-mono">NEURAL INTERFACE</p>
                  </div>
                </motion.div>

                {/* Sunburst pattern */}
                <div className="absolute top-4 right-4 w-16 h-16 opacity-20">
                  {[...Array(12)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute top-1/2 left-1/2 w-0.5 h-8 bg-brass origin-bottom"
                      style={{
                        transform: `translate(-50%, -100%) rotate(${i * 30}deg)`,
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Navigation Items */}
              <div className="p-8 space-y-4">
                {navItems.map((item, index) => (
                  <motion.a
                    key={item.label}
                    href={item.href}
                    initial={{ x: -50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.1 * index + 0.3 }}
                    className="group flex items-center space-x-4 p-4 rounded-lg bg-gradient-to-r from-marble-medium/50 to-transparent border border-brass/20 hover:border-brass/60 hover:bg-marble-medium/80 transition-all duration-300"
                    onClick={() => setIsOpen(false)}
                    whileHover={{ x: 10 }}
                  >
                    <div className="w-10 h-10 bg-gradient-to-br from-brass/20 to-brass/40 rounded-lg flex items-center justify-center group-hover:from-brass/40 group-hover:to-brass/60 transition-all duration-300">
                      <item.icon className="w-5 h-5 text-brass group-hover:text-brass-light" />
                    </div>
                    <div>
                      <span className="text-lg font-bold text-stardust-silver group-hover:text-brass transition-colors font-mono tracking-wider">
                        {item.label}
                      </span>
                    </div>
                    
                    {/* Art Deco accent */}
                    <motion.div
                      className="ml-auto w-6 h-1 bg-gradient-to-r from-transparent to-brass rounded-full"
                      animate={{
                        width: [24, 32, 24],
                        opacity: [0.5, 1, 0.5],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: index * 0.3,
                      }}
                    />
                  </motion.a>
                ))}
              </div>

              {/* Status Panel */}
              <div className="absolute bottom-8 left-8 right-8 p-4 bg-gradient-to-r from-marble-black/80 to-marble-medium/80 border border-brass/30 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-electric-blue rounded-full animate-pulse"></div>
                    <span className="text-stardust-silver/70 font-mono">QUANTUM LINK</span>
                  </div>
                  <span className="text-brass font-mono">ACTIVE</span>
                </div>
                
                <div className="mt-2 flex space-x-1">
                  {[...Array(8)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="w-1 h-4 bg-brass/40 rounded-full"
                      animate={{
                        scaleY: [0.3, 1, 0.3],
                        opacity: [0.3, 1, 0.3],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.1,
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Art Deco side pattern */}
              <div className="absolute right-0 top-1/4 bottom-1/4 w-1 bg-gradient-to-b from-transparent via-brass/60 to-transparent"></div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default LuxuryNavigation;