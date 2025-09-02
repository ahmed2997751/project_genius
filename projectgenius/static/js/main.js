/**
 * EduSense Main JavaScript
 * Contains global functionality and utilities for the application
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize auto-resize textareas
    initializeAutoResize();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize theme handling
    initializeTheme();
    
    // Initialize notification system
    initializeNotifications();
    
    // Initialize analytics tracking
    initializeAnalytics();
    
    console.log('EduSense initialized successfully');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Auto-resize textareas based on content
 */
function initializeAutoResize() {
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initial resize
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    });
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize theme handling
 */
function initializeTheme() {
    // Set theme based on user preference or system preference
    const savedTheme = localStorage.getItem('edu-theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const theme = savedTheme || systemTheme;
    
    setTheme(theme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('edu-theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

/**
 * Set application theme
 * @param {string} theme - 'light' or 'dark'
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('edu-theme', theme);
    
    // Update theme toggle button if it exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
    }
}

/**
 * Toggle theme
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 5000);
    });
}

/**
 * Initialize analytics tracking
 */
function initializeAnalytics() {
    // Track page views
    trackPageView();
    
    // Track button clicks
    trackButtonClicks();
    
    // Track form submissions
    trackFormSubmissions();
}

/**
 * Track page view
 */
function trackPageView() {
    const page = window.location.pathname;
    console.log(`Page view: ${page}`);
    
    // In production, you would send this to your analytics service
    // analytics.track('page_view', { page: page });
}

/**
 * Track button clicks
 */
function trackButtonClicks() {
    const buttons = document.querySelectorAll('.btn[data-track]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-track');
            console.log(`Button click: ${action}`);
            
            // In production, you would send this to your analytics service
            // analytics.track('button_click', { action: action });
        });
    });
}

/**
 * Track form submissions
 */
function trackFormSubmissions() {
    const forms = document.querySelectorAll('form[data-track]');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const formName = this.getAttribute('data-track');
            console.log(`Form submission: ${formName}`);
            
            // In production, you would send this to your analytics service
            // analytics.track('form_submit', { form: formName });
        });
    });
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds (optional)
 */
function showNotification(message, type = 'info', duration = 4000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    
    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <i class="${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            const alertInstance = new bootstrap.Alert(notification);
            alertInstance.close();
        }
    }, duration);
}

/**
 * Get notification icon based on type
 * @param {string} type - Notification type
 * @returns {string} - Font Awesome icon class
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-triangle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Loading state management
 */
class LoadingManager {
    /**
     * Show loading state on element
     * @param {Element} element - Element to show loading on
     * @param {string} text - Loading text (optional)
     */
    static show(element, text = 'Loading...') {
        element.disabled = true;
        element.setAttribute('data-original-html', element.innerHTML);
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </span>
            ${text}
        `;
    }
    
    /**
     * Hide loading state
     * @param {Element} element - Element to hide loading from
     */
    static hide(element) {
        element.disabled = false;
        const originalHtml = element.getAttribute('data-original-html');
        if (originalHtml) {
            element.innerHTML = originalHtml;
            element.removeAttribute('data-original-html');
        }
    }
}

/**
 * Local Storage utilities
 */
class StorageManager {
    /**
     * Set item in localStorage
     * @param {string} key - Storage key
     * @param {any} value - Value to store
     */
    static set(key, value) {
        try {
            localStorage.setItem(`edu_${key}`, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    }
    
    /**
     * Get item from localStorage
     * @param {string} key - Storage key
     * @param {any} defaultValue - Default value if not found
     * @returns {any} - Stored value or default
     */
    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`edu_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }
    
    /**
     * Remove item from localStorage
     * @param {string} key - Storage key
     */
    static remove(key) {
        try {
            localStorage.removeItem(`edu_${key}`);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    }
    
    /**
     * Clear all EduSense data from localStorage
     */
    static clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('edu_')) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    }
}

/**
 * API utilities
 */
class ApiManager {
    /**
     * Make API request
     * @param {string} url - API endpoint
     * @param {object} options - Request options
     * @returns {Promise} - API response
     */
    static async request(url, options = {}) {
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
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    /**
     * POST request
     * @param {string} url - API endpoint
     * @param {object} data - Request data
     * @returns {Promise} - API response
     */
    static post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    /**
     * PUT request
     * @param {string} url - API endpoint
     * @param {object} data - Request data
     * @returns {Promise} - API response
     */
    static put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    /**
     * DELETE request
     * @param {string} url - API endpoint
     * @returns {Promise} - API response
     */
    static delete(url) {
        return this.request(url, {
            method: 'DELETE',
        });
    }
}

/**
 * Form utilities
 */
class FormManager {
    /**
     * Serialize form data
     * @param {HTMLFormElement} form - Form element
     * @returns {object} - Serialized form data
     */
    static serialize(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    /**
     * Validate form
     * @param {HTMLFormElement} form - Form element
     * @returns {boolean} - Whether form is valid
     */
    static validate(form) {
        return form.checkValidity();
    }
    
    /**
     * Clear form
     * @param {HTMLFormElement} form - Form element
     */
    static clear(form) {
        form.reset();
        form.classList.remove('was-validated');
    }
}

/**
 * Utility functions
 */
const Utils = {
    /**
     * Debounce function
     * @param {function} func - Function to debounce
     * @param {number} delay - Delay in milliseconds
     * @returns {function} - Debounced function
     */
    debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },
    
    /**
     * Throttle function
     * @param {function} func - Function to throttle
     * @param {number} limit - Limit in milliseconds
     * @returns {function} - Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Format date
     * @param {Date|string} date - Date to format
     * @param {object} options - Intl.DateTimeFormat options
     * @returns {string} - Formatted date
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        };
        
        const config = { ...defaultOptions, ...options };
        return new Intl.DateTimeFormat('en-US', config).format(new Date(date));
    },
    
    /**
     * Generate random ID
     * @param {number} length - ID length
     * @returns {string} - Random ID
     */
    generateId(length = 8) {
        return Math.random().toString(36).substr(2, length);
    },
    
    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} - Whether copy was successful
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            return false;
        }
    },
    
    /**
     * Check if element is in viewport
     * @param {Element} element - Element to check
     * @returns {boolean} - Whether element is visible
     */
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Make utilities available globally
window.EduSense = {
    LoadingManager,
    StorageManager,
    ApiManager,
    FormManager,
    Utils,
    showNotification,
    toggleTheme
};

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('An unexpected error occurred. Please try again.', 'error');
});

// Handle global errors
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});
