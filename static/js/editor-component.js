/**
 * Enhanced Editor component for document content editing
 * Provides rich text editing capabilities and syncs with the document tree
 */

// Global variables
let editor; // CodeMirror instance
let currentSection = null; // Currently selected section
let isEditing = false; // Whether the editor is in edit mode
let originalContent = ''; // Store original content for comparison
let editorToolbar; // Toolbar instance if using a WYSIWYG editor

/**
 * Initialize the editor when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeEditor();
    setupEditorEvents();
});

/**
 * Initialize the CodeMirror editor with extended functionality
 */
function initializeEditor() {
    const editorElement = document.getElementById('section-content');
    if (!editorElement) {
        console.error('Editor element not found');
        return;
    }

    console.log('Creating CodeMirror instance');

    // Create a fresh CodeMirror instance
    if (window.editor) {
        // If there's an existing instance, try to clean it up
        try {
            window.editor.toTextArea();
        } catch (e) {
            console.error('Error cleaning up old editor:', e);
        }
    }

    // Initialize CodeMirror with Markdown support
    editor = CodeMirror.fromTextArea(editorElement, {
        mode: 'markdown',
        lineNumbers: true,
        lineWrapping: true,
        theme: 'default',
        readOnly: false, // Allow editing by default
        extraKeys: {
            'Ctrl-B': function(cm) { formatText('bold'); },
            'Ctrl-I': function(cm) { formatText('italic'); },
            'Ctrl-H': function(cm) { formatText('heading1'); },
            'Ctrl-Alt-1': function(cm) { formatText('heading1'); },
            'Ctrl-Alt-2': function(cm) { formatText('heading2'); },
            'Ctrl-Alt-3': function(cm) { formatText('heading3'); },
            'Ctrl-S': function(cm) { if (isEditing) saveSection(); },
            'Esc': function(cm) {
                if (isEditing && hasChanges()) {
                    if (confirm('You have unsaved changes. Discard changes?')) {
                        cancelEditing();
                    }
                }
            },
            'Tab': function(cm) {
                const spaces = Array(cm.getOption('indentUnit') + 1).join(' ');
                cm.replaceSelection(spaces);
            }
        }
    });

    // Set editor size
    editor.setSize('100%', '100%');

    // Initialize toolbar
    initializeEditorToolbar();

    // Start in edit mode
    isEditing = true;
    updateEditStatus(true);

    // Disable the Edit button since we're already in edit mode
    const editButton = document.getElementById('edit-section');
    if (editButton) {
        editButton.disabled = true;
    }

    // Enable toolbar buttons
    const toolbarButtons = document.querySelectorAll('#editor-toolbar button');
    toolbarButtons.forEach(button => button.disabled = false);

    // Focus editor to allow immediate typing
    setTimeout(() => {
        editor.refresh();
        editor.focus();

        // Test if editor is working
        try {
            editor.replaceRange('', editor.getCursor());
            console.log('Editor writing test successful');
        } catch (e) {
            console.error('Editor writing test failed:', e);
            // Attempt to fix by reinitializing
            setTimeout(() => {
                editor.setOption('readOnly', false);
                editor.refresh();
            }, 200);
        }
    }, 100);
}

/**
 * Initialize the editor toolbar
 */
function initializeEditorToolbar() {
    const toolbarContainer = document.getElementById('editor-toolbar');
    if (!toolbarContainer) return;

    // Create toolbar buttons
    const toolbarHTML = `
        <div class="btn-group mr-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="heading1" title="Heading 1">H1</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="heading2" title="Heading 2">H2</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="heading3" title="Heading 3">H3</button>
        </div>
        <div class="btn-group mr-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="bold" title="Bold"><i class="fa fa-bold"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="italic" title="Italic"><i class="fa fa-italic"></i></button>
        </div>
        <div class="btn-group mr-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="list" title="Bullet List"><i class="fa fa-list-ul"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="numbered" title="Numbered List"><i class="fa fa-list-ol"></i></button>
        </div>
        <div class="btn-group mr-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="link" title="Insert Link"><i class="fa fa-link"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="image" title="Insert Image"><i class="fa fa-image"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="table" title="Insert Table"><i class="fa fa-table"></i></button>
        </div>
        <div class="btn-group">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="quote" title="Blockquote"><i class="fa fa-quote-right"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="code" title="Inline Code"><i class="fa fa-code"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-format="codeblock" title="Code Block"><i class="fa fa-file-code-o"></i></button>
        </div>
    `;

    toolbarContainer.innerHTML = toolbarHTML;

    // Add event listeners to toolbar buttons
    toolbarContainer.querySelectorAll('button[data-format]').forEach(button => {
        button.addEventListener('click', function() {
            if (!isEditing) {
                showNotification('Please click "Edit" to enable editing first', 'warning');
                return;
            }
            formatText(this.dataset.format);
        });
    });
}

