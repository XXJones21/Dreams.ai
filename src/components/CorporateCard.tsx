import React, { useState, useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion';

interface CorporateCardProps {
  title: string;
  description: string;
  image?: string;
  category?: string;
  onClick?: () => void;
  className?: string;
}

const CorporateCard: React.FC<CorporateCardProps> = ({
  title,
  description,
  image,
  category,
  onClick,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["8deg", "-8deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-8deg", "8deg"]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;

    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
    setIsHovered(false);
  };

  return (
    <motion.div
      ref={cardRef}
      className={`
        relative overflow-hidden cursor-pointer group
        bg-gradient-to-br from-marble-black via-marble-dark to-marble-black
        border-2 border-gold/30 rounded-xl shadow-2xl
        ${className}
      `}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      whileHover={{ scale: 1.05, y: -10 }}
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {/* Luxury glow effect */}
      <motion.div
        className="absolute -inset-2 bg-gradient-to-r from-gold/20 via-brass/30 to-gold/20 rounded-xl blur-xl"
        animate={{
          opacity: isHovered ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
      />

      {/* Background Image */}
      {image && (
        <div className="relative h-56 overflow-hidden rounded-t-xl">
          <motion.img
            src={image}
            alt={title}
            className="w-full h-full object-cover"
            animate={{
              scale: isHovered ? 1.1 : 1,
            }}
            transition={{ duration: 0.6 }}
          />
          
          {/* Luxury overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-marble-black via-marble-black/50 to-transparent"></div>
          
          {/* Category Badge */}
          {category && (
            <motion.div
              className="absolute top-4 right-4 bg-gradient-to-r from-gold to-brass px-4 py-2 rounded-lg shadow-lg"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <span className="text-marble-black font-corporate font-bold text-sm tracking-wider">
                {category}
              </span>
            </motion.div>
          )}

          {/* Art Deco corner accents */}
          <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-gold/60"></div>
          <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-gold/60"></div>
        </div>
      )}

      {/* Content */}
      <div className="p-8 relative">
        {/* Marble texture overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-marble-dark/50 to-marble-black/50 rounded-b-xl"></div>
        
        <div className="relative z-10">
          <motion.h3
            className="text-2xl font-corporate font-bold text-gold mb-4 tracking-wide"
            animate={{
              textShadow: isHovered
                ? "0 0 20px rgba(255, 215, 0, 0.6)"
                : "0 0 10px rgba(255, 215, 0, 0.3)",
            }}
          >
            {title}
          </motion.h3>
          
          <p className="text-platinum/90 font-modern leading-relaxed mb-6 text-lg">
            {description}
          </p>

          {/* Luxury status bar */}
          <div className="flex items-center justify-between">
            <motion.div
              className="flex items-center space-x-3"
              animate={{
                x: isHovered ? 8 : 0,
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="w-3 h-3 bg-terminal-green rounded-full animate-pulse shadow-lg"></div>
              <span className="font-terminal text-terminal-green text-sm font-bold tracking-wider">
                ACTIVE
              </span>
            </motion.div>

            {/* Luxury accent line */}
            <motion.div
              className="h-1 bg-gradient-to-r from-transparent via-gold to-brass rounded-full shadow-lg"
              animate={{
                width: isHovered ? "80px" : "40px",
              }}
              transition={{ duration: 0.4 }}
            />
          </div>
        </div>
      </div>

      {/* Luxury particles */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {[...Array(12)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-br from-gold to-brass rounded-full shadow-lg"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                  y: [0, -30, -60],
                }}
                transition={{
                  duration: 2.5,
                  repeat: Infinity,
                  delay: Math.random() * 1.5,
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Luxury scan line */}
      <motion.div
        className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-terminal-green to-transparent"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'linear',
        }}
      />

      {/* Premium border glow */}
      <motion.div
        className="absolute inset-0 rounded-xl border-2 border-transparent"
        animate={{
          borderColor: isHovered
            ? "rgba(255, 215, 0, 0.6)"
            : "rgba(255, 215, 0, 0.3)",
          boxShadow: isHovered
            ? "0 0 40px rgba(255, 215, 0, 0.4), inset 0 0 20px rgba(255, 215, 0, 0.1)"
            : "0 0 20px rgba(255, 215, 0, 0.2)",
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
};

export default CorporateCard;