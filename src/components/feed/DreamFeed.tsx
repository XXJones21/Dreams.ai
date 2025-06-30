import React, { useState, useEffect, useCallback } from 'react';
import { Heart, MessageCircle, Share2, Bookmark, TrendingUp, Filter, Search, Eye, Clock, User, Sparkles } from 'lucide-react';
import { supabase } from '../../lib/supabase';
import DreamCard from './DreamCard';
import FeedFilters from './FeedFilters';
import TrendingTags from './TrendingTags';
import InfiniteScroll from './InfiniteScroll';

interface Dream {
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
  similarity_score?: number;
}

interface FeedFilters {
  category?: string;
  emotion?: string;
  theme?: string;
  timeRange?: 'day' | 'week' | 'month' | 'all';
  sortBy?: 'trending' | 'recent' | 'popular' | 'recommended';
}

interface DreamFeedProps {
  isAuthenticated: boolean;
  userId?: string;
  feedType?: 'main' | 'personalized' | 'trending' | 'following';
}

const DreamFeed: React.FC<DreamFeedProps> = ({ 
  isAuthenticated, 
  userId, 
  feedType = 'main' 
}) => {
  const [dreams, setDreams] = useState<Dream[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<FeedFilters>({
    sortBy: 'trending',
    timeRange: 'week'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [trendingTags, setTrendingTags] = useState<string[]>([]);

  // Load initial dreams
  useEffect(() => {
    loadDreams(true);
    loadTrendingTags();
  }, [filters, feedType, isAuthenticated]);

  // Search functionality
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (searchQuery) {
        loadDreams(true);
      }
    }, 500);

    return () => clearTimeout(delayedSearch);
  }, [searchQuery]);

  const loadTrendingTags = async () => {
    try {
      // Mock trending tags - in real implementation, this would come from analytics
      const mockTags = [
        'fantasy', 'adventure', 'mystery', 'sci-fi', 'horror', 
        'romance', 'thriller', 'comedy', 'drama', 'surreal'
      ];
      setTrendingTags(mockTags);
    } catch (error) {
      console.error('Error loading trending tags:', error);
    }
  };

  const loadDreams = async (reset = false) => {
    try {
      setLoading(true);
      const currentPage = reset ? 0 : page;
      const limit = 10;
      const offset = currentPage * limit;

      let dreams: Dream[];

      if (isAuthenticated && feedType === 'personalized') {
        dreams = await loadPersonalizedFeed(offset, limit);
      } else if (feedType === 'following') {
        dreams = await loadFollowingFeed(offset, limit);
      } else if (feedType === 'trending') {
        dreams = await loadTrendingFeed(offset, limit);
      } else {
        dreams = await loadMainFeed(offset, limit);
      }

      if (reset) {
        setDreams(dreams);
        setPage(1);
      } else {
        setDreams(prev => [...prev, ...dreams]);
        setPage(prev => prev + 1);
      }

      setHasMore(dreams.length === limit);
    } catch (error) {
      console.error('Error loading dreams:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMainFeed = async (offset: number, limit: number): Promise<Dream[]> => {
    // Mock implementation - replace with actual Supabase queries
    const mockDreams: Dream[] = [
      {
        id: '1',
        title: 'The Haunted Hospital',
        excerpt: 'Explore the abandoned corridors of St. Mary\'s Hospital...',
        content: 'Full dream content here...',
        creator: {
          id: 'user1',
          name: 'Sarah Chen',
          avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=100',
          verified: true
        },
        engagement: {
          likes: 1247,
          comments: 89,
          shares: 156,
          views: 5432
        },
        tags: ['horror', 'mystery', 'hospital', 'supernatural'],
        category: 'Horror',
        emotion: 'fear',
        theme: 'abandoned places',
        created_at: '2025-01-15T10:30:00Z',
        is_trending: true,
        is_featured: false
      },
      {
        id: '2',
        title: 'Dragon\'s Castle Quest',
        excerpt: 'A brave knight\'s journey to rescue Princess Aurelia...',
        content: 'Full dream content here...',
        creator: {
          id: 'user2',
          name: 'Marcus Rivera',
          avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100'
        },
        engagement: {
          likes: 2156,
          comments: 234,
          shares: 312,
          views: 8901
        },
        tags: ['fantasy', 'adventure', 'dragon', 'castle', 'knight'],
        category: 'Fantasy',
        emotion: 'excitement',
        theme: 'heroic journey',
        created_at: '2025-01-14T15:45:00Z',
        is_trending: true,
        is_featured: true
      },
      {
        id: '3',
        title: 'Neon Cyberpunk Streets',
        excerpt: 'Navigate the rain-soaked streets of Neo-Tokyo in 2087...',
        content: 'Full dream content here...',
        creator: {
          id: 'user3',
          name: 'Alex Kim',
          avatar: 'https://images.pexels.com/photos/697509/pexels-photo-697509.jpeg?auto=compress&cs=tinysrgb&w=100'
        },
        engagement: {
          likes: 1834,
          comments: 167,
          shares: 289,
          views: 7234
        },
        tags: ['cyberpunk', 'sci-fi', 'future', 'neon', 'tokyo'],
        category: 'Sci-Fi',
        emotion: 'wonder',
        theme: 'futuristic city',
        created_at: '2025-01-13T20:15:00Z',
        is_trending: false,
        is_featured: false
      }
    ];

    // Apply filters
    let filteredDreams = mockDreams;

    if (filters.category) {
      filteredDreams = filteredDreams.filter(dream => 
        dream.category.toLowerCase() === filters.category?.toLowerCase()
      );
    }

    if (filters.emotion) {
      filteredDreams = filteredDreams.filter(dream => 
        dream.emotion === filters.emotion
      );
    }

    if (searchQuery) {
      filteredDreams = filteredDreams.filter(dream =>
        dream.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dream.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dream.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply sorting
    switch (filters.sortBy) {
      case 'trending':
        filteredDreams.sort((a, b) => {
          if (a.is_trending && !b.is_trending) return -1;
          if (!a.is_trending && b.is_trending) return 1;
          return b.engagement.likes - a.engagement.likes;
        });
        break;
      case 'recent':
        filteredDreams.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        break;
      case 'popular':
        filteredDreams.sort((a, b) => b.engagement.likes - a.engagement.likes);
        break;
    }

    return filteredDreams.slice(offset, offset + limit);
  };

  const loadPersonalizedFeed = async (offset: number, limit: number): Promise<Dream[]> => {
    // Personalized algorithm:
    // 40% from followed users
    // 35% similar to user's posts
    // 25% trending/viral content
    
    const followedDreams = await loadFollowingFeed(0, Math.ceil(limit * 0.4));
    const similarDreams = await loadSimilarDreams(0, Math.ceil(limit * 0.35));
    const trendingDreams = await loadTrendingFeed(0, Math.ceil(limit * 0.25));

    // Combine and shuffle for natural feel
    const combinedDreams = [...followedDreams, ...similarDreams, ...trendingDreams];
    return shuffleArray(combinedDreams).slice(offset, offset + limit);
  };

  const loadFollowingFeed = async (offset: number, limit: number): Promise<Dream[]> => {
    // Mock implementation for followed users' dreams
    return [];
  };

  const loadSimilarDreams = async (offset: number, limit: number): Promise<Dream[]> => {
    // Mock implementation for dreams similar to user's content
    return [];
  };

  const loadTrendingFeed = async (offset: number, limit: number): Promise<Dream[]> => {
    // Load trending dreams based on engagement metrics
    return loadMainFeed(offset, limit);
  };

  const shuffleArray = <T,>(array: T[]): T[] => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  };

  const handleDreamInteraction = async (dreamId: string, action: 'like' | 'comment' | 'share' | 'bookmark') => {
    try {
      // Update local state optimistically
      setDreams(prev => prev.map(dream => {
        if (dream.id === dreamId) {
          const updated = { ...dream };
          switch (action) {
            case 'like':
              updated.engagement.likes += 1;
              break;
            case 'comment':
              updated.engagement.comments += 1;
              break;
            case 'share':
              updated.engagement.shares += 1;
              break;
          }
          return updated;
        }
        return dream;
      }));

      // Send to backend
      // await supabase.from('dream_interactions').insert({
      //   user_id: userId,
      //   dream_id: dreamId,
      //   action_type: action
      // });
    } catch (error) {
      console.error('Error handling dream interaction:', error);
    }
  };

  const handleFilterChange = (newFilters: Partial<FeedFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const handleTagClick = (tag: string) => {
    setSearchQuery(tag);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Feed Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-cinzel font-bold text-stardust-silver">
            {feedType === 'personalized' ? 'Your Personalized Feed' :
             feedType === 'trending' ? 'Trending Dreams' :
             feedType === 'following' ? 'Following' :
             'Discover Dreams'}
          </h2>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`glass-button flex items-center space-x-2 ${showFilters ? 'border-brass' : ''}`}
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search dreams, tags, or creators..."
            className="w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
          />
        </div>

        {/* Trending Tags */}
        <TrendingTags tags={trendingTags} onTagClick={handleTagClick} />

        {/* Filters Panel */}
        {showFilters && (
          <FeedFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            onClose={() => setShowFilters(false)}
          />
        )}
      </div>

      {/* Feed Content */}
      <div className="space-y-6">
        {dreams.length === 0 && !loading ? (
          <div className="text-center py-12">
            <Sparkles className="w-16 h-16 text-brass/50 mx-auto mb-4" />
            <h3 className="text-xl font-cinzel font-semibold text-stardust-silver mb-2">
              No dreams found
            </h3>
            <p className="text-stardust-silver/60">
              Try adjusting your filters or search terms
            </p>
          </div>
        ) : (
          <InfiniteScroll
            hasMore={hasMore}
            loadMore={() => loadDreams(false)}
            loading={loading}
          >
            <div className="space-y-6">
              {dreams.map((dream) => (
                <DreamCard
                  key={dream.id}
                  dream={dream}
                  onInteraction={handleDreamInteraction}
                  isAuthenticated={isAuthenticated}
                />
              ))}
            </div>
          </InfiniteScroll>
        )}
      </div>

      {/* Loading State */}
      {loading && dreams.length === 0 && (
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="flex items-center space-x-4 mb-4">
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
      )}
    </div>
  );
};

export default DreamFeed;