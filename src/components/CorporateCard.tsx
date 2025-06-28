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

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["5deg", "-5deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-5deg", "5deg"]);

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
        relative overflow-hidden marble-surface rounded-lg art-deco-corner cursor-pointer
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
      whileHover={{ scale: 1.02, y: -5 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.3 }}
    >
      {/* Background Image */}
      {image && (
        <div className="relative h-48 overflow-hidden">
          <motion.img
            src={image}
            alt={title}
            className="w-full h-full object-cover"
            animate={{
              scale: isHovered ? 1.1 : 1,
            }}
            transition={{ duration: 0.5 }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-marble-black via-transparent to-transparent"></div>
          
          {/* Category Badge */}
          {category && (
            <motion.div
              className="absolute top-4 right-4 brass-accent px-3 py-1 rounded-full"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <span className="text-marble-black font-corporate font-bold text-sm">{category}</span>
            </motion.div>
          )}
        </div>
      )}

      {/* Content */}
      <div className="p-6 relative">
        {/* Marble veining effect */}
        <div className="absolute inset-0 marble-veins opacity-30"></div>
        
        <div className="relative z-10">
          <motion.h3
            className="text-xl font-corporate font-bold text-gold mb-3"
            animate={{
              textShadow: isHovered
                ? "0 0 20px rgba(255, 215, 0, 0.5)"
                : "0 0 10px rgba(255, 215, 0, 0.2)",
            }}
          >
            {title}
          </motion.h3>
          
          <p className="text-platinum/80 font-modern leading-relaxed mb-4">
            {description}
          </p>

          {/* Interactive elements */}
          <div className="flex items-center justify-between">
            <motion.div
              className="flex items-center space-x-2"
              animate={{
                x: isHovered ? 10 : 0,
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="w-2 h-2 bg-terminal-green rounded-full animate-pulse"></div>
              <span className="font-terminal text-terminal-green text-sm">ACTIVE</span>
            </motion.div>

            {/* Brass accent line */}
            <motion.div
              className="h-0.5 bg-gradient-to-r from-transparent to-brass rounded-full"
              animate={{
                width: isHovered ? "60px" : "30px",
              }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </div>

      {/* Hover particles */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-gold rounded-full"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                  y: [0, -20, -40],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: Math.random() * 1,
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scan line effect */}
      <motion.div
        className="absolute bottom-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-terminal-green to-transparent"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
        }}
      />

      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-lg pointer-events-none"
        animate={{
          boxShadow: isHovered
            ? "0 0 40px rgba(255, 215, 0, 0.3), inset 0 0 20px rgba(255, 215, 0, 0.1)"
            : "0 0 20px rgba(255, 215, 0, 0.1)",
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
};

export default CorporateCard;