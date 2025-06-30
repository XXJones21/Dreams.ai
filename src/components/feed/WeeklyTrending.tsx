import React, { useState, useEffect } from 'react';
import { TrendingUp, Crown, Siren as Fire, Star, Calendar } from 'lucide-react';
import DreamCard from './DreamCard';

interface TrendingDream {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  creator: {
    id: string;
    name: string;
    avatar?: string;
    verified?: boolean;
  };
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    views: number;
  };
  tags: string[];
  category: string;
  emotion: string;
  theme: string;
  created_at: string;
  is_trending: boolean;
  is_featured: boolean;
  trend_score: number;
  rank: number;
}

interface WeeklyTrendingProps {
  onDreamInteraction: (dreamId: string, action: 'like' | 'comment' | 'share' | 'bookmark') => void;
  isAuthenticated: boolean;
}

const WeeklyTrending: React.FC<WeeklyTrendingProps> = ({ onDreamInteraction, isAuthenticated }) => {
  const [trendingDreams, setTrendingDreams] = useState<TrendingDream[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');

  useEffect(() => {
    loadTrendingDreams();
  }, [selectedPeriod]);

  const loadTrendingDreams = async () => {
    try {
      setLoading(true);
      
      // Mock trending dreams data
      const mockTrendingDreams: TrendingDream[] = [
        {
          id: '1',
          title: 'The Last Library on Earth',
          excerpt: 'In a post-apocalyptic world, you discover the final repository of human knowledge...',
          content: 'Full content here...',
          creator: {
            id: 'user1',
            name: 'Elena Rodriguez',
            avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=100',
            verified: true
          },
          engagement: {
            likes: 15420,
            comments: 892,
            shares: 2156,
            views: 45230
          },
          tags: ['post-apocalyptic', 'library', 'knowledge', 'survival'],
          category: 'Sci-Fi',
          emotion: 'wonder',
          theme: 'knowledge preservation',
          created_at: '2025-01-10T14:30:00Z',
          is_trending: true,
          is_featured: true,
          trend_score: 98.5,
          rank: 1
        },
        {
          id: '2',
          title: 'Dancing with Shadows',
          excerpt: 'A mysterious ballroom where shadows come alive and dance with the living...',
          content: 'Full content here...',
          creator: {
            id: 'user2',
            name: 'Marcus Chen',
            avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100'
          },
          engagement: {
            likes: 12890,
            comments: 654,
            shares: 1789,
            views: 38920
          },
          tags: ['supernatural', 'dance', 'ballroom', 'shadows'],
          category: 'Fantasy',
          emotion: 'mystery',
          theme: 'supernatural encounter',
          created_at: '2025-01-12T09:15:00Z',
          is_trending: true,
          is_featured: false,
          trend_score: 94.2,
          rank: 2
        },
        {
          id: '3',
          title: 'The Memory Merchant',
          excerpt: 'In a world where memories can be bought and sold, you run a black market memory shop...',
          content: 'Full content here...',
          creator: {
            id: 'user3',
            name: 'Aria Kim',
            avatar: 'https://images.pexels.com/photos/697509/pexels-photo-697509.jpeg?auto=compress&cs=tinysrgb&w=100',
            verified: true
          },
          engagement: {
            likes: 11234,
            comments: 567,
            shares: 1456,
            views: 32100
          },
          tags: ['cyberpunk', 'memories', 'black market', 'identity'],
          category: 'Sci-Fi',
          emotion: 'intrigue',
          theme: 'memory manipulation',
          created_at: '2025-01-11T16:45:00Z',
          is_trending: true,
          is_featured: false,
          trend_score: 89.7,
          rank: 3
        }
      ];

      setTrendingDreams(mockTrendingDreams);
    } catch (error) {
      console.error('Error loading trending dreams:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="w-5 h-5 text-yellow-400" />;
      case 2:
        return <Star className="w-5 h-5 text-gray-300" />;
      case 3:
        return <Fire className="w-5 h-5 text-orange-400" />;
      default:
        return <span className="text-brass font-bold">#{rank}</span>;
    }
  };

  const getPeriodLabel = (period: string) => {
    switch (period) {
      case 'day': return 'Today';
      case 'week': return 'This Week';
      case 'month': return 'This Month';
      default: return 'This Week';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-cinzel font-bold text-stardust-silver flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-brass" />
            <span>Weekly Trending</span>
          </h2>
          
          {/* Period Selector */}
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-brass" />
            <div className="flex bg-black-marble/50 border border-brass/30 rounded-lg overflow-hidden">
              {(['day', 'week', 'month'] as const).map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-4 py-2 text-sm font-inter transition-colors ${
                    selectedPeriod === period
                      ? 'bg-brass text-black-marble'
                      : 'text-stardust-silver hover:bg-brass/20'
                  }`}
                >
                  {getPeriodLabel(period)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="glass-card p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-cinzel font-bold text-brass">
                {trendingDreams.length}
              </div>
              <div className="text-sm text-stardust-silver/60">Trending Dreams</div>
            </div>
            <div>
              <div className="text-2xl font-cinzel font-bold text-electric-blue">
                {trendingDreams.reduce((sum, dream) => sum + dream.engagement.likes, 0).toLocaleString()}
              </div>
              <div className="text-sm text-stardust-silver/60">Total Likes</div>
            </div>
            <div>
              <div className="text-2xl font-cinzel font-bold text-nebula-pink">
                {trendingDreams.reduce((sum, dream) => sum + dream.engagement.views, 0).toLocaleString()}
              </div>
              <div className="text-sm text-stardust-silver/60">Total Views</div>
            </div>
            <div>
              <div className="text-2xl font-cinzel font-bold text-green-400">
                {trendingDreams.reduce((sum, dream) => sum + dream.engagement.shares, 0).toLocaleString()}
              </div>
              <div className="text-sm text-stardust-silver/60">Total Shares</div>
            </div>
          </div>
        </div>
      </div>

      {/* Trending Dreams List */}
      {loading ? (
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-8 h-8 bg-brass/20 rounded-full"></div>
                <div className="w-12 h-12 bg-brass/20 rounded-full"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-brass/20 rounded w-1/4"></div>
                  <div className="h-3 bg-brass/10 rounded w-1/6"></div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="h-6 bg-brass/20 rounded w-3/4"></div>
                <div className="h-4 bg-brass/10 rounded w-full"></div>
                <div className="h-4 bg-brass/10 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {trendingDreams.map((dream) => (
            <div key={dream.id} className="relative">
              {/* Rank Badge */}
              <div className="absolute -left-4 top-6 z-10 flex items-center justify-center w-12 h-12 bg-black-marble border-2 border-brass rounded-full">
                {getRankIcon(dream.rank)}
              </div>
              
              {/* Trend Score */}
              <div className="absolute -right-4 top-6 z-10 flex flex-col items-center justify-center w-16 h-16 bg-black-marble border-2 border-electric-blue rounded-full">
                <div className="text-xs font-bold text-electric-blue">
                  {dream.trend_score.toFixed(0)}
                </div>
                <div className="text-xs text-stardust-silver/60">
                  score
                </div>
              </div>

              {/* Dream Card with enhanced styling for trending */}
              <div className="ml-8 mr-8">
                <DreamCard
                  dream={dream}
                  onInteraction={onDreamInteraction}
                  isAuthenticated={isAuthenticated}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Call to Action */}
      <div className="glass-card p-8 text-center">
        <h3 className="text-xl font-cinzel font-bold text-stardust-silver mb-4">
          Want to see your dream trending?
        </h3>
        <p className="text-stardust-silver/70 mb-6">
          Create engaging, unique dreams that capture the imagination of our community
        </p>
        <button className="marble-button-large">
          <span className="relative z-10 text-brass font-inter font-semibold">
            Create Your Dream
          </span>
        </button>
      </div>
    </div>
  );
};

export default WeeklyTrending;