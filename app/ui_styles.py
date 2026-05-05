"""
UI styles: CSS and JavaScript for the Gradio interface.
Uses Gradio's theme variables for automatic light/dark mode compatibility.
"""

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

body, .gradio-container {
    background-color: var(--background-fill-primary, #ffffff) !important;
    margin: 0 !important; padding: 0 !important;
    height: 100vh !important; overflow: hidden !important;
}

/* Hide Gradio footer */
footer, .footer, .gradio-container .footer {
    display: none !important;
}

/* ── LOGIN PAGE ──────────────────────────────────────────────────────────── */

/* Full-height row so the card is vertically centered */
.login-row {
    min-height: 100vh !important;
    align-items: center !important;
    background: var(--background-fill-primary) !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide the two empty spacer columns visually */
.login-row > .gap > div:first-child,
.login-row > .gap > div:last-child {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* The actual login card */
.login-container {
    background: var(--background-fill-secondary, #1e1e1e) !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35) !important;
    padding: 3rem 2.5rem !important;   /* ↕ hauteur interne   ↔ largeur interne */
    min-height: 420px !important;
    /* No position:fixed — gr.Row handles centering */
}

.app-title {
    color: var(--body-text-color, #f9fafb) !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    text-align: center !important;
    margin: 0 0 1.25rem 0 !important;
}

/* ── MAIN APP LAYOUT (post-login) ────────────────────────────────────────── */

.main-container {
    display: flex !important; height: 100vh !important;
    max-height: 100vh !important; overflow: hidden !important;
}

/* Sidebar */
.sidebar {
    width: 240px !important;
    background: var(--background-fill-secondary, #f7f7f8) !important;
    border-right: 1px solid var(--border-color-primary, #e5e7eb) !important;
    overflow-y: auto !important;
    padding: 0.75rem !important; height: 100vh !important; flex-shrink: 0 !important;
}

.sidebar-header { padding: 0.5rem 0 !important; margin-bottom: 0.75rem !important; }

.new-chat-btn {
    width: 100% !important; padding: 0.5rem !important;
    background: var(--background-fill-primary, #ffffff) !important;
    border: 1px solid var(--border-color-primary, #d1d5db) !important;
    border-radius: 8px !important; font-size: 0.875rem !important; margin-bottom: 1rem !important;
    color: var(--body-text-color, inherit) !important;
}

.user-badge {
    background: var(--background-fill-secondary, #f0fdf4) !important;
    border: 1px solid var(--border-color-primary, #bbf7d0) !important;
    color: var(--body-text-color, #166534) !important;
    padding: 0.375rem 0.75rem !important;
    border-radius: 16px !important; font-size: 0.75rem !important;
    margin: 0.5rem 0 !important; text-align: center !important;
}

.session-date-header {
    font-size: 0.6875rem !important; font-weight: 600 !important;
    color: var(--block-label-text-color, #6b7280) !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.25rem !important; text-transform: uppercase !important;
}

/* Chat area */
.chat-container {
    flex: 1 !important; display: flex !important; flex-direction: column !important;
    max-width: 900px !important; margin: 0 auto !important;
    padding: 0 0.75rem !important; width: 100% !important;
    height: 100vh !important; overflow: hidden !important;
}

.app-header {
    text-align: center !important; padding: 0.75rem 0 !important;
    border-bottom: 1px solid var(--border-color-primary, #e5e7eb) !important;
    flex-shrink: 0 !important;
}

.logo-container {
    display: flex !important; align-items: center !important;
    justify-content: center !important; gap: 0.5rem !important; margin-bottom: 0.5rem !important;
}
.logo-container h1 {
    color: var(--body-text-color, inherit) !important;
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
}

.logo-img { width: 32px !important; height: 32px !important; object-fit: contain !important; }

.chatbot {
    border: none !important; background: transparent !important; box-shadow: none !important;
    flex: 1 !important; overflow-y: auto !important; padding: 1rem 0 !important;
    max-width: 750px !important; margin: 0 auto !important; width: 100% !important;
    height: calc(100vh - 180px) !important; max-height: calc(100vh - 180px) !important;
}

.message {
    padding: 0.75rem 1rem !important; margin: 0.375rem 0 !important;
    border-radius: 8px !important; width: 100% !important; max-width: 100% !important;
    font-size: 0.875rem !important; line-height: 1.4 !important;
}
.message.user {
    background: var(--background-fill-secondary, #f7f7f8) !important;
}
.message.bot {
    background: var(--background-fill-primary, #ffffff) !important;
}

.input-container-welcome,
.input-container-bottom {
    background: var(--background-fill-primary, #ffffff) !important;
    border: 1px solid var(--border-color-primary, #d1d5db) !important;
    border-radius: 20px !important; padding: 0.5rem 0.75rem !important;
    box-shadow: var(--shadow-drop, 0 1px 4px rgba(0,0,0,0.06)) !important;
    transition: all 0.2s !important;
    margin: 0.5rem auto !important; max-width: 750px !important;
    width: 100% !important; flex-shrink: 0 !important;
}
.input-container-welcome { margin-top: 0 !important; }
.input-container-bottom { position: sticky !important; bottom: 0.5rem !important; }

.welcome-screen {
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    height: calc(100vh - 200px) !important; text-align: center !important;
    padding: 0 !important; flex-shrink: 0 !important;
}

.logout-btn { margin-top: 0.5rem !important; padding: 0.375rem !important; font-size: 0.75rem !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px !important; }
::-webkit-scrollbar-track { background: var(--background-fill-secondary, #f1f1f1) !important; }
::-webkit-scrollbar-thumb { background: var(--border-color-primary, #c1c1c1) !important; border-radius: 3px !important; }
::-webkit-scrollbar-thumb:hover { background: var(--block-label-text-color, #a8a8a8) !important; }

@media (max-height: 700px) {
    .chatbot { height: calc(100vh - 150px) !important; max-height: calc(100vh - 150px) !important; }
    .welcome-screen { height: calc(100vh - 170px) !important; }
    .message { padding: 0.5rem 0.75rem !important; font-size: 0.8125rem !important; }
}

@media (max-width: 1200px) {
    .sidebar { width: 200px !important; }
    .chat-container { padding: 0 0.5rem !important; }
}
"""

# Paste fix remains unchanged
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
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
body, .gradio-container { 
    background-color: var(--background-fill-primary, #ffffff) !important; 
}
.gradio-container { max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
"""