/**
 * Set up editor events
 */
function setupEditorEvents() {
    // Handle edit button click
    const editButton = document.getElementById('edit-section');
    if (editButton) {
        editButton.addEventListener('click', startEditing);
    }

    // Handle save button click
    const saveButton = document.getElementById('save-section');
    if (saveButton) {
        saveButton.addEventListener('click', saveSection);
    }

    // Handle cancel button click
    const cancelButton = document.getElementById('cancel-edit');
    if (cancelButton) {
        cancelButton.addEventListener('click', cancelEditing);
    }

    // Track changes in editor content
    if (editor) {
        editor.on('change', function() {
            if (!isEditing) return;

            const content = editor.getValue();
            const hasChanged = content !== originalContent;

            // Enable/disable save button based on changes
            const saveButton = document.getElementById('save-section');
            if (saveButton) {
                saveButton.disabled = !hasChanged;
            }

            // Update word count
            updateWordCount(content);

            // If we're in a collaborative session, broadcast changes
            if (typeof socket !== 'undefined' && socket && hasChanged) {
                // Debounced sending to avoid flooding the server
                clearTimeout(editor.changeTimer);
                editor.changeTimer = setTimeout(function() {
                    socket.emit('section_edit', {
                        document_id: documentId,
                        section_id: currentSection.id,
                        user_id: userId,
                        content: content,
                        cursor_position: editor.getCursor()
                    });
                }, 500);
            }
        });
    }
}

/**
 * Check if there are unsaved changes
 */
function hasChanges() {
    if (!isEditing || !currentSection) return false;

    const content = editor.getValue();
    const title = document.getElementById('section-title').value;

    return content !== originalContent || title !== currentSection.title;
}

/**
 * Update word count in the status bar
 */
function updateWordCount(text) {
    const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
    const wordCountElement = document.getElementById('word-count');
    if (wordCountElement) {
        wordCountElement.textContent = `${wordCount} word${wordCount !== 1 ? 's' : ''}`;
    }
}

/**
 * Update edit status in the status bar
 */
function updateEditStatus(isEditingActive) {
    const statusElement = document.getElementById('edit-status');
    if (statusElement) {
        if (isEditingActive) {
            statusElement.textContent = 'Editing mode';
            statusElement.style.backgroundColor = '#d1e7dd';
            statusElement.style.color = '#0f5132';
        } else {
            statusElement.textContent = 'Read-only mode';
            statusElement.style.backgroundColor = '#e9ecef';
            statusElement.style.color = '#6c757d';
        }
    }
}

/**
 * Start editing the current section
 */
function startEditing() {
    if (!currentSection) {
        showNotification('Please select a section to edit', 'warning');
        return;
    }

    // Check if we can acquire a lock (if collaboration is enabled)
    if (typeof acquireSectionLock === 'function') {
        acquireSectionLock(currentSection.id).then(success => {
            if (success) {
                enableEditing();
            }
        });
    } else {
        enableEditing();
    }
}

/**
 * Enable editing mode
 */
function enableEditing() {
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
 * Save the current section
 */
function saveSection() {
    if (!currentSection || !isEditing) return;

    const content = editor.getValue();
    const title = document.getElementById('section-title').value;

    // Check if there are changes
    if (content === originalContent && title === currentSection.title) {
        showNotification('No changes to save', 'info');
        return;
    }

    // Show saving indicator
    document.getElementById('save-section').innerHTML = '<i class="fa fa-spinner fa-spin"></i> Saving...';
    document.getElementById('save-section').disabled = true;

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

            // Update save button
            document.getElementById('save-section').innerHTML = 'Save';
            document.getElementById('save-section').disabled = true;

            showNotification('Section saved successfully', 'success');

            // Broadcast changes to collaborators if enabled
            if (typeof socket !== 'undefined' && socket) {
                socket.emit('section_edit', {
                    document_id: documentId,
                    section_id: currentSection.id,
                    user_id: userId,
                    content: content,
                    cursor_position: editor.getCursor()
                });
            }
        } else {
            showNotification('Error saving: ' + (data.error || 'Unknown error'), 'error');
            document.getElementById('save-section').innerHTML = 'Save';
            document.getElementById('save-section').disabled = false;
        }
    })
    .catch(error => {
        console.error('Error saving section:', error);
        showNotification('Failed to save section: ' + error.message, 'error');
        document.getElementById('save-section').innerHTML = 'Save';
        document.getElementById('save-section').disabled = false;
    });
}

