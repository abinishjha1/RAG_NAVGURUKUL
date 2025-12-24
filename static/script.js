// ===== Global State =====
let isDocumentUploaded = false;

// ===== DOM Elements =====
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const uploadSuccess = document.getElementById('uploadSuccess');
const statusText = document.getElementById('statusText');
const successMessage = document.getElementById('successMessage');
const statsCard = document.getElementById('statsCard');
const totalDocs = document.getElementById('totalDocs');
const chunksCreated = document.getElementById('chunksCreated');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const chatStatus = document.getElementById('chatStatus');

// ===== Upload Functionality =====

// Click to upload
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        handleFileUpload(file);
    } else {
        showError('Please upload a PDF file');
    }
});

// Handle file upload
async function handleFileUpload(file) {
    // Validate file type
    if (!file.name.endsWith('.pdf')) {
        showError('Please upload a PDF file');
        return;
    }

    // Show upload status
    uploadArea.style.display = 'none';
    uploadSuccess.style.display = 'none';
    uploadStatus.style.display = 'block';
    statusText.textContent = 'Uploading and processing your PDF...';

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload file
        const response = await fetch('/upload-pdf', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Show success
            uploadStatus.style.display = 'none';
            uploadSuccess.style.display = 'block';
            successMessage.textContent = `${result.filename} - ${result.chunks_created} chunks created`;

            // Update stats
            statsCard.style.display = 'grid';
            totalDocs.textContent = result.total_documents;
            chunksCreated.textContent = result.chunks_created;

            // Enable chat
            isDocumentUploaded = true;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatStatus.textContent = 'Ready to chat';

            // Clear welcome message
            const welcomeMsg = chatMessages.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }

            // Add success message to chat
            addMessageToChat('ai', `Great! I've processed "${result.filename}". You can now ask me questions about the document.`);

            // Reset upload area after 3 seconds
            setTimeout(() => {
                uploadSuccess.style.display = 'none';
                uploadArea.style.display = 'block';
            }, 3000);

        } else {
            throw new Error(result.detail || result.message || 'Upload failed');
        }

    } catch (error) {
        uploadStatus.style.display = 'none';
        uploadArea.style.display = 'block';
        showError(`Error: ${error.message}`);
    }

    // Reset file input
    fileInput.value = '';
}

// ===== Chat Functionality =====

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter key
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message function
async function sendMessage() {
    const question = chatInput.value.trim();

    if (!question) return;

    // Add user message to chat
    addMessageToChat('user', question);

    // Clear input
    chatInput.value = '';

    // Disable input while processing
    chatInput.disabled = true;
    sendBtn.disabled = true;
    chatStatus.textContent = 'Thinking...';

    // Add loading message
    const loadingId = addLoadingMessage();

    try {
        // Send request to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question, k: 5 })
        });

        const result = await response.json();

        // Remove loading message
        removeLoadingMessage(loadingId);

        if (response.ok && result.success) {
            // Add AI response to chat
            addMessageToChat('ai', result.answer, result.sources);
        } else {
            throw new Error(result.detail || result.answer || 'Failed to get response');
        }

    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessageToChat('ai', `Sorry, I encountered an error: ${error.message}`);
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatStatus.textContent = 'Ready to chat';
        chatInput.focus();
    }
}

// Add message to chat
function addMessageToChat(type, text, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatarSvg = type === 'user'
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <h4>📚 Sources (${sources.length}):</h4>
                ${sources.map((source, idx) => `
                    <div class="source-item">
                        ${idx + 1}. ${source.source} (Chunk ${source.chunk_index})
                    </div>
                `).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarSvg}</div>
        <div class="message-content">
            <div class="message-text">${text}</div>
            ${sourcesHtml}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add loading message
function addLoadingMessage() {
    const loadingId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    messageDiv.id = loadingId;

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">
                <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return loadingId;
}

// Remove loading message
function removeLoadingMessage(loadingId) {
    const loadingMsg = document.getElementById(loadingId);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// ===== Clear Functionality =====
clearBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to clear all documents? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/clear', {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Reset UI
            isDocumentUploaded = false;
            chatInput.disabled = true;
            sendBtn.disabled = true;
            chatStatus.textContent = 'No documents';

            // Hide stats
            statsCard.style.display = 'none';

            // Clear chat messages
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <h3>Welcome to PDF RAG System</h3>
                    <p>Upload a PDF document above to start asking questions about its content.</p>
                </div>
            `;

            // Reset upload area
            uploadSuccess.style.display = 'none';
            uploadStatus.style.display = 'none';
            uploadArea.style.display = 'block';

            showSuccess('All documents cleared successfully');
        } else {
            throw new Error(result.detail || result.message || 'Failed to clear documents');
        }

    } catch (error) {
        showError(`Error: ${error.message}`);
    }
});

// ===== Utility Functions =====

function showError(message) {
    // You can implement a toast notification here
    alert(message);
}

function showSuccess(message) {
    // You can implement a toast notification here
    alert(message);
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', async () => {
    // Check if there are existing documents
    try {
        const response = await fetch('/status');
        const status = await response.json();

        if (status.initialized && status.total_documents > 0) {
            isDocumentUploaded = true;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatStatus.textContent = 'Ready to chat';

            statsCard.style.display = 'grid';
            totalDocs.textContent = status.total_documents;

            // Clear welcome message
            const welcomeMsg = chatMessages.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }

            addMessageToChat('ai', `Welcome back! I have ${status.total_documents} document chunks loaded. Feel free to ask me questions.`);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
});

