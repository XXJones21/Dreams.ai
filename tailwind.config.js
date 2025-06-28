/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 1980s Wall Street Corporate Colors
        'marble-black': '#0a0a0a',
        'marble-dark': '#1a1a1a',
        'marble-medium': '#2a2a2a',
        'marble-light': '#3a3a3a',
        'brass-dark': '#8b6914',
        'brass': '#b8860b',
        'brass-light': '#daa520',
        'gold-dark': '#b8860b',
        'gold': '#ffd700',
        'gold-light': '#ffed4e',
        'platinum': '#e5e4e2',
        'chrome': '#c0c0c0',
        
        // Cosmic Nebula Colors
        'nebula-purple': '#4a148c',
        'nebula-blue': '#1a237e',
        'nebula-pink': '#880e4f',
        'cosmic-teal': '#004d40',
        'stellar-white': '#f8f9fa',
        
        // Corporate Terminal Colors
        'terminal-green': '#00ff41',
        'terminal-amber': '#ffb000',
        'terminal-red': '#ff0040',
      },
      fontFamily: {
        'corporate': ['Orbitron', 'monospace'],
        'terminal': ['Courier New', 'monospace'],
        'luxury': ['Playfair Display', 'serif'],
        'modern': ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'marble-texture': 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%, #0a0a0a 100%)',
        'brass-gradient': 'linear-gradient(135deg, #8b6914 0%, #b8860b 50%, #daa520 100%)',
        'gold-gradient': 'linear-gradient(135deg, #b8860b 0%, #ffd700 50%, #ffed4e 100%)',
        'nebula-gradient': 'linear-gradient(135deg, #4a148c 0%, #1a237e 50%, #880e4f 100%)',
        'corporate-cosmic': 'linear-gradient(135deg, #0a0a0a 0%, #1a237e 25%, #4a148c 50%, #880e4f 75%, #0a0a0a 100%)',
        'wall-street': 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
      },
      boxShadow: {
        'marble': '0 8px 32px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 215, 0, 0.2)',
        'brass': '0 4px 20px rgba(184, 134, 11, 0.4), inset 0 1px 0 rgba(255, 215, 0, 0.3)',
        'gold': '0 8px 40px rgba(255, 215, 0, 0.3)',
        'nebula': '0 0 50px rgba(74, 20, 140, 0.5)',
        'corporate': '0 20px 60px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 215, 0, 0.1)',
      },
      animation: {
        'marble-shimmer': 'marble-shimmer 3s ease-in-out infinite',
        'brass-glow': 'brass-glow 2s ease-in-out infinite alternate',
        'terminal-flicker': 'terminal-flicker 0.1s infinite linear',
        'nebula-drift': 'nebula-drift 20s ease-in-out infinite',
        'gold-pulse': 'gold-pulse 2s ease-in-out infinite',
        'corporate-scan': 'corporate-scan 3s linear infinite',
      },
      keyframes: {
        'marble-shimmer': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'brass-glow': {
          '0%': { boxShadow: '0 0 20px rgba(184, 134, 11, 0.4)' },
          '100%': { boxShadow: '0 0 40px rgba(255, 215, 0, 0.6)' },
        },
        'terminal-flicker': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'nebula-drift': {
          '0%, 100%': { transform: 'translateX(0) translateY(0) rotate(0deg)' },
          '33%': { transform: 'translateX(30px) translateY(-20px) rotate(120deg)' },
          '66%': { transform: 'translateX(-20px) translateY(30px) rotate(240deg)' },
        },
        'gold-pulse': {
          '0%, 100%': { opacity: '0.8', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
        'corporate-scan': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100vw)' },
        },
      },
    },
  },
  plugins: [],
}