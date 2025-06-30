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

    // Flame-like particle system
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

      constructor(x: number, y: number) {
        this.baseX = x;
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = -1 - Math.random() * 2; // Always move upward like flame
        this.life = 0;
        this.maxLife = 80 + Math.random() * 40;
        this.size = 2 + Math.random() * 3;
        this.hue = 220 + Math.random() * 100; // Blue to purple to pink range
        this.swayOffset = Math.random() * Math.PI * 2;
      }

      update(time: number) {
        // Flame-like swaying motion
        const swayAmount = Math.sin(time * 2 + this.swayOffset) * 0.8;
        this.x = this.baseX + swayAmount + this.vx * this.life * 0.1;
        this.y += this.vy;
        
        // Slow down as particle rises (like real flame)
        this.vy *= 0.98;
        
        this.life++;
        
        // Fade out as particle ages and rises
        const alpha = 1 - (this.life / this.maxLife);
        return alpha > 0 && this.y > -50;
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = Math.max(0, 1 - (this.life / this.maxLife));
        const progress = this.life / this.maxLife;
        
        // Color transition: blue -> purple -> pink -> transparent
        let hue = this.hue;
        if (progress > 0.3) {
          hue = 280 + (progress - 0.3) * 100; // Purple to pink
        }
        
        ctx.save();
        ctx.globalAlpha = alpha * 0.7;
        
        // Create flame-like glow effect
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 2
        );
        gradient.addColorStop(0, `hsla(${hue}, 80%, 70%, ${alpha})`);
        gradient.addColorStop(0.5, `hsla(${hue}, 70%, 50%, ${alpha * 0.5})`);
        gradient.addColorStop(1, `hsla(${hue}, 60%, 30%, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    let particles: FlameParticle[] = [];
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      time += 0.03;

      // Spawn particles from the swirl area (flame base)
      if (Math.random() < 0.4) {
        const swirlCenterX = rect.width * 0.75;
        const swirlCenterY = rect.height * 0.25;
        
        // Create multiple spawn points for more realistic flame
        for (let i = 0; i < 2; i++) {
          const spawnX = swirlCenterX + (Math.random() - 0.5) * 30;
          const spawnY = swirlCenterY + (Math.random() - 0.5) * 15;
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
      if (particles.length > 60) {
        particles = particles.slice(-60);
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

        {/* Actual Logo Image */}
        <div className="absolute inset-4 flex items-center justify-center">
          <img 
            src="/image copy.png" 
            alt="Dreams.AI Logo" 
            className="w-full h-full object-contain filter drop-shadow-2xl"
            style={{
              filter: 'drop-shadow(0 20px 40px rgba(0, 0, 0, 0.5)) drop-shadow(0 0 20px rgba(207, 181, 59, 0.3))'
            }}
          />
        </div>

        {/* Flame-like Swirl Animation Overlay */}
        <div className="cosmic-swirl-container">
          {/* CSS-based flame sway animation */}
          <div className="cosmic-swirl flame-swirl-1"></div>
          <div className="cosmic-swirl flame-swirl-2"></div>
          <div className="cosmic-swirl flame-swirl-3"></div>
          
          {/* Enhanced Canvas Particles for vanishing effect */}
          {supportsCanvas && (
            <canvas
              ref={canvasRef}
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ mixBlendMode: 'screen' }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default LogoWithFluidSwirl;