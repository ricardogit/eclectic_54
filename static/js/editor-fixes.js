/**
 * Dash Editor Fixes
 * This file contains fixes and improvements for various editor components
 */

// Store references to original functions to avoid conflicts
const originalFunctions = {};

/**
 * Global initialization for all fixes
 */
function initializeAllFixes() {
    console.log('Initializing all editor fixes...');

    // Fix dashboard Edit button
    fixDashboardEditButton();

    // Fix New Document button
    fixNewDocumentButton();

    // Fix template insertion
    fixTemplateInsertion();

    // Fix Collaborator modal position
    fixCollaboratorModalPosition();

    // Implement auto-save
    implementAutoSave();

    // Fix Add Section dialog
    fixAddSectionDialog();

    // Fix action buttons
    fixActionButtons();

    // Fix add functionality
    fixAddSectionFunctionality();

    // Fix delete functionality
    fixDeleteFunctionality();

    // Fix collapse/expand functionality
    fixCollapseExpandFunctionality();

    // Fix collaborator modal
    fixCollaboratorModal();

    // Fix AI tabs
    fixAITabs();

    // Fix document creation
    fixDocumentCreation();

    // Add CSS fixes
    addGlobalCSSFixes();

    console.log('All editor fixes initialized');
}


/**
 * Fix Add Section dialog issues
 */
function fixAddSectionDialog() {
    console.log('Fixing Add Section dialog...');

    // Fix input field focusing issues
    function fixInputFocus() {
        // Fix for section title input
        $('#add-section-modal').on('shown.bs.modal', function() {
            setTimeout(() => {
                const titleInput = document.getElementById('new-section-title');
                if (titleInput) {
                    titleInput.focus();
                    // Test if input is working
                    titleInput.value = '';
                    titleInput.dispatchEvent(new Event('input'));
                }
            }, 300);
        });

        // Fix for subsection title input
        $('#add-subsection-modal').on('shown.bs.modal', function() {
            setTimeout(() => {
                const titleInput = document.getElementById('new-subsection-title');
                if (titleInput) {
                    titleInput.focus();
                    // Test if input is working
                    titleInput.value = '';
                    titleInput.dispatchEvent(new Event('input'));
                }
            }, 300);
        });
    }

    // Fix input field event handling
    function fixInputEvents() {
        const fixInput = function(inputId) {
            const input = document.getElementById(inputId);
            if (input) {
                // Remove any existing event listeners
                const newInput = input.cloneNode(true);
                input.parentNode.replaceChild(newInput, input);

                // Add working event listeners
                newInput.addEventListener('input', function() {
                    console.log(`${inputId} input event:`, this.value);
                });

                newInput.addEventListener('focus', function() {
                    console.log(`${inputId} focused`);
                });

                // Ensure input is enabled
                newInput.disabled = false;
                newInput.readOnly = false;
            }
        };

        // Fix section and subsection title inputs
        fixInput('new-section-title');
        fixInput('new-subsection-position');
        fixInput('new-subsection-title');
        fixInput('new-subsection-position');
    }

    // Fix section creation error reporting
    function fixErrorReporting() {
        // Override addNewSection function with improved error handling
        window.addNewRootSection = function() {
            const title = document.getElementById('new-section-title').value.trim();
            const position = parseInt(document.getElementById('new-section-position').value, 10) || 1;

            if (!title) {
                showNotification('Please enter a title for the section', 'warning');
                return;
            }

            console.log('Adding new root section:', title, 'at position', position);

            // Show loading state
            const confirmButton = document.getElementById('confirm-add-section');
            const originalText = confirmButton.textContent;
            confirmButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Adding...';
            confirmButton.disabled = true;

            // Send API request to create the section
            fetch('/api/sections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    document_id: documentId,
                    title: title,
                    parent_id: null,
                    position: position
                })
            })
            .then(response => {
                if (!response.ok) {
                    console.error('Server error:', response.status, response.statusText);
                    return response.json().then(errData => {
                        throw new Error(`Server error (${response.status}): ${errData.error || response.statusText}`);
                    }).catch(err => {
                        throw new Error(`Server error (${response.status}): ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Hide modal
                    $('#add-section-modal').modal('hide');

                    // Show success message
                    showNotification('Section added successfully', 'success');

                    // Refresh tree
                    refreshDocumentStructure();

                    // Load the new section if needed
                    if (data.section && data.section.id) {
                        setTimeout(() => {
                            loadSection(data.section.id);
                        }, 500); // Give time for tree to refresh
                    }
                } else {
                    throw new Error(data.error || 'Unknown error creating section');
                }
            })
            .catch(error => {
                console.error('Error adding section:', error);
                showNotification('Failed to add section: ' + error.message, 'error');
            })
            .finally(() => {
                // Reset button state
                confirmButton.innerHTML = originalText;
                confirmButton.disabled = false;
            });
        };

        // Similar fix for subsections
        window.addNewSubsection = function() {
            if (!currentSection) {
                showNotification('Please select a parent section first', 'warning');
                return;
            }

            const title = document.getElementById('new-subsection-title').value.trim();
            const position = parseInt(document.getElementById('new-subsection-position').value, 10) || 1;

            if (!title) {
                showNotification('Please enter a title for the subsection', 'warning');
                return;
            }

            console.log('Adding new subsection:', title, 'to parent', currentSection.id, 'at position', position);

            // Show loading state
            const confirmButton = document.getElementById('confirm-add-subsection');
            const originalText = confirmButton.textContent;
            confirmButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Adding...';
            confirmButton.disabled = true;

            // Send API request to create the subsection
            fetch('/api/sections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    document_id: documentId,
                    title: title,
                    parent_id: currentSection.id,
                    position: position
                })
            })
            .then(response => {
                if (!response.ok) {
                    console.error('Server error:', response.status, response.statusText);
                    return response.json().then(errData => {
                        throw new Error(`Server error (${response.status}): ${errData.error || response.statusText}`);
                    }).catch(err => {
                        throw new Error(`Server error (${response.status}): ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Hide modal
                    $('#add-subsection-modal').modal('hide');

                    // Show success message
                    showNotification('Subsection added successfully', 'success');

                    // Refresh tree
                    refreshDocumentStructure();

                    // Load the new section if needed
                    if (data.section && data.section.id) {
                        setTimeout(() => {
                            loadSection(data.section.id);
                        }, 500); // Give time for tree to refresh
                    }
                } else {
                    throw new Error(data.error || 'Unknown error creating subsection');
                }
            })
            .catch(error => {
                console.error('Error adding subsection:', error);
                showNotification('Failed to add subsection: ' + error.message, 'error');
            })
            .finally(() => {
                // Reset button state
                confirmButton.innerHTML = originalText;
                confirmButton.disabled = false;
            });
        };
    }

    // Apply all fixes
    fixInputFocus();
    fixInputEvents();
    fixErrorReporting();

    console.log('Add Section dialog fixed');
}

