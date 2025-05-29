/**
 * Common JavaScript functions for the Dash Editor application
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(function(message) {
            const closeButton = message.querySelector('button.close');
            if (closeButton) {
                closeButton.click();
            }
        });
    }, 5000);

    // Password confirmation validation
    const passwordFields = document.querySelectorAll('input[type="password"][id="password"]');
    const confirmFields = document.querySelectorAll('input[type="password"][id="confirm_password"]');

    if (passwordFields.length > 0 && confirmFields.length > 0) {
        confirmFields.forEach(function(confirmField) {
            confirmField.addEventListener('input', function() {
                const password = document.getElementById('password').value;
                const confirmPassword = this.value;

                if (password !== confirmPassword) {
                    this.setCustomValidity('Passwords do not match');
                } else {
                    this.setCustomValidity('');
                }
            });
        });
    }

    // Initialize any Bootstrap tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Initialize any Bootstrap popovers
    $('[data-toggle="popover"]').popover();
});

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The message type (success, info, warning, error)
 */
function showNotification(message, type = 'info') {
    // Map type to Bootstrap alert classes
    const alertClass = type === 'error' ? 'danger' : type;

    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;

    // Add to container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertElement, container.firstChild);

        // Auto-hide after 5 seconds
        setTimeout(function() {
            $(alertElement).alert('close');
        }, 5000);
    }
}

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(dateString, includeTime = false) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };

    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }

    return date.toLocaleDateString('en-US', options);
}

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
