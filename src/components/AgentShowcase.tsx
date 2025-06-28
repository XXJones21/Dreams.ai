import React from 'react';
import { Brain, Pen, Camera, Shield, Zap, Network } from 'lucide-react';

const agents = [
  {
    name: "Carthir",
    title: "The Narrative Architect",
    description: "Responsible for outlining the overarching narrative structure, establishing plot points, and ensuring logical progression. Carthir creates the foundation of your vision experience.",
    icon: Brain,
    color: "from-brass to-yellow-400",
    features: ["Story Structure", "Plot Development", "Narrative Logic", "Vision Campaigns"],
    tagline: "Conscious Creation"
  },
  {
    name: "Narnion",
    title: "The Dynamic Storyteller",
    description: "Dynamically adapts narratives based on your choices, improvises scenes, and manages story flow. Narnion brings your visions to life through intelligent storytelling.",
    icon: Pen,
    color: "from-electric-blue to-cyan-400",
    features: ["Dynamic Adaptation", "Player Checks", "Scene Improvisation", "Choice Integration"],
    tagline: "Reality Reimagined"
  },
  {
    name: "Cenedril",
    title: "The Cinematographer",
    description: "Transforms narrative elements into stunning visual experiences. Cenedril ensures every scene is cinematically crafted and visually consistent.",
    icon: Camera,
    color: "from-nebula-pink to-purple-400",
    features: ["Visual Generation", "Cinematic Style", "Scene Composition", "Visual Consistency"],
    tagline: "Vision Unleashed"
  }
];

const systemFeatures = [
  {
    icon: Shield,
    title: "Logical Coherence",
    description: "Advanced monitoring ensures narrative consistency and believable story progression.",
    tagline: "Dream Directed"
  },
  {
    icon: Zap,
    title: "Real-time Adaptation",
    description: "Stories evolve instantly based on your choices, creating truly personalized experiences.",
    tagline: "Conscious Creation"
  },
  {
    icon: Network,
    title: "Agent Collaboration",
    description: "Our AI agents work together seamlessly to craft the perfect narrative journey.",
    tagline: "Reality Reimagined"
  }
];

const AgentShowcase: React.FC = () => {
  return (
    <section className="relative z-20 py-20 bg-gradient-to-b from-black-marble/50 to-black-marble">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-cinzel font-bold text-stardust-silver mb-6">
            <span className="bg-gradient-to-r from-brass via-electric-blue to-nebula-pink bg-clip-text text-transparent">
              Meet Your AI Vision Team
            </span>
          </h2>
          <div className="text-2xl font-cinzel font-semibold text-brass mb-4">
            Vision Unleashed
          </div>
          <p className="text-xl text-stardust-silver/70 font-inter max-w-3xl mx-auto leading-relaxed">
            Our specialized AI agents work in harmony to create dynamic, responsive narratives that adapt to your every choice. Each agent brings unique expertise to craft your perfect vision experience.
          </p>
        </div>

        {/* Agent Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
          {agents.map((agent, index) => (
            <div key={index} className="agent-card group">
              <div className="relative p-8 h-full">
                {/* Agent Icon */}
                <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${agent.color} p-4 mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <agent.icon className="w-full h-full text-black-marble" />
                </div>

                {/* Agent Info */}
                <h3 className="text-2xl font-cinzel font-bold text-stardust-silver mb-2">
                  {agent.name}
                </h3>
                <h4 className={`text-lg font-inter font-semibold mb-2 bg-gradient-to-r ${agent.color} bg-clip-text text-transparent`}>
                  {agent.title}
                </h4>
                <div className="text-sm font-cinzel font-medium text-brass mb-4 opacity-80">
                  {agent.tagline}
                </div>
                <p className="text-stardust-silver/70 font-inter leading-relaxed mb-6">
                  {agent.description}
                </p>

                {/* Features */}
                <div className="space-y-2">
                  {agent.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${agent.color}`}></div>
                      <span className="text-sm text-stardust-silver/60 font-inter">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Hover Effect */}
                <div className={`absolute inset-0 bg-gradient-to-r ${agent.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300 rounded-2xl`}></div>
              </div>
            </div>
          ))}
        </div>

        {/* System Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {systemFeatures.map((feature, index) => (
            <div key={index} className="text-center p-6 glass-card group hover:border-brass/40 transition-all duration-300">
              <div className="w-12 h-12 mx-auto mb-4 text-brass group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-full h-full" />
              </div>
              <h3 className="text-xl font-cinzel font-semibold text-stardust-silver mb-2">
                {feature.title}
              </h3>
              <div className="text-sm font-cinzel font-medium text-brass mb-3 opacity-80">
                {feature.tagline}
              </div>
              <p className="text-stardust-silver/70 font-inter">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Technical Workflow */}
        <div className="p-8 glass-card">
          <h3 className="text-2xl font-cinzel font-bold text-center text-stardust-silver mb-4">
            How Lucids.Vision Works
          </h3>
          <div className="text-center text-brass font-cinzel font-medium mb-8">
            Conscious Creation in Action
          </div>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-center">
            {[
              "User Input",
              "Carthir Architects",
              "Narnion Adapts",
              "Cenedril Visualizes",
              "User Interacts",
              "Story Evolves"
            ].map((step, index) => (
              <React.Fragment key={index}>
                <div className="text-center">
                  <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-r from-brass to-electric-blue rounded-full flex items-center justify-center text-black-marble font-bold">
                    {index + 1}
                  </div>
                  <p className="text-sm text-stardust-silver/70 font-inter">{step}</p>
                </div>
                {index < 5 && (
                  <div className="hidden md:block w-full h-0.5 bg-gradient-to-r from-brass/30 to-electric-blue/30"></div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentShowcase;