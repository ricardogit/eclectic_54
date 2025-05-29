/**
 * Collaboration module for real-time editing and chat
 * Uses Socket.IO for real-time communication
 */

// Active users in current document
let activeUsers = [];
let socket; // Socket.IO connection for real-time collaboration

/**
 * Initialize collaboration features
 */
function initializeCollaboration() {
    console.log('Initializing collaboration features...');

    try {
        // Initialize Socket.IO connection
        socket = io();

        // Setup event handlers
        setupSocketEvents();

        // Join the document room
        joinDocument();

        console.log('Collaboration initialized successfully');
        showNotification('Connected to collaboration server', 'success');
    } catch (error) {
        console.error('Error initializing collaboration:', error);
        showNotification('Failed to initialize collaboration. Please refresh the page.', 'error');
    }
}

/**
 * Set up Socket.IO event handlers
 */
function setupSocketEvents() {
    // Connection established
    socket.on('connect', function() {
        console.log('Connected to real-time server');
        showNotification('Connected to collaboration server', 'success');

        // Rejoin document room if reconnected
        if (documentId) {
            joinDocument();
        }
    });

    // Connection lost
    socket.on('disconnect', function() {
        console.log('Disconnected from real-time server');
        showNotification('Collaboration connection lost. Trying to reconnect...', 'warning');
    });

    // Error handling
    socket.on('error', function(data) {
        console.error('Socket error:', data);
        showNotification(`Collaboration error: ${data.message}`, 'error');
    });

    // Document users list
    socket.on('document_users', function(data) {
        console.log('Received active users:', data.users);
        activeUsers = data.users;
        updateActiveUsersList();
    });

    // User joined
    socket.on('user_joined', function(data) {
        console.log('User joined:', data);
        showNotification(`A user has joined the document`);
        refreshActiveUsers();
    });

    // User left
    socket.on('user_left', function(data) {
        console.log('User left:', data);
        showNotification(`A user has left the document`);
        refreshActiveUsers();
    });

    // Section update from another user
    socket.on('section_update', function(data) {
        console.log('Section update received:', data);
        if (typeof handleCollaborativeUpdate === 'function') {
            handleCollaborativeUpdate(data);
        } else {
            console.warn('handleCollaborativeUpdate function not available');
        }
    });

    // Section locked by user
    socket.on('section_locked', function(data) {
        console.log('Section locked:', data);
        if (typeof handleSectionLock === 'function') {
            handleSectionLock(data);
        } else {
            console.warn('handleSectionLock function not available');
        }
    });

    // Section unlocked
    socket.on('section_unlocked', function(data) {
        console.log('Section unlocked:', data);
        if (typeof handleSectionUnlock === 'function') {
            handleSectionUnlock(data);
        } else {
            console.warn('handleSectionUnlock function not available');
        }
    });

    // New chat message
    socket.on('new_message', function(data) {
        console.log('New chat message:', data);
        addChatMessage(data);
    });
}

/**
 * Join the document collaboration room
 */
function joinDocument() {
    if (!socket || !socket.connected || !documentId) {
        console.warn('Cannot join document - socket not connected or document ID missing');
        return;
    }

    console.log('Joining document:', documentId);

    socket.emit('join_document', {
        document_id: documentId,
        user_id: userId
    });
}

/**
 * Leave the document collaboration room
 */
function leaveDocument() {
    if (!socket || !socket.connected || !documentId) return;

    console.log('Leaving document:', documentId);

    socket.emit('leave_document', {
        document_id: documentId,
        user_id: userId
    });
}

/**
 * Refresh the list of active users
 */
function refreshActiveUsers() {
    if (!socket || !socket.connected || !documentId) return;

    socket.emit('join_document', {
        document_id: documentId,
        user_id: userId
    });
}

/**
 * Update the active users list in the UI
 */
function updateActiveUsersList() {
    const container = document.getElementById('active-users-list');
    if (!container) return;

    container.innerHTML = '';

    if (activeUsers.length === 0) {
        container.innerHTML = '<li>No active users</li>';
    } else {
        activeUsers.forEach(user => {
            const userItem = document.createElement('li');
            userItem.innerHTML = `${user.full_name || 'User'} <span class="text-muted">(joined ${formatTimeAgo(user.joined_at)})</span>`;

            // Highlight current user
            if (user.user_id === userId) {
                userItem.classList.add('current-user');
                userItem.innerHTML += ' (you)';
            }

            container.appendChild(userItem);
        });
    }

    // Also update the collaborators tab counter
    updateCollaboratorsTabCounter(activeUsers.length);
}

/**
 * Update the counter on the collaborators tab
 */
function updateCollaboratorsTabCounter(count) {
    const tab = document.querySelector('.tab[data-tab="collaborators"]');
    if (!tab) return;

    // Remove existing counter
    const existingCounter = tab.querySelector('.active-count');
    if (existingCounter) {
        existingCounter.remove();
    }

    // Add new counter if there are active users
    if (count > 0) {
        const counter = document.createElement('span');
        counter.className = 'active-count';
        counter.textContent = count;
        counter.style.marginLeft = '5px';
        counter.style.padding = '0 5px';
        counter.style.backgroundColor = '#28a745';
        counter.style.color = 'white';
        counter.style.borderRadius = '10px';
        counter.style.fontSize = '0.8em';
        tab.appendChild(counter);
    }
}

