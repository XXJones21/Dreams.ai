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
  const [imageLoaded, setImageLoaded] = useState(false);

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

    // Flame-like particle system positioned over the cosmic swirl
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
        this.vx = (Math.random() - 0.5) * 0.1;
        this.vy = -0.3 - Math.random() * 0.4;
        this.life = 0;
        this.maxLife = 80 + Math.random() * 40;
        this.size = 0.6 + Math.random() * 1.0;
        this.hue = 220 + Math.random() * 60; // Blue to purple range
        this.swayOffset = Math.random() * Math.PI * 2;
        this.swayAmplitude = 0.15 + Math.random() * 0.3;
      }

      update(time: number) {
        // Gentle flame-like swaying motion
        const swayAmount = Math.sin(time * 0.8 + this.swayOffset) * this.swayAmplitude;
        this.x = this.baseX + swayAmount + this.vx * this.life * 0.015;
        this.y += this.vy;
        
        // Gradual deceleration
        this.vy *= 0.995;
        
        this.life++;
        
        return this.life < this.maxLife && this.y > -50;
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        const progress = this.life / this.maxLife;
        
        // Color transition: blue -> purple -> pink -> transparent
        let hue = this.hue + progress * 40;
        let saturation = 70 - progress * 20;
        let lightness = 45 + progress * 25;
        
        ctx.save();
        ctx.globalAlpha = alpha * 0.4;
        
        // Soft glow effect
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 2.5
        );
        gradient.addColorStop(0, `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha * 0.8})`);
        gradient.addColorStop(0.7, `hsla(${hue}, ${saturation - 15}%, ${lightness - 15}%, ${alpha * 0.2})`);
        gradient.addColorStop(1, `hsla(${hue}, ${saturation - 30}%, ${lightness - 30}%, 0)`);
        
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
      time += 0.01;

      // Spawn particles from the cosmic swirl area (top center of the logo)
      if (Math.random() < 0.15) {
        // Position particles over the cosmic swirl in the logo
        const swirlCenterX = rect.width * 0.5;
        const swirlCenterY = rect.height * 0.2; // Top area where the cosmic swirl is
        
        const spawnX = swirlCenterX + (Math.random() - 0.5) * 25;
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

      // Limit particle count
      if (particles.length > 30) {
        particles = particles.slice(-30);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [imageLoaded]);

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

        {/* CSS-based flame sway animation layers - behind the logo */}
        <div className="absolute inset-0 z-10">
          <div className="cosmic-swirl-container" style={{
            top: '10%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '50%',
            height: '50%'
          }}>
            <div className="cosmic-swirl flame-swirl-1"></div>
            <div className="cosmic-swirl flame-swirl-2"></div>
            <div className="cosmic-swirl flame-swirl-3"></div>
          </div>
        </div>

        {/* Canvas Particles for vanishing flame effect - behind logo */}
        {supportsCanvas && (
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none z-15"
            style={{ 
              mixBlendMode: 'screen',
              opacity: 0.7
            }}
          />
        )}

        {/* Actual Logo Image - ABOVE the flame particles */}
        <div className="absolute inset-4 flex items-center justify-center z-20">
          <img 
            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            alt="Dreams.AI Logo - Art Deco Bust with Cosmic Swirl" 
            className="w-full h-full object-contain opacity-0"
            style={{
              filter: 'drop-shadow(0 20px 40px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 30px rgba(207, 181, 59, 0.4))',
            }}
            onLoad={() => setImageLoaded(true)}
          />
          
          {/* Fallback: Use the provided image directly */}
          <div 
            className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: `url('/image copy copy.png')`,
              filter: 'drop-shadow(0 20px 40px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 30px rgba(207, 181, 59, 0.4))',
            }}
            onLoad={() => setImageLoaded(true)}
          />
        </div>
      </div>
    </div>
  );
};

export default LogoWithFluidSwirl;