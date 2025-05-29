/**
 * Collaborator management module
 * Handles adding, removing, and managing document collaborators
 */

// Store selected user for adding
let selectedUserId = null;

/**
 * Initialize collaborator management
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize collaborator functionality
    setupCollaboratorManagement();
});

/**
 * Set up collaborator management UI and events
 */
function setupCollaboratorManagement() {
    // "Add Collaborator" button in the main UI
    const addCollabBtn = document.getElementById('add-collaborator');
    if (addCollabBtn) {
        addCollabBtn.addEventListener('click', function() {
            showCollaboratorsModal();
        });
    }

    // "Manage Collaborators" link in dropdown
    const manageCollabLink = document.getElementById('manage-collaborators');
    if (manageCollabLink) {
        manageCollabLink.addEventListener('click', function(e) {
            e.preventDefault();
            showCollaboratorsModal();
        });
    }

    // Search button in collaborator modal
    const searchBtn = document.getElementById('search-collaborator');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            searchUsers();
        });
    }

    // Email input enter key handling
    const emailInput = document.getElementById('collaborator-email');
    if (emailInput) {
        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchUsers();
            }
        });
    }

    // "Add Collaborator" button in modal
    const addBtn = document.getElementById('add-collaborator-btn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            addCollaborator();
        });
    }

    // Close button/dismiss modal events
    const closeBtn = document.querySelector('#collaborators-modal .modal-footer button, #collaborators-modal .close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            $('#collaborators-modal').modal('hide');
        });
    }

    console.log('Collaborator management initialized');
}

/**
 * Show the collaborators management modal
 */
function showCollaboratorsModal() {
    console.log('Showing collaborator modal');

    // Create or ensure modal exists with proper structure
    ensureCollaboratorModalExists();

    // Reset modal state
    const emailInput = document.getElementById('collaborator-email');
    const resultsContainer = document.getElementById('user-search-results');
    const addButton = document.getElementById('add-collaborator-btn');

    if (emailInput) emailInput.value = '';
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
    }
    if (addButton) addButton.disabled = true;

    // Reset selected user
    selectedUserId = null;

    // Load current collaborators
    loadCollaborators();

    // Show modal
    $('#collaborators-modal').modal('show');

    // Force focus on email input after modal is shown
    $('#collaborators-modal').on('shown.bs.modal', function() {
        document.getElementById('collaborator-email').focus();
    });
}

/**
 * Ensure the collaborator modal exists with proper structure
 */
