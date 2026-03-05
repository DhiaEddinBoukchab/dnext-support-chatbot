"""
UI styles: CSS and JavaScript for the Gradio interface.
"""

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    /* Light Mode Colors */
    --bg-primary-light: #ffffff;
    --bg-secondary-light: #f8f9fa;
    --bg-tertiary-light: #f1f3f5;
    --text-primary-light: #1a1a1a;
    --text-secondary-light: #4b5563;
    --border-light: #e5e7eb;
    --accent-primary: #1e40af;
    --accent-secondary: #06b6d4;
    --success-light: #10b981;
    
    /* Dark Mode Colors */
    --bg-primary-dark: #0f172a;
    --bg-secondary-dark: #1e293b;
    --bg-tertiary-dark: #334155;
    --text-primary-dark: #f1f5f9;
    --text-secondary-dark: #cbd5e1;
    --border-dark: #475569;
    --shadow-dark: rgba(0, 0, 0, 0.4);
}

@media (prefers-color-scheme: dark) {
    :root {
        color-scheme: dark;
    }
}

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

/* Light Mode Base */
body, .gradio-container {
    background-color: var(--bg-primary-light) !important;
    color: var(--text-primary-light) !important;
    margin: 0 !important; 
    padding: 0 !important;
    height: 100vh !important; 
    overflow: hidden !important;
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
    body, .gradio-container {
        background-color: var(--bg-primary-dark) !important;
        color: var(--text-primary-dark) !important;
    }
}

.login-container {
    max-width: 380px !important; 
    margin: auto !important;
    padding: 2rem !important; 
    background: var(--bg-primary-light) !important;
    border-radius: 14px !important; 
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    position: absolute !important; 
    top: 50% !important; 
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    border: 1px solid var(--border-light) !important;
}

@media (prefers-color-scheme: dark) {
    .login-container {
        background: var(--bg-secondary-dark) !important;
        border: 1px solid var(--border-dark) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
}

.main-container {
    display: flex !important; 
    height: 100vh !important;
    max-height: 100vh !important; 
    overflow: hidden !important;
    background: var(--bg-primary-light) !important;
}

@media (prefers-color-scheme: dark) {
    .main-container {
        background: var(--bg-primary-dark) !important;
    }
}

.sidebar {
    width: 240px !important; 
    background: var(--bg-secondary-light) !important;
    border-right: 1px solid var(--border-light) !important; 
    overflow-y: auto !important;
    padding: 1rem !important; 
    height: 100vh !important; 
    flex-shrink: 0 !important;
}

@media (prefers-color-scheme: dark) {
    .sidebar {
        background: var(--bg-secondary-dark) !important;
        border-right: 1px solid var(--border-dark) !important;
    }
}

.sidebar-header { 
    padding: 0.5rem 0 !important; 
    margin-bottom: 0.75rem !important; 
}

.new-chat-btn {
    width: 100% !important; 
    padding: 0.625rem !important;
    background: var(--bg-primary-light) !important; 
    border: 1.5px solid var(--border-light) !important;
    border-radius: 8px !important; 
    font-size: 0.875rem !important; 
    font-weight: 500 !important;
    margin-bottom: 1rem !important;
    color: var(--text-primary-light) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.new-chat-btn:hover {
    background: var(--accent-secondary) !important;
    border-color: var(--accent-secondary) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(6, 182, 212, 0.2) !important;
}

@media (prefers-color-scheme: dark) {
    .new-chat-btn {
        background: var(--bg-tertiary-dark) !important; 
        border-color: var(--border-dark) !important;
        color: var(--text-primary-dark) !important;
    }
    
    .new-chat-btn:hover {
        background: var(--accent-secondary) !important;
        color: white !important;
    }
}

.user-badge {
    background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%) !important; 
    border: 1px solid var(--accent-secondary) !important;
    color: white !important; 
    padding: 0.5rem 0.875rem !important;
    border-radius: 20px !important; 
    font-size: 0.75rem !important;
    margin: 0.75rem 0 !important; 
    text-align: center !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(6, 182, 212, 0.15) !important;
}

@media (prefers-color-scheme: dark) {
    .user-badge {
        background: linear-gradient(135deg, #06b6d4 0%, #0d9488 100%) !important;
    }
}

.session-date-header {
    font-size: 0.65rem !important; 
    font-weight: 700 !important;
    color: var(--text-secondary-light) !important; 
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important; 
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

@media (prefers-color-scheme: dark) {
    .session-date-header {
        color: var(--text-secondary-dark) !important;
    }
}

.chat-container {
    flex: 1 !important; 
    display: flex !important; 
    flex-direction: column !important;
    max-width: 900px !important; 
    margin: 0 auto !important;
    padding: 0 1rem !important; 
    width: 100% !important;
    height: 100vh !important; 
    overflow: hidden !important;
    background: var(--bg-primary-light) !important;
}

@media (prefers-color-scheme: dark) {
    .chat-container {
        background: var(--bg-primary-dark) !important;
    }
}

.app-header {
    text-align: center !important; 
    padding: 1rem 0 !important;
    border-bottom: 1px solid var(--border-light) !important; 
    flex-shrink: 0 !important;
    background: var(--bg-primary-light) !important;
}

@media (prefers-color-scheme: dark) {
    .app-header {
        border-bottom: 1px solid var(--border-dark) !important;
        background: var(--bg-primary-dark) !important;
    }
}

.logo-container {
    display: flex !important; 
    align-items: center !important;
    justify-content: center !important; 
    gap: 0.75rem !important; 
    margin-bottom: 0.5rem !important;
}

.logo-img { 
    width: 36px !important; 
    height: 36px !important; 
    object-fit: contain !important;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1)) !important;
}

@media (prefers-color-scheme: dark) {
    .logo-img {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4)) !important;
    }
}

