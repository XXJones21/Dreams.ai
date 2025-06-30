import React, { useEffect, useRef, useCallback } from 'react';
import { Loader2 } from 'lucide-react';

interface InfiniteScrollProps {
  children: React.ReactNode;
  hasMore: boolean;
  loadMore: () => void;
  loading: boolean;
  threshold?: number;
}

const InfiniteScroll: React.FC<InfiniteScrollProps> = ({
  children,
  hasMore,
  loadMore,
  loading,
  threshold = 200
}) => {
  const sentinelRef = useRef<HTMLDivElement>(null);

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loading) {
        loadMore();
      }
    },
    [hasMore, loading, loadMore]
  );

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(handleIntersection, {
      rootMargin: `${threshold}px`,
      threshold: 0.1
    });

    observer.observe(sentinel);

    return () => {
      observer.unobserve(sentinel);
    };
  }, [handleIntersection, threshold]);

  return (
    <>
      {children}
      
      {/* Sentinel element for intersection observer */}
      <div ref={sentinelRef} className="h-4" />
      
      {/* Loading indicator */}
      {loading && hasMore && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-3 text-brass">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="font-inter">Loading more dreams...</span>
          </div>
        </div>
      )}
      
      {/* End of feed indicator */}
      {!hasMore && !loading && (
        <div className="text-center py-8">
          <div className="text-stardust-silver/60 font-inter">
            You've reached the end of the feed
          </div>
          <div className="mt-2 text-sm text-brass">
            ✨ Time to create your own dream! ✨
          </div>
        </div>
      )}
    </>
  );
};

export default InfiniteScroll;