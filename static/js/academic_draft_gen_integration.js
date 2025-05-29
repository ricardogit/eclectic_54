/**
 * Integration of Academic Paper Draft Generator with the Editor
 * This script adds the Draft Generator module to the dashboard menu
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply integrations when the DOM is loaded
    integrateAcademicDraftGenerator();
});

/**
 * Integrate the Academic Paper Draft Generator into the dashboard
 */
function integrateAcademicDraftGenerator() {
    console.log('Integrating Academic Paper Draft Generator...');

    // Add to dashboard menu
    addDraftGeneratorToMenu();

    // Handle quick action button if exists
    setupQuickActionButton();
}

/**
 * Add the Draft Generator option to the dashboard menu
 */
function addDraftGeneratorToMenu() {
    // 1. Find the dashboard menu
    const dashboardMenu = document.querySelector('.dashboard-menu, .main-menu, #document-actions');

    if (!dashboardMenu) {
        console.warn('Dashboard menu not found, creating fallback button');
        createFallbackButton();
        return;
    }

    // 2. Check if it's a dropdown menu or a sidebar menu
    if (dashboardMenu.classList.contains('dropdown-menu')) {
        // It's a dropdown menu, add item before the last divider
        const menuItems = dashboardMenu.querySelectorAll('.dropdown-item');

        if (menuItems.length > 0) {
            // Create the new menu item
            const draftGenItem = document.createElement('a');
            draftGenItem.href = '#';
            draftGenItem.className = 'dropdown-item';
            draftGenItem.id = 'draft-generator-menu';
            draftGenItem.innerHTML = '<i class="fa fa-file-text-o mr-2"></i> Academic Draft Generator';

            // Add click handler
            draftGenItem.addEventListener('click', function(e) {
                e.preventDefault();
                openDraftGenerator();
            });

            // Find a good place to insert - before a divider or at the end
            const divider = dashboardMenu.querySelector('.dropdown-divider');
            if (divider) {

                dashboardMenu.insertBefore(draftGenItem, divider);
            } else {
                dashboardMenu.appendChild(draftGenItem);
            }
        }
    } else {
        // It's likely a sidebar menu, add as new item
        const sidebarItem = document.createElement('li');
        sidebarItem.className = 'nav-item';
        sidebarItem.innerHTML = `
            <a href="#" class="nav-link" id="draft-generator-menu">
                <i class="fa fa-file-text-o"></i>
                <span>Academic Draft Generator</span>
            </a>
        `;

        // Add click handler
        sidebarItem.querySelector('a').addEventListener('click', function(e) {
            e.preventDefault();
            openDraftGenerator();
        });

        dashboardMenu.appendChild(sidebarItem);
    }

    console.log('Draft Generator menu item added');
}

/**
 * Create a fallback button if menu not found
 */
function createFallbackButton() {
    // Create a floating action button
    const fab = document.createElement('button');
    fab.className = 'btn btn-primary position-fixed';
    fab.id = 'draft-generator-fab';
    fab.innerHTML = '<i class="fa fa-file-text-o"></i> Draft Generator';
    fab.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000;';

    // Add click handler
    fab.addEventListener('click', function() {
        openDraftGenerator();
    });

    // Add to body
    document.body.appendChild(fab);

    console.log('Draft Generator fallback button added');
}

/**
 * Set up quick action button if it exists on the dashboard
 */
function setupQuickActionButton() {
    // Look for quick action container
    const quickActions = document.querySelector('.quick-actions, .dashboard-actions');

    if (!quickActions) return;

    // Create quick action button
    const quickActionBtn = document.createElement('div');
    quickActionBtn.className = 'quick-action-item';
    quickActionBtn.innerHTML = `
        <div class="card h-100">
            <div class="card-body text-center">
                <i class="fa fa-file-text-o fa-3x mb-2"></i>
                <h5>Create Academic Draft</h5>
                <p class="text-muted small">Generate paper drafts with AI</p>
            </div>
        </div>
    `;

    // Add click handler
    quickActionBtn.addEventListener('click', function() {
        openDraftGenerator();
    });

    // Add to quick actions
    quickActions.appendChild(quickActionBtn);

    console.log('Quick action button added');
}

/**
 * Open the Draft Generator module
 */
function openDraftGenerator() {
    console.log('Opening Draft Generator...');

    // Get the base URL from the current page
    const baseUrl = window.location.origin;

    // Determine how to open the module
    const moduleUrl = `${baseUrl}/academic-draft-generator`;

    // Check module display preference from localStorage
    const openInIframe = localStorage.getItem('open_modules_in_iframe') === 'true';

    if (openInIframe) {
        // Open in iframe/modal
        showModuleInModal(moduleUrl, 'Academic Paper Draft Generator');
    } else {
        // Open in new tab
        window.open(moduleUrl, '_blank');
    }
}

/**
 * Show the module in a modal with iframe
 */
function showModuleInModal(url, title) {
    // Create modal if it doesn't exist
    let moduleModal = document.getElementById('module-modal');

    if (!moduleModal) {
        const modalHTML = `
        <div class="modal fade" id="module-modal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog modal-xl" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="module-modal-title"></h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body p-0">
                        <iframe id="module-iframe" style="width:100%; height:80vh; border:none;"></iframe>
                    </div>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        moduleModal = document.getElementById('module-modal');
    }

    // Set modal title and iframe src
    document.getElementById('module-modal-title').textContent = title;
    document.getElementById('module-iframe').src = url;

    // Show the modal
    $('#module-modal').modal('show');
}

/**
 * Handle sending generated content to the editor
 * This will be called from the Dash app via postMessage
 */
function receiveGeneratedContent(content) {
    // Check if we have an active editor
    if (typeof editor !== 'undefined' && editor) {
        // Insert content at cursor position
        const cursor = editor.getCursor();
        editor.replaceRange(content, cursor);

        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Draft content inserted into editor', 'success');
        } else {
            alert('Draft content inserted into editor');
        }
    } else {
        console.error('Editor not available');
        alert('Cannot insert content: Editor not available');
    }
}

// Set up event listener for messages from the Dash app
window.addEventListener('message', function(event) {
    // Verify sender origin for security
    const trustedOrigins = [window.location.origin];
    if (!trustedOrigins.includes(event.origin)) return;

    // Process message data
    const data = event.data;
    if (data && data.type === 'draftContent') {
        receiveGeneratedContent(data.content);
    }
});

// Expose necessary functions globally
window.openDraftGenerator = openDraftGenerator;
window.receiveGeneratedContent = receiveGeneratedContent;