/**
 * Format time as "X minutes ago"
 */
function formatTimeAgo(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);

    if (diffSec < 60) {
        return 'just now';
    } else if (diffMin < 60) {
        return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
    } else {
        return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
    }
}

/**
 * Send a chat message
 */
function sendChatMessage() {
    const messageInput = document.getElementById('chat-message');
    if (!messageInput || !socket || !socket.connected) return;

    const message = messageInput.value.trim();

    if (!message) return;

    console.log('Sending chat message:', message);

    // Clear input
    messageInput.value = '';

    // Send to server
    socket.emit('chat_message', {
        document_id: documentId,
        user_id: userId,
        message: message
    });

    // Add to UI immediately (optimistic UI)
    addChatMessage({
        user_id: userId,
        message: message,
        timestamp: new Date().toISOString()
    });
}

/**
 * Add a chat message to the UI
 */
function addChatMessage(data) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const messageElem = document.createElement('div');

    // Determine if message is from current user
    const isSelf = data.user_id === userId;
    messageElem.className = `chat-message ${isSelf ? 'sent' : 'received'}`;

    // Find user info if possible
    let userName = `User ${data.user_id}`;
    activeUsers.forEach(user => {
        if (user.user_id === data.user_id) {
            userName = user.full_name || user.name || userName;
        }
    });

    // Format time
    const time = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Build message content
    messageElem.innerHTML = `
        ${!isSelf ? `<div class="message-sender">${userName}</div>` : ''}
        <div class="message-content">${escapeHtml(data.message)}</div>
        <div class="message-time">${time}</div>
    `;

    // Add to container
    container.appendChild(messageElem);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;

    // Flash the chat tab if not active
    const chatTab = document.querySelector('.tab[data-tab="collaborators"]');
    if (chatTab && !chatTab.classList.contains('active')) {
        flashElement(chatTab);
    }
}

/**
 * Flash an element to draw attention
 */
function flashElement(element, times = 3) {
    let count = 0;
    const originalBackground = window.getComputedStyle(element).backgroundColor;

    const interval = setInterval(() => {
        element.style.backgroundColor = count % 2 === 0 ? '#ffc107' : originalBackground;
        count++;

        if (count >= times * 2) {
            clearInterval(interval);
            element.style.backgroundColor = originalBackground;
        }
    }, 300);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Lock a section for editing
 */
function acquireSectionLock(sectionId) {
    console.log('Acquiring lock for section:', sectionId);

    if (!socket || !socket.connected) {
        console.log('No socket connection, proceeding without lock');
        return Promise.resolve(true);
    }

    return new Promise((resolve) => {
        // Set up a one-time listener for the response
        socket.once('section_locked', function(data) {
            if (data.section_id === sectionId && data.user_id === userId) {
                console.log('Lock acquired successfully');
                resolve(true);
            }
        });

        socket.once('lock_denied', function(data) {
            if (data.section_id === sectionId) {
                console.log('Lock denied');
                showNotification(`Section is currently being edited by another user`, 'warning');
                resolve(false);
            }
        });

        // Send the lock request
        socket.emit('section_lock', {
            document_id: documentId,
            section_id: sectionId,
            user_id: userId
        });

        // Timeout for server response
        setTimeout(() => {
            console.log('Lock request timed out, proceeding anyway');
            resolve(true); // Assume success if no response
        }, 2000);
    });
}

/**
 * Release a section lock
 */
function releaseSectionLock(sectionId) {
    console.log('Releasing lock for section:', sectionId);

    if (!socket || !socket.connected) {
        console.log('No socket connection, cannot release lock');
        return;
    }

    socket.emit('section_unlock', {
        document_id: documentId,
        section_id: sectionId,
        user_id: userId
    });
}

/**
 * Set up chat event handlers
 */
function setupChatEvents() {
    // Send button click
    const sendBtn = document.getElementById('send-chat');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }

    // Enter key in input
    const chatInput = document.getElementById('chat-message');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
}

// Initialize collaboration and chat when document loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Checking for collaboration features...');

    // Set up chat events regardless of collaboration state
    setupChatEvents();

    // Check if collaboration is enabled for this document
    if (typeof documentStructure !== 'undefined' &&
        documentStructure.collaboration_enabled) {
        console.log('Collaboration is enabled, initializing...');
        initializeCollaboration();
    } else {
        console.log('Collaboration is not enabled for this document');
    }
});

// Export functions for use in other components
window.acquireSectionLock = acquireSectionLock;
window.releaseSectionLock = releaseSectionLock;
window.sendChatMessage = sendChatMessage;
window.refreshActiveUsers = refreshActiveUsers;
