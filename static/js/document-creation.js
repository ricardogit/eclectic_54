/**
 * Document Creation module for the Dash Editor
 * Handles document initialization and type-specific templates
 */

// Document template descriptions
const documentTemplates = {
    'academic': {
        title: 'Academic Paper',
        description: 'Standard academic research paper with abstract, introduction, methods, results, discussion, and conclusion.',
        icon: 'fa-graduation-cap'
    },
    'thesis': {
        title: 'Thesis/Dissertation',
        description: 'Full thesis or dissertation format with acknowledgements, literature review, methodology, multiple chapters, and appendices.',
        icon: 'fa-book'
    },
    'report': {
        title: 'Technical Report',
        description: 'Professional report with executive summary, findings, and recommendations.',
        icon: 'fa-file-text'
    },
    'article': {
        title: 'Article',
        description: 'Article format with headline, byline, introduction, body, and conclusion.',
        icon: 'fa-newspaper-o'
    },
    'book': {
        title: 'Book',
        description: 'Book format with title page, table of contents, preface, multiple chapters, and appendices.',
        icon: 'fa-book'
    },
    'presentation': {
        title: 'Presentation',
        description: 'Presentation format with title slide, agenda, introduction, main content, conclusion, and Q&A sections.',
        icon: 'fa-desktop'
    }
};

/**
 * Initialize document type selection interface
 */
function initializeDocumentTypeSelector() {
    const container = document.getElementById('document-type-cards');

    if (!container) return;  // Not on document creation page

    // Create a card for each document type
    Object.keys(documentTemplates).forEach(typeId => {
        const template = documentTemplates[typeId];

        const card = document.createElement('div');
        card.className = 'document-type-card';
        card.dataset.type = typeId;

        card.innerHTML = `
            <div class="card-icon"><i class="fa ${template.icon}"></i></div>
            <h3>${template.title}</h3>
            <p>${template.description}</p>
        `;

        // Add click listener
        card.addEventListener('click', function() {
            // Remove active class from all cards
            document.querySelectorAll('.document-type-card').forEach(card => {
                card.classList.remove('active');
            });

            // Add active class to selected card
            this.classList.add('active');

            // Update hidden input field
            document.getElementById('document-type').value = this.dataset.type;

            // Show preview of structure
            showDocumentTypePreview(this.dataset.type);

            // Enable next button if document title is also valid
            validateDocumentCreationForm();
        });

        container.appendChild(card);
    });

    // Add listener to document title field
    document.getElementById('document-title').addEventListener('input', validateDocumentCreationForm);
}

/**
 * Show a preview of the document structure based on selected type
 */
function showDocumentTypePreview(docType) {
    // Simulate fetch request for demonstration
    // In a real implementation, you would call the API
    const previewContainer = document.getElementById('structure-preview');

    // Get template data based on type
    let templateData = [];

    switch(docType) {
        case 'academic':
            templateData = [
                {title: 'Abstract', children: []},
                {title: 'Introduction', children: []},
                {title: 'Methods', children: []},
                {title: 'Results', children: []},
                {title: 'Discussion', children: []},
                {title: 'Conclusion', children: []},
                {title: 'References', children: []}
            ];
            break;
        case 'thesis':
            templateData = [
                {title: 'Abstract', children: []},
                {title: 'Acknowledgements', children: []},
                {title: 'Introduction', children: []},
                {title: 'Literature Review', children: []},
                {title: 'Methodology', children: []},
                {title: 'Results', children: []},
                {title: 'Discussion', children: []},
                {title: 'Conclusion', children: []},
                {title: 'Bibliography', children: []},
                {title: 'Appendices', children: []}
            ];
            break;
        case 'report':
            templateData = [
                {title: 'Executive Summary', children: []},
                {title: 'Introduction', children: []},
                {title: 'Background', children: []},
                {title: 'Findings', children: []},
                {title: 'Recommendations', children: []},
                {title: 'Conclusion', children: []}
            ];
            break;
        case 'article':
            templateData = [
                {title: 'Headline', children: []},
                {title: 'Byline', children: []},
                {title: 'Introduction', children: []},
                {title: 'Body', children: []},
                {title: 'Conclusion', children: []}
            ];
            break;
        case 'book':
            templateData = [
                {title: 'Title Page', children: []},
                {title: 'Table of Contents', children: []},
                {title: 'Preface', children: []},
                {title: 'Chapter 1', children: []},
                {title: 'Chapter 2', children: []},
                {title: 'Chapter 3', children: []},
                {title: 'Bibliography', children: []}
            ];
            break;
        case 'presentation':
            templateData = [
                {title: 'Title Slide', children: []},
                {title: 'Agenda', children: []},
                {title: 'Introduction', children: []},
                {title: 'Main Content', children: []},
                {title: 'Conclusion', children: []},
                {title: 'Q&A', children: []}
            ];
            break;
        default:
            templateData = [{title: 'Section 1', children: []}];
    }

    // Create tree HTML
    let html = '<ul class="structure-tree">';

    templateData.forEach(section => {
        html += buildPreviewTreeItem(section);
    });

    html += '</ul>';

    previewContainer.innerHTML = html;
}

