import React from 'react';
import { X, Calendar, Tag, Heart, Sparkles } from 'lucide-react';

interface FeedFilters {
  category?: string;
  emotion?: string;
  theme?: string;
  timeRange?: 'day' | 'week' | 'month' | 'all';
  sortBy?: 'trending' | 'recent' | 'popular' | 'recommended';
}

interface FeedFiltersProps {
  filters: FeedFilters;
  onFilterChange: (filters: Partial<FeedFilters>) => void;
  onClose: () => void;
}

const categories = [
  'All', 'Fantasy', 'Sci-Fi', 'Horror', 'Adventure', 'Mystery', 
  'Romance', 'Thriller', 'Comedy', 'Drama', 'Surreal'
];

const emotions = [
  'All', 'excitement', 'fear', 'wonder', 'joy', 'sadness', 
  'anger', 'surprise', 'disgust', 'anticipation', 'trust'
];

const themes = [
  'All', 'heroic journey', 'abandoned places', 'futuristic city', 
  'magical realm', 'underwater world', 'space exploration', 
  'time travel', 'parallel universe', 'ancient civilization'
];

const FeedFilters: React.FC<FeedFiltersProps> = ({ filters, onFilterChange, onClose }) => {
  const handleCategoryChange = (category: string) => {
    onFilterChange({ category: category === 'All' ? undefined : category.toLowerCase() });
  };

  const handleEmotionChange = (emotion: string) => {
    onFilterChange({ emotion: emotion === 'All' ? undefined : emotion });
  };

  const handleThemeChange = (theme: string) => {
    onFilterChange({ theme: theme === 'All' ? undefined : theme });
  };

  const handleTimeRangeChange = (timeRange: FeedFilters['timeRange']) => {
    onFilterChange({ timeRange });
  };

  const handleSortByChange = (sortBy: FeedFilters['sortBy']) => {
    onFilterChange({ sortBy });
  };

  const clearAllFilters = () => {
    onFilterChange({
      category: undefined,
      emotion: undefined,
      theme: undefined,
      timeRange: 'week',
      sortBy: 'trending'
    });
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-cinzel font-bold text-stardust-silver flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-brass" />
          <span>Filter Dreams</span>
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearAllFilters}
            className="text-sm text-brass hover:text-stardust-silver transition-colors"
          >
            Clear All
          </button>
          <button
            onClick={onClose}
            className="text-stardust-silver hover:text-brass transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Sort By */}
        <div>
          <label className="block text-stardust-silver font-inter font-medium mb-3 flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-brass" />
            <span>Sort By</span>
          </label>
          <div className="space-y-2">
            {[
              { value: 'trending', label: 'Trending' },
              { value: 'recent', label: 'Most Recent' },
              { value: 'popular', label: 'Most Popular' },
              { value: 'recommended', label: 'Recommended' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => handleSortByChange(option.value as FeedFilters['sortBy'])}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  filters.sortBy === option.value
                    ? 'bg-brass/20 border border-brass/40 text-brass'
                    : 'bg-black-marble/30 border border-brass/20 text-stardust-silver hover:border-brass/40'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Time Range */}
        <div>
          <label className="block text-stardust-silver font-inter font-medium mb-3">
            Time Range
          </label>
          <div className="space-y-2">
            {[
              { value: 'day', label: 'Today' },
              { value: 'week', label: 'This Week' },
              { value: 'month', label: 'This Month' },
              { value: 'all', label: 'All Time' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => handleTimeRangeChange(option.value as FeedFilters['timeRange'])}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  filters.timeRange === option.value
                    ? 'bg-brass/20 border border-brass/40 text-brass'
                    : 'bg-black-marble/30 border border-brass/20 text-stardust-silver hover:border-brass/40'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Category */}
        <div>
          <label className="block text-stardust-silver font-inter font-medium mb-3 flex items-center space-x-2">
            <Tag className="w-4 h-4 text-brass" />
            <span>Category</span>
          </label>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => handleCategoryChange(category)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  (filters.category === category.toLowerCase() || (!filters.category && category === 'All'))
                    ? 'bg-brass/20 border border-brass/40 text-brass'
                    : 'bg-black-marble/30 border border-brass/20 text-stardust-silver hover:border-brass/40'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Emotion */}
        <div>
          <label className="block text-stardust-silver font-inter font-medium mb-3 flex items-center space-x-2">
            <Heart className="w-4 h-4 text-brass" />
            <span>Emotion</span>
          </label>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {emotions.map((emotion) => (
              <button
                key={emotion}
                onClick={() => handleEmotionChange(emotion)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors capitalize ${
                  (filters.emotion === emotion || (!filters.emotion && emotion === 'All'))
                    ? 'bg-brass/20 border border-brass/40 text-brass'
                    : 'bg-black-marble/30 border border-brass/20 text-stardust-silver hover:border-brass/40'
                }`}
              >
                {emotion}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Theme Filter */}
      <div>
        <label className="block text-stardust-silver font-inter font-medium mb-3">
          Themes
        </label>
        <div className="flex flex-wrap gap-2">
          {themes.map((theme) => (
            <button
              key={theme}
              onClick={() => handleThemeChange(theme)}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                (filters.theme === theme || (!filters.theme && theme === 'All'))
                  ? 'bg-brass/20 border border-brass/40 text-brass'
                  : 'bg-black-marble/30 border border-brass/20 text-stardust-silver hover:border-brass/40'
              }`}
            >
              {theme}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeedFilters;