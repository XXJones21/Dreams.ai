import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Heart, Eye, Users, Star, Lock, Globe } from 'lucide-react';

interface DreamCollection {
  id: string;
  title: string;
  description: string;
  cover_image?: string;
  creator: {
    id: string;
    name: string;
    avatar?: string;
  };
  dream_count: number;
  followers: number;
  is_public: boolean;
  is_featured: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface DreamCollectionsProps {
  userId?: string;
  isAuthenticated: boolean;
  viewMode?: 'discover' | 'my-collections';
}

const DreamCollections: React.FC<DreamCollectionsProps> = ({ 
  userId, 
  isAuthenticated, 
  viewMode = 'discover' 
}) => {
  const [collections, setCollections] = useState<DreamCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadCollections();
  }, [viewMode, userId]);

  const loadCollections = async () => {
    try {
      setLoading(true);
      
      // Mock collections data
      const mockCollections: DreamCollection[] = [
        {
          id: '1',
          title: 'Cosmic Adventures',
          description: 'Journey through space and time with these mind-bending sci-fi dreams',
          cover_image: 'https://images.pexels.com/photos/2387793/pexels-photo-2387793.jpeg?auto=compress&cs=tinysrgb&w=400',
          creator: {
            id: 'curator1',
            name: 'Dream Curator',
            avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=100'
          },
          dream_count: 24,
          followers: 1520,
          is_public: true,
          is_featured: true,
          tags: ['sci-fi', 'space', 'adventure', 'cosmic'],
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-15T12:00:00Z'
        },
        {
          id: '2',
          title: 'Haunted Realms',
          description: 'Spine-chilling horror dreams that will keep you on the edge of your seat',
          cover_image: 'https://images.pexels.com/photos/263402/pexels-photo-263402.jpeg?auto=compress&cs=tinysrgb&w=400',
          creator: {
            id: 'curator2',
            name: 'Horror Master',
            avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100'
          },
          dream_count: 18,
          followers: 892,
          is_public: true,
          is_featured: false,
          tags: ['horror', 'supernatural', 'mystery', 'dark'],
          created_at: '2025-01-05T00:00:00Z',
          updated_at: '2025-01-14T18:30:00Z'
        },
        {
          id: '3',
          title: 'Fantasy Kingdoms',
          description: 'Magical realms filled with dragons, knights, and epic quests',
          cover_image: 'https://images.pexels.com/photos/161154/castle-hohenschwangau-alps-alpsee-161154.jpeg?auto=compress&cs=tinysrgb&w=400',
          creator: {
            id: 'curator3',
            name: 'Fantasy Weaver',
            avatar: 'https://images.pexels.com/photos/697509/pexels-photo-697509.jpeg?auto=compress&cs=tinysrgb&w=100'
          },
          dream_count: 31,
          followers: 2156,
          is_public: true,
          is_featured: true,
          tags: ['fantasy', 'magic', 'adventure', 'medieval'],
          created_at: '2024-12-20T00:00:00Z',
          updated_at: '2025-01-13T14:15:00Z'
        }
      ];

      setCollections(mockCollections);
    } catch (error) {
      console.error('Error loading collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowCollection = async (collectionId: string) => {
    try {
      // Update local state optimistically
      setCollections(prev => prev.map(collection => {
        if (collection.id === collectionId) {
          return {
            ...collection,
            followers: collection.followers + 1
          };
        }
        return collection;
      }));

      // Send to backend
      // await supabase.from('collection_followers').insert({
      //   user_id: userId,
      //   collection_id: collectionId
      // });
    } catch (error) {
      console.error('Error following collection:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-cinzel font-bold text-stardust-silver flex items-center space-x-3">
          <BookOpen className="w-8 h-8 text-brass" />
          <span>
            {viewMode === 'my-collections' ? 'My Collections' : 'Dream Collections'}
          </span>
        </h2>
        
        {isAuthenticated && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="marble-button flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span className="relative z-10 text-brass font-inter font-medium">
              Create Collection
            </span>
          </button>
        )}
      </div>

      {/* Featured Collections Banner */}
      {viewMode === 'discover' && (
        <div className="glass-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Star className="w-5 h-5 text-brass" />
            <h3 className="text-lg font-cinzel font-semibold text-stardust-silver">
              Featured Collections
            </h3>
          </div>
          <p className="text-stardust-silver/70 text-sm">
            Curated collections handpicked by our community for exceptional storytelling and creativity
          </p>
        </div>
      )}

      {/* Collections Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="aspect-video bg-brass/20 rounded-lg mb-4"></div>
              <div className="space-y-3">
                <div className="h-5 bg-brass/20 rounded w-3/4"></div>
                <div className="h-4 bg-brass/10 rounded w-full"></div>
                <div className="h-4 bg-brass/10 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((collection) => (
            <div key={collection.id} className="glass-card overflow-hidden hover:border-brass/40 transition-all duration-300 group">
              {/* Cover Image */}
              <div className="relative aspect-video overflow-hidden">
                {collection.cover_image ? (
                  <img
                    src={collection.cover_image}
                    alt={collection.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-brass/20 to-electric-blue/20 flex items-center justify-center">
                    <BookOpen className="w-12 h-12 text-brass/50" />
                  </div>
                )}
                
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black-marble/80 via-transparent to-transparent"></div>
                
                {/* Featured Badge */}
                {collection.is_featured && (
                  <div className="absolute top-3 left-3 px-2 py-1 bg-brass/90 rounded-full text-xs text-black-marble font-inter font-medium">
                    Featured
                  </div>
                )}
                
                {/* Privacy Badge */}
                <div className="absolute top-3 right-3 p-2 bg-black-marble/60 rounded-full">
                  {collection.is_public ? (
                    <Globe className="w-4 h-4 text-green-400" />
                  ) : (
                    <Lock className="w-4 h-4 text-stardust-silver" />
                  )}
                </div>
                
                {/* Stats Overlay */}
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-white text-sm">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-1">
                      <BookOpen className="w-4 h-4" />
                      <span>{collection.dream_count}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{collection.followers}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4">
                {/* Title and Creator */}
                <div>
                  <h3 className="text-lg font-cinzel font-bold text-stardust-silver group-hover:text-brass transition-colors mb-2">
                    {collection.title}
                  </h3>
                  <div className="flex items-center space-x-2 text-sm text-stardust-silver/60">
                    {collection.creator.avatar ? (
                      <img
                        src={collection.creator.avatar}
                        alt={collection.creator.name}
                        className="w-5 h-5 rounded-full"
                      />
                    ) : (
                      <div className="w-5 h-5 rounded-full bg-brass/20"></div>
                    )}
                    <span>by {collection.creator.name}</span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-stardust-silver/80 text-sm leading-relaxed">
                  {collection.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {collection.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-black-marble/50 border border-brass/30 rounded-full text-xs text-brass"
                    >
                      #{tag}
                    </span>
                  ))}
                  {collection.tags.length > 3 && (
                    <span className="px-2 py-1 bg-black-marble/50 border border-brass/30 rounded-full text-xs text-stardust-silver/60">
                      +{collection.tags.length - 3}
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-2">
                  <div className="text-xs text-stardust-silver/50">
                    Updated {formatDate(collection.updated_at)}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {isAuthenticated && (
                      <button
                        onClick={() => handleFollowCollection(collection.id)}
                        className="glass-button text-sm flex items-center space-x-1"
                      >
                        <Heart className="w-3 h-3" />
                        <span>Follow</span>
                      </button>
                    )}
                    
                    <button className="marble-button text-sm">
                      <span className="relative z-10 text-brass font-inter font-medium flex items-center space-x-1">
                        <Eye className="w-3 h-3" />
                        <span>View</span>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && collections.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-brass/50 mx-auto mb-4" />
          <h3 className="text-xl font-cinzel font-semibold text-stardust-silver mb-2">
            {viewMode === 'my-collections' ? 'No collections yet' : 'No collections found'}
          </h3>
          <p className="text-stardust-silver/60 mb-6">
            {viewMode === 'my-collections' 
              ? 'Create your first collection to organize your favorite dreams'
              : 'Be the first to create a collection and share it with the community'
            }
          </p>
          {isAuthenticated && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="marble-button"
            >
              <span className="relative z-10 text-brass font-inter font-medium">
                Create Collection
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default DreamCollections;