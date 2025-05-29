/**
 * Tree component for document structure visualization
 * Based on jsTree library
 */

// Section icons by type
const sectionIcons = {
    'abstract': 'fa fa-file-text-o',
    'introduction': 'fa fa-info-circle',
    'methods': 'fa fa-cogs',
    'results': 'fa fa-bar-chart',
    'discussion': 'fa fa-comments',
    'conclusion': 'fa fa-check-circle',
    'references': 'fa fa-book',
    'acknowledgements': 'fa fa-heart',
    'literature review': 'fa fa-search',
    'methodology': 'fa fa-wrench',
    'bibliography': 'fa fa-list-ul',
    'appendices': 'fa fa-paperclip',
    'executive summary': 'fa fa-file-text',
    'background': 'fa fa-history',
    'findings': 'fa fa-lightbulb-o',
    'recommendations': 'fa fa-thumbs-up',
    'headline': 'fa fa-newspaper-o',
    'byline': 'fa fa-user',
    'body': 'fa fa-align-left',
    'title page': 'fa fa-bookmark',
    'table of contents': 'fa fa-list',
    'preface': 'fa fa-quote-left',
    'chapter': 'fa fa-bookmark-o',
    'title slide': 'fa fa-desktop',
    'agenda': 'fa fa-list-ol',
    'main content': 'fa fa-file-o',
    'q&a': 'fa fa-question-circle',
    // Default icon
    'default': 'fa fa-file-o'
};

// Track the last selected node for restoration after reload
let lastSelectedNodeId = null;

/**
 * Initialize the document tree using jsTree
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the document tree
    initializeDocumentTree();

    // Set up add section handler
    document.getElementById('add-section').addEventListener('click', function() {
        showAddSectionModal(null);
    });

    // Set up delete button handler
    const deleteButton = document.getElementById('delete-section');
    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            if (!currentSection) {
                showNotification('Please select a section first', 'warning');
                return;
            }

            // Set the section title in the modal
            document.getElementById('delete-section-title').textContent = currentSection.title;

            // Show modal
            $('#delete-section-modal').modal('show');

            // Set up confirmation button
            document.getElementById('confirm-delete-section').onclick = function() {
                deleteSection(currentSection.id);
            };
        });
    }

    // Set up add section confirmation
    document.getElementById('confirm-add-section').addEventListener('click', function() {
        addNewSection(null); // Add as root section
    });

    // Set up add subsection confirmation
    document.getElementById('confirm-add-subsection').addEventListener('click', function() {
        if (!currentSection) return;
        addNewSection(currentSection.id); // Add as child of current section
    });

    // Add tree toggle handler
    const toggleButton = document.getElementById('toggle-tree');
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleTreeExpansion);
    }
});

/**
 * Initialize the document tree
 */
function initializeDocumentTree() {
    // Prepare tree data
    let treeData = [];

    // Check if we have sections
    if (documentStructure && documentStructure.sections && documentStructure.sections.length > 0) {
        treeData = convertToJSTreeFormat(documentStructure.sections);
    } else {
        console.log('No sections found in document structure');
        // Show empty state guidance in editor
        if (typeof editor !== 'undefined' && editor) {
            editor.setValue('Welcome to your new document! Create a section by clicking the "+" button in the sidebar.');
            document.getElementById('section-title').value = 'No sections yet';
        }
    }

    // Initialize jsTree
    $('#document-tree').jstree({
        'core': {
            'data': treeData,
            'themes': {
                'name': 'default',
                'icons': true
            },
            'check_callback': true,  // Allow tree modifications
            'multiple': false        // Disable multiple selection
        },
        'plugins': ['dnd', 'wholerow', 'state', 'types'],
        'state': {
            'key': `document_${documentId}_tree`
        },
        'types': {
            'default': {
                'icon': 'fa fa-file-o'
            }
        }
    });

    // Handle node selection
    $('#document-tree').on('select_node.jstree', function(e, data) {
        const nodeId = data.node.id;
        const sectionId = parseInt(nodeId.replace('node_', ''), 10);

        // Save last selected node for potential restoration
        lastSelectedNodeId = nodeId;

        // Enable the delete button when a node is selected
        document.getElementById('delete-section').disabled = false;

        // Load the section content
        loadSection(sectionId);
    });

    // Handle tree ready event
    $('#document-tree').on('ready.jstree', function() {
        // If we have a last selected node, restore selection
        if (lastSelectedNodeId) {
            $('#document-tree').jstree('select_node', lastSelectedNodeId);
        }
        // Otherwise select the first node if available
        else {
            const firstNode = $('#document-tree').jstree(true).get_node($('#document-tree').jstree(true).get_children_dom('#')[0]);
            if (firstNode) {
                $('#document-tree').jstree('select_node', firstNode);
            }
        }
    });

    // Handle node deselection
    $('#document-tree').on('deselect_node.jstree', function() {
        // Disable delete button when no node is selected
        document.getElementById('delete-section').disabled = true;
    });

    // Handle drag and drop for reordering/restructuring
    $('#document-tree').on('move_node.jstree', function(e, data) {
        const sectionId = parseInt(data.node.id.replace('node_', ''), 10);
        const newParentId = data.parent === '#' ? null : parseInt(data.parent.replace('node_', ''), 10);
        const newPosition = data.position + 1;  // jsTree is 0-indexed, our API is 1-indexed

        moveSection(sectionId, newParentId, newPosition);
    });
}