.chatbot {
    border: none !important; 
    background: transparent !important; 
    box-shadow: none !important;
    flex: 1 !important; 
    overflow-y: auto !important; 
    padding: 1.5rem 0 !important;
    max-width: 750px !important; 
    margin: 0 auto !important; 
    width: 100% !important;
    height: calc(100vh - 200px) !important; 
    max-height: calc(100vh - 200px) !important;
}

.message {
    padding: 0.875rem 1.125rem !important; 
    margin: 0.5rem 0 !important;
    border-radius: 10px !important; 
    width: 100% !important; 
    max-width: 100% !important;
    font-size: 0.9125rem !important; 
    line-height: 1.5 !important;
    word-wrap: break-word !important;
}

.message.user { 
    background: var(--accent-primary) !important; 
    color: white !important;
    border: none !important;
    margin-left: auto !important;
    max-width: 85% !important;
}

.message.bot  { 
    background: var(--bg-secondary-light) !important;
    color: var(--text-primary-light) !important;   
    border: 1px solid var(--border-light) !important;
}

@media (prefers-color-scheme: dark) {
    .message.bot {
        background: var(--bg-tertiary-dark) !important;
        color: var(--text-primary-dark) !important;
        border: 1px solid var(--border-dark) !important;
    }
}

.input-container-welcome {
    background: var(--bg-primary-light) !important; 
    border: 1.5px solid var(--border-light) !important;
    border-radius: 24px !important; 
    padding: 0.75rem 1rem !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05) !important; 
    transition: all 0.3s ease !important;
    margin: 1rem auto 0 !important; 
    max-width: 750px !important;
    width: 100% !important; 
    flex-shrink: 0 !important;
}

.input-container-welcome:focus-within {
    border-color: var(--accent-secondary) !important;
    box-shadow: 0 4px 16px rgba(6, 182, 212, 0.15) !important;
}

@media (prefers-color-scheme: dark) {
    .input-container-welcome {
        background: var(--bg-secondary-dark) !important; 
        border: 1.5px solid var(--border-dark) !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    .input-container-welcome:focus-within {
        box-shadow: 0 4px 16px rgba(6, 182, 212, 0.25) !important;
    }
}

.input-container-bottom {
    background: var(--bg-primary-light) !important; 
    border: 1.5px solid var(--border-light) !important;
    border-radius: 24px !important; 
    padding: 0.75rem 1rem !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05) !important; 
    transition: all 0.3s ease !important;
    margin: 1rem auto !important; 
    max-width: 750px !important; 
    width: 100% !important;
    flex-shrink: 0 !important; 
    position: sticky !important; 
    bottom: 1rem !important;
}

.input-container-bottom:focus-within {
    border-color: var(--accent-secondary) !important;
    box-shadow: 0 4px 16px rgba(6, 182, 212, 0.15) !important;
}

