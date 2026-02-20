"""
UI styles: CSS and JavaScript for the Gradio interface.
"""

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

body, .gradio-container {
    background-color: #ffffff !important;
    margin: 0 !important; padding: 0 !important;
    height: 100vh !important; overflow: hidden !important;
}

.login-container {
    max-width: 380px !important; margin: auto !important;
    padding: 1.5rem !important; background: white !important;
    border-radius: 12px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    position: absolute !important; top: 50% !important; left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

.main-container {
    display: flex !important; height: 100vh !important;
    max-height: 100vh !important; overflow: hidden !important;
}

.sidebar {
    width: 240px !important; background: #f7f7f8 !important;
    border-right: 1px solid #e5e7eb !important; overflow-y: auto !important;
    padding: 0.75rem !important; height: 100vh !important; flex-shrink: 0 !important;
}

.sidebar-header { padding: 0.5rem 0 !important; margin-bottom: 0.75rem !important; }

.new-chat-btn {
    width: 100% !important; padding: 0.5rem !important;
    background: white !important; border: 1px solid #d1d5db !important;
    border-radius: 8px !important; font-size: 0.875rem !important; margin-bottom: 1rem !important;
}

.user-badge {
    background: #f0fdf4 !important; border: 1px solid #bbf7d0 !important;
    color: #166534 !important; padding: 0.375rem 0.75rem !important;
    border-radius: 16px !important; font-size: 0.75rem !important;
    margin: 0.5rem 0 !important; text-align: center !important;
}

.session-date-header {
    font-size: 0.6875rem !important; font-weight: 600 !important;
    color: #6b7280 !important; margin-top: 0.75rem !important;
    margin-bottom: 0.25rem !important; text-transform: uppercase !important;
}

.chat-container {
    flex: 1 !important; display: flex !important; flex-direction: column !important;
    max-width: 900px !important; margin: 0 auto !important;
    padding: 0 0.75rem !important; width: 100% !important;
    height: 100vh !important; overflow: hidden !important;
}

.app-header {
    text-align: center !important; padding: 0.75rem 0 !important;
    border-bottom: 1px solid #e5e7eb !important; flex-shrink: 0 !important;
}

.logo-container {
    display: flex !important; align-items: center !important;
    justify-content: center !important; gap: 0.5rem !important; margin-bottom: 0.5rem !important;
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

.message.user { background: #f7f7f8 !important; border: none !important; }
.message.bot  { background: white !important;   border: none !important; }

.input-container-welcome {
    background: white !important; border: 1px solid #d1d5db !important;
    border-radius: 20px !important; padding: 0.5rem 0.75rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important; transition: all 0.2s !important;
    margin: 0.5rem auto 0 !important; max-width: 750px !important;
    width: 100% !important; flex-shrink: 0 !important;
}

.input-container-bottom {
    background: white !important; border: 1px solid #d1d5db !important;
    border-radius: 20px !important; padding: 0.5rem 0.75rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important; transition: all 0.2s !important;
    margin: 0.5rem auto !important; max-width: 750px !important; width: 100% !important;
    flex-shrink: 0 !important; position: sticky !important; bottom: 0.5rem !important;
}

.welcome-screen {
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    height: calc(100vh - 200px) !important; text-align: center !important;
    padding: 0 !important; flex-shrink: 0 !important;
}

.logout-btn { margin-top: 0.5rem !important; padding: 0.375rem !important; font-size: 0.75rem !important; }

::-webkit-scrollbar { width: 6px !important; }
::-webkit-scrollbar-track { background: #f1f1f1 !important; }
::-webkit-scrollbar-thumb { background: #c1c1c1 !important; border-radius: 3px !important; }
::-webkit-scrollbar-thumb:hover { background: #a8a8a8 !important; }

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
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
body, .gradio-container { background-color: #ffffff !important; }
.gradio-container { max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
"""