function ensureCollaboratorModalExists() {
    // Check if modal already exists
    let modal = document.getElementById('collaborators-modal');

    // If it exists but doesn't have the right structure, remove it
    if (modal && (!modal.classList.contains('modal') || !modal.querySelector('.modal-dialog'))) {
        modal.remove();
        modal = null;
    }

    // Create modal if it doesn't exist
    if (!modal) {
        const modalHTML = `
        <div class="modal fade" id="collaborators-modal" tabindex="-1" role="dialog" aria-labelledby="collaborators-modal-label" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="collaborators-modal-label">Manage Collaborators</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="collaborator-email">Add Collaborator</label>
                            <div class="input-group">
                                <input type="email" class="form-control" id="collaborator-email" placeholder="Enter email">
                                <div class="input-group-append">
                                    <button class="btn btn-primary" id="search-collaborator">Search</button>
                                </div>
                            </div>
                        </div>
                        <div id="user-search-results" class="mb-3" style="display: none;">
                            <!-- Results will be populated here -->
                        </div>
                        <div class="form-group">
                            <label for="permission-level">Permission Level</label>
                            <select class="form-control" id="permission-level">
                                <option value="view">View Only</option>
                                <option value="comment">Comment</option>
                                <option value="edit">Edit</option>
                            </select>
                        </div>
                        <button id="add-collaborator-btn" class="btn btn-success mb-3" disabled>Add Collaborator</button>
                        <hr>
                        <h6>Current Collaborators</h6>
                        <div id="current-collaborators-list">
                            <!-- Populated via JavaScript -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Re-initialize event handlers for the new modal
        setupCollaboratorManagement();
    }

    // Ensure modal has proper z-index and positioning
    addCollaboratorModalStyles();
}

/**
 * Add CSS styles for the collaborator modal
 */
function addCollaboratorModalStyles() {
    const styleId = 'collaborator-modal-styles';

    // Don't add duplicate styles
    if (document.getElementById(styleId)) return;

    const styleEl = document.createElement('style');
    styleEl.id = styleId;
    styleEl.textContent = `
        #collaborators-modal {
            position: fixed !important;
            top: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            left: 0 !important;
            z-index: 1050 !important;
            display: none;
            overflow: hidden;
            outline: 0;
        }

        #collaborators-modal .modal-dialog {
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 500px;
            max-width: 90%;
            margin: 0 !important;
        }

        .user-result-item {
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin-bottom: 5px;
            cursor: pointer;
        }

        .user-result-item:hover {
            background-color: #f8f9fa;
        }

        .user-result-item.selected {
            background-color: #e9ecef;
            border-color: #007bff;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }

        .collaborator-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin-bottom: 5px;
        }

        .permission-view {
            background-color: #cff4fc;
            color: #055160;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8rem;
        }

        .permission-comment {
            background-color: #fff3cd;
            color: #664d03;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8rem;
        }

        .permission-edit {
            background-color: #d1e7dd;
            color: #0f5132;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8rem;
        }
    `;

    document.head.appendChild(styleEl);
}

/**
 * Search for users by email
 */
function searchUsers() {
    const email = document.getElementById('collaborator-email').value.trim();
    const searchButton = document.getElementById('search-collaborator');
    const resultsContainer = document.getElementById('user-search-results');

    if (!email || email.length < 3) {
        showNotification('Please enter at least 3 characters', 'warning');
        return;
    }

    console.log('Searching for users with email:', email);

    // Show loading state
    searchButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Searching...';
    searchButton.disabled = true;
    resultsContainer.innerHTML = '<div class="text-center"><i class="fa fa-spinner fa-spin"></i> Searching...</div>';
    resultsContainer.style.display = 'block';

    // Add a timeout to handle network failures
    const searchTimeout = setTimeout(() => {
        searchButton.innerHTML = 'Search';
        searchButton.disabled = false;
        resultsContainer.innerHTML = '<div class="alert alert-danger">Search request timed out. Please try again.</div>';
    }, 8000); // 8 second timeout

    fetch(`/api/users/search?q=${encodeURIComponent(email)}`)
        .then(response => {
            clearTimeout(searchTimeout);
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Reset button
            searchButton.innerHTML = 'Search';
            searchButton.disabled = false;

            // Process results
            resultsContainer.innerHTML = '';

            if (!data.users || data.users.length === 0) {
                resultsContainer.innerHTML = '<p>No users found with that email address.</p>';
                return;
            }

            console.log('Found users:', data.users.length);

            // Create user list
            data.users.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'user-result-item';
                userItem.dataset.userId = user.id;
                userItem.dataset.email = user.email;
                userItem.dataset.fullName = user.full_name || user.name || user.email;

                userItem.innerHTML = `
                    <strong>${user.full_name || user.name || 'User'}</strong>
                    <div>${user.email}</div>
                `;

                userItem.addEventListener('click', function() {
                    // Store selected user
                    selectedUserId = user.id;
                    console.log('User selected:', this.dataset.email, 'ID:', selectedUserId);

                    // Highlight the selected user
                    document.querySelectorAll('.user-result-item').forEach(item => {
                        item.classList.remove('selected');
                    });
                    this.classList.add('selected');

                    // Enable the add button
                    const addButton = document.getElementById('add-collaborator-btn');
                    if (addButton) addButton.disabled = false;
                });

                resultsContainer.appendChild(userItem);
            });
        })
        .catch(error => {
            clearTimeout(searchTimeout);
            // Reset button and show error
            searchButton.innerHTML = 'Search';
            searchButton.disabled = false;

            console.error('Error searching users:', error);
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error searching for users: ${error.message}</div>`;
        });
}

/**
 * Add a collaborator to the document
 */