/**
 * Implement automatic saving when navigating the document tree
 */
function implementAutoSave() {
    console.log('Implementing automatic saving...');

    // Store original loadSection function
    const originalLoadSection = window.loadSection;

    // Override loadSection to include auto-save
    window.loadSection = function(sectionId) {
        // Check if there are unsaved changes and auto-save
        if (typeof editor !== 'undefined' && editor && currentSection && hasChanges()) {
            // Auto-save current section before loading new one
            autoSaveSection().then(() => {
                // After saving, load the new section
                callOriginalLoadSection(sectionId);
            }).catch((error) => {
                console.error('Auto-save failed:', error);

                // Ask user if they want to discard changes or stay on current section
                if (confirm('Auto-save failed. Discard changes and continue?')) {
                    callOriginalLoadSection(sectionId);
                } else {
                    // Reselect current node in tree
                    const tree = $('#document-tree').jstree(true);
                    if (tree && currentSection) {
                        tree.deselect_all(true);
                        tree.select_node(`node_${currentSection.id}`);
                    }
                }
            });
        } else {
            // No changes to save, load the section directly
            callOriginalLoadSection(sectionId);
        }
    };

    // Helper function to call original loadSection function
    function callOriginalLoadSection(sectionId) {
        if (typeof originalLoadSection === 'function') {
            originalLoadSection(sectionId);
        } else {
            console.error('Original loadSection function not found');

            // Fallback implementation
            // ... (same as the loadSection function from previous code)
        }
    }

    // Auto-save function
    function autoSaveSection() {
        return new Promise((resolve, reject) => {
            if (!currentSection || !isEditing) {
                resolve();
                return;
            }

            const content = editor.getValue();
            const title = document.getElementById('section-title').value;

            // Check if there are changes
            if (content === originalContent && title === currentSection.title) {
                resolve();
                return;
            }

            // Show saving indicator
            const statusElement = document.getElementById('edit-status');
            const originalStatus = statusElement ? statusElement.textContent : '';
            if (statusElement) {
                statusElement.textContent = 'Auto-saving...';
                statusElement.style.backgroundColor = '#cff4fc';
                statusElement.style.color = '#055160';
            }

            // Send update to server
            fetch(`/api/sections/${currentSection.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the section in memory
                    currentSection.title = title;
                    currentSection.content = content;

                    // Update the tree node title if it changed
                    if (title !== currentSection.title) {
                        updateTreeNodeTitle(currentSection.id, title);
                    }

                    // Update original content with the saved content
                    originalContent = content;

                    // Update status
                    if (statusElement) {
                        statusElement.textContent = 'Auto-saved';
                        setTimeout(() => {
                            statusElement.textContent = originalStatus;
                            statusElement.style.backgroundColor = '';
                            statusElement.style.color = '';
                        }, 2000);
                    }

                    resolve();
                } else {
                    if (statusElement) {
                        statusElement.textContent = originalStatus;
                        statusElement.style.backgroundColor = '';
                        statusElement.style.color = '';
                    }
                    reject(new Error(data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error auto-saving section:', error);
                if (statusElement) {
                    statusElement.textContent = originalStatus;
                    statusElement.style.backgroundColor = '';
                    statusElement.style.color = '';
                }
                reject(error);
            });
        });
    }

    // Add auto-save on interval
    let autoSaveInterval;

    // Start auto-save interval
    function startAutoSaveInterval() {
        // Auto-save every 30 seconds if there are changes
        autoSaveInterval = setInterval(() => {
            if (hasChanges()) {
                autoSaveSection().catch(error => {
                    console.error('Auto-save interval failed:', error);
                });
            }
        }, 30000); // 30 seconds
    }

    // Stop auto-save interval
    function stopAutoSaveInterval() {
        clearInterval(autoSaveInterval);
    }

    // Start auto-save interval when editing starts
    const originalEnableEditing = window.enableEditing;
    if (typeof originalEnableEditing === 'function') {
        window.enableEditing = function() {
            originalEnableEditing();
            startAutoSaveInterval();
        };
    }

    // Stop auto-save interval when editing ends
    const originalExitEditMode = window.exitEditMode;
    if (typeof originalExitEditMode === 'function') {
        window.exitEditMode = function() {
            originalExitEditMode();
            stopAutoSaveInterval();
        };
    }

    // Make autoSaveSection available globally
    window.autoSaveSection = autoSaveSection;

    console.log('Automatic saving implemented');
}

/**
 * Fix New Document button performance
 */
function fixNewDocumentButton() {
    console.log('Fixing New Document button performance...');

    // Find New Document buttons
    const newDocButtons = document.querySelectorAll('.new-document-btn, .create-document-btn, .dashboard-header .btn-primary');

    newDocButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Only if it's a link to new document page
            if (this.getAttribute('href') === '/editor/new' ||
                this.getAttribute('href') === '/editor/create' ||
                this.classList.contains('new-document-btn')) {

                e.preventDefault();

                // Show loading spinner in the button
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading...';
                this.disabled = true;

                // Create overlay to prevent additional clicks
                const overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '100%';
                overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
                overlay.style.zIndex = '9999';
                overlay.innerHTML = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);"><i class="fa fa-spinner fa-spin fa-3x"></i><p>Loading new document form...</p></div>';
                document.body.appendChild(overlay);

                // Navigate after a small delay to allow UI update
                setTimeout(() => {
                    window.location.href = this.getAttribute('href');
                }, 50);
            }
        });
    });

    console.log('New Document button performance fixed');
}

/**
 * Fix template insertion in editor
 */
function fixTemplateInsertion() {
    console.log('Fixing template insertion...');

    // Override the insertTemplate function
    window.insertTemplate = function(templateType) {
        if (!window.editor) {
            console.error('Editor not initialized');
            showNotification('Editor not ready. Please try again.', 'error');
            return;
        }

        if (!isEditing) {
            showNotification('Please click "Edit" to enable editing first', 'warning');
            return;
        }

        let templateText = '';

        // Define different templates
        switch (templateType) {
            case 'abstract':
                templateText = `## Abstract\n\nThis study examines [topic] by [methodology]. The results indicate [main findings]. These findings suggest [implications] which contribute to [field].`;
                break;
            case 'introduction':
                templateText = `## Introduction\n\n### Background\n[Provide context and background information]\n\n### Research Problem\n[State the research problem or question]\n\n### Significance\n[Explain why this research is important]\n\n### Objectives\n[List the main objectives of the study]`;
                break;
            case 'methods':
                templateText = `## Methods\n\n### Research Design\n[Describe the research design]\n\n### Participants\n[Describe the participants and sampling method]\n\n### Data Collection\n[Explain how data was collected]\n\n### Data Analysis\n[Explain how data was analyzed]`;
                break;
            case 'results':
                templateText = `## Results\n\n### Main Finding 1\n[Describe first main finding]\n\n### Main Finding 2\n[Describe second main finding]\n\n### Additional Findings\n[Describe any additional findings]`;
                break;
            case 'discussion':
                templateText = `## Discussion\n\n### Interpretation of Results\n[Interpret the main findings]\n\n### Comparison with Previous Research\n[Compare findings with previous studies]\n\n### Limitations\n[Discuss limitations of the study]\n\n### Implications\n[Discuss implications of the findings]`;
                break;
            case 'conclusion':
                templateText = `## Conclusion\n\n[Summarize the main findings and their importance]\n\n### Future Directions\n[Suggest directions for future research]`;
                break;
            case 'references':
                templateText = `## References\n\n- Author, A. A. (Year). Title of work. Publisher.\n- Author, B. B., & Author, C. C. (Year). Title of article. Journal Title, Volume(Issue), page range.\n- Author, D. D. (Year). Title of web document. Retrieved from URL`;
                break;
            case 'table':
                templateText = `| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n| Cell 4   | Cell 5   | Cell 6   |`;
                break;
        }

        if (templateText) {
            try {
                const cursor = editor.getCursor();

                // Insert the template text at the cursor position
                editor.replaceRange(templateText, cursor);

                // Show success notification
                showNotification(`Inserted ${templateType} template`, 'success');

                // Focus editor
                setTimeout(() => {
                    editor.focus();
                }, 50);

                // Close any open dropdowns
                document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
                    dropdown.classList.remove('show');
                });

                // Set flag to indicate content has changed
                const saveButton = document.getElementById('save-section');
                if (saveButton) {
                    saveButton.disabled = false;
                }
            } catch (error) {
                console.error('Failed to insert template:', error);
                showNotification('Failed to insert template. Please try again.', 'error');
            }
        }
    };

    console.log('Template insertion fixed');
}

/**
 * Fix dashboard Edit button performance
 */
function fixDashboardEditButton() {
    console.log('Fixing dashboard Edit button performance...');

    // Find all Edit buttons in the dashboard
    const editButtons = document.querySelectorAll('.dashboard-document-actions .edit-document-btn, .dashboard .edit-btn');

    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Prevent default only if we're handling it
            const documentId = this.dataset.documentId || this.getAttribute('href').split('/').pop();
            if (!documentId) return; // Let the default action handle it

            e.preventDefault();

            // Show loading spinner in the button
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading...';
            this.disabled = true;

            // Create overlay to prevent additional clicks
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
            overlay.style.zIndex = '9999';
            overlay.innerHTML = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);"><i class="fa fa-spinner fa-spin fa-3x"></i><p>Loading document...</p></div>';
            document.body.appendChild(overlay);

            // Navigate after a small delay to allow UI update
            setTimeout(() => {
                window.location.href = `/editor/${documentId}`;
            }, 50);
        });
    });

    console.log('Dashboard Edit button performance fixed');
}

/**
 * Fix document and section action dropdowns
 */
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
        const templateMatch = onclickAttr ? onclickAttr.match(/insertTemplate\('([^']+)'\)/) : null;

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
            if (!dropdown.contains(e.target) &&
                !dropdown.previousElementSibling.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });

    console.log('Action buttons fixed');
}

