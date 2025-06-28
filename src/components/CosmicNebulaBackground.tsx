import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const CosmicNebulaBackground: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const animationIdRef = useRef<number>();

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );

    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: "high-performance"
    });
    rendererRef.current = renderer;
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mountRef.current.appendChild(renderer.domElement);

    // Nebula shader material
    const nebulaVertexShader = `
      varying vec2 vUv;
      varying vec3 vPosition;
      
      void main() {
        vUv = uv;
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const nebulaFragmentShader = `
      uniform float uTime;
      uniform vec2 uResolution;
      varying vec2 vUv;
      varying vec3 vPosition;

      // Noise function
      float noise(vec3 p) {
        return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
      }

      float fbm(vec3 p) {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;
        
        for(int i = 0; i < 6; i++) {
          value += amplitude * noise(p * frequency);
          amplitude *= 0.5;
          frequency *= 2.0;
        }
        return value;
      }

      void main() {
        vec2 uv = vUv;
        vec3 pos = vPosition + vec3(uTime * 0.1, uTime * 0.05, uTime * 0.08);
        
        // Create flowing nebula patterns
        float n1 = fbm(pos * 2.0);
        float n2 = fbm(pos * 3.0 + vec3(100.0));
        float n3 = fbm(pos * 1.5 + vec3(200.0));
        
        // Combine noise for complex patterns
        float pattern = n1 * 0.5 + n2 * 0.3 + n3 * 0.2;
        
        // Create color gradients
        vec3 color1 = vec3(0.16, 0.08, 0.30); // Deep purple #2A0A4C
        vec3 color2 = vec3(0.0, 0.4, 0.8);    // Electric blue #0066CC
        vec3 color3 = vec3(1.0, 0.41, 0.71);  // Nebula pink #FF69B4
        vec3 color4 = vec3(0.1, 0.1, 0.1);    // Black marble #1A1A1A
        
        // Mix colors based on pattern
        vec3 finalColor = mix(color4, color1, pattern);
        finalColor = mix(finalColor, color2, smoothstep(0.3, 0.7, pattern));
        finalColor = mix(finalColor, color3, smoothstep(0.6, 1.0, pattern));
        
        // Add some brightness variation
        finalColor *= (0.5 + 0.5 * sin(uTime + pattern * 10.0));
        
        gl_FragColor = vec4(finalColor, 0.8);
      }
    `;

    // Create nebula plane
    const nebulaGeometry = new THREE.PlaneGeometry(20, 20, 100, 100);
    const nebulaMaterial = new THREE.ShaderMaterial({
      vertexShader: nebulaVertexShader,
      fragmentShader: nebulaFragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
      },
      transparent: true,
      blending: THREE.AdditiveBlending
    });

    const nebulaMesh = new THREE.Mesh(nebulaGeometry, nebulaMaterial);
    nebulaMesh.position.z = -5;
    scene.add(nebulaMesh);

    // Star particles
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 2000;
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 50;
      positions[i + 1] = (Math.random() - 0.5) * 50;
      positions[i + 2] = (Math.random() - 0.5) * 20;

      // Brass and silver star colors
      const isBrass = Math.random() > 0.7;
      if (isBrass) {
        colors[i] = 0.81;     // Brass R
        colors[i + 1] = 0.71; // Brass G
        colors[i + 2] = 0.23; // Brass B
      } else {
        colors[i] = 0.75;     // Silver R
        colors[i + 1] = 0.75; // Silver G
        colors[i + 2] = 0.75; // Silver B
      }
    }

    starGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    starGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const starMaterial = new THREE.PointsMaterial({
      size: 2,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    camera.position.z = 5;

    // Mouse interaction
    const mouse = new THREE.Vector2();
    const handleMouseMove = (event: MouseEvent) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);

      const time = Date.now() * 0.001;
      
      // Update nebula shader
      if (nebulaMaterial.uniforms) {
        nebulaMaterial.uniforms.uTime.value = time;
      }

      // Rotate nebula slowly
      nebulaMesh.rotation.z = time * 0.1;

      // Animate stars
      stars.rotation.x = time * 0.05;
      stars.rotation.y = time * 0.02;

      // Mouse parallax effect
      camera.position.x = mouse.x * 0.5;
      camera.position.y = mouse.y * 0.5;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      
      if (nebulaMaterial.uniforms) {
        nebulaMaterial.uniforms.uResolution.value.set(window.innerWidth, window.innerHeight);
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      renderer.dispose();
    };
  }, []);

  return (
    <div 
      ref={mountRef} 
      className="fixed inset-0 z-0"
      style={{ background: 'linear-gradient(135deg, #1A1A1A 0%, #2A0A4C 50%, #0066CC 100%)' }}
    />
  );
};

export default CosmicNebulaBackground;