/**
 * Reinitialize the tree after structure changes
 */
function reinitializeDocumentTree() {
    // Destroy existing tree
    if ($('#document-tree').jstree(true)) {
        $('#document-tree').jstree('destroy');
    }

    // Reinitialize
    initializeDocumentTree();
}

/**
 * Convert the document structure to jsTree format
 */
function convertToJSTreeFormat(sections) {
    if (!sections || !Array.isArray(sections)) return [];

    return sections.map(section => {
        // Determine icon based on section title
        let icon = sectionIcons.default;
        const titleLower = section.title.toLowerCase();

        // Check for exact matches
        if (sectionIcons[titleLower]) {
            icon = sectionIcons[titleLower];
        }
        // Check for partial matches (like "Chapter 1" matching "chapter")
        else {
            for (const key in sectionIcons) {
                if (titleLower.includes(key)) {
                    icon = sectionIcons[key];
                    break;
                }
            }
        }

        return {
            id: `node_${section.id}`,
            text: section.title,
            icon: icon,
            children: section.children && section.children.length > 0 ?
                     convertToJSTreeFormat(section.children) : [],
            state: {
                opened: true
            },
            type: 'default',
            li_attr: {
                'data-id': section.id,
                'title': `Section ID: ${section.id}, Last Modified: ${new Date(section.modified_date || Date.now()).toLocaleString()}`
            }
        };
    });
}

/**
 * Show the modal for adding a section or subsection
 */
function showAddSectionModal(parentId) {
    if (parentId) {
        // Adding a subsection to an existing parent
        const selectedNode = $(`#document-tree`).jstree(true).get_node(`node_${parentId}`);

        // Update modal title
        const modalTitle = document.querySelector('#add-subsection-modal .modal-title');
        if (modalTitle) {
            modalTitle.textContent = `Add Subsection to "${selectedNode.text}"`;
        }

        // Reset form
        const form = document.getElementById('add-subsection-form');
        if (form) form.reset();

        // Show modal
        $('#add-subsection-modal').modal('show');
    } else {
        // Adding a top-level section
        const modalTitle = document.querySelector('#add-section-modal .modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Add New Section';
        }

        // Reset form
        const form = document.getElementById('add-section-form');
        if (form) form.reset();

        // Show modal
        $('#add-section-modal').modal('show');
    }
}

/**
 * Add a new section to the document
 */
function addNewSection(parentId) {
    let title, position, modalId;

    if (parentId) {
        // Adding a subsection
        title = document.getElementById('new-subsection-title').value;
        position = parseInt(document.getElementById('new-subsection-position').value, 10) || 1;
        modalId = '#add-subsection-modal';
    } else {
        // Adding a top-level section
        title = document.getElementById('new-section-title').value;
        position = parseInt(document.getElementById('new-section-position').value, 10) || 1;
        modalId = '#add-section-modal';
    }

    if (!title || !title.trim()) {
        showNotification('Please enter a title for the section', 'warning');
        return;
    }

    // Create section via API
    fetch('/api/sections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_id: documentId,
            title: title.trim(),
            parent_id: parentId,
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
            $(modalId).modal('hide');

            // Show notification
            showNotification(`${parentId ? 'Subsection' : 'Section'} added successfully`, 'success');

            // Refresh tree structure
            refreshDocumentStructure();

            // Select the new section after refresh
            if (data.section && data.section.id) {
                setTimeout(() => {
                    $('#document-tree').jstree('select_node', `node_${data.section.id}`);
                }, 500); // Give time for the tree to refresh
            }
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error adding section:', error);
        showNotification(`Failed to add ${parentId ? 'subsection' : 'section'}: ${error.message}`, 'error');
    });
}