/**
 * Cancel editing and revert changes
 */
function cancelEditing() {
    if (!isEditing) return;

    // Ask for confirmation if content changed
    if (hasChanges()) {
        if (!confirm('You have unsaved changes. Are you sure you want to discard them?')) {
            return;
        }
    }

    // Revert to original content
    editor.setValue(originalContent);
    if (currentSection) {
        document.getElementById('section-title').value = currentSection.title || '';
    }

    // Exit edit mode
    exitEditMode();

    // Release lock if collaboration is enabled
    if (typeof releaseSectionLock === 'function' && currentSection) {
        releaseSectionLock(currentSection.id);
    }

    showNotification('Editing cancelled', 'info');
}

/**
 * Exit edit mode
 */
function exitEditMode() {
    // Update flag
    isEditing = false;

    // Make editor read-only
    editor.setOption('readOnly', true);

    // Disable title editing
    document.getElementById('section-title').readOnly = true;

    // Update UI buttons
    document.getElementById('edit-section').disabled = false;
    document.getElementById('save-section').disabled = true;
    document.getElementById('save-section').innerHTML = 'Save';
    document.getElementById('cancel-edit').disabled = true;

    // Disable toolbar buttons
    const toolbarButtons = document.querySelectorAll('#editor-toolbar button');
    toolbarButtons.forEach(button => button.disabled = true);

    // Update status
    updateEditStatus(false);
}

/**
 * Format selected text in the editor
 */
function formatText(format) {
    if (!isEditing) return;

    const selectedText = editor.getSelection();
    let formattedText = '';

    switch (format) {
        case 'bold':
            formattedText = `**${selectedText}**`;
            break;
        case 'italic':
            formattedText = `*${selectedText}*`;
            break;
        case 'heading1':
            formattedText = `# ${selectedText}`;
            break;
        case 'heading2':
            formattedText = `## ${selectedText}`;
            break;
        case 'heading3':
            formattedText = `### ${selectedText}`;
            break;
        case 'quote':
            formattedText = selectedText.split('\n').map(line => `> ${line}`).join('\n');
            break;
        case 'code':
            formattedText = `\`${selectedText}\``;
            break;
        case 'codeblock':
            formattedText = `\`\`\`\n${selectedText}\n\`\`\``;
            break;
        case 'list':
            formattedText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
            break;
        case 'numbered':
            formattedText = selectedText.split('\n').map((line, i) => `${i+1}. ${line}`).join('\n');
            break;
        case 'link':
            const url = prompt('Enter URL:');
            if (url) {
                formattedText = `[${selectedText || 'Link text'}](${url})`;
            } else {
                return;
            }
            break;
        case 'image':
            const imageUrl = prompt('Enter image URL:');
            if (imageUrl) {
                formattedText = `![${selectedText || 'Image description'}](${imageUrl})`;
            } else {
                return;
            }
            break;
        case 'table':
            formattedText = `| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n| Cell 4   | Cell 5   | Cell 6   |`;
            break;
    }

    if (formattedText) {
        if (selectedText) {
            // Replace selected text with formatted text
            editor.replaceSelection(formattedText);
        } else {
            // Insert at cursor position
            const cursor = editor.getCursor();
            editor.replaceRange(formattedText, cursor);

            // If it's a table, move cursor to a useful position
            if (format === 'table') {
                editor.setCursor({line: cursor.line + 1, ch: 2});
            }
        }
    }
}

/**
 * Load a section from the tree into the editor
 */
/**
 * Load a section from the tree into the editor
 */
