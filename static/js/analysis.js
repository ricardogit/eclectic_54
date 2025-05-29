/**
 * Analysis module for document metrics and visualization
 * Uses Chart.js for visualizations
 */

// Store charts for later reference
let wordCountChart = null;
let readabilityChart = null;

/**
 * Initialize analysis functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize analysis panel
    initAnalysis();

    // Add event listener for refresh button
    document.getElementById('refresh-analysis').addEventListener('click', function() {
        refreshAnalysis();
    });

    // Also set up analysis-related document actions
    document.getElementById('analyze-document').addEventListener('click', function(e) {
        e.preventDefault();
        // Switch to analysis tab
        document.querySelector('.tab[data-tab="analysis"]').click();
        // Refresh analysis
        refreshAnalysis();
    });
});

/**
 * Initialize the analysis panel
 */
function initAnalysis() {
    // Initial load of analysis data
    refreshAnalysis();
}

/**
 * Refresh the analysis data
 */
function refreshAnalysis() {
    const analysisResults = document.querySelector('.analysis-results');

    // Show loading state
    analysisResults.innerHTML = '<div class="text-center my-4"><i class="fa fa-spinner fa-spin"></i> Loading analysis...</div>';

    // Fetch analysis data from server
    fetch(`/api/documents/${documentId}/analysis`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update UI with analysis results
            updateAnalysisUI(data);
        })
        .catch(error => {
            console.error('Error loading analysis:', error);
            analysisResults.innerHTML = '<div class="alert alert-danger">Error loading analysis. Please try again.</div>';
        });
}

/**
 * Update the analysis UI with data
 */
function updateAnalysisUI(data) {
    // If we have existing charts, destroy them to prevent duplicates
    if (wordCountChart) {
        wordCountChart.destroy();
        wordCountChart = null;
    }

    if (readabilityChart) {
        readabilityChart.destroy();
        readabilityChart = null;
    }

    // Recreate the entire analysis content
    const analysisResults = document.querySelector('.analysis-results');

    analysisResults.innerHTML = `
        <div class="analysis-section">
            <h4>Structure</h4>
            <div class="progress">
                <div id="completeness-bar" class="progress-bar" role="progressbar" style="width: ${data.completeness || 0}%"></div>
            </div>
            <p>Completeness: <span id="completeness-value">${data.completeness || 0}%</span></p>
            <div id="missing-sections">
                <h5>Missing Sections:</h5>
                <ul id="missing-sections-list">
                    ${data.missingSections && data.missingSections.length > 0 ?
                      data.missingSections.map(section => `<li>${section}</li>`).join('') :
                      '<li>No missing sections</li>'}
                </ul>
            </div>
        </div>
        <div class="analysis-section">
            <h4>Content</h4>
            <p>Total Words: <span id="total-words">${data.totalWords || 0}</span></p>
            <div id="word-count-chart" class="chart-container"></div>
        </div>
        <div class="analysis-section">
            <h4>Readability</h4>
            <div id="readability-chart" class="chart-container"></div>
        </div>
    `;

    // Initialize charts
    if (data.sectionWordCounts) {
        initWordCountChart(data.sectionWordCounts);
    }

    if (data.readabilityScores) {
        initReadabilityChart(data.readabilityScores);
    }
}

/**
 * Initialize word count chart
 */
function initWordCountChart(wordCounts) {
    if (!wordCounts || Object.keys(wordCounts).length === 0) return;

    const ctx = document.getElementById('word-count-chart');
    if (!ctx) return;

    const chartCtx = ctx.getContext('2d');

    // Convert data to chart format
    const labels = Object.keys(wordCounts);
    const data = labels.map(key => wordCounts[key]);

    // Create chart
    wordCountChart = new Chart(chartCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Word Count',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Initialize readability chart
 */
function initReadabilityChart(readabilityScores) {
    if (!readabilityScores || Object.keys(readabilityScores).length === 0) return;

    const ctx = document.getElementById('readability-chart');
    if (!ctx) return;

    const chartCtx = ctx.getContext('2d');

    // Convert data to chart format
    const labels = Object.keys(readabilityScores);
    const data = labels.map(key => readabilityScores[key]);

    // Create chart
    readabilityChart = new Chart(chartCtx, {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Readability Score',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

/**
 * Generate downloadable report
 */
function generateAnalysisReport() {
    // Get current analysis data
    const totalWords = document.getElementById('total-words').textContent;
    const completeness = document.getElementById('completeness-value').textContent;
    const missingSectionsList = document.getElementById('missing-sections-list');
    const missingSections = [];

    // Extract missing sections
    if (missingSectionsList) {
        const items = missingSectionsList.querySelectorAll('li');
        items.forEach(item => {
            if (item.textContent !== 'No missing sections') {
                missingSections.push(item.textContent);
            }
        });
    }

    // Create summary text
    const reportText = `
# Document Analysis Report
## ${document.getElementById('document-title').value}
Generated: ${new Date().toLocaleString()}

## Summary
- Document Type: ${documentStructure.document_type || 'Document'}
- Total Words: ${totalWords}
- Structure Completeness: ${completeness}
- Missing Sections: ${missingSections.length}

## Missing Sections
${missingSections.length > 0 ? missingSections.map(section => `- ${section}`).join('\n') : '- None'}

## Recommendations
${parseInt(completeness) < 100 ? '- Add missing sections to complete the document structure' : '- Document structure is complete'}
${parseInt(totalWords) < 1000 ? '- Consider expanding content for more thorough coverage' : ''}
${parseInt(completeness.replace('%', '')) < 70 ? '- Focus on completing the document structure before refining content' : ''}
`;

    // Create download link
    const blob = new Blob([reportText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);

    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = `analysis_${documentId}.md`;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    URL.revokeObjectURL(url);

    showNotification('Analysis report downloaded', 'success');
}

// Export functions for use in other modules
window.refreshAnalysis = refreshAnalysis;
window.generateAnalysisReport = generateAnalysisReport;
