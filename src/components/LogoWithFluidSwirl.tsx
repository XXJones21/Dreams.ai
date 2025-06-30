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

    // Particle system for enhanced swirl effects
    class Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      life: number;
      maxLife: number;
      size: number;
      hue: number;

      constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.life = 0;
        this.maxLife = 60 + Math.random() * 60;
        this.size = 1 + Math.random() * 2;
        this.hue = 220 + Math.random() * 60; // Blue to purple range
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life++;
        
        // Fade out as particle ages
        const alpha = 1 - (this.life / this.maxLife);
        return alpha > 0;
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = 1 - (this.life / this.maxLife);
        ctx.save();
        ctx.globalAlpha = alpha * 0.6;
        ctx.fillStyle = `hsl(${this.hue}, 70%, 60%)`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    let particles: Particle[] = [];
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      time += 0.02;

      // Add new particles occasionally
      if (Math.random() < 0.3) {
        const swirlCenterX = rect.width * 0.7;
        const swirlCenterY = rect.height * 0.3;
        particles.push(new Particle(
          swirlCenterX + Math.cos(time * 2) * 20,
          swirlCenterY + Math.sin(time * 2) * 20
        ));
      }

      // Update and draw particles
      particles = particles.filter(particle => {
        const alive = particle.update();
        if (alive) {
          particle.draw(ctx);
        }
        return alive;
      });

      // Limit particle count for performance
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

        {/* Marble Bust */}
        <div className="absolute inset-4 marble-bust-logo">
          {/* Bust Base */}
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-3/4 h-1/6 bg-gradient-to-t from-gray-300 via-gray-200 to-gray-100 rounded-b-full border-2 border-brass"></div>
          
          {/* Bust Body */}
          <div className="absolute bottom-1/6 left-1/2 transform -translate-x-1/2 w-2/3 h-2/3 marble-bust-body">
            {/* Geometric Art Deco Patterns */}
            <div className="absolute inset-0 geometric-patterns">
              <div className="pattern-line diagonal-1"></div>
              <div className="pattern-line diagonal-2"></div>
              <div className="pattern-line vertical-1"></div>
              <div className="pattern-line vertical-2"></div>
            </div>
            
            {/* Face Features */}
            <div className="absolute top-1/4 left-1/2 transform -translate-x-1/2 w-4/5 h-3/5 face-features">
              <div className="eye left-eye"></div>
              <div className="eye right-eye"></div>
              <div className="nose"></div>
              <div className="mouth"></div>
            </div>
          </div>

          {/* Cosmic Swirl - CSS Animation */}
          <div className="cosmic-swirl-container">
            <div className="cosmic-swirl swirl-layer-1"></div>
            <div className="cosmic-swirl swirl-layer-2"></div>
            <div className="cosmic-swirl swirl-layer-3"></div>
            
            {/* Enhanced Canvas Particles */}
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
    </div>
  );
};

export default LogoWithFluidSwirl;