/**
 * Settings module JavaScript utilities
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings module JavaScript initialized');

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Show confirmation for delete actions
    setupDeleteConfirmations();

    // Handle theme changes if applicable
    setupThemeToggle();
});

/**
 * Setup confirmation prompts for delete actions
 */
function setupDeleteConfirmations() {
    // Find all delete links or buttons
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const itemName = this.getAttribute('data-item-name') || 'item';
            const confirmationMessage = `Are you sure you want to delete this ${itemName}?`;

            if (confirm(confirmationMessage)) {
                // Get delete URL from data attribute
                const deleteUrl = this.getAttribute('data-delete-url');

                if (!deleteUrl) {
                    console.error('No delete URL specified.');
                    return;
                }

                // Perform delete action
                fetch(deleteUrl, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        showNotification(data.message || `${itemName} deleted successfully.`, 'success');

                        // Remove the element from the page if applicable
                        const targetId = this.getAttribute('data-target-id');
                        if (targetId) {
                            const target = document.getElementById(targetId);
                            if (target) {
                                target.remove();
                            }
                        } else {
                            // Refresh the page if no target specified
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                    } else {
                        // Show error message
                        showNotification(data.message || 'Error deleting item.', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('An error occurred. Please try again.', 'danger');
                });
            }
        });
    });
}

/**
 * Set up theme toggle functionality
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-preference');

    if (!themeToggle) return;

    themeToggle.addEventListener('change', function() {
        const selectedTheme = this.value;

        // Save theme preference
        saveThemePreference(selectedTheme);

        // Apply theme immediately
        applyTheme(selectedTheme);
    });

    // Apply current theme on page load
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (themeToggle.value !== currentTheme) {
        themeToggle.value = currentTheme;
    }
    applyTheme(currentTheme);
}

/**
 * Save theme preference to both localStorage and server
 */
function saveThemePreference(theme) {
    // Save to localStorage for immediate effect
    localStorage.setItem('theme', theme);

    // Save to server for persistence
    fetch('/settings/update-preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            theme: theme
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.warn('Failed to save theme preference to server:', data.message);
        }
    })
    .catch(error => {
        console.error('Error saving theme preference:', error);
    });
}

/**
 * Apply the selected theme to the page
 */
function applyTheme(theme) {
    const body = document.body;

    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');

    // Apply selected theme
    if (theme === 'dark') {
        body.classList.add('theme-dark');
    } else if (theme === 'light') {
        body.classList.add('theme-light');
    } else if (theme === 'system') {
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            body.classList.add('theme-dark');
        } else {
            body.classList.add('theme-light');
        }
    }
}

/**
 * Show notification message to the user
 */
function showNotification(message, type = 'info') {
    // Check if notification container exists
    let container = document.getElementById('notification-container');

    // Create container if it doesn't exist
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';

    // Add message
    notification.innerHTML = message;

    // Add close button
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close';
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');
    notification.appendChild(closeButton);

    // Add to container
    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}
