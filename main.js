// AI-Powered Smart Agriculture System - Main JavaScript

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Add fade in animation
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.animation = 'fadeIn 0.5s ease forwards';
    });
});

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Utility function to format numbers
function formatNumber(num) {
    return num.toFixed(2);
}

// Utility function to show spinner
function showSpinner(elementId) {
    document.getElementById(elementId).style.display = 'block';
}

// Utility function to hide spinner
function hideSpinner(elementId) {
    document.getElementById(elementId).style.display = 'none';
}

// Utility function to show alert
function showAlert(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

// API call wrapper
async function makeAPICall(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format time
function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-IN');
}

// Check if user is logged in (simple check)
function isLoggedIn() {
    return document.querySelector('nav .dropdown-toggle') !== null;
}

// Auto-dismiss alerts after 5 seconds
window.addEventListener('load', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Prevent form double submission
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function() {
        const buttons = this.querySelectorAll('button[type="submit"]');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        });
    });
});

// Log out functionality
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

console.log('Smart Agriculture System loaded successfully!');