/**
 * Fix Add Section/Subsection functionality
 */
function fixAddSectionFunctionality() {
    console.log('Fixing Add Section functionality...');

    // Fix Add Section button
    const addSectionBtn = document.getElementById('add-section');
    if (addSectionBtn) {
        addSectionBtn.addEventListener('click', function() {
            console.log('Add section button clicked');
            showAddSectionModal(null);
        });
    }

    // Fix Add Subsection link in dropdown
    const addSubsectionLink = document.getElementById('add-subsection');
    if (addSubsectionLink) {
        addSubsectionLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Add subsection link clicked');

            if (!currentSection) {
                showNotification('Please select a section first', 'warning');
                return;
            }

            showAddSectionModal(currentSection.id);
        });
    }

    // Fix confirmation buttons in modals
    const confirmAddSection = document.getElementById('confirm-add-section');
    if (confirmAddSection) {
        confirmAddSection.addEventListener('click', function() {
            console.log('Confirm add section clicked');
            addNewRootSection();
        });
    }

    const confirmAddSubsection = document.getElementById('confirm-add-subsection');
    if (confirmAddSubsection) {
        confirmAddSubsection.addEventListener('click', function() {
            console.log('Confirm add subsection clicked');
            addNewSubsection();
        });
    }

    // Save references to original functions if they exist
    if (typeof window.showAddSectionModal === 'function') {
        originalFunctions.showAddSectionModal = window.showAddSectionModal;
    }

    // Override with fixed functions
    window.showAddSectionModal = showAddSectionModalFixed;
    window.addNewRootSection = addNewRootSection;
    window.addNewSubsection = addNewSubsection;

    console.log('Add Section functionality fixed');
}

/**
 * Fixed function to show add section/subsection modal
 */
function showAddSectionModalFixed(parentId) {
    console.log('Showing add section modal for parent:', parentId);

    if (parentId) {
        // Adding a subsection - get parent section title
        let parentTitle = 'Parent Section';

        try {
            const tree = $('#document-tree').jstree(true);
            const parentNode = tree.get_node(`node_${parentId}`);
            parentTitle = parentNode.text;
        } catch (error) {
            console.error('Error getting parent section title:', error);
        }

        // Update modal title
        const modalTitle = document.querySelector('#add-subsection-modal .modal-title');
        if (modalTitle) {
            modalTitle.textContent = `Add Subsection to "${parentTitle}"`;
        }

        // Reset form
        const form = document.getElementById('add-subsection-form');
        if (form) form.reset();

        // Show modal
        $('#add-subsection-modal').modal('show');
    } else {
        // Adding a top-level section
        // Reset form
        const form = document.getElementById('add-section-form');
        if (form) form.reset();

        // Show modal
        $('#add-section-modal').modal('show');
    }
}

/**
 * Add a new root section
 */
function addNewRootSection() {
    const title = document.getElementById('new-section-title').value.trim();
    const position = parseInt(document.getElementById('new-section-position').value, 10) || 1;

    if (!title) {
        showNotification('Please enter a title for the section', 'warning');
        return;
    }

    console.log('Adding new root section:', title, 'at position', position);

    // Send API request to create the section
    fetch('/api/sections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_id: documentId,
            title: title,
            parent_id: null,
            position: position
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create section');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Hide modal
            $('#add-section-modal').modal('hide');

            // Show success message
            showNotification('Section added successfully', 'success');

            // Refresh tree
            refreshDocumentStructure();

            // Load the new section if needed
            if (data.section && data.section.id) {
                setTimeout(() => {
                    loadSection(data.section.id);
                }, 500); // Give time for tree to refresh
            }
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error adding section:', error);
        showNotification('Failed to add section: ' + error.message, 'error');
    });
}

/**
 * Add a new subsection to the current section
 */
function addNewSubsection() {
    if (!currentSection) {
        showNotification('Please select a parent section first', 'warning');
        return;
    }

    const title = document.getElementById('new-subsection-title').value.trim();
    const position = parseInt(document.getElementById('new-subsection-position').value, 10) || 1;

    if (!title) {
        showNotification('Please enter a title for the subsection', 'warning');
        return;
    }

    console.log('Adding new subsection:', title, 'to parent', currentSection.id, 'at position', position);

    // Send API request to create the subsection
    fetch('/api/sections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_id: documentId,
            title: title,
            parent_id: currentSection.id,
            position: position
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create subsection');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Hide modal
            $('#add-subsection-modal').modal('hide');

            // Show success message
            showNotification('Subsection added successfully', 'success');

            // Refresh tree
            refreshDocumentStructure();

            // Load the new section if needed
            if (data.section && data.section.id) {
                setTimeout(() => {
                    loadSection(data.section.id);
                }, 500); // Give time for tree to refresh
            }
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error adding subsection:', error);
        showNotification('Failed to add subsection: ' + error.message, 'error');
    });
}

/**
 * Fix Delete Section/Document functionality
 */
function fixDeleteFunctionality() {
    console.log('Fixing Delete functionality...');

    // Fix Delete Section button
    const deleteSectionBtn = document.getElementById('delete-section');
    if (deleteSectionBtn) {
        deleteSectionBtn.addEventListener('click', function() {
            console.log('Delete section button clicked');

            if (!currentSection) {
                showNotification('Please select a section first', 'warning');
                return;
            }

            // Update modal with section title
            const titleElement = document.getElementById('delete-section-title');
            if (titleElement) {
                titleElement.textContent = currentSection.title;
            }

            // Show confirmation modal
            $('#delete-section-modal').modal('show');
        });
    }

    // Fix Delete Section confirmation
    const confirmDeleteSection = document.getElementById('confirm-delete-section');
    if (confirmDeleteSection) {
        confirmDeleteSection.addEventListener('click', function() {
            console.log('Confirm delete section clicked');

            if (!currentSection) {
                showNotification('No section selected', 'error');
                $('#delete-section-modal').modal('hide');
                return;
            }

            deleteSectionById(currentSection.id);
        });
    }

    // Fix Delete Document confirmation
    const confirmDeleteDocument = document.getElementById('confirm-delete-document');
    if (confirmDeleteDocument) {
        confirmDeleteDocument.addEventListener('click', function() {
            console.log('Confirm delete document clicked');
            deleteDocumentAction();
        });
    }

    // Save reference to original function if it exists
    if (typeof window.deleteSection === 'function') {
        originalFunctions.deleteSection = window.deleteSection;
    }

    // Override with fixed function
    window.deleteSectionById = deleteSectionById;

    console.log('Delete functionality fixed');
}

