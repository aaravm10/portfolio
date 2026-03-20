// MATCHDAY JavaScript

// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize flash message auto-hide
    initFlashMessages();
    
    // Initialize responsive navigation
    initMobileNavigation();
    
    // Initialize form enhancements
    initFormEnhancements();
    
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    console.log('MATCHDAY app initialized');
}

// Flash Messages
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideFlashMessage(message);
        }, 5000);
        
        // Add manual close functionality
        const closeBtn = message.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideFlashMessage(message);
            });
        }
    });
}

function hideFlashMessage(message) {
    message.style.animation = 'slideOutUp 0.3s ease';
    setTimeout(() => {
        message.remove();
    }, 300);
}

function showFlashMessage(text, type = 'info') {
    const flashContainer = document.querySelector('.flash-messages .container') || createFlashContainer();
    
    const message = document.createElement('div');
    message.className = `flash-message flash-${type}`;
    message.innerHTML = `
        <span>${text}</span>
        <button class="flash-close" type="button">&times;</button>
    `;
    
    // Add event listener for close button
    const closeBtn = message.querySelector('.flash-close');
    closeBtn.addEventListener('click', () => {
        hideFlashMessage(message);
    });
    
    flashContainer.appendChild(message);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideFlashMessage(message);
    }, 5000);
}

function createFlashContainer() {
    const flashSection = document.createElement('div');
    flashSection.className = 'flash-messages';
    
    const container = document.createElement('div');
    container.className = 'container';
    flashSection.appendChild(container);
    
    document.body.insertBefore(flashSection, document.querySelector('.main'));
    
    return container;
}

// Mobile Navigation
function initMobileNavigation() {
    // Add mobile menu toggle if needed
    const navbar = document.querySelector('.navbar');
    
    // Handle window resize
    window.addEventListener('resize', () => {
        // Reset mobile nav state on resize
        handleResponsiveNavigation();
    });
    
    handleResponsiveNavigation();
}

function handleResponsiveNavigation() {
    const navbar = document.querySelector('.navbar');
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        navbar.classList.add('mobile');
    } else {
        navbar.classList.remove('mobile');
    }
}

// Form Enhancements
function initFormEnhancements() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Add input validation feedback
    const inputs = document.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidationError);
    });
}

function handleFormSubmit(event) {
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn && !submitBtn.disabled) {
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;
        
        // Re-enable button after 10 seconds as fallback
        setTimeout(() => {
            if (submitBtn.disabled) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }, 10000);
    }
}

function validateInput(event) {
    const input = event.target;
    const isValid = input.checkValidity();
    
    // Remove existing validation styling
    input.classList.remove('valid', 'invalid');
    
    if (input.value.trim() !== '') {
        if (isValid) {
            input.classList.add('valid');
        } else {
            input.classList.add('invalid');
            showInputError(input, input.validationMessage);
        }
    }
}

function clearValidationError(event) {
    const input = event.target;
    input.classList.remove('invalid');
    
    // Remove error message
    const errorMsg = input.parentNode.querySelector('.input-error');
    if (errorMsg) {
        errorMsg.remove();
    }
}

function showInputError(input, message) {
    // Remove existing error message
    const existingError = input.parentNode.querySelector('.input-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'input-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#f44336';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentNode.appendChild(errorDiv);
}

// Smooth Scrolling
function initSmoothScrolling() {
    // Smooth scroll for anchor links
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        if (target.matches('a[href^="#"]')) {
            event.preventDefault();
            
            const targetId = target.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 100; // Account for fixed nav
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        }
    });
}

// Utility Functions
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

function throttle(func, wait) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, wait);
        }
    };
}

// API Utilities
async function makeRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Loading States
function showLoadingSpinner(element, text = 'Loading...') {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
        <div class="spinner"></div>
        <span>${text}</span>
    `;
    
    spinner.style.cssText = `
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        color: #666;
    `;
    
    const spinnerElement = spinner.querySelector('.spinner');
    spinnerElement.style.cssText = `
        width: 30px;
        height: 30px;
        border: 3px solid rgba(42, 167, 255, 0.3);
        border-top: 3px solid #2aa7ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    `;
    
    // Add CSS animation
    if (!document.querySelector('#spinner-styles')) {
        const style = document.createElement('style');
        style.id = 'spinner-styles';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    element.innerHTML = '';
    element.appendChild(spinner);
}

function hideLoadingSpinner(element) {
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Local Storage Utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return defaultValue;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
        return false;
    }
}

// Error Handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    
    // Show user-friendly error message
    showFlashMessage('An unexpected error occurred. Please refresh the page and try again.', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Show user-friendly error message
    showFlashMessage('A network error occurred. Please check your connection and try again.', 'error');
});

// Performance Monitoring
function measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
}

// Export useful functions to global scope
window.MATCHDAY = {
    showFlashMessage,
    hideFlashMessage,
    makeRequest,
    showLoadingSpinner,
    hideLoadingSpinner,
    debounce,
    throttle,
    saveToLocalStorage,
    loadFromLocalStorage,
    removeFromLocalStorage,
    measurePerformance
};

// Analytics (placeholder for future implementation)
function trackEvent(eventName, properties = {}) {
    // Placeholder for analytics tracking
    console.log('Event tracked:', eventName, properties);
}