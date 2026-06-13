document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messagesContainer = document.getElementById('messagesContainer');
    const intentsList = document.getElementById('intentsList');
    
    // Stats Elements
    const statSessionId = document.getElementById('statSessionId');
    const statMessageCount = document.getElementById('statMessageCount');
    const statContext = document.getElementById('statContext');
    const statDuration = document.getElementById('statDuration');
    
    // Actions & Panels
    const btnReset = document.getElementById('btnReset');
    const btnShowChat = document.getElementById('btnShowChat');
    const btnShowLogs = document.getElementById('btnShowLogs');
    const chatPanel = document.getElementById('chatPanel');
    const logsPanel = document.getElementById('logsPanel');
    const logsContent = document.getElementById('logsContent');
    const btnDownloadLogs = document.getElementById('btnDownloadLogs');

    // Load initial data
    loadIntents();
    updateStats();
    
    // Stats polling (every 2 seconds to keep timer updated)
    setInterval(updateStats, 2000);

    // Form Submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msgText = userInput.value.trim();
        if (!msgText) return;

        // Clear input
        userInput.value = '';
        
        // Append User Message
        appendMessage('user', msgText);
        scrollToBottom();

        // Show Bot Typing Indicator
        const typingId = showTypingIndicator();
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msgText })
            });

            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator(typingId);

            if (data.error) {
                appendMessage('bot', `Error: ${data.error}`);
            } else {
                appendMessage('bot', data.response);
                // Update stats immediately
                updateStats();
            }
        } catch (error) {
            removeTypingIndicator(typingId);
            appendMessage('bot', 'Sorry, I am having trouble connecting to the server. Please check if the backend is running.');
            console.error('Error sending message:', error);
        }
        scrollToBottom();
    });

    // Reset Session Button
    btnReset.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the conversation and reset the session?')) {
            try {
                const res = await fetch('/api/reset', { method: 'POST' });
                const data = await res.json();
                
                // Clear messages container
                messagesContainer.innerHTML = '';
                
                // Add initial bot greeting
                appendMessage('bot', 'Session reset. Welcome! I am **CodePulse AI**, your interactive developer companion. Ready to answer your coding queries!');
                
                updateStats();
                
                // Switch back to chat panel if in log panel
                showPanel('chat');
            } catch (err) {
                console.error('Error resetting session:', err);
            }
        }
    });

    // Tab Navigation
    btnShowChat.addEventListener('click', () => showPanel('chat'));
    btnShowLogs.addEventListener('click', () => {
        showPanel('logs');
        loadLogs();
    });

    // Panel switching logic
    function showPanel(panelName) {
        if (panelName === 'chat') {
            btnShowChat.classList.add('active');
            btnShowLogs.classList.remove('active');
            chatPanel.classList.add('active');
            logsPanel.classList.remove('active');
        } else {
            btnShowChat.classList.remove('active');
            btnShowLogs.classList.add('active');
            chatPanel.classList.remove('active');
            logsPanel.classList.add('active');
        }
    }

    // Load supported intents from server
    async function loadIntents() {
        try {
            const res = await fetch('/api/intents');
            const intents = await res.json();
            
            intentsList.innerHTML = '';
            intents.forEach(intent => {
                const item = document.createElement('div');
                item.className = 'intent-item';
                // Trigger typing of that intent's prompt when clicked
                item.addEventListener('click', () => {
                    userInput.value = getUtteranceForIntent(intent.tag);
                    userInput.focus();
                });
                
                const tagSpan = document.createElement('span');
                tagSpan.className = 'intent-tag';
                tagSpan.textContent = `#${intent.tag}`;
                
                const descSpan = document.createElement('span');
                descSpan.className = 'intent-count';
                descSpan.textContent = 'View';
                
                item.appendChild(tagSpan);
                item.appendChild(descSpan);
                intentsList.appendChild(item);
            });
        } catch (err) {
            console.error('Error loading intents:', err);
            intentsList.innerHTML = '<div class="error-placeholder">Failed to load intents</div>';
        }
    }

    // Return a sample utterance when clicking a sidebar intent
    function getUtteranceForIntent(tag) {
        const samples = {
            'greeting': 'Hello!',
            'goodbye': 'Goodbye',
            'bot_identity': 'Who are you?',
            'help': 'What can you do?',
            'python_basics': 'How do I learn python?',
            'git_basics': 'How do I use Git?',
            'api_basics': 'What is an API?',
            'sql_queries': 'What is a SQL query?',
            'frontend_vs_backend': 'Frontend vs backend difference',
            'debug_code': 'How do I fix a bug in my code?',
            'interview_tips': 'Prep for coding interview',
            'context_example': 'Give me an example',
            'context_more': 'Tell me more'
        };
        return samples[tag] || '';
    }

    // Load active logs
    async function loadLogs() {
        try {
            const res = await fetch('/api/logs');
            const data = await res.json();
            logsContent.textContent = data.logs;
        } catch (err) {
            logsContent.textContent = 'Failed to retrieve logs from server.';
            console.error('Error loading logs:', err);
        }
    }

    // Get session stats
    async function updateStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) return;
            const stats = await res.json();
            
            statSessionId.textContent = stats.session_id.substring(0, 8);
            statMessageCount.textContent = stats.message_count;
            statDuration.textContent = stats.duration;
            
            // Context badge color formatting
            let badgeClass = 'badge-none';
            const ctx = stats.active_context;
            if (ctx !== 'None') {
                if (ctx.includes('python')) badgeClass = 'badge-python';
                else if (ctx.includes('git')) badgeClass = 'badge-git';
                else if (ctx.includes('sql')) badgeClass = 'badge-sql';
                else if (ctx.includes('api')) badgeClass = 'badge-api';
                else if (ctx.includes('webdev')) badgeClass = 'badge-webdev';
                else if (ctx.includes('debug')) badgeClass = 'badge-debug';
                else if (ctx.includes('interview')) badgeClass = 'badge-interview';
            }
            
            statContext.innerHTML = `<span class="badge ${badgeClass}">${ctx}</span>`;
        } catch (err) {
            console.error('Error updating stats:', err);
        }
    }

    // Append Chat Bubble
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Custom Markdown & Code block formatting
        if (sender === 'bot') {
            contentDiv.innerHTML = parseMarkdown(text);
        } else {
            // Escape HTML for user input, simple formatting
            contentDiv.textContent = text;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        const now = new Date();
        timeDiv.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        messagesContainer.appendChild(messageDiv);
    }

    // Display typing indicators
    function showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = typingId;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        for(let i=0; i<3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicator.appendChild(dot);
        }
        
        contentDiv.appendChild(indicator);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        return typingId;
    }

    function removeTypingIndicator(id) {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Custom Lightweight Markdown & Syntax Highlighting Parser
    function parseMarkdown(text) {
        if (!text) return '';
        
        // 1. Escaping HTML first to prevent XSS issues
        let html = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
            
        // 2. Code Blocks parsing: ```language ... ```
        const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
        html = html.replace(codeBlockRegex, (match, lang, code) => {
            const highlighted = highlightCode(code.trim(), lang);
            return `<pre><code class="language-${lang}">${highlighted}</code></pre>`;
        });

        // 3. Inline Code: `code`
        html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');

        // 4. Bold text: **text**
        html = html.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');

        // 5. Bullet Lists
        html = html.replace(/^\-\s+(.+)$/gm, '• $1');

        // 6. Double newlines to paragraph breaks, single to br
        html = html.split('\n\n').map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`).join('');
        
        return html;
    }

    // Custom simple code highlighter
    function highlightCode(code, lang) {
        if (!lang) return code;
        
        const normalizedLang = lang.toLowerCase();
        
        // Syntax Highlight patterns
        if (normalizedLang === 'python' || normalizedLang === 'py') {
            return code
                // Comments
                .replace(/(#.*)/g, '<span class="code-comment">$1</span>')
                // Strings
                .replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="code-string">$1</span>')
                // Keywords
                .replace(/\b(def|class|import|from|return|if|else|elif|for|in|try|except|as|print|while|None|True|False)\b/g, '<span class="code-keyword">$1</span>')
                // Function names
                .replace(/\bdef\s+(\w+)/g, 'def <span class="code-def">$1</span>')
                // Numbers
                .replace(/\b(\d+)\b/g, '<span class="code-number">$1</span>');
        }
        
        if (normalizedLang === 'sql') {
            return code
                // Keywords
                .replace(/\b(SELECT|FROM|WHERE|INNER JOIN|LEFT JOIN|RIGHT JOIN|ON|ORDER BY|GROUP BY|DESC|ASC|AND|OR|IN|AS|INSERT|UPDATE|DELETE|CREATE|TABLE)\b/gi, '<span class="code-keyword">$1</span>')
                // Strings
                .replace(/('(?:[^'\\]|\\.)*')/g, '<span class="code-string">$1</span>')
                // Numbers
                .replace(/\b(\d+)\b/g, '<span class="code-number">$1</span>');
        }

        if (normalizedLang === 'bash' || normalizedLang === 'sh') {
            return code
                // Comments
                .replace(/(#.*)/g, '<span class="code-comment">$1</span>')
                // Commands/Keywords
                .replace(/\b(git|init|add|commit|push|pull|clone|checkout|branch|origin|main)\b/g, '<span class="code-keyword">$1</span>')
                // Strings
                .replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="code-string">$1</span>');
        }

        if (normalizedLang === 'json') {
            return code
                // Strings (Keys and Values)
                .replace(/("(?:[^"\\]|\\.)*")/g, '<span class="code-string">$1</span>')
                // Keywords (true, false, null)
                .replace(/\b(true|false|null)\b/g, '<span class="code-keyword">$1</span>')
                // Numbers
                .replace(/\b(\d+)\b/g, '<span class="code-number">$1</span>');
        }

        return code;
    }
});
