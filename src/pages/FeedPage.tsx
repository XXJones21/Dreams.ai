import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { TrendingUp, Users, BookOpen, Sparkles } from 'lucide-react';
import { supabase } from '../lib/supabase';
import CosmicBackground from '../components/CosmicBackground';
import Header from '../components/Header';
import DreamFeed from '../components/feed/DreamFeed';
import WeeklyTrending from '../components/feed/WeeklyTrending';
import DreamCollections from '../components/feed/DreamCollections';

type FeedTab = 'discover' | 'trending' | 'following' | 'collections';

const FeedPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<FeedTab>('discover');
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Check authentication status
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setIsLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Set initial tab based on URL or default
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const tab = searchParams.get('tab') as FeedTab;
    if (tab && ['discover', 'trending', 'following', 'collections'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [location]);

  const handleDreamInteraction = async (dreamId: string, action: 'like' | 'comment' | 'share' | 'bookmark') => {
    if (!user) return;
    
    try {
      // Handle dream interactions
      console.log(`User ${user.id} performed ${action} on dream ${dreamId}`);
      // Implement actual interaction logic here
    } catch (error) {
      console.error('Error handling dream interaction:', error);
    }
  };

  const tabs = [
    {
      id: 'discover' as FeedTab,
      label: 'Discover',
      icon: Sparkles,
      description: 'Explore trending and popular dreams',
      available: true
    },
    {
      id: 'trending' as FeedTab,
      label: 'Trending',
      icon: TrendingUp,
      description: 'Weekly trending dreams',
      available: true
    },
    {
      id: 'following' as FeedTab,
      label: 'Following',
      icon: Users,
      description: 'Dreams from people you follow',
      available: user !== null
    },
    {
      id: 'collections' as FeedTab,
      label: 'Collections',
      icon: BookOpen,
      description: 'Curated dream collections',
      available: true
    }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black-marble overflow-hidden">
        <CosmicBackground />
        <div className="relative z-10 min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin w-12 h-12 border-4 border-brass border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-stardust-silver">Loading feed...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black-marble overflow-hidden">
      <CosmicBackground />
      <Header />
      
      <div className="relative z-10 container mx-auto px-6 py-12">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-cinzel font-bold text-stardust-silver mb-4">
            <span className="bg-gradient-to-r from-brass via-electric-blue to-nebula-pink bg-clip-text text-transparent">
              Dream Feed
            </span>
          </h1>
          <p className="text-xl text-stardust-silver/70 font-inter max-w-2xl mx-auto">
            Discover, explore, and experience the most captivating dreams from our community
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="glass-card p-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                const isAvailable = tab.available;
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => isAvailable && setActiveTab(tab.id)}
                    disabled={!isAvailable}
                    className={`relative p-4 rounded-lg transition-all duration-300 ${
                      isActive
                        ? 'bg-brass text-black-marble'
                        : isAvailable
                          ? 'text-stardust-silver hover:bg-brass/20 hover:text-brass'
                          : 'text-stardust-silver/30 cursor-not-allowed'
                    }`}
                  >
                    <div className="flex flex-col items-center space-y-2">
                      <Icon className="w-6 h-6" />
                      <div className="text-center">
                        <div className="font-inter font-semibold text-sm">
                          {tab.label}
                        </div>
                        <div className={`text-xs ${
                          isActive ? 'text-black-marble/70' : 'text-stardust-silver/60'
                        }`}>
                          {tab.description}
                        </div>
                      </div>
                    </div>
                    
                    {!isAvailable && (
                      <div className="absolute inset-0 flex items-center justify-center bg-black-marble/50 rounded-lg">
                        <span className="text-xs text-stardust-silver/60">
                          {tab.id === 'following' ? 'Sign in required' : 'Coming soon'}
                        </span>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[600px]">
          {activeTab === 'discover' && (
            <DreamFeed
              isAuthenticated={!!user}
              userId={user?.id}
              feedType={user ? 'personalized' : 'main'}
            />
          )}
          
          {activeTab === 'trending' && (
            <WeeklyTrending
              onDreamInteraction={handleDreamInteraction}
              isAuthenticated={!!user}
            />
          )}
          
          {activeTab === 'following' && user && (
            <DreamFeed
              isAuthenticated={true}
              userId={user.id}
              feedType="following"
            />
          )}
          
          {activeTab === 'collections' && (
            <DreamCollections
              userId={user?.id}
              isAuthenticated={!!user}
              viewMode="discover"
            />
          )}
        </div>

        {/* Call to Action for Non-Authenticated Users */}
        {!user && (
          <div className="mt-12 glass-card p-8 text-center">
            <h3 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
              Join the Dreams.AI Community
            </h3>
            <p className="text-stardust-silver/70 mb-6 max-w-2xl mx-auto">
              Sign up to create your own dreams, follow other dreamers, build collections, 
              and get personalized recommendations based on your interests.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="marble-button-large">
                <span className="relative z-10 text-brass font-inter font-semibold">
                  Start Dreaming
                </span>
              </button>
              <button className="glass-button">
                <span className="relative z-10 text-stardust-silver font-inter font-medium">
                  Learn More
                </span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedPage;