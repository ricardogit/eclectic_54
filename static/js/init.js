/**
 * Main initialization script for the Dash Editor
 * This file handles the core functionality and coordinates between components
 */

/**
 * Initialize everything when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Dash Editor...');

    // Initialize editor tabs
    initializeTabs();

    // Set up document action buttons
    setupDocumentActions();

    // Set up section action buttons
    setupSectionActions();

    // Set up notification system
    setupNotifications();

    console.log('Dash Editor initialization complete');
});

/**
 * Initialize the tabs in the tools sidebar
 */
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.tool-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Deactivate all tabs and panels
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            // Activate the clicked tab and corresponding panel
            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-panel').classList.add('active');

            // If analysis tab is selected, refresh analysis
            if (this.dataset.tab === 'analysis') {
                if (typeof refreshAnalysis === 'function') {
                    refreshAnalysis();
                }
            }
        });
    });
}

/**
 * Set up document action buttons
 */
function setupDocumentActions() {
    // Set up document actions dropdown
    setupDocumentActionsDropdown();

    // Save document button
    const saveButton = document.getElementById('save-document');
    if (saveButton) {
        // Remove any existing handler
        const clonedBtn = saveButton.cloneNode(true);
        saveButton.parentNode.replaceChild(clonedBtn, saveButton);

        // Add fresh handler
        document.getElementById('save-document').addEventListener('click', function() {
            saveDocument();
        });
    }

    // Document title editing
    const docTitle = document.getElementById('document-title');
    if (docTitle) {
        docTitle.addEventListener('change', function() {
            saveDocumentTitle(this.value);
        });
    }
}

/**
 * Set up document actions dropdown
 */
function setupDocumentActionsDropdown() {
    // Clear any existing handlers to avoid duplicates
    const exportDoc = document.getElementById('export-document');
    const analyzeDoc = document.getElementById('analyze-document');
    const manageCollab = document.getElementById('manage-collaborators');
    const deleteDoc = document.getElementById('delete-document');

    // Remove existing listeners (best practice for avoiding duplicates)
    if (exportDoc) {
        const clonedExport = exportDoc.cloneNode(true);
        exportDoc.parentNode.replaceChild(clonedExport, exportDoc);
    }

    if (analyzeDoc) {
        const clonedAnalyze = analyzeDoc.cloneNode(true);
        analyzeDoc.parentNode.replaceChild(clonedAnalyze, analyzeDoc);
    }

    if (manageCollab) {
        const clonedManage = manageCollab.cloneNode(true);
        manageCollab.parentNode.replaceChild(clonedManage, manageCollab);
    }

    if (deleteDoc) {
        const clonedDelete = deleteDoc.cloneNode(true);
        deleteDoc.parentNode.replaceChild(clonedDelete, deleteDoc);
    }

    // Add fresh event listeners
    document.getElementById('export-document').addEventListener('click', function(e) {
        e.preventDefault();
        exportDocument();
    });

    document.getElementById('analyze-document').addEventListener('click', function(e) {
        e.preventDefault();
        analyzeDocument();
    });

    if (isOwner) {
        document.getElementById('manage-collaborators').addEventListener('click', function(e) {
            e.preventDefault();
            $('#collaborators-modal').modal('show');
        });

        document.getElementById('delete-document').addEventListener('click', function(e) {
            e.preventDefault();
            $('#delete-document-modal').modal('show');

            // Set up confirmation button
            document.getElementById('confirm-delete-document').onclick = function() {
                deleteDocumentAction();
            };
        });
    }
}

/**
 * Set up section action buttons
 */
function setupSectionActions() {
    // Set up section actions dropdown
    setupSectionActionsDropdown();
}

/**
 * Set up section actions dropdown
 */
function setupSectionActionsDropdown() {
    // Clear any existing handlers for section actions
    const addSubsection = document.getElementById('add-subsection');
    const viewRevisions = document.getElementById('view-revisions');

    // Remove existing listeners
    if (addSubsection) {
        const clonedAddSub = addSubsection.cloneNode(true);
        addSubsection.parentNode.replaceChild(clonedAddSub, addSubsection);
    }

    if (viewRevisions) {
        const clonedViewRev = viewRevisions.cloneNode(true);
        viewRevisions.parentNode.replaceChild(clonedViewRev, viewRevisions);
    }

    // Re-add template insertion handlers
    document.querySelectorAll('.dropdown-item[onclick^="insertTemplate"]').forEach(item => {
        const templateType = item.getAttribute('onclick').match(/'([^']+)'/)[1];
        const newItem = item.cloneNode(true);
        newItem.removeAttribute('onclick');
        newItem.addEventListener('click', function(e) {
            e.preventDefault();
            insertTemplate(templateType);
        });
        item.parentNode.replaceChild(newItem, item);
    });

    // Add fresh event listeners for section actions
    document.getElementById('add-subsection').addEventListener('click', function(e) {
        e.preventDefault();
        if (!currentSection) {
            showNotification('Please select a section first', 'warning');
            return;
        }
        showAddSectionModal(currentSection.id);
    });

    document.getElementById('view-revisions').addEventListener('click', function(e) {
        e.preventDefault();
        if (!currentSection) {
            showNotification('Please select a section first', 'warning');
            return;
        }
        loadSectionRevisions();
    });
}

/**
 * Load section revision history
 */
function loadSectionRevisions() {
    if (!currentSection) {
        showNotification('Please select a section first', 'warning');
        return;
    }

    // Show loading message
    const revisionsContainer = document.getElementById('revisions-list');
    revisionsContainer.innerHTML = '<div class="text-center"><i class="fa fa-spinner fa-spin"></i> Loading revisions...</div>';

    // Show modal
    $('#revisions-modal').modal('show');

    // Fetch revisions from API
    fetch(`/api/sections/${currentSection.id}/revisions`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load revisions');
            }
            return response.json();
        })
        .then(data => {
            // Clear container
            revisionsContainer.innerHTML = '';

            if (!data.revisions || data.revisions.length === 0) {
                revisionsContainer.innerHTML = '<p>No revision history available</p>';
                return;
            }

            // Add each revision to the list
            data.revisions.forEach(revision => {
                const date = new Date(revision.created_at);
                const formattedDate = date.toLocaleString();

                const revisionElement = document.createElement('div');
                revisionElement.className = 'revision-item';
                revisionElement.innerHTML = `
                    <div class="revision-header">
                        <span class="revision-author">${revision.user_name || 'User ' + revision.user_id}</span>
                        <span class="revision-date">${formattedDate}</span>
                    </div>
                    <div class="revision-content">${revision.content || '(No content)'}</div>
                `;

                revisionsContainer.appendChild(revisionElement);
            });
        })
        .catch(error => {
            console.error('Error loading revisions:', error);
            revisionsContainer.innerHTML = `<div class="alert alert-danger">Failed to load revisions: ${error.message}</div>`;
        });
}

/**
 * Save document title
 */
function saveDocumentTitle(title) {
    if (!title || !isOwner) return;

    // Show saving indicator
    const titleInput = document.getElementById('document-title');
    const originalValue = titleInput.value;
    titleInput.disabled = true;

    fetch(`/api/documents/${documentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: title })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update title');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Document title updated', 'success');
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error updating document title:', error);
        titleInput.value = originalValue;
        showNotification('Failed to update document title: ' + error.message, 'error');
    })
    .finally(() => {
        titleInput.disabled = false;
    });
}

/**
 * Save the entire document
 */
function saveDocument() {
    const title = document.getElementById('document-title').value;
    const saveButton = document.getElementById('save-document');

    // Show saving indicator
    saveButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Saving...';
    saveButton.disabled = true;

    fetch(`/api/documents/${documentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
            status: 'draft' // Could be updated to allow changing status
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save document');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Document saved successfully', 'success');
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error saving document:', error);
        showNotification('Failed to save document: ' + error.message, 'error');
    })
    .finally(() => {
        saveButton.innerHTML = 'Save';
        saveButton.disabled = false;
    });
}

/**
 * Export document function
 */
function exportDocument() {
    console.log('Exporting document...');

    const exportBtn = document.getElementById('export-document');
    if (exportBtn) {
        const originalText = exportBtn.textContent;
        exportBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Exporting...';
        exportBtn.disabled = true;
    }

    // Create a download URL for the document
    fetch(`/api/documents/${documentId}/export`, {
        method: 'GET',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Export failed');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = document.getElementById('document-title').value + '.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showNotification('Document exported successfully', 'success');
    })
    .catch(error => {
        console.error('Error exporting document:', error);
        showNotification('Failed to export document: ' + error.message, 'error');
    })
    .finally(() => {
        if (exportBtn) {
            exportBtn.innerHTML = originalText || 'Export';
            exportBtn.disabled = false;
        }
    });
}

/**
 * Analyze document function
 */
function analyzeDocument() {
    console.log('Analyzing document...');

    // Switch to analysis tab
    document.querySelector('.tab[data-tab="analysis"]').click();
}

/**
 * Delete document action
 */
function deleteDocumentAction() {
    fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete document');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Document deleted', 'success');
            // Redirect to documents list
            window.location.href = '/documents';
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error deleting document:', error);
        showNotification('Failed to delete document: ' + error.message, 'error');
        $('#delete-document-modal').modal('hide');
    });
}

/**
 * Helper function to acquire a section lock
 */
function acquireSectionLock(sectionId) {
    return fetch(`/api/sections/${sectionId}/lock`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => {
        if (response.ok) {
            return response.json().then(data => data.success === true);
        } else {
            console.error('Failed to acquire lock, status:', response.status);
            return false;
        }
    })
    .catch(error => {
        console.error('Error acquiring lock:', error);
        return false;
    });
}

/**
 * Helper function to release a section lock
 */
function releaseSectionLock(sectionId) {
    if (!sectionId) return Promise.resolve(false);

    return fetch(`/api/sections/${sectionId}/unlock`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => {
        if (response.ok) {
            return response.json().then(data => data.success === true);
        } else {
            console.error('Failed to release lock, status:', response.status);
            return false;
        }
    })
    .catch(error => {
        console.error('Error releasing lock:', error);
        return false;
    });
}

/**
 * Set up notification system
 */
