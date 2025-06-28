import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Users, Clock, Star } from 'lucide-react';

const dreamExamples = [
  {
    title: "The Haunted Hospital",
    description: "Explore the abandoned corridors of St. Mary's Hospital, where shadows hold secrets and every door leads to a new mystery.",
    image: "https://images.pexels.com/photos/263402/pexels-photo-263402.jpeg?auto=compress&cs=tinysrgb&w=800",
    genre: "Horror",
    duration: "15-20 min",
    players: "1.2k"
  },
  {
    title: "Dragon's Castle",
    description: "A brave knight's quest to rescue Princess Aurelia from the ancient Castle Drakon, guarded by the fearsome dragon Ignis.",
    image: "https://images.pexels.com/photos/161154/castle-hohenschwangau-alps-alpsee-161154.jpeg?auto=compress&cs=tinysrgb&w=800",
    genre: "Fantasy",
    duration: "20-25 min",
    players: "2.8k"
  },
  {
    title: "Neon Cyberpunk",
    description: "Navigate the rain-soaked streets of Neo-Tokyo in 2087, where corporate espionage meets underground rebellion.",
    image: "https://images.pexels.com/photos/2387793/pexels-photo-2387793.jpeg?auto=compress&cs=tinysrgb&w=800",
    genre: "Sci-Fi",
    duration: "18-22 min",
    players: "3.1k"
  },
  {
    title: "Pirate's Treasure",
    description: "Set sail across treacherous waters to find the legendary treasure of Captain Blackbeard on a mysterious island.",
    image: "https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?auto=compress&cs=tinysrgb&w=800",
    genre: "Adventure",
    duration: "16-20 min",
    players: "1.9k"
  }
];

const DreamCarousel: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (!isAutoPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % dreamExamples.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % dreamExamples.length);
    setIsAutoPlaying(false);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + dreamExamples.length) % dreamExamples.length);
    setIsAutoPlaying(false);
  };

  return (
    <section className="relative z-20 py-20 bg-gradient-to-b from-transparent to-black-marble/50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-cinzel font-bold text-stardust-silver mb-4">
            <span className="bg-gradient-to-r from-brass to-nebula-pink bg-clip-text text-transparent">
              Popular Dreams
            </span>
          </h2>
          <p className="text-xl text-stardust-silver/70 font-inter max-w-2xl mx-auto">
            Discover what others are dreaming about, or let these inspire your next adventure
          </p>
        </div>

        <div className="relative max-w-6xl mx-auto">
          {/* Carousel Container */}
          <div className="relative overflow-hidden rounded-2xl">
            <div 
              className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${currentIndex * 100}%)` }}
            >
              {dreamExamples.map((dream, index) => (
                <div key={index} className="w-full flex-shrink-0">
                  <div className="relative h-96 md:h-[500px]">
                    <img 
                      src={dream.image} 
                      alt={dream.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black-marble via-black-marble/50 to-transparent"></div>
                    
                    {/* Content Overlay */}
                    <div className="absolute bottom-0 left-0 right-0 p-8 md:p-12">
                      <div className="max-w-2xl">
                        <div className="flex items-center space-x-4 mb-4">
                          <span className="px-3 py-1 bg-brass/20 border border-brass/40 rounded-full text-brass text-sm font-inter font-medium">
                            {dream.genre}
                          </span>
                          <div className="flex items-center space-x-1 text-stardust-silver/60">
                            <Clock className="w-4 h-4" />
                            <span className="text-sm font-inter">{dream.duration}</span>
                          </div>
                          <div className="flex items-center space-x-1 text-stardust-silver/60">
                            <Users className="w-4 h-4" />
                            <span className="text-sm font-inter">{dream.players}</span>
                          </div>
                        </div>
                        
                        <h3 className="text-3xl md:text-4xl font-cinzel font-bold text-stardust-silver mb-4">
                          {dream.title}
                        </h3>
                        <p className="text-lg text-stardust-silver/80 font-inter leading-relaxed mb-6">
                          {dream.description}
                        </p>
                        
                        <div className="flex space-x-4">
                          <button className="marble-button">
                            <span className="relative z-10 text-brass font-inter font-semibold">
                              Experience Dream
                            </span>
                          </button>
                          <button className="glass-button">
                            <span className="relative z-10 text-stardust-silver font-inter font-medium flex items-center space-x-2">
                              <Star className="w-4 h-4" />
                              <span>Save</span>
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation Arrows */}
          <button 
            onClick={prevSlide}
            className="absolute left-4 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-black-marble/80 border border-brass/30 rounded-full flex items-center justify-center text-brass hover:bg-brass hover:text-black-marble transition-all duration-300"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button 
            onClick={nextSlide}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-black-marble/80 border border-brass/30 rounded-full flex items-center justify-center text-brass hover:bg-brass hover:text-black-marble transition-all duration-300"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* Dots Indicator */}
          <div className="flex justify-center space-x-2 mt-8">
            {dreamExamples.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentIndex(index);
                  setIsAutoPlaying(false);
                }}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentIndex 
                    ? 'bg-brass scale-125' 
                    : 'bg-stardust-silver/30 hover:bg-stardust-silver/50'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default DreamCarousel;