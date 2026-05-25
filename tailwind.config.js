/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Dreams.ai OLED design-system tokens (design-system/dreams.ai/MASTER.md)
        'oled': {
          bg: '#000000',        // background
          primary: '#0F0F23',   // primary surface
          midnight: '#1E1B4B',  // secondary / midnight blue
          cta: '#E11D48',       // CTA / play red
          text: '#F8FAFC',      // foreground text
        },
        // Legacy cosmic palette (kept so existing surfaces still build)
        'black-marble': '#1A1A1A',
        'brass': '#CFB53B',
        'deep-purple': '#2A0A4C',
        'electric-blue': '#0066CC',
        'nebula-pink': '#FF69B4',
        'stardust-silver': '#C0C0C0',
      },
      fontFamily: {
        'atkinson': ['Atkinson Hyperlegible', 'system-ui', 'sans-serif'],
        'sans': ['Atkinson Hyperlegible', 'system-ui', 'sans-serif'],
        'cinzel': ['Cinzel', 'serif'],
        'inter': ['Inter', 'sans-serif'],
      },
      minHeight: {
        'touch': '44px',
      },
      minWidth: {
        'touch': '44px',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'nebula-swirl': 'nebulaSwirl 20s linear infinite',
        'particle-float': 'particleFloat 10s ease-in-out infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'tap-ring': 'tapRing 600ms ease-out forwards',
        'pulse-soft': 'pulseSoft 1.6s ease-in-out infinite',
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
        tapRing: {
          '0%': { transform: 'translate(-50%, -50%) scale(0.4)', opacity: '0.9' },
          '100%': { transform: 'translate(-50%, -50%) scale(1.6)', opacity: '0' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.55' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};