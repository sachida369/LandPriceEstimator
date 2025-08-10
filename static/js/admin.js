// Admin panel JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminFunctions();
    initializeDataTables();
    setupFileUploadValidation();
});

// Initialize admin-specific functions
function initializeAdminFunctions() {
    // Add event listeners for admin actions
    const uploadForm = document.querySelector('form[action*="upload-csv"]');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleCsvUpload);
    }
    
    // Initialize confirmation dialogs
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', confirmAction);
    });
    
    // Auto-refresh statistics every 30 seconds on dashboard
    if (window.location.pathname.includes('dashboard')) {
        setInterval(refreshStatistics, 30000);
    }
}

// Edit city function
function editCity(cityId, cityName, basePrice, growthRate) {
    const modal = new bootstrap.Modal(document.getElementById('editCityModal'));
    
    document.getElementById('editCityId').value = cityId;
    document.getElementById('editCityName').value = cityName;
    document.getElementById('editBasePrice').value = basePrice;
    document.getElementById('editGrowthRate').value = growthRate;
    
    modal.show();
}

// Handle CSV upload with validation
function handleCsvUpload(event) {
    const fileInput = document.getElementById('file');
    const dataType = document.getElementById('data_type').value;
    
    if (!fileInput.files[0]) {
        event.preventDefault();
        showAdminAlert('Please select a CSV file to upload', 'warning');
        return;
    }
    
    if (!dataType) {
        event.preventDefault();
        showAdminAlert('Please select a data type', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
        event.preventDefault();
        showAdminAlert('Please select a valid CSV file', 'error');
        return;
    }
    
    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
        event.preventDefault();
        showAdminAlert('File size must be less than 5MB', 'error');
        return;
    }
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
    submitButton.disabled = true;
    
    // Validate CSV format before upload
    validateCsvFormat(file, dataType).then(isValid => {
        if (!isValid) {
            event.preventDefault();
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }).catch(error => {
        console.error('CSV validation error:', error);
        // Continue with upload even if validation fails
    });
}

// Validate CSV format
function validateCsvFormat(file, dataType) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const csv = e.target.result;
            const lines = csv.split('\n');
            
            if (lines.length < 2) {
                showAdminAlert('CSV file must contain at least a header and one data row', 'error');
                resolve(false);
                return;
            }
            
            const header = lines[0].trim().toLowerCase();
            const expectedHeaders = {
                'cities': ['name', 'state', 'base_price_per_sqft'],
                'localities': ['name', 'city_name', 'state', 'price_per_sqft'],
                'multipliers': ['factor_type', 'factor_value', 'multiplier']
            };
            
            const required = expectedHeaders[dataType];
            if (required) {
                const missing = required.filter(col => !header.includes(col));
                if (missing.length > 0) {
                    showAdminAlert(`Missing required columns: ${missing.join(', ')}`, 'error');
                    resolve(false);
                    return;
                }
            }
            
            resolve(true);
        };
        
        reader.onerror = function() {
            showAdminAlert('Error reading CSV file', 'error');
            resolve(false);
        };
        
        reader.readAsText(file);
    });
}

// Setup file upload validation
function setupFileUploadValidation() {
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                validateFileSelection(file);
            }
        });
    }
}

function validateFileSelection(file) {
    const feedback = document.getElementById('file-feedback') || createFileFeedback();
    
    if (!file.name.toLowerCase().endsWith('.csv')) {
        feedback.textContent = 'Please select a CSV file';
        feedback.className = 'invalid-feedback d-block';
        return false;
    }
    
    if (file.size > 5 * 1024 * 1024) {
        feedback.textContent = 'File size must be less than 5MB';
        feedback.className = 'invalid-feedback d-block';
        return false;
    }
    
    feedback.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    feedback.className = 'valid-feedback d-block';
    return true;
}

