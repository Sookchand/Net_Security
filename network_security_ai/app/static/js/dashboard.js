/**
 * Dashboard JavaScript for Network Security AI Platform
 */

// Global variables
let currentConversationId = null;

/**
 * Initialize the dashboard
 */
function initDashboard() {
    console.log('Initializing dashboard...');
    
    // Add event listeners to buttons
    addEventListeners();
}

/**
 * Add event listeners to dashboard elements
 */
function addEventListeners() {
    // Sample drift button
    const driftBtn = document.getElementById('sample-drift-btn');
    if (driftBtn) {
        driftBtn.addEventListener('click', generateSampleDrift);
    }
    
    // Sample attack button
    const attackBtn = document.getElementById('sample-attack-btn');
    if (attackBtn) {
        attackBtn.addEventListener('click', generateSampleAttack);
    }
    
    // Ask question button
    const askBtn = document.getElementById('ask-question-btn');
    if (askBtn) {
        askBtn.addEventListener('click', askQuestion);
    }
    
    // Question input (for Enter key)
    const questionInput = document.getElementById('question-input');
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
    }
}

/**
 * Format a severity level with appropriate color
 * @param {string} severity - The severity level (Critical, High, Medium, Low)
 * @returns {string} HTML for the formatted severity
 */
function formatSeverity(severity) {
    let colorClass;
    
    switch (severity) {
        case 'Critical':
            colorClass = 'danger';
            break;
        case 'High':
            colorClass = 'warning';
            break;
        case 'Medium':
            colorClass = 'info';
            break;
        case 'Low':
            colorClass = 'success';
            break;
        default:
            colorClass = 'secondary';
    }
    
    return `<span class="badge bg-${colorClass}">${severity}</span>`;
}

/**
 * Format a timestamp as a localized string
 * @param {string} timestamp - ISO timestamp
 * @returns {string} Formatted date and time
 */
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

/**
 * Add a message to the conversation history
 * @param {string} role - The role of the message sender ('user' or 'ai')
 * @param {string} content - The message content
 */
function addConversationMessage(role, content) {
    const conversationHistory = document.getElementById('conversation-history');
    if (!conversationHistory) return;
    
    const alertClass = role === 'user' ? 'secondary' : 'info';
    const sender = role === 'user' ? 'You' : 'AI';
    
    conversationHistory.innerHTML += `
        <div class="alert alert-${alertClass}">
            <strong>${sender}:</strong> ${content}
        </div>
    `;
    
    // Scroll to the bottom of the conversation
    conversationHistory.scrollTop = conversationHistory.scrollHeight;
}

/**
 * Add a loading indicator to the conversation history
 * @returns {void}
 */
function addLoadingIndicator() {
    const conversationHistory = document.getElementById('conversation-history');
    if (!conversationHistory) return;
    
    conversationHistory.innerHTML += `
        <div class="text-center my-2 loading-indicator">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Scroll to the bottom of the conversation
    conversationHistory.scrollTop = conversationHistory.scrollHeight;
}

/**
 * Remove the loading indicator from the conversation history
 * @returns {void}
 */
function removeLoadingIndicator() {
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', initDashboard);
