/**
 * KodeMinds 3D Animated Background
 * Seamless futuristic background with section-specific color themes
 */

class AnimatedBackground {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.waves = [];
        this.currentSection = 'hero';
        this.targetColors = {};
        this.currentColors = {};
        
        // Section color configurations
        this.sectionColors = {
            hero: {
                primary: new THREE.Color(0x0a1628),    // Deep blue
                secondary: new THREE.Color(0x00d9ff),  // Neon cyan
                accent: new THREE.Color(0x1e3a8a)      // Mid blue
            },
            about: {
                primary: new THREE.Color(0x1a0a28),    // Soft purple
                secondary: new THREE.Color(0xff69b4),  // Pink glow
                accent: new THREE.Color(0x8b5cf6)      // Purple accent
            },
            services: {
                primary: new THREE.Color(0x0a2828),    // Teal
                secondary: new THREE.Color(0x00ff88),  // Light green
                accent: new THREE.Color(0x14b8a6)      // Teal accent
            },
            contact: {
                primary: new THREE.Color(0x0a0f1e),    // Dark navy
                secondary: new THREE.Color(0xffd700),  // Golden
                accent: new THREE.Color(0x1e40af)      // Navy accent
            }
        };
        
        this.init();
        this.setupIntersectionObserver();
        this.animate();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        
        // Setup camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.z = 50;
        
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('bg-canvas'),
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Initialize colors
        this.currentColors = { ...this.sectionColors.hero };
        this.targetColors = { ...this.sectionColors.hero };
        
        // Create elements
        this.createParticles();
        this.createWaves();
        this.createLights();
        
        // Handle resize
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    createParticles() {
        const particleCount = 2000;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const velocities = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 200;
            positions[i + 1] = (Math.random() - 0.5) * 200;
            positions[i + 2] = (Math.random() - 0.5) * 100;
            
            velocities[i] = (Math.random() - 0.5) * 0.02;
            velocities[i + 1] = (Math.random() - 0.5) * 0.02;
            velocities[i + 2] = (Math.random() - 0.5) * 0.02;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
        
        const material = new THREE.PointsMaterial({
            size: 0.5,
            color: 0x00d9ff,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });
        
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }
    
    createWaves() {
        for (let i = 0; i < 3; i++) {
            const geometry = new THREE.PlaneGeometry(200, 200, 50, 50);
            const material = new THREE.MeshPhongMaterial({
                color: 0x1e3a8a,
                transparent: true,
                opacity: 0.15,
                wireframe: true,
                side: THREE.DoubleSide
            });
            
            const wave = new THREE.Mesh(geometry, material);
            wave.rotation.x = -Math.PI / 2;
            wave.position.y = -20 - (i * 10);
            wave.position.z = -30;
            
            this.waves.push(wave);
            this.scene.add(wave);
        }
    }
    
    createLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambientLight);
        
        // Point lights
        const light1 = new THREE.PointLight(0x00d9ff, 1, 100);
        light1.position.set(20, 20, 20);
        this.scene.add(light1);
        
        const light2 = new THREE.PointLight(0xff69b4, 0.8, 100);
        light2.position.set(-20, -20, 20);
        this.scene.add(light2);
        
        const light3 = new THREE.PointLight(0x00ff88, 0.6, 100);
        light3.position.set(0, 0, -20);
        this.scene.add(light3);
    }
    
    setupIntersectionObserver() {
        const sections = document.querySelectorAll('section[data-bg-section]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio > 0.3) {
                    const section = entry.target.dataset.bgSection;
                    this.transitionToSection(section);
                }
            });
        }, {
            threshold: [0, 0.3, 0.5, 0.7, 1.0]
        });
        
        sections.forEach(section => observer.observe(section));
    }
    
    transitionToSection(section) {
        if (this.currentSection === section) return;
        
        this.currentSection = section;
        const colors = this.sectionColors[section] || this.sectionColors.hero;
        
        this.targetColors = { ...colors };
    }
    
    updateColors() {
        const lerpFactor = 0.02;
        
        // Lerp colors
        this.currentColors.primary.lerp(this.targetColors.primary, lerpFactor);
        this.currentColors.secondary.lerp(this.targetColors.secondary, lerpFactor);
        this.currentColors.accent.lerp(this.targetColors.accent, lerpFactor);
        
        // Update scene background
        this.scene.background = this.currentColors.primary;
        
        // Update particle color
        if (this.particles) {
            this.particles.material.color.copy(this.currentColors.secondary);
        }
        
        // Update wave colors
        this.waves.forEach((wave, index) => {
            wave.material.color.copy(this.currentColors.accent);
        });
        
        // Update lights
        const lights = this.scene.children.filter(child => child instanceof THREE.PointLight);
        if (lights.length >= 3) {
            lights[0].color.copy(this.currentColors.secondary);
            lights[1].color.copy(this.currentColors.accent);
            lights[2].color.copy(this.currentColors.primary);
        }
    }
    
    animateParticles() {
        if (!this.particles) return;
        
        const positions = this.particles.geometry.attributes.position.array;
        const velocities = this.particles.geometry.attributes.velocity.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            positions[i] += velocities[i];
            positions[i + 1] += velocities[i + 1];
            positions[i + 2] += velocities[i + 2];
            
            // Boundary check
            if (Math.abs(positions[i]) > 100) velocities[i] *= -1;
            if (Math.abs(positions[i + 1]) > 100) velocities[i + 1] *= -1;
            if (Math.abs(positions[i + 2]) > 50) velocities[i + 2] *= -1;
        }
        
        this.particles.geometry.attributes.position.needsUpdate = true;
        this.particles.rotation.y += 0.0005;
    }
    
    animateWaves() {
        const time = Date.now() * 0.0005;
        
        this.waves.forEach((wave, waveIndex) => {
            const positions = wave.geometry.attributes.position.array;
            
            for (let i = 0; i < positions.length; i += 3) {
                const x = positions[i];
                const y = positions[i + 1];
                
                positions[i + 2] = Math.sin(x * 0.1 + time + waveIndex) * 3 +
                                   Math.cos(y * 0.1 + time + waveIndex) * 3;
            }
            
            wave.geometry.attributes.position.needsUpdate = true;
            wave.rotation.z += 0.0002 * (waveIndex + 1);
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.updateColors();
        this.animateParticles();
        this.animateWaves();
        
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if Three.js is loaded
    if (typeof THREE !== 'undefined') {
        new AnimatedBackground();
    } else {
        console.error('Three.js is required for animated background');
    }
});