/**
 * Delete a section from the document
 */
function deleteSection(sectionId) {
    if (!sectionId) return;

    // Call API to delete section
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
            // Hide modal
            $('#delete-section-modal').modal('hide');

            // Show notification
            showNotification('Section deleted successfully', 'success');

            // Clear editor if we were viewing the deleted section
            if (currentSection && currentSection.id === sectionId) {
                currentSection = null;
                if (typeof editor !== 'undefined' && editor) {
                    editor.setValue('');
                }
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
 * Move a section to a new position in the document
 */
function moveSection(sectionId, newParentId, newPosition) {
    // Show notification that we're processing
    showNotification('Moving section...', 'info');

    fetch(`/api/sections/${sectionId}/move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            parent_id: newParentId,
            position: newPosition
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to move section');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Section moved successfully', 'success');
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error moving section:', error);
        showNotification('Failed to move section: ' + error.message, 'error');
        // Refresh tree to reset to correct structure
        refreshDocumentStructure();
    });
}

/**
 * Refresh the document structure from the server
 */
function refreshDocumentStructure() {
    fetch(`/api/documents/${documentId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch document structure');
            }
            return response.json();
        })
        .then(data => {
            // Update document structure
            documentStructure = data;

            // Refresh tree
            reinitializeDocumentTree();
        })
        .catch(error => {
            console.error('Error refreshing document structure:', error);
            showNotification('Failed to refresh document structure: ' + error.message, 'error');
        });
}

/**
 * Toggle expansion/collapse of all tree nodes
 */
function toggleTreeExpansion() {
    const tree = $('#document-tree').jstree(true);
    if (!tree) return;

    const allNodes = tree.get_container_ul().find('li');
    const anyCollapsed = allNodes.toArray().some(node =>
        !tree.is_leaf(node) && !tree.is_open(node)
    );

    if (anyCollapsed) {
        tree.open_all();
    } else {
        tree.close_all();
    }
}

/**
 * Expand all nodes in the tree
 */
function expandAllNodes() {
    $('#document-tree').jstree('open_all');
}

/**
 * Collapse all nodes in the tree
 */
function collapseAllNodes() {
    $('#document-tree').jstree('close_all');
}

/**
 * Add Section/Subsection Fix
 * Add this to tree-component.js
 */
// Fix Add Section functionality
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

    console.log('Add Section functionality fixed');
}

// Show modal for adding a section or subsection
function showAddSectionModal(parentId) {
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

// Add a new root section
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

// Add a new subsection to the current section
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
 * Delete Section/Document Fix
 * Add this to init.js or tree-component.js
 */
// Fix Delete functionality
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

    console.log('Delete functionality fixed');
}

// Delete a section by ID
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
 * Collapse/Expand Fix
 * Add this to tree-component.js
 */
// Fix Collapse/Expand functionality
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

    console.log('Collapse/Expand functionality fixed');
}

// Toggle tree expansion state
function toggleTreeExpansion() {
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

// Call the fix function on DOM load
document.addEventListener('DOMContentLoaded', fixCollapseExpandFunctionality);
// Call the fix function on DOM load
document.addEventListener('DOMContentLoaded', fixDeleteFunctionality);
// Call the fix function on DOM load
document.addEventListener('DOMContentLoaded', fixAddSectionFunctionality);
// Export functions for use in other modules
window.initializeDocumentTree = initializeDocumentTree;
window.reinitializeDocumentTree = reinitializeDocumentTree;
window.refreshDocumentStructure = refreshDocumentStructure;
window.showAddSectionModal = showAddSectionModal;
window.addNewSection = addNewSection;
window.deleteSection = deleteSection;
