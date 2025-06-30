import React, { useState, useEffect } from 'react';
import { Menu, X, Brain, Sparkles, User, LogOut, Home, Library, TrendingUp } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import AuthModal from './auth/AuthModal';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setIsLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    window.location.href = '/';
  };

  const handleStartDreaming = () => {
    if (user) {
      // User is logged in, go to profile or dreams
      window.location.href = '/profile';
    } else {
      // User not logged in, open auth modal
      setIsAuthModalOpen(true);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthModalOpen(false);
    // Redirect to main page after successful authentication
    window.location.href = '/';
  };

  const isProfilePage = location.pathname === '/profile';
  const isFeedPage = location.pathname === '/feed' || location.pathname === '/dreams';

  const getNavigationItems = () => {
    if (isProfilePage) {
      return [
        { href: '/', label: 'Home', icon: Home },
        { href: '/feed', label: 'Dreams', icon: TrendingUp }
      ];
    } else if (isFeedPage) {
      return [
        { href: '/', label: 'Home', icon: Home },
        { href: '/profile', label: 'Library', icon: Library, requiresAuth: true }
      ];
    } else {
      return [
        { href: '#technology', label: 'Technology' },
        { href: '#agents', label: 'Agents' },
        { href: '/feed', label: 'Dreams', icon: TrendingUp }
      ];
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <>
      <header className="relative z-50 w-full">
        <div className="container mx-auto px-6 py-8">
          <nav className="flex items-center justify-between">
            {/* Logo */}
            <div className="logo-container flex items-center space-x-3">
              <div className="relative">
                <Brain className="text-brass w-8 h-8" />
                <Sparkles className="absolute -top-1 -right-1 text-brass w-4 h-4" />
              </div>
              <div>
                <a href="/" className="text-brass text-2xl font-cinzel font-bold tracking-wider">
                  DREAMS.AI
                </a>
                <div className="logo-underline"></div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                
                // Skip items that require auth when user is not authenticated
                if (item.requiresAuth && !user) return null;
                
                return (
                  <a
                    key={item.href}
                    href={item.href}
                    className="nav-link text-stardust-silver hover:text-brass transition-all duration-300 font-inter font-medium tracking-wide flex items-center space-x-2"
                  >
                    {Icon && <Icon className="w-4 h-4" />}
                    <span>{item.label}</span>
                  </a>
                );
              })}
            </div>

            {/* User Actions */}
            <div className="hidden md:flex items-center space-x-4">
              {isLoading ? (
                <div className="w-8 h-8 animate-spin border-2 border-brass border-t-transparent rounded-full"></div>
              ) : user ? (
                <div className="flex items-center space-x-4">
                  {!isProfilePage && (
                    <a
                      href="/profile"
                      className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors"
                    >
                      <User className="w-5 h-5" />
                      <span className="font-inter font-medium">Profile</span>
                    </a>
                  )}
                  <button
                    onClick={handleSignOut}
                    className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors"
                  >
                    <LogOut className="w-5 h-5" />
                    <span className="font-inter font-medium">Sign Out</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setIsAuthModalOpen(true)}
                    className="text-stardust-silver hover:text-brass transition-colors font-inter font-medium"
                  >
                    Sign In
                  </button>
                  <button onClick={handleStartDreaming} className="marble-button">
                    <span className="relative z-10 text-brass font-inter font-semibold tracking-wide">
                      Start Dreaming
                    </span>
                  </button>
                </div>
              )}
            </div>

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
                {/* Navigation Links for Mobile */}
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  
                  // Skip items that require auth when user is not authenticated
                  if (item.requiresAuth && !user) return null;
                  
                  return (
                    <a
                      key={item.href}
                      href={item.href}
                      className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors font-inter font-medium"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      {Icon && <Icon className="w-5 h-5" />}
                      <span>{item.label}</span>
                    </a>
                  );
                })}
                
                {user ? (
                  <div className="space-y-4 pt-4 border-t border-brass/20">
                    {!isProfilePage && (
                      <a
                        href="/profile"
                        className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        <User className="w-5 h-5" />
                        <span className="font-inter font-medium">Profile</span>
                      </a>
                    )}
                    <button
                      onClick={() => {
                        handleSignOut();
                        setIsMenuOpen(false);
                      }}
                      className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors"
                    >
                      <LogOut className="w-5 h-5" />
                      <span className="font-inter font-medium">Sign Out</span>
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4 pt-4 border-t border-brass/20">
                    <button
                      onClick={() => {
                        setIsAuthModalOpen(true);
                        setIsMenuOpen(false);
                      }}
                      className="block text-stardust-silver hover:text-brass transition-colors font-inter font-medium"
                    >
                      Sign In
                    </button>
                    <button onClick={handleStartDreaming} className="marble-button w-full">
                      <span className="relative z-10 text-brass font-inter font-semibold">
                        Start Dreaming
                      </span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal 
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
};

export default Header;