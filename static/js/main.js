// Main JavaScript functionality for Land Price Estimator

// Language support
const translations = {
    en: {
        'calculate_estimate': 'Calculate Price Estimate',
        'recent_searches': 'Recent Searches',
        'loading': 'Loading...',
        'error_occurred': 'An error occurred',
        'no_recent_searches': 'No recent searches found',
        'download_pdf': 'Download PDF Report',
        'copy_success': 'Copied to clipboard!',
        'copy_failed': 'Failed to copy'
    },
    hi: {
        'calculate_estimate': 'मूल्य अनुमान की गणना करें',
        'recent_searches': 'हाल की खोज',
        'loading': 'लोड हो रहा है...',
        'error_occurred': 'एक त्रुटि हुई',
        'no_recent_searches': 'कोई हाल की खोज नहीं मिली',
        'download_pdf': 'पीडीएफ रिपोर्ट डाउनलोड करें',
        'copy_success': 'क्लिपबोर्ड में कॉपी हो गया!',
        'copy_failed': 'कॉपी करने में असफल'
    }
};

let currentLanguage = localStorage.getItem('language') || 'en';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeLanguage();
    initializeFormValidation();
    initializeTooltips();
    loadRecentSearches();
    
    // Add loading animation to forms
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingOverlay();
        });
    });
});

// Language functions
function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    updatePageLanguage();
    
    // Show success message
    showToast(translations[lang]['copy_success'] || 'Language updated', 'success');
}

function initializeLanguage() {
    updatePageLanguage();
}

function updatePageLanguage() {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

function translate(key) {
    return translations[currentLanguage] && translations[currentLanguage][key] 
        ? translations[currentLanguage][key] 
        : key;
}

// Form validation and enhancement
function initializeFormValidation() {
    const estimationForm = document.getElementById('estimationForm');
    if (estimationForm) {
        estimationForm.addEventListener('submit', function(event) {
            if (!validateEstimationForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
        
        // Add real-time validation
        const plotSizeInput = document.getElementById('plot_size');
        if (plotSizeInput) {
            plotSizeInput.addEventListener('input', validatePlotSize);
        }
        
        const roadWidthInput = document.getElementById('road_width');
        if (roadWidthInput) {
            roadWidthInput.addEventListener('input', validateRoadWidth);
        }
    }
}

function validateEstimationForm() {
    let isValid = true;
    
    // Validate required fields
    const requiredFields = ['state', 'city', 'plot_size'];
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate plot size
    const plotSize = document.getElementById('plot_size');
    if (plotSize && plotSize.value) {
        const value = parseFloat(plotSize.value);
        if (value < 100 || value > 100000) {
            showFieldError(plotSize, 'Plot size must be between 100 and 100,000 sq ft');
            isValid = false;
        }
    }
    
    // Validate road width
    const roadWidth = document.getElementById('road_width');
    if (roadWidth && roadWidth.value) {
        const value = parseFloat(roadWidth.value);
        if (value < 6 || value > 100) {
            showFieldError(roadWidth, 'Road width must be between 6 and 100 feet');
            isValid = false;
        }
    }
    
    return isValid;
}

function validatePlotSize() {
    const plotSize = document.getElementById('plot_size');
    const value = parseFloat(plotSize.value);
    
    if (isNaN(value) || value < 100 || value > 100000) {
        showFieldError(plotSize, 'Plot size must be between 100 and 100,000 sq ft');
    } else {
        clearFieldError(plotSize);
    }
}

function validateRoadWidth() {
    const roadWidth = document.getElementById('road_width');
    const value = parseFloat(roadWidth.value);
    
    if (isNaN(value) || value < 6 || value > 100) {
        showFieldError(roadWidth, 'Road width must be between 6 and 100 feet');
    } else {
        clearFieldError(roadWidth);
    }
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    if (field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// Recent searches functionality
function showRecentSearches() {
    const modal = new bootstrap.Modal(document.getElementById('recentSearchesModal'));
    modal.show();
    loadRecentSearches();
}

function loadRecentSearches() {
    const listContainer = document.getElementById('recentSearchesList');
    if (!listContainer) return;
    
    fetch('/recent-searches')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                listContainer.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">${translate('no_recent_searches')}</h5>
                        <p class="text-muted">Your recent property searches will appear here</p>
                    </div>
                `;
            } else {
                const searchesHtml = data.map(search => `
                    <div class="card mb-2">
                        <div class="card-body py-2">
                            <div class="row align-items-center">
                                <div class="col-md-6">
                                    <strong>${search.city}, ${search.state}</strong>
                                    ${search.locality ? `<br><small class="text-muted">${search.locality}</small>` : ''}
                                </div>
                                <div class="col-md-3">
                                    <small class="text-muted">${search.plot_size} sq ft</small>
                                </div>
                                <div class="col-md-3 text-end">
                                    <span class="text-success fw-bold">${search.total_price}</span>
                                    <br><small class="text-muted">${search.timestamp}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                listContainer.innerHTML = searchesHtml;
            }
        })
        .catch(error => {
            console.error('Error loading recent searches:', error);
            listContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${translate('error_occurred')} while loading recent searches
                </div>
            `;
        });
}

// Utility functions
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast(translate('copy_success'), 'success');
        }).catch(() => {
            showToast(translate('copy_failed'), 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast(translate('copy_success'), 'success');
        } catch (err) {
            showToast(translate('copy_failed'), 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'}" 
             role="alert" aria-live="assertive" aria-atomic="true" id="${toastId}">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">${translate('loading')}</span>
            </div>
            <div class="mt-3 text-white">${message}</div>
        </div>
    `;
    document.body.appendChild(overlay);
    
    // Auto-remove after 30 seconds as failsafe
    setTimeout(() => {
        if (overlay.parentNode) {
            overlay.remove();
        }
    }, 30000);
    
    return overlay;
}

function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Format Indian currency
function formatIndianCurrency(amount) {
    if (amount >= 10000000) {
        return `₹${(amount / 10000000).toFixed(2)} Cr`;
    } else if (amount >= 100000) {
        return `₹${(amount / 100000).toFixed(2)} L`;
    } else {
        return `₹${amount.toLocaleString('en-IN')}`;
    }
}

// Debounce function for search inputs
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

// Auto-save form data to localStorage
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    const savedData = localStorage.getItem(`form_${formId}`);
    
    // Load saved data
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            inputs.forEach(input => {
                if (data[input.name] !== undefined) {
                    if (input.type === 'checkbox') {
                        input.checked = data[input.name];
                    } else {
                        input.value = data[input.name];
                    }
                }
            });
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }
    
    // Save data on change
    const saveData = debounce(() => {
        const data = {};
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                data[input.name] = input.checked;
            } else {
                data[input.name] = input.value;
            }
        });
        localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    }, 500);
    
    inputs.forEach(input => {
        input.addEventListener('change', saveData);
        input.addEventListener('input', saveData);
    });
    
    // Clear saved data on successful submission
    form.addEventListener('submit', () => {
        localStorage.removeItem(`form_${formId}`);
    });
}

// Initialize auto-save for estimation form
document.addEventListener('DOMContentLoaded', () => {
    autoSaveForm('estimationForm');
});

// Export functions for global use
window.landPriceEstimator = {
    setLanguage,
    showRecentSearches,
    copyToClipboard,
    showToast,
    formatIndianCurrency,
    showLoadingOverlay,
    hideLoadingOverlay
};
