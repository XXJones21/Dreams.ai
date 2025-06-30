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
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = -0.8 - Math.random() * 1.2; // Always move upward like flame
        this.life = 0;
        this.maxLife = 100 + Math.random() * 60;
        this.size = 1.5 + Math.random() * 2.5;
        this.hue = 220 + Math.random() * 80; // Blue to purple range
        this.swayOffset = Math.random() * Math.PI * 2;
        this.swayAmplitude = 0.5 + Math.random() * 1;
      }

      update(time: number) {
        // Flame-like swaying motion - slow back and forth
        const swayAmount = Math.sin(time * 1.5 + this.swayOffset) * this.swayAmplitude;
        this.x = this.baseX + swayAmount + this.vx * this.life * 0.05;
        this.y += this.vy;
        
        // Slow down as particle rises (realistic flame physics)
        this.vy *= 0.985;
        
        this.life++;
        
        // Fade out as particle ages and rises
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        return alpha > 0.05 && this.y > -100;
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        const progress = this.life / this.maxLife;
        
        // Color transition: blue -> purple -> pink -> transparent (vanishing effect)
        let hue = this.hue;
        let saturation = 80;
        let lightness = 60;
        
        if (progress > 0.4) {
          // Transition to purple/pink as it rises
          hue = 280 + (progress - 0.4) * 100;
          saturation = 70 - progress * 20;
          lightness = 50 + progress * 20;
        }
        
        ctx.save();
        ctx.globalAlpha = alpha * 0.8;
        
        // Create flame-like glow effect with vanishing trail
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 3
        );
        gradient.addColorStop(0, `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha * 0.9})`);
        gradient.addColorStop(0.4, `hsla(${hue}, ${saturation - 10}%, ${lightness - 10}%, ${alpha * 0.6})`);
        gradient.addColorStop(0.8, `hsla(${hue}, ${saturation - 20}%, ${lightness - 20}%, ${alpha * 0.3})`);
        gradient.addColorStop(1, `hsla(${hue}, ${saturation - 30}%, ${lightness - 30}%, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * (1 + progress * 0.5), 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    let particles: FlameParticle[] = [];
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      time += 0.02; // Slower time progression for gentle flame movement

      // Spawn particles from the cosmic swirl area (top-right of logo)
      if (Math.random() < 0.35) {
        const swirlCenterX = rect.width * 0.7;
        const swirlCenterY = rect.height * 0.15;
        
        // Create multiple spawn points for fuller flame effect
        for (let i = 0; i < 2; i++) {
          const spawnX = swirlCenterX + (Math.random() - 0.5) * 40;
          const spawnY = swirlCenterY + (Math.random() - 0.5) * 20;
          particles.push(new FlameParticle(spawnX, spawnY));
        }
      }

      // Update and draw particles
      particles = particles.filter(particle => {
        const alive = particle.update(time);
        if (alive) {
          particle.draw(ctx);
        }
        return alive;
      });

      // Limit particle count for performance
      if (particles.length > 80) {
        particles = particles.slice(-80);
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

        {/* Actual Logo Image - Using the correct Art Deco bust */}
        <div className="absolute inset-4 flex items-center justify-center">
          <img 
            src="/ChatGPT Image Jun 29, 2025, 09_05_56 PM copy.png" 
            alt="Dreams.AI Logo - Art Deco Bust with Cosmic Swirl" 
            className="w-full h-full object-contain"
            style={{
              filter: 'drop-shadow(0 20px 40px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 30px rgba(207, 181, 59, 0.4))'
            }}
            onError={(e) => {
              // Fallback to alternative image paths
              const img = e.target as HTMLImageElement;
              if (img.src.includes('copy.png')) {
                img.src = '/ChatGPT Image Jun 29, 2025, 09_05_56 PM.png';
              } else if (img.src.includes('ChatGPT')) {
                img.src = '/image copy.png';
              }
            }}
          />
        </div>

        {/* Flame-like Swirl Animation Overlay - positioned over the cosmic swirl */}
        <div className="cosmic-swirl-container">
          {/* CSS-based flame sway animation layers */}
          <div className="cosmic-swirl flame-swirl-1"></div>
          <div className="cosmic-swirl flame-swirl-2"></div>
          <div className="cosmic-swirl flame-swirl-3"></div>
          
          {/* Enhanced Canvas Particles for vanishing flame effect */}
          {supportsCanvas && (
            <canvas
              ref={canvasRef}
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ 
                mixBlendMode: 'screen',
                opacity: 0.9
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default LogoWithFluidSwirl;