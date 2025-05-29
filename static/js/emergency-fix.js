/**
 * EMERGENCY FIX - Direct DOM Manipulation to add Academic Draft Generator
 *
 * This script creates a visible button for the Academic Draft Generator
 * NO MATTER WHAT, without relying on any existing HTML structure
 */

// Create and add the floating button immediately
(function() {
    console.log('EMERGENCY FIX: Adding Academic Draft Generator button...');

    // Create the floating button
    const button = document.createElement('button');
    button.id = 'academic-draft-generator-button';
    button.innerHTML = 'Academic Draft Generator';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 15px;
        font-size: 14px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;

    // Add hover effect
    button.onmouseover = function() {
        this.style.backgroundColor = '#0069d9';
    };
    button.onmouseout = function() {
        this.style.backgroundColor = '#007bff';
    };

    // Add click handler
    button.onclick = function() {
        openDraftGenerator();
    };

    // Add to body immediately
    document.body.appendChild(button);

    // Function to open the draft generator
    window.openDraftGenerator = function() {
        window.location.href = '/draft_generator';
    };

    console.log('Academic Draft Generator button added successfully');
})();

// Also run when DOM is loaded (in case the immediate execution was too early)
document.addEventListener('DOMContentLoaded', function() {
    // If the button doesn't exist yet, create it
    if (!document.getElementById('academic-draft-generator-button')) {
        console.log('Adding Academic Draft Generator button on DOMContentLoaded...');

        // Create the button again
        const button = document.createElement('button');
        button.id = 'academic-draft-generator-button';
        button.innerHTML = 'Academic Draft Generator';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 15px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        `;

        // Add hover effect
        button.onmouseover = function() {
            this.style.backgroundColor = '#0069d9';
        };
        button.onmouseout = function() {
            this.style.backgroundColor = '#007bff';
        };

        // Add click handler
        button.onclick = function() {
            openDraftGenerator();
        };

        // Add to body
        document.body.appendChild(button);

        console.log('Academic Draft Generator button added successfully on DOMContentLoaded');
    }
});
