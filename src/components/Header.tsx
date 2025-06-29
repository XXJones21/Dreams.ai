import React, { useState } from 'react';
import { Menu, X, Brain, Sparkles } from 'lucide-react';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="relative z-50 w-full">
      <div className="container mx-auto px-6 py-8">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <div className="logo-container flex items-center space-x-3">
            <div className="relative">
              <Brain className="text-brass w-8 h-8" />
              <Sparkles className="absolute -top-1 -right-1 text-nebula-pink w-4 h-4" />
            </div>
            <div>
              <span className="text-brass text-2xl font-cinzel font-bold tracking-wider">
                DREAMS.AI
              </span>
              <div className="logo-underline"></div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {['Technology', 'Agents', 'Dreams', 'Community'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="nav-link text-stardust-silver hover:text-brass transition-all duration-300 font-inter font-medium tracking-wide"
              >
                {item}
              </a>
            ))}
          </div>

          {/* CTA Button */}
          <button className="hidden md:block marble-button">
            <span className="relative z-10 text-brass font-inter font-semibold tracking-wide">
              Start Dreaming
            </span>
          </button>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden text-brass hover:text-stardust-silver transition-colors duration-300"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </nav>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-black-marble/95 backdrop-blur-md border-t border-brass/20">
            <div className="container mx-auto px-6 py-6 space-y-4">
              {['Technology', 'Agents', 'Dreams', 'Community'].map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="block text-stardust-silver hover:text-brass transition-colors duration-300 font-inter font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item}
                </a>
              ))}
              <button className="marble-button w-full mt-4">
                <span className="relative z-10 text-brass font-inter font-semibold">
                  Start Dreaming
                </span>
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;