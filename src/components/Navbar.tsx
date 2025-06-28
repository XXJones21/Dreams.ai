import React from 'react';
import { motion } from 'framer-motion';
import { Building2, Sparkles, Terminal, Crown } from 'lucide-react';
import Logo from './Logo';

const Navbar: React.FC = () => {
  const navItems = [
    { label: 'DREAMS', icon: Sparkles, href: '/' },
    { label: 'GALLERY', icon: Building2, href: '/stories' },
    { label: 'TERMINAL', icon: Terminal, href: '/console' },
    { label: 'EXECUTIVE', icon: Crown, href: '/premium' },
  ];

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="fixed top-0 left-0 right-0 z-50 luxury-backdrop border-b border-gold/20"
    >
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Logo />

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item, index) => (
              <motion.a
                key={item.label}
                href={item.href}
                className="group flex items-center space-x-2 px-4 py-2 rounded-lg corporate-border hover:bg-marble-dark/50 transition-all duration-300"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.6 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <item.icon className="w-5 h-5 text-gold group-hover:text-gold-light transition-colors" />
                <span className="font-corporate font-bold text-platinum group-hover:text-gold transition-colors tracking-wider">
                  {item.label}
                </span>
              </motion.a>
            ))}
          </div>

          {/* Corporate Status Indicator */}
          <motion.div
            className="hidden lg:flex items-center space-x-4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <div className="flex items-center space-x-2 brass-accent px-4 py-2 rounded-lg">
              <div className="w-2 h-2 bg-terminal-green rounded-full animate-pulse"></div>
              <span className="font-terminal text-marble-black font-bold text-sm">ONLINE</span>
            </div>
            
            <div className="flex items-center space-x-2 marble-surface px-4 py-2 rounded-lg">
              <Terminal className="w-4 h-4 text-terminal-green" />
              <span className="font-terminal text-terminal-green text-sm">v2.0</span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Corporate scan line effect */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gold to-transparent opacity-50"></div>
    </motion.nav>
  );
};

export default Navbar;