@media (prefers-color-scheme: dark) {
    .input-container-bottom {
        background: var(--bg-secondary-dark) !important; 
        border: 1.5px solid var(--border-dark) !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    .input-container-bottom:focus-within {
        box-shadow: 0 4px 16px rgba(6, 182, 212, 0.25) !important;
    }
}

.welcome-screen {
    display: flex !important; 
    flex-direction: column !important;
    align-items: center !important; 
    justify-content: center !important;
    height: calc(100vh - 280px) !important; 
    text-align: center !important;
    padding: 0 !important; 
    flex-shrink: 0 !important;
}

.welcome-screen h2 {
    color: var(--text-primary-light) !important;
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    margin-bottom: 1.5rem !important;
    letter-spacing: -0.5px !important;
}

@media (prefers-color-scheme: dark) {
    .welcome-screen h2 {
        color: var(--text-primary-dark) !important;
    }
}

.logout-btn { 
    margin-top: 1rem !important; 
    padding: 0.5rem 0.75rem !important; 
    font-size: 0.8rem !important;
    background: var(--bg-tertiary-light) !important;
    color: var(--text-secondary-light) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}

.logout-btn:hover {
    background: #fee2e2 !important;
    border-color: #ef4444 !important;
    color: #dc2626 !important;
}

@media (prefers-color-scheme: dark) {
    .logout-btn {
        background: var(--bg-tertiary-dark) !important;
        color: var(--text-secondary-dark) !important;
        border: 1px solid var(--border-dark) !important;
    }
    
    .logout-btn:hover {
        background: rgba(239, 68, 68, 0.15) !important;
        border-color: #ef4444 !important;
        color: #fca5a5 !important;
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar { 
    width: 8px !important; 
}

::-webkit-scrollbar-track { 
    background: var(--bg-secondary-light) !important;
}

::-webkit-scrollbar-thumb { 
    background: var(--border-light) !important; 
    border-radius: 4px !important;
    transition: background 0.2s ease !important;
}

::-webkit-scrollbar-thumb:hover { 
    background: #b0b9c6 !important; 
}

@media (prefers-color-scheme: dark) {
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary-dark) !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-dark) !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b !important;
    }
}

/* Input & Button Styling */
input, textarea, select {
    background: var(--bg-primary-light) !important;
    color: var(--text-primary-light) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
    font-size: 0.9rem !important;
}

input:focus, textarea:focus, select:focus {
    outline: none !important;
    border-color: var(--accent-secondary) !important;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
}

@media (prefers-color-scheme: dark) {
    input, textarea, select {
        background: var(--bg-tertiary-dark) !important;
        color: var(--text-primary-dark) !important;
        border: 1px solid var(--border-dark) !important;
    }
    
    input:focus, textarea:focus, select:focus {
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.25) !important;
    }
}

/* Responsive */
@media (max-height: 700px) {
    .chatbot { 
        height: calc(100vh - 180px) !important; 
        max-height: calc(100vh - 180px) !important; 
    }
    .welcome-screen { 
        height: calc(100vh - 200px) !important; 
    }
    .message { 
        padding: 0.625rem 0.875rem !important; 
        font-size: 0.8375rem !important; 
    }
}

@media (max-width: 1200px) {
    .sidebar { 
        width: 200px !important; 
    }
    .chat-container { 
        padding: 0 0.75rem !important; 
    }
}
"""

# Intercepts paste events so plain-text pastes go into the textarea,
# not into Gradio's file-upload handler.
PASTE_FIX_JS = """
function pasteFixInit() {
    function interceptPaste(e) {
        var items = (e.clipboardData || e.originalEvent.clipboardData).items;
        var hasFile = false;
        for (var i = 0; i < items.length; i++) {
            if (items[i].kind === 'file') { hasFile = true; break; }
        }
        if (hasFile) return;

        var text = (e.clipboardData || e.originalEvent.clipboardData).getData('text/plain');
        if (!text) return;

        var textarea = e.target.closest(
            '.multimodal-textbox, [data-testid="multimodal-textbox-input"], .gr-multimodal-textbox'
        )?.querySelector('textarea');
        if (!textarea) {
            textarea = document.activeElement.tagName === 'TEXTAREA' ? document.activeElement : null;
        }
        if (!textarea) return;

        e.preventDefault();
        e.stopPropagation();

        var start = textarea.selectionStart;
        var end   = textarea.selectionEnd;
        textarea.value = textarea.value.substring(0, start) + text + textarea.value.substring(end);
        textarea.selectionStart = textarea.selectionEnd = start + text.length;
        textarea.dispatchEvent(new Event('input',  { bubbles: true }));
        textarea.dispatchEvent(new Event('change', { bubbles: true }));
    }
    document.addEventListener('paste', interceptPaste, true);
}
"""

LAUNCH_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary-light: #ffffff;
    --bg-primary-dark: #0f172a;
    --text-primary-light: #1a1a1a;
    --text-primary-dark: #f1f5f9;
}

* { 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; 
}

body, .gradio-container { 
    background-color: var(--bg-primary-light) !important;
    color: var(--text-primary-light) !important;
}

@media (prefers-color-scheme: dark) {
    body, .gradio-container { 
        background-color: var(--bg-primary-dark) !important;
        color: var(--text-primary-dark) !important;
    }
}

.gradio-container { 
    max-width: 100% !important; 
    margin: 0 !important; 
    padding: 0 !important; 
}
"""
