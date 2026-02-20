"""
UI builder: Gradio interface layout and all event handler wiring.
Depends on ChatbotApp (passed in) for all business logic.
"""

import base64
import logging
from pathlib import Path

import gradio as gr

from app.ui_styles import CUSTOM_CSS, PASTE_FIX_JS, LAUNCH_CSS

logger = logging.getLogger(__name__)


def get_logo_base64() -> str:
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""


def build_interface(app) -> gr.Blocks:
    """
    Build and return the Gradio Blocks demo.
    `app` is a ChatbotApp instance that exposes:
      - app.session_mgr   (SessionManager)
      - app.msg_handler   (MessageHandler)
      - app.auth          (AuthenticationService)
    """
    logo_data = get_logo_base64()

    with gr.Blocks(title="Customer AI Assistant", css=CUSTOM_CSS, js=PASTE_FIX_JS) as demo:
        user_state        = gr.State(None)
        current_session_id = gr.State(None)

        # ── LOGIN ────────────────────────────────────────────────────────────
        with gr.Column(visible=True, elem_classes="login-container") as login_section:
            if logo_data:
                gr.HTML(f"""
                    <div style="text-align:center;margin-bottom:1.5rem;">
                        <img src="{logo_data}" style="width:80px;height:80px;margin:0 auto 1rem auto;
                             display:block;object-fit:contain;">
                        <h1 style="margin:0;font-size:1.5rem;font-weight:600;color:#1f2937;">
                            Customer AI Assistant</h1>
                    </div>
                """)
            else:
                gr.Markdown("# 🤖 Customer AI Assistant")

            gr.Markdown("**Sign in to start chatting**")
            email_input  = gr.Textbox(label="Email",     placeholder="your.email@example.com")
            name_input   = gr.Textbox(label="Full Name", placeholder="John Doe")
            signup_btn   = gr.Button("Sign In / Sign Up", variant="primary", size="sm")
            signup_status = gr.Markdown("")

        # ── MAIN CHAT ────────────────────────────────────────────────────────
        with gr.Row(visible=False, elem_classes="main-container") as chat_section:

            # Sidebar
            with gr.Column(scale=1, elem_classes="sidebar", min_width=240):
                with gr.Column(elem_classes="sidebar-header"):
                    new_chat_btn     = gr.Button("➕ New Chat", elem_classes="new-chat-btn")
                    user_info_display = gr.HTML("")

                gr.HTML('<div class="session-date-header">Recent Conversations</div>')
                conversation_selector = gr.Radio(
                    label="", choices=[], interactive=True,
                    show_label=False, elem_classes="conversation-list"
                )
                logout_btn = gr.Button("🚪 Logout", size="sm", elem_classes="logout-btn")

            # Chat area
            with gr.Column(scale=3, elem_classes="chat-container"):
                gr.HTML(f"""
                    <div class="app-header">
                        <div class="logo-container">
                            <img src="{logo_data}" class="logo-img" alt="Dnext Logo">
                            <h1>Customer AI Assistant</h1>
                        </div>
                    </div>
                """)

                # Welcome screen (shown when chat is empty)
                with gr.Column(visible=True, elem_classes="welcome-screen") as welcome_screen:
                    gr.HTML("""
                        <div style="margin-bottom:1.5rem;">
                            <h2>How can I help you today?</h2>
                            <p>Ask me anything about Dnext services, or upload an image for assistance</p>
                        </div>
                    """)
                    with gr.Column(elem_classes="input-container-welcome"):
                        msg_welcome = gr.MultimodalTextbox(
                            placeholder="Message Dnext Support...",
                            file_types=["image", ".pdf", ".txt"],
                            file_count="multiple",
                            show_label=False, submit_btn=True, interactive=True,
                        )

                # Chatbot + bottom input (shown after first message)
                chatbot = gr.Chatbot(value=[], show_label=False, visible=False,
                                     elem_id="chatbot-container")

                with gr.Column(elem_classes="input-container-bottom", visible=False) as input_bottom:
                    msg = gr.MultimodalTextbox(
                        placeholder="Message Dnext Support...",
                        file_types=["image", ".pdf", ".txt"],
                        file_count="multiple",
                        show_label=False, submit_btn=True, interactive=True,
                    )

        # ── EVENT HANDLERS ───────────────────────────────────────────────────

        def signup_handler(email, name):
            success, message, user = app.auth.register_user(email, name)
            if success and user:
                session       = app.session_mgr.get_or_create(user.user_id)
                sidebar       = app.session_mgr.get_sidebar_choices(user.user_id)
                welcome_html  = f'<div class="user-badge">✓ {user.full_name}</div>'
                return {
                    login_section:         gr.update(visible=False),
                    chat_section:          gr.update(visible=True),
                    signup_status:         gr.update(value=""),
                    user_state:            user,
                    current_session_id:    session.session_id,
                    user_info_display:     welcome_html,
                    conversation_selector: gr.update(choices=sidebar, value=None),
                    welcome_screen:        gr.update(visible=True),
                    chatbot:               gr.update(visible=False, value=[]),
                    input_bottom:          gr.update(visible=False),
                    msg_welcome:           gr.update(visible=True, interactive=True,
                                                     value={"text": "", "files": []}),
                    email_input:           gr.update(value=""),
                    name_input:            gr.update(value=""),
                }
            return {signup_status: gr.update(value=f"❌ {message}"), user_state: None}

        def new_chat_handler(user, _current_session):
            if not user:
                return (None, gr.update(visible=False, value=[]), gr.update(visible=True),
                        gr.update(choices=[]), gr.update(visible=False), gr.update(visible=True))
            session  = app.session_mgr.get_or_create(user.user_id)
            sidebar  = app.session_mgr.get_sidebar_choices(user.user_id)
            return {
                current_session_id:    session.session_id,
                chatbot:               gr.update(visible=False, value=[]),
                welcome_screen:        gr.update(visible=True),
                conversation_selector: gr.update(choices=sidebar, value=None),
                input_bottom:          gr.update(visible=False),
                msg_welcome:           gr.update(visible=True, interactive=True,
                                                  value={"text": "", "files": []}),
            }

        def respond(multimodal_input, chat_history, user, session_id):
            if not user or not session_id:
                yield (chat_history, gr.update(visible=False), gr.update(visible=True),
                       gr.update(visible=False), gr.update(visible=True), gr.update())
                return

            text_message = multimodal_input.get("text", "") if isinstance(multimodal_input, dict) else ""
            files        = list(multimodal_input.get("files", [])) if isinstance(multimodal_input, dict) else []

            # Safety net: .txt files that slipped through → read as text
            real_files = []
            for f in files:
                fp = f if isinstance(f, str) else getattr(f, 'name', str(f))
                if str(fp).lower().endswith('.txt'):
                    try:
                        with open(fp, 'r', encoding='utf-8') as fh:
                            extra = fh.read().strip()
                        if extra:
                            text_message = (text_message + "\n\n" + extra).strip()
                    except Exception:
                        real_files.append(f)
                else:
                    real_files.append(f)
            files = real_files

            if not text_message.strip() and not files:
                vis = bool(chat_history)
                yield (chat_history,
                       gr.update(visible=vis),  gr.update(visible=not vis),
                       gr.update(visible=vis),  gr.update(visible=not vis),
                       gr.update())
                return

            session = app.session_mgr.get_or_create(user.user_id, session_id)

            user_content = text_message if text_message else "[Image uploaded]"
            if files:
                user_content += f" 📎 {len(files)} file(s)"

            chat_history.append({"role": "user",      "content": user_content})
            chat_history.append({"role": "assistant", "content": ""})

            # Clear input instantly on first yield
            clear = gr.update(value={"text": "", "files": []})
            yield (chat_history,
                   gr.update(visible=True), gr.update(visible=False),
                   gr.update(visible=True), gr.update(visible=False),
                   clear)

            for chunk in app.msg_handler.process_stream(text_message, files, session, user.user_id):
                chat_history[-1]["content"] = chunk
                yield (chat_history,
                       gr.update(visible=True), gr.update(visible=False),
                       gr.update(visible=True), gr.update(visible=False),
                       gr.update())

        def load_session_handler(session_id, user):
            if not user or not session_id:
                return ([], gr.update(visible=True), gr.update(visible=False),
                        gr.update(visible=False), gr.update(visible=True), None)

            session = app.session_mgr.restore_from_db(user.user_id, session_id)
            history = session.get_chat_history()

            if not history:
                return ([], gr.update(visible=True), gr.update(visible=False),
                        gr.update(visible=False), gr.update(visible=True), session_id)

            return (history,
                    gr.update(visible=True),  gr.update(visible=False),
                    gr.update(visible=True),  gr.update(visible=False),
                    session_id)

        def refresh_sidebar(user):
            if not user:
                return gr.update(choices=[])
            return gr.update(choices=app.session_mgr.get_sidebar_choices(user.user_id))

        def logout_handler(user, _session):
            if user:
                app.session_mgr.clear_user(user.user_id)
            return {
                login_section:         gr.update(visible=True),
                chat_section:          gr.update(visible=False),
                user_state:            None,
                current_session_id:    None,
                chatbot:               gr.update(value=[], visible=False),
                welcome_screen:        gr.update(visible=True),
                msg:                   None,
                msg_welcome:           None,
                email_input:           "",
                name_input:            "",
                conversation_selector: gr.update(choices=[], value=None),
            }

        # ── WIRE EVENTS ──────────────────────────────────────────────────────

        signup_btn.click(
            signup_handler,
            inputs=[email_input, name_input],
            outputs=[login_section, chat_section, signup_status, user_state, current_session_id,
                     user_info_display, conversation_selector, welcome_screen, chatbot,
                     input_bottom, msg_welcome, email_input, name_input],
        ).then(
            new_chat_handler,
            inputs=[user_state, current_session_id],
            outputs=[current_session_id, chatbot, welcome_screen, conversation_selector,
                     input_bottom, msg_welcome],
        )

        new_chat_btn.click(
            new_chat_handler,
            inputs=[user_state, current_session_id],
            outputs=[current_session_id, chatbot, welcome_screen, conversation_selector,
                     input_bottom, msg_welcome],
        )

        # Welcome-screen input
        msg_welcome.submit(
            respond,
            inputs=[msg_welcome, chatbot, user_state, current_session_id],
            outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome, msg_welcome],
        ).then(refresh_sidebar, inputs=[user_state], outputs=[conversation_selector])

        # Bottom input
        msg.submit(
            respond,
            inputs=[msg, chatbot, user_state, current_session_id],
            outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome, msg],
        ).then(refresh_sidebar, inputs=[user_state], outputs=[conversation_selector])

        # Sidebar session selection
        conversation_selector.change(
            load_session_handler,
            inputs=[conversation_selector, user_state],
            outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome, current_session_id],
        )

        logout_btn.click(
            logout_handler,
            inputs=[user_state, current_session_id],
            outputs=[login_section, chat_section, user_state, current_session_id,
                     chatbot, welcome_screen, msg, msg_welcome, email_input, name_input,
                     conversation_selector],
        )

    return demo