import React, { useState, useEffect } from 'react';
import { Sparkles, Zap, Globe, Shield, Cpu, Network } from 'lucide-react';

interface CosmicGlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'accent';
  interactive?: boolean;
}

const CosmicGlassCard: React.FC<CosmicGlassCardProps> = ({ 
  children, 
  className = '', 
  variant = 'primary',
  interactive = false 
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: ((e.clientX - rect.left) / rect.width) * 100,
      y: ((e.clientY - rect.top) / rect.height) * 100,
    });
  };

  const variantClasses = {
    primary: 'cosmic-glass-primary',
    secondary: 'cosmic-glass-secondary',
    accent: 'cosmic-glass-accent'
  };

  return (
    <div
      className={`cosmic-glass ${variantClasses[variant]} ${interactive ? 'cosmic-glass-interactive' : ''} ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        '--mouse-x': `${mousePosition.x}%`,
        '--mouse-y': `${mousePosition.y}%`,
      } as React.CSSProperties}
    >
      <div className="cosmic-glass-content">
        {children}
      </div>
      {interactive && (
        <div className={`cosmic-glass-light-orb ${isHovered ? 'active' : ''}`} />
      )}
    </div>
  );
};

const CosmicGlassShowcase: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const features = [
    {
      icon: Sparkles,
      title: "Quantum Processing",
      description: "Advanced quantum algorithms for unprecedented computational power",
      metric: "99.9% Uptime"
    },
    {
      icon: Shield,
      title: "Cosmic Security",
      description: "Multi-dimensional encryption protecting your data across realities",
      metric: "Zero Breaches"
    },
    {
      icon: Network,
      title: "Neural Networks",
      description: "Self-evolving AI systems that adapt to cosmic conditions",
      metric: "∞ Scalability"
    },
    {
      icon: Globe,
      title: "Universal Access",
      description: "Seamless connectivity across all known dimensions",
      metric: "24/7/365"
    }
  ];

  return (
    <div className="cosmic-showcase">
      {/* Hero Section */}
      <CosmicGlassCard variant="primary" interactive className="cosmic-hero">
        <div className="cosmic-hero-content">
          <div className="cosmic-logo">
            <Cpu className="cosmic-logo-icon" />
            <div className="cosmic-logo-text">
              <h1>COSMIC CORP</h1>
              <span>Beyond Reality</span>
            </div>
          </div>
          <p className="cosmic-tagline">
            Pioneering the future of interdimensional technology
          </p>
          <div className="cosmic-cta-group">
            <button className="cosmic-btn-primary">
              <Zap className="w-5 h-5" />
              Launch Platform
            </button>
            <button className="cosmic-btn-secondary">
              Explore Universe
            </button>
          </div>
        </div>
        <div className="cosmic-hero-visual">
          <div className="cosmic-orb-container">
            <div className="cosmic-orb cosmic-orb-1"></div>
            <div className="cosmic-orb cosmic-orb-2"></div>
            <div className="cosmic-orb cosmic-orb-3"></div>
          </div>
        </div>
      </CosmicGlassCard>

      {/* Navigation */}
      <CosmicGlassCard variant="secondary" className="cosmic-nav">
        <nav className="cosmic-nav-content">
          {['Platform', 'Solutions', 'Research', 'Contact'].map((item, index) => (
            <button
              key={item}
              className={`cosmic-nav-item ${activeTab === index ? 'active' : ''}`}
              onClick={() => setActiveTab(index)}
            >
              {item}
            </button>
          ))}
        </nav>
      </CosmicGlassCard>

      {/* Feature Grid */}
      <div className="cosmic-grid">
        {features.map((feature, index) => (
          <CosmicGlassCard key={index} variant="accent" interactive className="cosmic-feature-card">
            <div className="cosmic-feature-icon">
              <feature.icon className="w-8 h-8" />
            </div>
            <h3 className="cosmic-feature-title">{feature.title}</h3>
            <p className="cosmic-feature-description">{feature.description}</p>
            <div className="cosmic-feature-metric">{feature.metric}</div>
          </CosmicGlassCard>
        ))}
      </div>

      {/* Dashboard Preview */}
      <CosmicGlassCard variant="primary" interactive className="cosmic-dashboard">
        <div className="cosmic-dashboard-header">
          <h2>Cosmic Command Center</h2>
          <div className="cosmic-status-indicators">
            <div className="cosmic-status active">
              <div className="cosmic-status-dot"></div>
              <span>Systems Online</span>
            </div>
            <div className="cosmic-status">
              <div className="cosmic-status-dot warning"></div>
              <span>Quantum Sync</span>
            </div>
          </div>
        </div>
        <div className="cosmic-dashboard-content">
          <div className="cosmic-metrics-grid">
            <div className="cosmic-metric">
              <span className="cosmic-metric-label">Energy Output</span>
              <span className="cosmic-metric-value">1.21 GW</span>
            </div>
            <div className="cosmic-metric">
              <span className="cosmic-metric-label">Dimensions</span>
              <span className="cosmic-metric-value">∞</span>
            </div>
            <div className="cosmic-metric">
              <span className="cosmic-metric-label">Efficiency</span>
              <span className="cosmic-metric-value">99.97%</span>
            </div>
          </div>
          <div className="cosmic-chart-placeholder">
            <div className="cosmic-chart-bars">
              {Array.from({ length: 12 }).map((_, i) => (
                <div 
                  key={i} 
                  className="cosmic-chart-bar"
                  style={{ height: `${Math.random() * 80 + 20}%` }}
                />
              ))}
            </div>
          </div>
        </div>
      </CosmicGlassCard>
    </div>
  );
};

export default CosmicGlassShowcase;
export { CosmicGlassCard };