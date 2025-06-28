/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Exact color palette from specifications
        'marble-black': '#1A1A1A',
        'marble-medium': '#2A2A2A',
        'marble-light': '#3A3A3A',
        'brass-dark': '#8B6914',
        'brass': '#CFB53B',
        'brass-light': '#DAA520',
        'deep-purple': '#2A0A4C',
        'electric-blue': '#0066CC',
        'nebula-pink': '#FF69B4',
        'stardust-silver': '#C0C0C0',
        'platinum': '#E5E4E2',
        'chrome': '#C0C0C0',
      },
      fontFamily: {
        'serif': ['Playfair Display', 'serif'],
        'mono': ['Courier New', 'monospace'],
        'sans': ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'marble-texture': 'linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 25%, #3A3A3A 50%, #2A2A2A 75%, #1A1A1A 100%)',
        'brass-gradient': 'linear-gradient(135deg, #8B6914 0%, #CFB53B 50%, #DAA520 100%)',
        'cosmic-gradient': 'linear-gradient(135deg, #2A0A4C 0%, #0066CC 50%, #FF69B4 100%)',
      },
      boxShadow: {
        'marble': '0 8px 32px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(207, 181, 59, 0.2)',
        'brass': '0 4px 20px rgba(207, 181, 59, 0.4), inset 0 1px 0 rgba(218, 165, 32, 0.3)',
        'cosmic': '0 0 50px rgba(42, 10, 76, 0.5)',
        'luxury': '0 20px 60px rgba(0, 0, 0, 0.9), 0 0 30px rgba(207, 181, 59, 0.1)',
      },
      animation: {
        'marble-shimmer': 'marble-shimmer 6s ease-in-out infinite',
        'brass-glow': 'brass-glow 3s ease-in-out infinite alternate',
        'cosmic-drift': 'cosmic-drift 20s ease-in-out infinite',
        'luxury-scan': 'luxury-scan 4s linear infinite',
      },
      keyframes: {
        'marble-shimmer': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'brass-glow': {
          '0%': { boxShadow: '0 0 20px rgba(207, 181, 59, 0.4)' },
          '100%': { boxShadow: '0 0 40px rgba(218, 165, 32, 0.6)' },
        },
        'cosmic-drift': {
          '0%, 100%': { transform: 'translateX(0) translateY(0) rotate(0deg)' },
          '33%': { transform: 'translateX(30px) translateY(-20px) rotate(120deg)' },
          '66%': { transform: 'translateX(-20px) translateY(30px) rotate(240deg)' },
        },
        'luxury-scan': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100vw)' },
        },
      },
    },
  },
  plugins: [],
}