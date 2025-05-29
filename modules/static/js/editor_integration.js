/**
 * Force Academic Draft Generator Menu Integration
 * This script GUARANTEES that a menu item or button for the Draft Generator will appear
 */

// Execute this script immediately
(function() {
    console.log('Forcing Academic Draft Generator menu integration...');

    // Try multiple times to ensure it works with dynamically loaded content
    addMenuItemNow();
    setTimeout(addMenuItemNow, 500);
    setTimeout(addMenuItemNow, 1000);
    setTimeout(addMenuItemNow, 2000);

    // Also run when DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        addMenuItemNow();
        setTimeout(addMenuItemNow, 500);
    });

    // Also run when window is fully loaded
    window.addEventListener('load', function() {
        addMenuItemNow();
    });

    /**
     * Forcefully add menu item using multiple strategies
     */
    function addMenuItemNow() {
        // Only add once
        if (document.querySelector('[data-generator-added="true"]')) {
            return;
        }

        // DIRECT INJECTION: Try to find and enhance specific elements
        let added = false;

        // STRATEGY 1: Try to add to dropdown menus
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        for (const menu of dropdowns) {
            // Skip very small or empty menus
            if (menu.children.length < 2) continue;

            // Add item to menu
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'dropdown-item';
            item.setAttribute('data-generator-added', 'true');
            item.innerHTML = '<i class="fa fa-file-text"></i> Academic Draft Generator';
            item.addEventListener('click', function(e) {
                e.preventDefault();
                openDraftGenerator();
            });

            menu.appendChild(item);
            added = true;
            break;
        }

        // STRATEGY 2: Try to find action buttons and add alongside them
        if (!added) {
            const btnGroups = document.querySelectorAll('.editor-controls, .toolbar, .btn-group, .action-buttons');
            for (const group of btnGroups) {
                if (group.children.length < 1) continue;

                // Add button to group
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = [...group.querySelector('button')?.classList || ['btn', 'btn-outline-secondary']].join(' ');
                btn.setAttribute('data-generator-added', 'true');
                btn.innerHTML = '<i class="fa fa-file-text"></i>';
                btn.title = 'Academic Draft Generator';
                btn.addEventListener('click', openDraftGenerator);

                group.appendChild(btn);
                added = true;
                break;
            }
        }

        // STRATEGY 3: Inject near editor
        if (!added) {
            const editorElements = document.querySelectorAll('#section-content, #editor, .editor-container, .CodeMirror');
            for (const editor of editorElements) {
                // Create button
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-sm btn-outline-secondary';
                btn.setAttribute('data-generator-added', 'true');
                btn.innerHTML = '<i class="fa fa-file-text"></i> Draft Generator';
                btn.style.position = 'absolute';
                btn.style.top = '5px';
                btn.style.right = '10px';
                btn.style.zIndex = '100';
                btn.addEventListener('click', openDraftGenerator);

                // Add button near editor
                editor.parentNode.style.position = 'relative';
                editor.parentNode.appendChild(btn);
                added = true;
                break;
            }
        }

        // STRATEGY 4: Add to any visible header or navbar
        if (!added) {
            const headers = document.querySelectorAll('.card-header, .navbar, .header, .editor-header');
            for (const header of headers) {
                // Create button
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-sm btn-outline-secondary';
                btn.setAttribute('data-generator-added', 'true');
                btn.innerHTML = '<i class="fa fa-file-text"></i> Draft Generator';
                btn.style.marginLeft = '10px';
                btn.addEventListener('click', openDraftGenerator);

                // Add button to header
                header.appendChild(btn);
                added = true;
                break;
            }
        }

        // STRATEGY 5: GUARANTEED FALLBACK - Always add floating button
        const fabId = 'draft-generator-fab';
        if (!document.getElementById(fabId)) {
            const fab = document.createElement('button');
            fab.id = fabId;
            fab.className = 'btn btn-primary position-fixed';
            fab.setAttribute('data-generator-added', 'true');
            fab.innerHTML = '<i class="fa fa-file"></i> Academic Draft';
            fab.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999; box-shadow: 0 2px 10px rgba(0,0,0,0.3);';
            fab.addEventListener('click', openDraftGenerator);

            document.body.appendChild(fab);
            console.log('Added floating Draft Generator button');
        }
    }

    /**
     * Open the Draft Generator
     */
    function openDraftGenerator() {
        console.log('Opening Draft Generator...');

        const baseUrl = window.location.origin + '/draft-generator';

        // Create or update modal
        let modal = document.getElementById('draft-generator-modal');

        if (!modal) {
            // Create modal
            const modalHTML = `
            <div class="modal fade" id="draft-generator-modal" tabindex="-1" role="dialog" aria-hidden="true">
                <div class="modal-dialog modal-xl" role="document" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
                    <div class="modal-content" style="height: 100%;">
                        <div class="modal-header">
                            <h5 class="modal-title">Academic Draft Generator</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body p-0" style="height: calc(100% - 56px);">
                            <iframe id="draft-generator-iframe" src="${baseUrl}" style="width: 100%; height: 100%; border: none;"></iframe>
                        </div>
                    </div>
                </div>
            </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('draft-generator-modal');

            // Add custom styling to ensure modal appears properly
            const modalStyle = document.createElement('style');
            modalStyle.textContent = `
                #draft-generator-modal {
                    z-index: 9999 !important;
                }
                #draft-generator-modal .modal-dialog {
                    max-width: 90% !important;
                    height: 90vh !important;
                    margin: 5vh auto !important;
                }
                #draft-generator-modal .modal-content {
                    height: 100% !important;
                }
                #draft-generator-modal .modal-body {
                    height: calc(100% - 56px) !important;
                    padding: 0 !important;
                }
                #draft-generator-iframe {
                    width: 100% !important;
                    height: 100% !important;
                    border: none !important;
                }
                .modal-backdrop {
                    z-index: 9998 !important;
                }
            `;
            document.head.appendChild(modalStyle);
        } else {
            // Update iframe src
            document.getElementById('draft-generator-iframe').src = baseUrl;
        }

        // Try to use jQuery modal if available
        if (typeof $ !== 'undefined' && typeof $.fn.modal !== 'undefined') {
            try {
                $('#draft-generator-modal').modal('show');
                return;
            } catch (e) {
                console.error('Error showing modal with jQuery:', e);
            }
        }

        // Fallback to manual modal display
        try {
            modal.style.display = 'block';
            modal.classList.add('show');

            // Add backdrop
            let backdrop = document.querySelector('.modal-backdrop');
            if (!backdrop) {
                backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }

            // Handle close button
            const closeBtn = modal.querySelector('.close');
            if (closeBtn) {
                closeBtn.onclick = function() {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    if (backdrop && backdrop.parentNode) {
                        backdrop.parentNode.removeChild(backdrop);
                    }
                };
            }
        } catch (e) {
            console.error('Error showing modal manually:', e);

            // Last resort: open in new window/tab
            window.open(baseUrl, '_blank');
        }
    }

    // Listen for messages from iframe
    window.addEventListener('message', function(event) {
        if (event.origin !== window.location.origin) return;

        const data = event.data;

        if (data && data.type === 'draftContent') {
            // Try to insert content into editor
            insertDraftContent(data.content);
        } else if (data && data.type === 'closeModal') {
            // Close modal
            try {
                if (typeof $ !== 'undefined') {
                    $('#draft-generator-modal').modal('hide');
                } else {
                    const modal = document.getElementById('draft-generator-modal');
                    if (modal) {
                        modal.style.display = 'none';
                        modal.classList.remove('show');

                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop && backdrop.parentNode) {
                            backdrop.parentNode.removeChild(backdrop);
                        }
                    }
                }
            } catch (e) {
                console.error('Error closing modal:', e);
            }
        }
    });

    /**
     * Insert content into editor
     */
    function insertDraftContent(content) {
        // Try to find CodeMirror editor
        if (typeof editor !== 'undefined' && editor) {
            try {
                const cursor = editor.getCursor();
                editor.replaceRange(content, cursor);
                alert('Draft content inserted into editor successfully');
            } catch (e) {
                console.error('Error inserting into CodeMirror editor:', e);
                fallbackInsert(content);
            }
        } else {
            // Check for any visible textareas
            const textareas = document.querySelectorAll('textarea');
            let inserted = false;

            for (const textarea of textareas) {
                if (textarea.offsetParent !== null) { // Check if visible
                    const start = textarea.selectionStart;
                    textarea.value = textarea.value.substring(0, start) +
                                     content +
                                     textarea.value.substring(textarea.selectionEnd);

                    alert('Draft content inserted into editor successfully');
                    inserted = true;
                    break;
                }
            }

            if (!inserted) {
                fallbackInsert(content);
            }
        }
    }

    /**
     * Fallback insert method
     */
    function fallbackInsert(content) {
        // Store in localStorage for later retrieval
        localStorage.setItem('draftGeneratorContent', content);

        // Let user know
        alert('Draft content saved. You can access it later by opening a document and clicking the Draft Generator button.');
    }

    // Expose function globally
    window.openDraftGenerator = openDraftGenerator;
})();