function setupNotifications() {
    // Create a notification container if it doesn't exist
    let notificationContainer = document.getElementById('notification-container');

    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }

    // Set up global notification function
    window.customNotify = function(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-popup`;
        notification.innerHTML = message;
        notification.style.maxWidth = '300px';
        notification.style.marginBottom = '10px';
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease-in-out';

        // Add to container
        notificationContainer.appendChild(notification);

        // Fade in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notificationContainer.removeChild(notification);
            }, 300);
        }, 3000);
    };
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);

    // Use custom notification system if available
    if (typeof window.customNotify === 'function') {
        window.customNotify(message, type);
    } else {
        // Fallback to alert
        alert(message);
    }
}

/**
 * Search for users by email
 */
function searchUsers() {
    const email = document.getElementById('collaborator-email').value.trim();
    const searchButton = document.getElementById('search-collaborator');
    const resultsContainer = document.getElementById('user-search-results');

    if (email.length < 3) {
        showNotification('Please enter at least 3 characters', 'warning');
        return;
    }

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
                    // Highlight the selected user
                    document.querySelectorAll('.user-result-item').forEach(item => {
                        item.classList.remove('selected');
                    });
                    this.classList.add('selected');

                    // Enable the add button
                    document.getElementById('add-collaborator-btn').disabled = false;
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
    const selectedUser = document.querySelector('.user-result-item.selected');
    const addButton = document.getElementById('add-collaborator-btn');

    if (!selectedUser) {
        showNotification('Please select a user', 'warning');
        return;
    }

    const userId = selectedUser.dataset.userId;
    const permissionLevel = document.getElementById('permission-level').value;

    // Show loading state
    addButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Adding...';
    addButton.disabled = true;

    fetch(`/api/documents/${documentId}/collaborators`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
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

        if (data.success) {
            showNotification('Collaborator added successfully', 'success');

            // Load updated collaborator list
            loadCollaborators();

            // Reset the UI
            document.getElementById('collaborator-email').value = '';
            document.getElementById('user-search-results').innerHTML = '';
            document.getElementById('user-search-results').style.display = 'none';
            addButton.disabled = true;
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
                        ${isOwner ? `<button class="btn btn-sm btn-danger remove-collaborator" data-user-id="${collab.user_id}">Remove</button>` : ''}
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
 * Actions Buttons Fix
 * Add this to init.js
 */
// Fix document and section action dropdowns
function fixActionButtons() {
    console.log('Fixing action buttons...');

    // 1. Document Actions dropdown
    const docActionsBtn = document.getElementById('document-actions');
    if (docActionsBtn) {
        // Ensure dropdown toggle works
        $(docActionsBtn).off('click').on('click', function(e) {
            e.stopPropagation();
            $(this).next('.dropdown-menu').toggleClass('show');
        });
    }

    // Document action items
    const exportDoc = document.getElementById('export-document');
    const analyzeDoc = document.getElementById('analyze-document');
    const manageCollab = document.getElementById('manage-collaborators');
    const deleteDoc = document.getElementById('delete-document');

    if (exportDoc) {
        exportDoc.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Export document clicked');
            exportDocument();
        });
    }

    if (analyzeDoc) {
        analyzeDoc.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Analyze document clicked');
            analyzeDocument();
        });
    }

    if (manageCollab) {
        manageCollab.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Manage collaborators clicked');
            showCollaboratorsModal();
        });
    }

    if (deleteDoc) {
        deleteDoc.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Delete document clicked');
            $('#delete-document-modal').modal('show');
        });
    }

    // 2. Section Actions dropdown
    const sectionActionsBtn = document.getElementById('section-actions');
    if (sectionActionsBtn) {
        // Ensure dropdown toggle works
        $(sectionActionsBtn).off('click').on('click', function(e) {
            e.stopPropagation();
            $(this).next('.dropdown-menu').toggleClass('show');
        });
    }

    // Section action items
    const addSubsection = document.getElementById('add-subsection');
    const viewRevisions = document.getElementById('view-revisions');

    if (addSubsection) {
        addSubsection.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Add subsection clicked');
            if (!currentSection) {
                showNotification('Please select a section first', 'warning');
                return;
            }
            showAddSectionModal(currentSection.id);
        });
    }

    if (viewRevisions) {
        viewRevisions.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('View revisions clicked');
            if (!currentSection) {
                showNotification('Please select a section first', 'warning');
                return;
            }
            loadSectionRevisions();
        });
    }

    // Fix template insertion handlers - remove inline onclick
    document.querySelectorAll('.dropdown-item[onclick^="insertTemplate"]').forEach(item => {
        const onclickAttr = item.getAttribute('onclick');
        const templateMatch = onclickAttr.match(/insertTemplate\('([^']+)'\)/);

        if (templateMatch && templateMatch[1]) {
            const templateType = templateMatch[1];

            // Replace onclick with proper event listener
            item.removeAttribute('onclick');
            item.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Insert template clicked:', templateType);
                insertTemplate(templateType);
            });
        }
    });

    // Also fix dropdown hiding when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target) && !dropdown.previousElementSibling.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });

    console.log('Action buttons fixed');
}

/**
 * Global Initialization
 * Add this to your init.js file
 */
// Global initialization for all fixes
function initializeAllFixes() {
    console.log('Initializing all fixes...');

    // Fix action buttons
    if (typeof fixActionButtons === 'function') fixActionButtons();

    // Fix Add functionality
    if (typeof fixAddSectionFunctionality === 'function') fixAddSectionFunctionality();

    // Fix Delete functionality
    if (typeof fixDeleteFunctionality === 'function') fixDeleteFunctionality();

    // Fix Collapse/Expand functionality
    if (typeof fixCollapseExpandFunctionality === 'function') fixCollapseExpandFunctionality();

    // Fix Collaborator Modal
    if (typeof fixCollaboratorModal === 'function') fixCollaboratorModal();

    // Add CSS to fix modal z-index and positioning
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .modal {
            z-index: 1050 !important;
        }

        .modal-dialog {
            margin: 1.75rem auto;
            max-width: 500px;
        }

        .dropdown-menu {
            z-index: 1030 !important;
        }
    `;
    document.head.appendChild(styleEl);

    console.log('All fixes initialized');
}

// Call the initialization function after a slight delay
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeAllFixes, 100);
});

// Call this function on DOM load
document.addEventListener('DOMContentLoaded', fixActionButtons);
// Export functions for use in other modules
window.initializeTabs = initializeTabs;
window.saveDocument = saveDocument;
window.exportDocument = exportDocument;
window.analyzeDocument = analyzeDocument;
window.showNotification = showNotification;
window.acquireSectionLock = acquireSectionLock;
window.releaseSectionLock = releaseSectionLock;