function loadSection(sectionId) {
    // Check if sectionId is valid
    if (!sectionId) {
        // For new documents with no sections, show a welcome message
        editor.setValue('Welcome to your new document! Select a section to edit it, or create a new section using the "+" button in the sidebar.');
        document.getElementById('section-title').value = 'No section selected';
        currentSection = null;
        return;
    }

    // Check for unsaved changes
    if (hasChanges()) {
        if (!confirm('You have unsaved changes. Discard changes?')) {
            // Reselect current node in tree
            if (currentSection) {
                const tree = $('#document-tree').jstree(true);
                if (tree) {
                    tree.deselect_all(true);
                    tree.select_node(`node_${currentSection.id}`);
                }
            }
            return;
        }

        // Release locks if collaboration is enabled
        if (typeof releaseSectionLock === 'function' && currentSection) {
            releaseSectionLock(currentSection.id);
        }
    }

    // Show loading indicator
    editor.setValue('Loading...');
    document.getElementById('section-title').value = '';

    // Fetch section data from server
    fetch(`/api/sections/${sectionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(section => {
            // Update current section
            currentSection = section;

            // Update UI
            document.getElementById('section-title').value = section.title || '';
            editor.setValue(section.content || '');

            // Store original content
            originalContent = section.content || '';

            // Update word count
            updateWordCount(section.content || '');

            // Ensure we're in edit mode
            isEditing = true;
            editor.setOption('readOnly', false);
            document.getElementById('edit-section').disabled = true;
            document.getElementById('save-section').disabled = true;
            document.getElementById('cancel-edit').disabled = false;

            // Enable toolbar buttons
            const toolbarButtons = document.querySelectorAll('#editor-toolbar button');
            toolbarButtons.forEach(button => button.disabled = false);

            // Update status
            updateEditStatus(true);

            // Highlight the selected node in the tree
            const tree = $('#document-tree').jstree(true);
            if (tree) {
                tree.deselect_all(true);
                tree.select_node(`node_${sectionId}`);
            }

            // Allow a moment for CodeMirror to update before refreshing and focusing
            setTimeout(() => {
                editor.refresh();
                editor.focus();
            }, 10);
        })
        .catch(error => {
            console.error('Error loading section:', error);
            editor.setValue('This appears to be a new document. Create your first section by clicking the "+" button in the sidebar.');
            document.getElementById('section-title').value = 'Getting Started';
            showNotification('Create a section to begin editing your document', 'info');
        });
}

/**
 * Insert a template at the cursor position
 */
function insertTemplate(templateType) {
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
        const cursor = editor.getCursor();
        editor.replaceRange(templateText, cursor);
    }
}

/**
 * Handle section update from collaborative editing
 */
function handleCollaborativeUpdate(data) {
    // Only update if we're viewing the same section but not editing it
    if (currentSection && currentSection.id === data.section_id && !isEditing) {
        // Update content
        editor.setValue(data.content);

        // Show notification
        showNotification(`Section updated by another user`);
    }
}

/**
 * Handle section lock from another user
 */
function handleSectionLock(data) {
    // If we're viewing the locked section
    if (currentSection && currentSection.id === data.section_id) {
        // If someone else locked it
        if (data.user_id !== userId) {
            // Disable editing
            document.getElementById('edit-section').disabled = true;

            // Show notification
            const expiresAt = new Date(data.expires_at);
            const formattedTime = expiresAt.toLocaleTimeString();
            showNotification(`Section is being edited by another user until ${formattedTime}`, 'warning');
        }
    }
}

/**
 * Handle section unlock from another user
 */
function handleSectionUnlock(data) {
    // If we're viewing the unlocked section
    if (currentSection && currentSection.id === data.section_id) {
        // If someone else unlocked it
        if (data.user_id !== userId) {
            // Enable editing
            document.getElementById('edit-section').disabled = false;

            // Show notification
            showNotification(`Section is now available for editing`);
        }
    }
}

/**
 * Update tree node title after editing
 */
function updateTreeNodeTitle(sectionId, newTitle) {
    const tree = $('#document-tree').jstree(true);
    if (tree) {
        const node = tree.get_node(`node_${sectionId}`);
        if (node) {
            tree.rename_node(node, newTitle);
        }
    }
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);

    // You can replace this with your own notification system
    if (typeof window.customNotify === 'function') {
        window.customNotify(message, type);
    } else {
        alert(message);
    }
}

// Export functions for use in other modules
window.loadSection = loadSection;
window.insertTemplate = insertTemplate;
window.formatText = formatText;
window.showNotification = showNotification;
window.updateTreeNodeTitle = updateTreeNodeTitle;