/**
 * Delete a section by ID
 */
function deleteSectionById(sectionId) {
    console.log('Deleting section:', sectionId);

    fetch(`/api/sections/${sectionId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete section');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Close modal
            $('#delete-section-modal').modal('hide');

            // Show success message
            showNotification('Section deleted successfully', 'success');

            // Clear editor if we were viewing the deleted section
            if (currentSection && currentSection.id === sectionId) {
                currentSection = null;
                editor.setValue('');
                document.getElementById('section-title').value = '';
            }

            // Refresh tree
            refreshDocumentStructure();
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error deleting section:', error);
        showNotification('Failed to delete section: ' + error.message, 'error');
        $('#delete-section-modal').modal('hide');
    });
}

/**
 * Fix Collapse/Expand functionality
 */
function fixCollapseExpandFunctionality() {
    console.log('Fixing Collapse/Expand functionality...');

    // Fix Toggle Tree button
    const toggleBtn = document.getElementById('toggle-tree');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            console.log('Toggle tree button clicked');
            toggleTreeExpansion();
        });
    }

    // Save reference to original function if it exists
    if (typeof window.toggleTreeExpansion === 'function') {
        originalFunctions.toggleTreeExpansion = window.toggleTreeExpansion;
    }

    // Override with fixed function
    window.toggleTreeExpansion = toggleTreeExpansionFixed;

    console.log('Collapse/Expand functionality fixed');
}

/**
 * Fixed function to toggle tree expansion state
 */
function toggleTreeExpansionFixed() {
    const tree = $('#document-tree').jstree(true);
    if (!tree) {
        console.error('jstree not initialized');
        return;
    }

    try {
        // Check current state - are any nodes collapsed?
        const allNodes = tree.get_container_ul().find('li');
        const anyClosedNodes = Array.from(allNodes).some(node => {
            const nodeId = node.id;
            return !tree.is_leaf(nodeId) && !tree.is_open(nodeId);
        });

        console.log('Tree state check - any closed nodes:', anyClosedNodes);

        if (anyClosedNodes) {
            // Some nodes are closed, open all
            tree.open_all();
            showNotification('Expanded all sections', 'info');
        } else {
            // All nodes are open, close all except root
            tree.close_all();

            // Open first level for better UX
            const rootNodes = tree.get_children_dom('#');
            rootNodes.each(function() {
                tree.open_node(this.id);
            });

            showNotification('Collapsed sections', 'info');
        }
    } catch (error) {
        console.error('Error toggling tree expansion:', error);
        showNotification('Error toggling tree expansion', 'error');
    }
}

/**
 * Fix Collaborator Modal
 */
function fixCollaboratorModal() {
    console.log('Fixing Collaborator Modal...');

    // Ensure modal has the proper Bootstrap structure by creating it dynamically
    const createCollaboratorModal = function() {
        // Check if modal already exists
        if (document.getElementById('collaborators-modal')) {
            // Fix existing modal positioning
            const modal = document.getElementById('collaborators-modal');
            if (!modal.classList.contains('modal') || !modal.classList.contains('fade')) {
                // This might be improperly formatted modal, recreate it
                modal.remove();
            } else {
                // It's a proper modal, make sure it has the right structure
                return;
            }
        }

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
    };

    // Create modal if it doesn't exist or fix if it does
    createCollaboratorModal();

    // Fix "Add Collaborator" button in the interface
    const addCollabBtn = document.getElementById('add-collaborator');
    if (addCollabBtn) {
        addCollabBtn.addEventListener('click', function() {
            console.log('Add collaborator button clicked');
            showCollaboratorsModal();
        });
    }

    // Fix "Manage Collaborators" link in dropdown
    const manageCollabLink = document.getElementById('manage-collaborators');
    if (manageCollabLink) {
        manageCollabLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Manage collaborators link clicked');
            showCollaboratorsModal();
        });
    }

    // Fix Search button
    const searchBtn = document.getElementById('search-collaborator');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            console.log('Search collaborator button clicked');
            searchUsers();
        });
    }

    // Fix email input enter key handling
    const emailInput = document.getElementById('collaborator-email');
    if (emailInput) {
        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchUsers();
            }
        });
    }

    // Fix "Add Collaborator" button in modal
    const addBtn = document.getElementById('add-collaborator-btn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            console.log('Add collaborator button in modal clicked');
            addCollaborator();
        });
    }

    // Save references to original functions if they exist
    if (typeof window.showCollaboratorsModal === 'function') {
        originalFunctions.showCollaboratorsModal = window.showCollaboratorsModal;
    }

    // Override with fixed functions
    window.showCollaboratorsModal = showCollaboratorsModalFixed;

    console.log('Collaborator Modal fixed');
}

/**
 * Fixed function to show collaborator modal
 */
function showCollaboratorsModalFixed() {
    console.log('Showing collaborator modal');

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

    // Load current collaborators
    loadCollaborators();

    // Show modal
    $('#collaborators-modal').modal('show');
}

/**
 * Fix AI Assistant Tabs
 */
function fixAITabs() {
    console.log('Fixing AI Tabs...');

    // Fix tab switching
    const aiTabs = document.querySelectorAll('.tools-tabs .tab');
    const toolPanels = document.querySelectorAll('.tool-panel');

    aiTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetPanel = this.getAttribute('data-tab');
            console.log('Tab clicked:', targetPanel);

            // Deactivate all tabs and panels
            aiTabs.forEach(t => t.classList.remove('active'));
            toolPanels.forEach(p => p.classList.remove('active'));

            // Activate selected tab and panel
            this.classList.add('active');
            document.getElementById(`${targetPanel}-panel`).classList.add('active');

            // Refresh analysis if analysis tab
            if (targetPanel === 'analysis' && typeof refreshAnalysis === 'function') {
                refreshAnalysis();
            }
        });
    });

    // Fix AI mode buttons
    const aiModeButtons = document.querySelectorAll('.ai-mode');
    aiModeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            setAIMode(mode);
        });
    });

    // Fix analyze button
    const analyzeBtn = document.getElementById('ai-analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            console.log('AI analyze button clicked');
            analyzeText();
        });
    }

    // Fix apply suggestion button
    const applyBtn = document.getElementById('ai-apply-btn');
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            console.log('Apply AI suggestion button clicked');
            applyAISuggestion();
        });
    }

    console.log('AI Tabs fixed');
}

/**
 * Fix Document Creation
 */
function fixDocumentCreation() {
    console.log('Fixing Document Creation...');

    // Fix Create Document button
    const createBtn = document.getElementById('create-document-btn');
    if (createBtn) {
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Create document button clicked');

            // Validate form first
            if (!validateDocumentCreationForm()) {
                showNotification('Please enter a document title and select a document type', 'warning');
                return;
            }

            // Show confirmation modal
            $('#document-confirmation-modal').modal('show');
        });
    }

    // Fix confirmation button in modal
    const confirmCreateBtn = document.getElementById('confirm-create-document');
    if (confirmCreateBtn) {
        confirmCreateBtn.addEventListener('click', function() {
            console.log('Confirm create document button clicked');
            document.getElementById('new-document-form').submit();
        });
    }

    console.log('Document Creation fixed');
}

/**
 * Add global CSS fixes for UI components
 */
function addGlobalCSSFixes() {
    console.log('Adding global CSS fixes...');

    // Create style element
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        /* Modal fixes */
        .modal {
            z-index: 1050 !important;
        }

        .modal-dialog {
            margin: 1.75rem auto !important;
            max-width: 500px !important;
            position: relative !important;
        }

        /* Dropdown fixes */
        .dropdown-menu {
            z-index: 1030 !important;
            position: absolute !important;
        }

        /* User search results style */
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

        /* Collaborator item style */
        .collaborator-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin-bottom: 5px;
        }

        /* Tree node style fix */
        .jstree-anchor {
            white-space: normal !important;
            height: auto !important;
            padding-right: 24px !important;
        }

        /* Notification style */
        .notification-popup {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
            margin-bottom: 10px;
            opacity: 1;
            transition: opacity 0.3s ease-in-out;
        }
    `;

    // Add to document head
    document.head.appendChild(styleEl);

    console.log('Global CSS fixes added');
}

/**
 * Helper function for notifications
 */
function showNotificationFixed(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);

    // Check if we already have our own notification
    if (typeof window.customNotify === 'function') {
        window.customNotify(message, type);
        return;
    }

    // Create a notification container if it doesn't exist
    let container = document.getElementById('notification-container');
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
    notification.className = `alert alert-${type} notification-popup`;
    notification.innerHTML = message;
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease-in-out';

    // Add to container
    container.appendChild(notification);

    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (container.contains(notification)) {
                container.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Fix the Edit button loading issue
 */
function fixEditButtonLoading() {
    console.log('Fixing Edit button loading issue...');

    // Fix dashboard Edit buttons
    const editButtons = document.querySelectorAll('.dashboard-document-actions .edit-document-btn, .dashboard .edit-btn');
    editButtons.forEach(button => {
        // Remove existing event handlers by cloning the button
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        // Add new event handler
        newButton.addEventListener('click', function(e) {
            const documentId = this.dataset.documentId || this.getAttribute('href').split('/').pop();
            if (!documentId) return; // Let the default action handle it

            e.preventDefault();

            // Show loading state
            this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading...';
            this.disabled = true;

            // Navigate immediately without delay
            window.location.href = `/editor/${documentId}`;
        });
    });

    // Fix section Edit button
    const sectionEditBtn = document.getElementById('edit-section');
    if (sectionEditBtn) {
        // Remove existing event handlers by cloning the button
        const newEditBtn = sectionEditBtn.cloneNode(true);
        sectionEditBtn.parentNode.replaceChild(newEditBtn, sectionEditBtn);

        // Add proper event handler
        newEditBtn.addEventListener('click', function() {
            if (!currentSection) {
                showNotification('Please select a section to edit', 'warning');
                return;
            }

            // Bypass lock checking and directly enable editing
            enableEditingDirectly();
        });
    }

    console.log('Edit button loading issue fixed');
}

/**
 * Enable editing directly without lock checking
 * This bypasses the potentially problematic acquireSectionLock function
 */
function enableEditingDirectly() {
    // Save original content for change detection and potential cancellation
    originalContent = editor.getValue();

    // Set editing flag
    isEditing = true;

    // Make editor editable
    editor.setOption('readOnly', false);

    // Enable title editing
    document.getElementById('section-title').readOnly = false;

    // Update UI buttons
    document.getElementById('edit-section').disabled = true;
    document.getElementById('save-section').disabled = true; // Initially disabled until changes are made
    document.getElementById('cancel-edit').disabled = false;

    // Enable toolbar buttons
    const toolbarButtons = document.querySelectorAll('#editor-toolbar button');
    toolbarButtons.forEach(button => button.disabled = false);

    // Update edit status
    updateEditStatus(true);

    // Focus editor
    editor.focus();
}

/**
 * Fix Collaborator modal positioning
 */
function fixCollaboratorModalPosition() {
    console.log('Fixing Collaborator Modal position...');

    // Add CSS to properly position the modal
    const styleId = 'collaborator-modal-fix-styles';

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
            z-index: 9999 !important;
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

        .modal-backdrop {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            z-index: 1040;
            background-color: #000;
        }

        .modal-backdrop.show {
            opacity: 0.5;
        }
    `;

    document.head.appendChild(styleEl);

    // Ensure modal is properly created on page load
    // Prevent it from automatically showing when the page loads
    const originalShowModal = window.showCollaboratorsModal;
    if (typeof originalShowModal === 'function') {
        window.showCollaboratorsModal = function() {
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

            // Load current collaborators
            loadCollaborators();

            // Show modal
            $('#collaborators-modal').modal('show');
        };
    }

    // Override the setup function to make sure it doesn't auto-show the modal
    const originalSetup = window.setupCollaboratorManagement;
    if (typeof originalSetup === 'function') {
        window.setupCollaboratorManagement = function() {
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

            // Set up the rest of the handlers without auto-showing the modal
            setupCollaboratorHandlers();
        };
    }

    // Check if the modal is being auto-shown on page load
    // If found, remove that initialization
    const autoShowCode = document.querySelector('script:not([src])');
    if (autoShowCode && autoShowCode.textContent.includes('$(\'#collaborators-modal\').modal(\'show\')')) {
        autoShowCode.remove();
    }

    console.log('Collaborator Modal position fixed');
}

/**
 * Set up collaborator handlers without showing the modal
 */
function setupCollaboratorHandlers() {
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
}

// Apply the fix to window object
window.enableEditingDirectly = enableEditingDirectly;
window.fixEditButtonLoading = fixEditButtonLoading;
window.fixCollaboratorModalPosition = fixCollaboratorModalPosition;

/**
 * Editor and modal fixes
 * This script fixes the Edit button loading issue and the Collaborator modal positioning
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply fixes when the DOM is loaded
    fixEditButtonLoading();
    fixCollaboratorModalPosition();
});

// Call the initialization function after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a moment to ensure all other scripts have loaded
    setTimeout(initializeAllFixes, 300);

    // Backup for showNotification in case it's not defined elsewhere
    if (typeof window.showNotification !== 'function') {
        window.showNotification = showNotificationFixed;
    }
});
