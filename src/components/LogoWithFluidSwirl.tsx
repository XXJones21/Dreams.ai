import React, { useEffect, useRef, useState } from 'react';

interface LogoWithFluidSwirlProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
}

const LogoWithFluidSwirl: React.FC<LogoWithFluidSwirlProps> = ({ 
  className = '', 
  size = 'large' 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [supportsCanvas, setSupportsCanvas] = useState(true);

  const sizeClasses = {
    small: 'w-32 h-32',
    medium: 'w-48 h-48', 
    large: 'w-64 h-64 md:w-80 md:h-80'
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      setSupportsCanvas(false);
      return;
    }

    // Set canvas size for high DPI displays
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Flame-like particle system that vanishes into background
    class FlameParticle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      life: number;
      maxLife: number;
      size: number;
      hue: number;
      baseX: number;
      swayOffset: number;
      swayAmplitude: number;

      constructor(x: number, y: number) {
        this.baseX = x;
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.2;
        this.vy = -0.6 - Math.random() * 0.8; // Gentler upward movement
        this.life = 0;
        this.maxLife = 120 + Math.random() * 80; // Longer life for smoother vanishing
        this.size = 1 + Math.random() * 1.5; // Smaller, more subtle particles
        this.hue = 220 + Math.random() * 60; // Blue to purple range
        this.swayOffset = Math.random() * Math.PI * 2;
        this.swayAmplitude = 0.3 + Math.random() * 0.7; // Reduced sway for subtlety
      }

      update(time: number) {
        // Gentle flame-like swaying motion
        const swayAmount = Math.sin(time * 1.2 + this.swayOffset) * this.swayAmplitude;
        this.x = this.baseX + swayAmount + this.vx * this.life * 0.03;
        this.y += this.vy;
        
        // Gradual deceleration as particle rises
        this.vy *= 0.988;
        
        this.life++;
        
        // Smooth fade out as particle ages and rises
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        return alpha > 0.02 && this.y > -150;
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        const progress = this.life / this.maxLife;
        
        // Smooth color transition: blue -> purple -> pink -> transparent
        let hue = this.hue;
        let saturation = 70;
        let lightness = 55;
        
        if (progress > 0.3) {
          // Gradual transition to purple/pink as it rises and vanishes
          hue = 260 + (progress - 0.3) * 80;
          saturation = 60 - progress * 15;
          lightness = 45 + progress * 25;
        }
        
        ctx.save();
        ctx.globalAlpha = alpha * 0.6; // More subtle opacity
        
        // Soft flame-like glow effect
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 2.5
        );
        gradient.addColorStop(0, `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha * 0.8})`);
        gradient.addColorStop(0.5, `hsla(${hue}, ${saturation - 10}%, ${lightness - 10}%, ${alpha * 0.4})`);
        gradient.addColorStop(1, `hsla(${hue}, ${saturation - 20}%, ${lightness - 20}%, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * (1 + progress * 0.3), 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    let particles: FlameParticle[] = [];
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      time += 0.015; // Slower time progression for gentler movement

      // Spawn particles from the center-top area where the cosmic swirl should be
      if (Math.random() < 0.25) { // Reduced spawn rate for cleaner effect
        // Center the spawn area at the top of the logo where the cosmic swirl is
        const swirlCenterX = rect.width * 0.5; // Perfectly centered
        const swirlCenterY = rect.height * 0.2; // Top area of the logo
        
        // Single spawn point for cleaner, more focused effect
        const spawnX = swirlCenterX + (Math.random() - 0.5) * 30;
        const spawnY = swirlCenterY + (Math.random() - 0.5) * 15;
        particles.push(new FlameParticle(spawnX, spawnY));
      }

      // Update and draw particles
      particles = particles.filter(particle => {
        const alive = particle.update(time);
        if (alive) {
          particle.draw(ctx);
        }
        return alive;
      });

      // Limit particle count for performance and cleaner visual
      if (particles.length > 50) {
        particles = particles.slice(-50);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className={`logo-with-fluid-swirl ${sizeClasses[size]} ${className}`}>
      {/* Main Logo Container */}
      <div className="relative w-full h-full">
        {/* Art Deco Frame */}
        <div className="absolute inset-0 art-deco-frame">
          <div className="frame-corner top-left"></div>
          <div className="frame-corner top-right"></div>
          <div className="frame-corner bottom-left"></div>
          <div className="frame-corner bottom-right"></div>
          <div className="frame-border top"></div>
          <div className="frame-border right"></div>
          <div className="frame-border bottom"></div>
          <div className="frame-border left"></div>
        </div>

        {/* Flame Particles Layer - BEHIND the logo image */}
        <div className="absolute inset-0 z-10">
          {/* CSS-based flame sway animation layers - centered and subtle */}
          <div className="cosmic-swirl-container">
            <div className="cosmic-swirl flame-swirl-1"></div>
            <div className="cosmic-swirl flame-swirl-2"></div>
            <div className="cosmic-swirl flame-swirl-3"></div>
          </div>
          
          {/* Canvas Particles for vanishing flame effect - behind logo */}
          {supportsCanvas && (
            <canvas
              ref={canvasRef}
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ 
                mixBlendMode: 'screen',
                opacity: 0.7
              }}
            />
          )}
        </div>

        {/* Actual Logo Image - ABOVE the flame particles */}
        <div className="absolute inset-4 flex items-center justify-center z-20">
          <img 
            src="/image.png" 
            alt="Dreams.AI Logo - Art Deco Bust with Cosmic Swirl" 
            className="w-full h-full object-contain"
            style={{
              filter: 'drop-shadow(0 20px 40px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 30px rgba(207, 181, 59, 0.4))'
            }}
            onError={(e) => {
              // Fallback to alternative image paths
              const img = e.target as HTMLImageElement;
              if (img.src.includes('image.png')) {
                img.src = '/ChatGPT Image Jun 29, 2025, 09_05_56 PM copy.png';
              } else if (img.src.includes('copy.png')) {
                img.src = '/ChatGPT Image Jun 29, 2025, 09_05_56 PM.png';
              } else if (img.src.includes('ChatGPT')) {
                img.src = '/image copy.png';
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default LogoWithFluidSwirl;