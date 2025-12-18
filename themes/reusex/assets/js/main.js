// ReUseX Theme JavaScript

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.open-mobile-menu');
    const closeMobileMenuButton = document.querySelector('.close-mobile-menu');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.add('open');
        });
    }
    
    if (closeMobileMenuButton && mobileMenu) {
        closeMobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.remove('open');
        });
    }
    
    // Close mobile menu when clicking on menu links
    if (mobileMenu) {
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('open');
            });
        });
    }

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add animation classes on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeInUp');
            }
        });
    }, observerOptions);

    // Observe elements that should animate on scroll
    const animatedElements = document.querySelectorAll('.grid > div, .prose > *, section > div');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
});

// ========================================
// Before-and-After Image Slider Component
// ========================================

/**
 * Initialize all before-and-after sliders on the page
 * This function can be called multiple times and will work with multiple sliders
 */
function initBeforeAfterSliders() {
    // Find all slider containers
    const sliders = document.querySelectorAll('.before-after-slider');
    
    sliders.forEach((slider, index) => {
        // Skip if already initialized
        if (slider.dataset.initialized === 'true') {
            return;
        }
        
        // Mark as initialized to prevent duplicate initialization
        slider.dataset.initialized = 'true';
        
        const beforeImage = slider.querySelector('.before-image');
        const divider = slider.querySelector('.before-after-divider');
        const handle = slider.querySelector('.before-after-handle');
        
        if (!beforeImage || !divider || !handle) {
            console.warn('Before-after slider missing required elements:', slider);
            return;
        }
        
        let isDragging = false;
        
        // Create AbortController for proper cleanup of event listeners
        const abortController = new AbortController();
        const signal = abortController.signal;
        
        // Store cleanup function on the slider element for potential later cleanup
        slider._cleanupSlider = () => {
            abortController.abort();
        };
        
        /**
         * Update the position of the divider and clip the before image
         * @param {number} percentage - Position as percentage (0-100)
         */
        function updateSliderPosition(percentage) {
            // Clamp percentage between 0 and 100
            percentage = Math.max(0, Math.min(100, percentage));
            
            // Update divider position
            divider.style.left = percentage + '%';
            
            // Clip the before image (show only the left portion)
            beforeImage.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;
        }
        
        /**
         * Get the percentage position from a mouse/touch event
         * @param {MouseEvent|TouchEvent} event
         * @returns {number} Percentage position (0-100)
         */
        function getPositionPercentage(event) {
            const rect = slider.getBoundingClientRect();
            let clientX;
            
            // Handle both mouse and touch events
            if (event.type.startsWith('touch')) {
                // Safety check for touch events
                if (!event.touches || event.touches.length === 0) {
                    return 50; // Default to center if no touch data
                }
                clientX = event.touches[0].clientX;
            } else {
                clientX = event.clientX;
            }
            
            const x = clientX - rect.left;
            const percentage = (x / rect.width) * 100;
            return percentage;
        }
        
        /**
         * Start dragging
         */
        function startDragging(event) {
            isDragging = true;
            slider.style.cursor = 'ew-resize';
            event.preventDefault();
        }
        
        /**
         * Stop dragging
         */
        function stopDragging() {
            isDragging = false;
            slider.style.cursor = 'default';
        }
        
        /**
         * Handle dragging
         */
        function onDrag(event) {
            if (isDragging) {
                const percentage = getPositionPercentage(event);
                updateSliderPosition(percentage);
            }
        }
        
        // Mouse events
        handle.addEventListener('mousedown', startDragging, { signal });
        slider.addEventListener('mousedown', function(event) {
            // Allow clicking anywhere on the slider to move the divider
            if (event.target === slider || event.target === beforeImage || 
                event.target === slider.querySelector('.after-image')) {
                startDragging(event);
                const percentage = getPositionPercentage(event);
                updateSliderPosition(percentage);
            }
        }, { signal });
        
        document.addEventListener('mousemove', onDrag, { signal });
        document.addEventListener('mouseup', stopDragging, { signal });
        
        // Touch events for mobile
        handle.addEventListener('touchstart', startDragging, { passive: false, signal });
        slider.addEventListener('touchstart', function(event) {
            if (event.target === slider || event.target === beforeImage || 
                event.target === slider.querySelector('.after-image')) {
                startDragging(event);
                const percentage = getPositionPercentage(event);
                updateSliderPosition(percentage);
            }
        }, { passive: false, signal });
        
        document.addEventListener('touchmove', onDrag, { passive: false, signal });
        document.addEventListener('touchend', stopDragging, { signal });
        
        // Keyboard accessibility
        handle.setAttribute('tabindex', '0');
        handle.setAttribute('role', 'slider');
        handle.setAttribute('aria-label', 'Slide to compare before and after images');
        handle.setAttribute('aria-valuemin', '0');
        handle.setAttribute('aria-valuemax', '100');
        handle.setAttribute('aria-valuenow', '50');
        
        handle.addEventListener('keydown', function(event) {
            let currentPercentage = parseFloat(divider.style.left) || 50;
            let newPercentage = currentPercentage;
            
            // Arrow keys to move the slider
            if (event.key === 'ArrowLeft') {
                newPercentage = currentPercentage - 5;
                event.preventDefault();
            } else if (event.key === 'ArrowRight') {
                newPercentage = currentPercentage + 5;
                event.preventDefault();
            } else if (event.key === 'Home') {
                newPercentage = 0;
                event.preventDefault();
            } else if (event.key === 'End') {
                newPercentage = 100;
                event.preventDefault();
            }
            
            if (newPercentage !== currentPercentage) {
                updateSliderPosition(newPercentage);
                handle.setAttribute('aria-valuenow', Math.round(newPercentage));
            }
        }, { signal });
        
        // Initialize at 50%
        updateSliderPosition(50);
        
        console.log('Before-after slider initialized:', index);
    });
}

// Initialize sliders when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBeforeAfterSliders);
} else {
    initBeforeAfterSliders();
}

// Console log for Hugo
console.log('ReUseX - Sustainable Resource Revolution | Built with Hugo');
