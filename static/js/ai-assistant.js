/**
 * AI Assistant module for the Dash Editor
 * Provides AI-powered writing assistance and suggestions
 */

// Current AI mode
let currentAIMode = 'grammar';
// Store last result for applying suggestion
let lastAIResult = '';

/**
 * Set the active AI mode
 */
function setAIMode(mode) {
    // Update active class on buttons
    document.querySelectorAll('.ai-mode').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Update current mode
    currentAIMode = mode;

    // Update placeholder text based on mode
    const aiInput = document.getElementById('ai-input');

    switch (mode) {
        case 'grammar':
            aiInput.placeholder = 'Enter text to check for grammar and spelling issues';
            break;
        case 'rewrite':
            aiInput.placeholder = 'Enter text to rewrite for improved clarity and flow';
            break;
        case 'expand':
            aiInput.placeholder = 'Enter text to expand with additional details';
            break;
        case 'simplify':
            aiInput.placeholder = 'Enter text to simplify for better accessibility';
            break;
        case 'academic':
            aiInput.placeholder = 'Enter text to revise to academic writing standards';
            break;
    }

    // Clear previous results
    document.getElementById('ai-result').innerHTML = '';
    document.getElementById('ai-apply-btn').disabled = true;
    lastAIResult = '';
}

/**
 * Analyze text with AI
 */
function analyzeText() {
    // Get text from input or editor selection
    let text = document.getElementById('ai-input').value.trim();

    // If no text in the input field, try to get selection from editor
    if (!text && isEditing) {
        const selection = editor.getSelection();
        if (selection && selection.trim().length > 0) {
            text = selection;
            document.getElementById('ai-input').value = text;
        }
    }

    if (!text) {
        showNotification('Please enter or select text to analyze', 'warning');
        return;
    }

    // Show loading state
    const resultContainer = document.getElementById('ai-result');
    resultContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><div>Processing...</div></div>';
    document.getElementById('ai-apply-btn').disabled = true;

    // Send to API
    fetch('/api/ai/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            type: currentAIMode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display result
            resultContainer.innerHTML = formatAIResult(data.result);
            lastAIResult = data.result;

            // Enable apply button
            document.getElementById('ai-apply-btn').disabled = false;
        } else {
            resultContainer.innerHTML = `<div class="alert alert-danger">${data.error || 'Analysis failed'}</div>`;
        }
    })
    .catch(error => {
        console.error('Error analyzing text:', error);
        resultContainer.innerHTML = '<div class="alert alert-danger">Error processing request. Please try again.</div>';
    });
}

/**
 * Apply AI suggestion to the editor
 */
function applyAISuggestion() {
    if (!isEditing || !lastAIResult) return;

    // Apply the suggestion to the editor
    const selection = editor.getSelection();

    if (selection && selection.trim().length > 0) {
        // Replace selected text
        editor.replaceSelection(lastAIResult);
    } else {
        // Insert at cursor position
        const cursor = editor.getCursor();
        editor.replaceRange(lastAIResult, cursor);
    }

    // Clear AI input and result
    document.getElementById('ai-input').value = '';
    document.getElementById('ai-result').innerHTML = '';
    document.getElementById('ai-apply-btn').disabled = true;
    lastAIResult = '';

    // Show notification
    showNotification('Suggestion applied');
}

/**
 * Format AI result with proper styling
 */
function formatAIResult(result) {
    // Basic formatting - could be enhanced for different result types
    const formattedResult = result
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic

    return formattedResult;
}

/**
 * Get section-specific suggestions
 */
function getSectionSuggestions(sectionType, documentType) {
    if (!currentSection) return;

    // Get some context from the document
    const sectionTitles = [];
    documentStructure.sections.forEach(section => {
        sectionTitles.push(section.title);
    });

    const context = `Document title: ${document.getElementById('document-title').value}
Document type: ${documentType}
Sections: ${sectionTitles.join(', ')}`;

    // Show loading state
    const resultContainer = document.getElementById('ai-result');
    resultContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><div>Generating suggestions...</div></div>';
    document.getElementById('ai-apply-btn').disabled = true;

    // Send to API
    fetch('/api/ai/suggest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            section_type: sectionType,
            document_type: documentType,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display result
            resultContainer.innerHTML = formatAIResult(data.result);
            lastAIResult = data.result;

            // Enable apply button
            document.getElementById('ai-apply-btn').disabled = false;
        } else {
            resultContainer.innerHTML = `<div class="alert alert-danger">${data.error || 'Failed to generate suggestions'}</div>`;
        }
    })
    .catch(error => {
        console.error('Error getting suggestions:', error);
        resultContainer.innerHTML = '<div class="alert alert-danger">Error processing request. Please try again.</div>';
    });
}

// Initialize AI Assistant module
document.addEventListener('DOMContentLoaded', function() {
    // Set default mode
    setAIMode('grammar');

    // Add event listeners for section-specific suggestions
    document.getElementById('get-section-suggestions').addEventListener('click', function() {
        if (currentSection) {
            getSectionSuggestions(currentSection.title, documentStructure.document_type);
        } else {
            showNotification('Please select a section first', 'warning');
        }
    });
});

/**
 * AI Assistant Tabs Fix
 * Add this to ai-assistant.js
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing AI Assistant...');

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
        analyzeBtn.addEventListener('click', analyzeText);
    }

    // Fix apply suggestion button
    const applyBtn = document.getElementById('ai-apply-btn');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyAISuggestion);
    }

    // Initialize with default mode
    setAIMode('grammar');

    console.log('AI Assistant initialized');
});
