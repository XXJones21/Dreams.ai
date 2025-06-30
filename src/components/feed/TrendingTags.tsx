import React from 'react';
import { TrendingUp, Hash } from 'lucide-react';

interface TrendingTagsProps {
  tags: string[];
  onTagClick: (tag: string) => void;
}

const TrendingTags: React.FC<TrendingTagsProps> = ({ tags, onTagClick }) => {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center space-x-2 mb-3">
        <TrendingUp className="w-4 h-4 text-brass" />
        <h3 className="text-sm font-cinzel font-semibold text-stardust-silver">
          Trending Tags
        </h3>
      </div>
      <div className="flex flex-wrap gap-2">
        {tags.slice(0, 8).map((tag, index) => (
          <button
            key={tag}
            onClick={() => onTagClick(tag)}
            className="flex items-center space-x-1 px-3 py-1 bg-black-marble/30 border border-brass/30 rounded-full text-sm text-brass hover:border-brass/60 hover:bg-brass/10 transition-all duration-200 group"
          >
            <Hash className="w-3 h-3 group-hover:text-stardust-silver transition-colors" />
            <span className="group-hover:text-stardust-silver transition-colors">{tag}</span>
            {index < 3 && (
              <div className="w-1 h-1 bg-brass rounded-full animate-pulse"></div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TrendingTags;