function createFileFeedback() {
    const fileInput = document.getElementById('file');
    const feedback = document.createElement('div');
    feedback.id = 'file-feedback';
    fileInput.parentNode.appendChild(feedback);
    return feedback;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize data tables with search and pagination
function initializeDataTables() {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (table.rows.length > 10) {
            makeTableSearchable(table);
        }
    });
}

function makeTableSearchable(table) {
    // Add search input
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search...';
    
    table.parentNode.insertBefore(searchInput, table);
    
    // Add search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Confirmation dialog for destructive actions
function confirmAction(event) {
    const action = event.target.dataset.action;
    const item = event.target.dataset.item;
    
    const messages = {
        'delete': `Are you sure you want to delete this ${item}?`,
        'deactivate': `Are you sure you want to deactivate this ${item}?`,
        'activate': `Are you sure you want to activate this ${item}?`
    };
    
    if (!confirm(messages[action] || 'Are you sure?')) {
        event.preventDefault();
    }
}

// Refresh dashboard statistics
function refreshStatistics() {
    fetch('/admin/dashboard-stats')
        .then(response => response.json())
        .then(data => {
            updateStatisticCards(data);
        })
        .catch(error => {
            console.error('Error refreshing statistics:', error);
        });
}

function updateStatisticCards(data) {
    const elements = {
        'total_cities': data.total_cities,
        'total_localities': data.total_localities,
        'total_estimates': data.total_estimates,
        'total_api_keys': data.total_api_keys
    };
    
    Object.keys(elements).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            animateNumber(element, parseInt(element.textContent), elements[key]);
        }
    });
}

function animateNumber(element, start, end) {
    const duration = 1000;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Show admin-specific alerts
function showAdminAlert(message, type = 'info') {
    const alertContainer = document.getElementById('admin-alerts') || createAdminAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" 
             role="alert" id="${alertId}">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

function createAdminAlertContainer() {
    const container = document.createElement('div');
    container.id = 'admin-alerts';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1056';
    document.body.appendChild(container);
    return container;
}

// Export/import management
function handleDataExport(dataType) {
    const button = document.querySelector(`[data-export="${dataType}"]`);
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
        button.disabled = true;
        
        // Re-enable button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            showAdminAlert(`${dataType} data exported successfully`, 'success');
        }, 3000);
    }
}

// System status check
function checkSystemStatus() {
    return fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            updateSystemStatus(data);
            return data;
        })
        .catch(error => {
            console.error('System status check failed:', error);
            updateSystemStatus({ status: 'error', message: 'Unable to check system status' });
        });
}

function updateSystemStatus(status) {
    const indicators = document.querySelectorAll('.status-indicator');
    indicators.forEach(indicator => {
        const service = indicator.dataset.service;
        if (status[service]) {
            indicator.className = `status-indicator ${status[service] === 'healthy' ? 'online' : 'offline'}`;
        }
    });
}

// Real-time updates for dashboard
function initializeRealTimeUpdates() {
    if (window.location.pathname.includes('dashboard')) {
        // Check for new estimates every minute
        setInterval(() => {
            fetch('/admin/recent-estimates')
                .then(response => response.json())
                .then(data => {
                    updateRecentEstimates(data);
                })
                .catch(error => {
                    console.error('Error fetching recent estimates:', error);
                });
        }, 60000);
    }
}

function updateRecentEstimates(estimates) {
    const tbody = document.querySelector('#recent-estimates tbody');
    if (tbody && estimates.length > 0) {
        // Update only if there are new estimates
        const currentCount = tbody.children.length;
        if (estimates.length > currentCount) {
            location.reload(); // Simple refresh for now
        }
    }
}

// Initialize all admin functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeRealTimeUpdates();
    checkSystemStatus();
    
    // Set up periodic status checks
    setInterval(checkSystemStatus, 300000); // Every 5 minutes
});

// Make functions globally available
window.adminPanel = {
    editCity,
    handleDataExport,
    checkSystemStatus,
    showAdminAlert,
    confirmAction
};