/**
 * Build HTML for a tree item in the preview
 */
function buildPreviewTreeItem(section) {
    let html = `<li>
        <span class="section-title">${section.title}</span>
    `;

    if (section.children && section.children.length > 0) {
        html += '<ul>';

        section.children.forEach(child => {
            html += buildPreviewTreeItem(child);
        });

        html += '</ul>';
    }

    html += '</li>';

    return html;
}

/**
 * Validate the document creation form
 */
function validateDocumentCreationForm() {
    const title = document.getElementById('document-title').value.trim();
    const type = document.getElementById('document-type').value;

    const isValid = title.length > 0 && type.length > 0;

    // Enable/disable create button
    const createButton = document.getElementById('create-document-btn');
    if (createButton) {
        createButton.disabled = !isValid;
    }

    return isValid;
}

/**
 * Create a new document with confirmation
 */
function createDocument(event) {
    if (event) {
        event.preventDefault();
    }

    // Submit the form directly (the confirmation was already shown)
    document.getElementById('new-document-form').submit();
}

/**
 * Show the document confirmation modal
 */
function showDocumentConfirmationModal() {
    // Check form validity
    if (!validateDocumentCreationForm()) {
        alert('Please enter a document title and select a document type');
        return;
    }

    // Get form values
    const title = document.getElementById('document-title').value.trim();
    const type = document.getElementById('document-type').value;

    try {
        // Try to get type name from card
        const typeCard = document.querySelector(`.document-type-card[data-type="${type}"]`);
        const typeName = typeCard ? typeCard.querySelector('h3').textContent : type.charAt(0).toUpperCase() + type.slice(1);

        // Update modal content
        const titleElement = document.getElementById('confirm-document-title');
        const typeElement = document.getElementById('confirm-document-type');

        if (titleElement) titleElement.textContent = title;
        if (typeElement) typeElement.textContent = typeName;

        // Show the modal
        $('#document-confirmation-modal').modal('show');
    } catch (error) {
        console.error('Error showing confirmation modal:', error);
        // Fallback - just submit the form
        createDocument();
    }
}

/**
 * Handle document import from file
 */
function handleDocumentImport() {
    // Show file selector
    document.getElementById('import-file').click();
}

/**
 * Process imported document file
 */
function processImportedFile(input) {
    const file = input.files[0];

    if (!file) return;

    // Show loading state
    const statusElement = document.getElementById('import-status');
    if (statusElement) {
        statusElement.textContent = 'Reading file...';
        statusElement.style.display = 'block';
    }

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);

    // In a real implementation, you would send this to your server
    // For now, we'll simulate a response after a delay
    setTimeout(() => {
        if (statusElement) {
            statusElement.textContent = 'Import completed! Redirecting...';
        }
        // Redirect to a new page after 1 second
        setTimeout(() => {
            window.location.href = '/editor/dashboard';
        }, 1000);
    }, 2000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize document type selector
    initializeDocumentTypeSelector();

    // Add event listeners for confirmation buttons
    const confirmButtons = [
        document.getElementById('plain-confirm-btn'),
        document.querySelector('.emergency-confirm')
    ];

    confirmButtons.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', showDocumentConfirmationModal);
        }
    });

    // Create document button in modal
    const confirmCreateBtn = document.getElementById('confirm-create-document');
    if (confirmCreateBtn) {
        confirmCreateBtn.addEventListener('click', createDocument);
    }

    // Main create button
    const createBtn = document.getElementById('create-document-btn');
    if (createBtn) {
        createBtn.addEventListener('click', showDocumentConfirmationModal);
    }

    // Import document button
    const importBtn = document.getElementById('import-document-btn');
    if (importBtn) {
        importBtn.addEventListener('click', handleDocumentImport);
    }

    // File input change
    const importFile = document.getElementById('import-file');
    if (importFile) {
        importFile.addEventListener('change', function() {
            processImportedFile(this);
        });
    }
});

/**
 * Create Document Button Fix
 * Add this to document-creation.js
 */
document.addEventListener('DOMContentLoaded', function() {
    // Fix Create Document button
    const createBtn = document.getElementById('create-document-btn');
    if (createBtn) {
        createBtn.removeEventListener('click', showDocumentConfirmationModal);
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();

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
        confirmCreateBtn.removeEventListener('click', createDocument);
        confirmCreateBtn.addEventListener('click', function() {
            document.getElementById('new-document-form').submit();
        });
    }
});

// Global function for inline onclick handlers
window.showConfirmationModal = showDocumentConfirmationModal;