function addCollaborator() {
    console.log('Adding collaborator');

    if (!selectedUserId) {
        showNotification('Please select a user first', 'warning');
        return;
    }

    const permissionLevel = document.getElementById('permission-level').value;
    const addButton = document.getElementById('add-collaborator-btn');

    console.log('Adding collaborator with ID:', selectedUserId, 'and permission:', permissionLevel);

    // Show loading state
    addButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Adding...';
    addButton.disabled = true;

    fetch(`/api/documents/${documentId}/collaborators`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: selectedUserId,
            permission_level: permissionLevel
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Reset button
        addButton.innerHTML = 'Add Collaborator';
        addButton.disabled = true;

        if (data.success) {
            showNotification('Collaborator added successfully', 'success');

            // Reset selection
            selectedUserId = null;

            // Load updated collaborator list
            loadCollaborators();

            // Reset the UI
            document.getElementById('collaborator-email').value = '';
            document.getElementById('user-search-results').innerHTML = '';
            document.getElementById('user-search-results').style.display = 'none';

            // Focus on email input for adding another collaborator
            document.getElementById('collaborator-email').focus();
        } else {
            throw new Error(data.error || 'Unknown error adding collaborator');
        }
    })
    .catch(error => {
        // Reset button
        addButton.innerHTML = 'Add Collaborator';
        addButton.disabled = false;

        console.error('Error adding collaborator:', error);
        showNotification('Failed to add collaborator: ' + error.message, 'error');
    });
}

/**
 * Load the collaborators list
 */
function loadCollaborators() {
    const container = document.getElementById('current-collaborators-list');
    if (!container) return;

    // Show loading state
    container.innerHTML = '<div class="text-center"><i class="fa fa-spinner fa-spin"></i> Loading collaborators...</div>';

    fetch(`/api/documents/${documentId}/collaborators`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Clear container
            container.innerHTML = '';

            if (!data.collaborators || data.collaborators.length === 0) {
                container.innerHTML = '<p>No collaborators added yet.</p>';
                return;
            }

            console.log('Loaded collaborators:', data.collaborators.length);

            // Create collaborator list
            data.collaborators.forEach(collab => {
                const item = document.createElement('div');
                item.className = 'collaborator-item';

                const permissionClass = `permission-${collab.permission_level}`;

                item.innerHTML = `
                    <div class="collaborator-info">
                        <div class="collaborator-name">${collab.full_name || collab.name || 'User'}</div>
                        <div class="collaborator-email">${collab.email}</div>
                    </div>
                    <div class="collaborator-actions">
                        <span class="collaborator-permission ${permissionClass}">${collab.permission_level}</span>
                        ${typeof isOwner !== 'undefined' && isOwner ?
                          `<button class="btn btn-sm btn-danger remove-collaborator" data-user-id="${collab.user_id}">Remove</button>` :
                          ''}
                    </div>
                `;

                container.appendChild(item);

                // Add event listener for the remove button
                const removeBtn = item.querySelector('.remove-collaborator');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        removeCollaborator(this.dataset.userId);
                    });
                }
            });
        })
        .catch(error => {
            console.error('Error loading collaborators:', error);
            container.innerHTML = `<div class="alert alert-danger">Error loading collaborators: ${error.message}</div>`;
        });
}

/**
 * Remove a collaborator from the document
 */
function removeCollaborator(userId) {
    if (!userId) return;

    if (!confirm('Are you sure you want to remove this collaborator?')) return;

    console.log('Removing collaborator with ID:', userId);

    fetch(`/api/documents/${documentId}/collaborators/${userId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Collaborator removed successfully', 'success');
            loadCollaborators();
        } else {
            throw new Error(data.error || 'Unknown error removing collaborator');
        }
    })
    .catch(error => {
        console.error('Error removing collaborator:', error);
        showNotification('Failed to remove collaborator: ' + error.message, 'error');
    });
}

// Export functions for use in other modules
window.showCollaboratorsModal = showCollaboratorsModal;
window.loadCollaborators = loadCollaborators;
window.addCollaborator = addCollaborator;
window.removeCollaborator = removeCollaborator;
window.searchUsers = searchUsers;
