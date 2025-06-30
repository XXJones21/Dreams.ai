import React, { useState } from 'react';
import { Heart, MessageCircle, Share2, Bookmark, Eye, Clock, MoreHorizontal, Play, Verified } from 'lucide-react';

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

interface DreamCardProps {
  dream: Dream;
  onInteraction: (dreamId: string, action: 'like' | 'comment' | 'share' | 'bookmark') => void;
  isAuthenticated: boolean;
  showSimilarityScore?: boolean;
}

const DreamCard: React.FC<DreamCardProps> = ({ 
  dream, 
  onInteraction, 
  isAuthenticated,
  showSimilarityScore = false 
}) => {
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [showFullContent, setShowFullContent] = useState(false);

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatTimeAgo = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return `${Math.floor(diffInHours / 168)}w ago`;
  };

  const handleLike = () => {
    if (!isAuthenticated) return;
    setIsLiked(!isLiked);
    onInteraction(dream.id, 'like');
  };

  const handleBookmark = () => {
    if (!isAuthenticated) return;
    setIsBookmarked(!isBookmarked);
    onInteraction(dream.id, 'bookmark');
  };

  const handleShare = () => {
    onInteraction(dream.id, 'share');
    // Implement share functionality
    if (navigator.share) {
      navigator.share({
        title: dream.title,
        text: dream.excerpt,
        url: `${window.location.origin}/dreams/${dream.id}`
      });
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(`${window.location.origin}/dreams/${dream.id}`);
    }
  };

  const getEmotionColor = (emotion: string): string => {
    const emotionColors: Record<string, string> = {
      'fear': 'text-red-400',
      'excitement': 'text-yellow-400',
      'wonder': 'text-blue-400',
      'joy': 'text-green-400',
      'sadness': 'text-purple-400',
      'anger': 'text-orange-400',
      'surprise': 'text-pink-400',
      'disgust': 'text-gray-400'
    };
    return emotionColors[emotion] || 'text-stardust-silver';
  };

  return (
    <article className="glass-card p-6 hover:border-brass/40 transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {/* Creator Avatar */}
          <div className="relative">
            {dream.creator.avatar ? (
              <img
                src={dream.creator.avatar}
                alt={dream.creator.name}
                className="w-12 h-12 rounded-full object-cover border-2 border-brass/30"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-brass/20 flex items-center justify-center">
                <span className="text-brass font-cinzel font-bold">
                  {dream.creator.name.charAt(0)}
                </span>
              </div>
            )}
            {dream.creator.verified && (
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-electric-blue rounded-full flex items-center justify-center">
                <Verified className="w-3 h-3 text-white" />
              </div>
            )}
          </div>

          {/* Creator Info */}
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-inter font-semibold text-stardust-silver">
                {dream.creator.name}
              </h3>
              {dream.is_featured && (
                <span className="px-2 py-1 bg-nebula-pink/20 border border-nebula-pink/40 rounded-full text-xs text-nebula-pink font-inter font-medium">
                  Featured
                </span>
              )}
              {dream.is_trending && (
                <span className="px-2 py-1 bg-brass/20 border border-brass/40 rounded-full text-xs text-brass font-inter font-medium flex items-center space-x-1">
                  <span>Trending</span>
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2 text-xs text-stardust-silver/60">
              <Clock className="w-3 h-3" />
              <span>{formatTimeAgo(dream.created_at)}</span>
              <span>•</span>
              <span className={getEmotionColor(dream.emotion)}>
                {dream.emotion}
              </span>
            </div>
          </div>
        </div>

        {/* Actions Menu */}
        <button className="text-stardust-silver/60 hover:text-stardust-silver transition-colors">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {/* Title */}
        <h2 className="text-xl font-cinzel font-bold text-stardust-silver group-hover:text-brass transition-colors">
          {dream.title}
        </h2>

        {/* Excerpt */}
        <p className="text-stardust-silver/80 font-inter leading-relaxed">
          {showFullContent ? dream.content : dream.excerpt}
          {dream.content.length > dream.excerpt.length && (
            <button
              onClick={() => setShowFullContent(!showFullContent)}
              className="ml-2 text-brass hover:text-stardust-silver transition-colors font-medium"
            >
              {showFullContent ? 'Show less' : 'Read more'}
            </button>
          )}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {dream.tags.slice(0, 4).map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-black-marble/50 border border-brass/30 rounded-full text-xs text-brass font-inter hover:border-brass/60 transition-colors cursor-pointer"
            >
              #{tag}
            </span>
          ))}
          {dream.tags.length > 4 && (
            <span className="px-3 py-1 bg-black-marble/50 border border-brass/30 rounded-full text-xs text-stardust-silver/60 font-inter">
              +{dream.tags.length - 4} more
            </span>
          )}
        </div>

        {/* Similarity Score (for personalized feeds) */}
        {showSimilarityScore && dream.similarity_score && (
          <div className="flex items-center space-x-2 text-sm text-electric-blue">
            <span>Match: {Math.round(dream.similarity_score * 100)}%</span>
          </div>
        )}
      </div>

      {/* Engagement Bar */}
      <div className="flex items-center justify-between pt-4 mt-4 border-t border-brass/20">
        {/* Stats */}
        <div className="flex items-center space-x-6 text-sm text-stardust-silver/60">
          <div className="flex items-center space-x-1">
            <Eye className="w-4 h-4" />
            <span>{formatNumber(dream.engagement.views)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Heart className="w-4 h-4" />
            <span>{formatNumber(dream.engagement.likes)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <MessageCircle className="w-4 h-4" />
            <span>{formatNumber(dream.engagement.comments)}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-4">
          <button
            onClick={handleLike}
            disabled={!isAuthenticated}
            className={`flex items-center space-x-1 transition-colors ${
              isLiked 
                ? 'text-red-400' 
                : isAuthenticated 
                  ? 'text-stardust-silver/60 hover:text-red-400' 
                  : 'text-stardust-silver/30 cursor-not-allowed'
            }`}
          >
            <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
          </button>

          <button
            onClick={() => onInteraction(dream.id, 'comment')}
            disabled={!isAuthenticated}
            className={`transition-colors ${
              isAuthenticated 
                ? 'text-stardust-silver/60 hover:text-electric-blue' 
                : 'text-stardust-silver/30 cursor-not-allowed'
            }`}
          >
            <MessageCircle className="w-5 h-5" />
          </button>

          <button
            onClick={handleShare}
            className="text-stardust-silver/60 hover:text-green-400 transition-colors"
          >
            <Share2 className="w-5 h-5" />
          </button>

          <button
            onClick={handleBookmark}
            disabled={!isAuthenticated}
            className={`transition-colors ${
              isBookmarked 
                ? 'text-brass' 
                : isAuthenticated 
                  ? 'text-stardust-silver/60 hover:text-brass' 
                  : 'text-stardust-silver/30 cursor-not-allowed'
            }`}
          >
            <Bookmark className={`w-5 h-5 ${isBookmarked ? 'fill-current' : ''}`} />
          </button>

          {/* Experience Dream Button */}
          <button className="marble-button text-sm">
            <span className="relative z-10 text-brass font-inter font-medium flex items-center space-x-1">
              <Play className="w-4 h-4" />
              <span>Experience</span>
            </span>
          </button>
        </div>
      </div>
    </article>
  );
};

export default DreamCard;