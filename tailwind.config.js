/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'black-marble': '#1A1A1A',
        'brass': '#CFB53B',
        'deep-purple': '#2A0A4C',
        'electric-blue': '#0066CC',
        'nebula-pink': '#FF69B4',
        'stardust-silver': '#C0C0C0',
      },
      fontFamily: {
        'cinzel': ['Cinzel', 'serif'],
        'inter': ['Inter', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'nebula-swirl': 'nebulaSwirl 20s linear infinite',
        'particle-float': 'particleFloat 10s ease-in-out infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        nebulaSwirl: {
          '0%': { transform: 'rotate(0deg) scale(1)' },
          '50%': { transform: 'rotate(180deg) scale(1.1)' },
          '100%': { transform: 'rotate(360deg) scale(1)' },
        },
        particleFloat: {
          '0%, 100%': { transform: 'translateY(0px) translateX(0px)', opacity: '0.3' },
          '25%': { transform: 'translateY(-30px) translateX(10px)', opacity: '0.8' },
          '50%': { transform: 'translateY(-15px) translateX(-5px)', opacity: '1' },
          '75%': { transform: 'translateY(-25px) translateX(15px)', opacity: '0.6' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(207, 181, 59, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(207, 181, 59, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};