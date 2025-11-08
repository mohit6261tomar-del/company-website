// Enhanced Home Page JavaScript with Advanced Animations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all animations and effects
    initParticleSystem();
    initScrollAnimations();
    initAdvancedHoverEffects();
    initCounterAnimations();
    initParallaxEffects();
    initInteractiveElements();
    initLoadingAnimations();

    // Particle System for Background Effects
    function initParticleSystem() {
        const particleContainers = document.querySelectorAll('.particle-bg');

        particleContainers.forEach(container => {
            for (let i = 0; i < 20; i++) {
                createParticle(container);
            }
        });

        function createParticle(container) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';

            // Random size for particles
            const size = Math.random() * 6 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';

            container.appendChild(particle);

            // Remove particle after animation ends
            particle.addEventListener('animationend', () => {
                particle.remove();
                createParticle(container);
            });
        }
    }

    // Advanced Scroll Animations
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const staggerObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;

                    // Add stagger delays for multiple elements
                    const siblings = [...element.parentElement.children];
                    const index = siblings.indexOf(element);
                    element.style.animationDelay = (index * 0.1) + 's';

                    element.classList.add('animate-fade-in-up');
                    staggerObserver.unobserve(element);
                }
            });
        }, observerOptions);

        // Observe elements for staggered animations
        document.querySelectorAll('.service-card, .feature-box, .testimonial-card').forEach(element => {
            staggerObserver.observe(element);
        });

        // Scroll reveal animations
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.scroll-reveal').forEach(element => {
            revealObserver.observe(element);
        });
    }

    // Enhanced Hover Effects
    function initAdvancedHoverEffects() {
        // Magnetic effect for buttons
        const magneticButtons = document.querySelectorAll('.btn-gradient');

        magneticButtons.forEach(button => {
            button.addEventListener('mousemove', (e) => {
                const rect = button.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;

                button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) translateY(-5px) scale(1.05)`;
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = '';
            });
        });

        // Ripple effect for cards
        const cards = document.querySelectorAll('.service-card, .feature-box, .testimonial-card');

        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');

                this.appendChild(ripple);

                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Add ripple CSS dynamically
        const rippleCSS = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
                z-index: 1;
            }

            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;

        const style = document.createElement('style');
        style.textContent = rippleCSS;
        document.head.appendChild(style);
    }

    // Enhanced Counter Animations
    function initCounterAnimations() {
        function animateCounter(element, target, duration = 2000) {
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;

            function updateCounter() {
                current += increment;
                if (current < target) {
                    element.textContent = Math.floor(current).toLocaleString();
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = target.toLocaleString();
                }
            }

            updateCounter();
        }

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const target = parseInt(element.dataset.counter);
                    animateCounter(element, target);
                    counterObserver.unobserve(element);
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('.stats-number').forEach(element => {
            counterObserver.observe(element);
        });
    }

    // Advanced Parallax Effects
    function initParallaxEffects() {
        let ticking = false;

        function updateParallax() {
            const scrolled = window.pageYOffset;

            // Parallax for hero section elements
            const heroElements = document.querySelectorAll('.hero-section img, .hero-content');
            heroElements.forEach((element, index) => {
                const speed = 0.1 + (index * 0.05);
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });

            // Parallax for floating elements
            const floatingElements = document.querySelectorAll('.floating-element');
            floatingElements.forEach((element, index) => {
                const speed = 0.05 + (index * 0.02);
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });

            ticking = false;
        }

        function requestParallaxUpdate() {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }

        window.addEventListener('scroll', requestParallaxUpdate);
    }

    // Interactive Elements
    function initInteractiveElements() {
        // Smooth scrolling for anchor links with enhanced easing
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start',
                        inline: 'nearest'
                    });
                }
            });
        });

        // Enhanced back to top functionality
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 300) {
                    backToTop.style.display = 'block';
                    backToTop.style.transform = 'scale(1)';
                    backToTop.style.opacity = '1';
                } else {
                    backToTop.style.transform = 'scale(0.8)';
                    backToTop.style.opacity = '0.7';
                }
            });

            backToTop.addEventListener('click', (e) => {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }

        // Interactive service cards with 3D tilt effect
        const serviceCards = document.querySelectorAll('.service-card');
        serviceCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-15px) scale(1.02)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });

        // Animated progress bars
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const width = entry.target.dataset.width || '100%';
                        entry.target.style.setProperty('--progress-width', width);
                        entry.target.classList.add('animate');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(bar);
        });
    }

    // Loading Animations
    function initLoadingAnimations() {
        // Fade in elements on page load
        const animateOnLoad = document.querySelectorAll('.animate-fade-in-up');
        animateOnLoad.forEach((element, index) => {
            element.style.animationDelay = (index * 0.1) + 's';
            element.classList.add('animate-fade-in-up');
        });

        // Typing effect for hero text
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            const text = heroTitle.textContent;
            heroTitle.textContent = '';

            let i = 0;
            function typeWriter() {
                if (i < text.length) {
                    heroTitle.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 50);
                }
            }

            // Start typing after a delay
            setTimeout(typeWriter, 1000);
        }
    }

    // Enhanced mobile menu with animations
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('menu-open');

            // Animate hamburger icon
            const icon = this.querySelector('.navbar-toggler-icon');
            if (document.body.classList.contains('menu-open')) {
                icon.style.transform = 'rotate(90deg)';
            } else {
                icon.style.transform = 'rotate(0deg)';
            }
        });
    }

    // Mouse move parallax for hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.addEventListener('mousemove', (e) => {
            const mouseX = (e.clientX / window.innerWidth) * 100;
            const mouseY = (e.clientY / window.innerHeight) * 100;

            const bg = heroSection.querySelector('::before') || heroSection;
            bg.style.backgroundPosition = `${mouseX}% ${mouseY}%`;
        });
    }

    // Auto-animate elements on viewport entry
    const autoAnimateObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                autoAnimateObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        autoAnimateObserver.observe(element);
    });

    // Performance optimization: Debounce scroll events
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Apply debouncing to scroll-heavy functions
    window.addEventListener('scroll', debounce(() => {
        // Any scroll-based calculations that don't need to run on every frame
    }, 100));

    console.log('Enhanced animations initialized successfully!');
});
