"""
AdminDashboard: top-level class.
Composes auth, analytics, user_manager, exporter, and UI into one object.
Exposes create_interface() and launch() — same API as the original admin_dashboard.py.
"""

import logging
from datetime import datetime

import gradio as gr

from database import DatabaseRepository
from auth_service import AuthenticationService

from admin_dashboard.auth        import AdminAuth
from admin_dashboard.analytics   import Analytics
from admin_dashboard.user_manager import UserManager
from admin_dashboard.exporter    import ConversationExporter
from admin_dashboard.dataframes  import (
    build_users_df, build_recent_convs_df, build_user_convs_df
)
from admin_dashboard.ui_tabs import (
    build_stats_tab, build_users_tab, build_user_details_tab,
    build_live_monitor_tab, build_conversations_tab,
)

logger = logging.getLogger(__name__)


class AdminDashboard:
    """
    Admin Dashboard — SRP: orchestrates admin UI only.
    All heavy lifting is delegated to focused sub-modules.
    """

    def __init__(self, db: DatabaseRepository, auth_service: AuthenticationService):
        self.db          = db
        self.admin_auth  = AdminAuth(db, auth_service)
        self.analytics   = Analytics(db)
        self.user_mgr    = UserManager(db)
        self.exporter    = ConversationExporter(db)

    # ── convenience wrappers ─────────────────────────────────────────────────

    def _recent_convs_df(self, limit: int = 50):
        return build_recent_convs_df(self.db.get_recent_conversations(limit=limit))

    def _filtered_convs_df(self, email, date_from, date_to, conv_type):
        from admin_dashboard.dataframes import parse_date
        pairs = self.db.get_conversations_filtered(
            user_email=email or None,
            date_from=parse_date(date_from),
            date_to=parse_date(date_to, end_of_day=True),
            conversation_type=conv_type or None,
            limit=500,
        )
        return build_recent_convs_df(pairs)

    # ── interface ────────────────────────────────────────────────────────────

    def create_interface(self) -> gr.Blocks:
        with gr.Blocks(title="Admin Dashboard") as demo:
            auth_state = gr.State(False)

            # ── Login ────────────────────────────────────────────────────────
            with gr.Column(visible=True) as login_section:
                gr.Markdown("## 🔐 Admin Login")
                username_input = gr.Textbox(label="Username", placeholder="admin")
                password_input = gr.Textbox(label="Password", type="password")
                login_btn      = gr.Button("Login", variant="primary")
                login_status   = gr.Markdown("")

            # ── Dashboard ────────────────────────────────────────────────────
            with gr.Column(visible=False) as dashboard_section:
                gr.Markdown("## 🎛️ Admin Dashboard — Dnext Support Chatbot")

                with gr.Tabs():
                    with gr.Tab("📊 Statistics"):
                        stats_display, stats_ts, refresh_stats_btn = build_stats_tab()

                    with gr.Tab("👥 Users"):
                        (users_table, refresh_users_btn,
                         user_id_input, user_status_input,
                         update_status_btn, status_msg) = build_users_tab()

                    with gr.Tab("🔍 User Details"):
                        (detail_user_id, get_details_btn,
                         user_details_md, user_convs_table) = build_user_details_tab()

                    with gr.Tab("📡 Live Monitor"):
                        (live_table, live_last_refresh, gallery,
                         auto_toggle, manual_refresh_btn,
                         live_timer) = build_live_monitor_tab()

                    with gr.Tab("💬 Conversations & Export"):
                        (filter_email, filter_from, filter_to, filter_type,
                         apply_filters_btn, export_btn,
                         convs_table, export_status, export_file) = build_conversations_tab()

            # ── Event handlers ───────────────────────────────────────────────

            def login_handler(username, password):
                ok, msg = self.admin_auth.login(username, password)
                if not ok:
                    return {login_status: msg, auth_state: False}
                return {
                    login_section:         gr.update(visible=False),
                    dashboard_section:     gr.update(visible=True),
                    login_status:          msg,
                    auth_state:            True,
                    stats_display:         self.analytics.get_statistics_md(),
                    stats_ts:              self.analytics.get_timeseries_df(),
                    users_table:           build_users_df(self.db.get_all_users(limit=1000)),
                    convs_table:           self._recent_convs_df(limit=100),
                    live_table:            self._recent_convs_df(limit=50),
                    live_last_refresh:     f"_Last updated at {datetime.now().strftime('%H:%M:%S')}_",
                    gallery:               self.analytics.get_recent_image_paths(),
                }

            login_btn.click(
                login_handler,
                inputs=[username_input, password_input],
                outputs=[login_section, dashboard_section, login_status, auth_state,
                         stats_display, stats_ts, users_table, convs_table,
                         live_table, live_last_refresh, gallery],
            )

            # Statistics
            refresh_stats_btn.click(
                lambda: (self.analytics.get_statistics_md(), self.analytics.get_timeseries_df()),
                outputs=[stats_display, stats_ts],
            )

            # Users
            refresh_users_btn.click(
                lambda: build_users_df(self.db.get_all_users(limit=1000)),
                outputs=users_table,
            )
            update_status_btn.click(
                lambda uid, s: self.user_mgr.update_status(int(uid) if uid else 0, s),
                inputs=[user_id_input, user_status_input],
                outputs=status_msg,
            )

            # User details
            def user_details_handler(user_id):
                uid   = int(user_id) if user_id else 0
                md    = self.user_mgr.get_user_details_md(uid)
                convs = build_user_convs_df(self.db.get_user_conversations(uid, limit=100))
                if 'User' in convs.columns:
                    convs = convs.drop(columns=['User'])
                return md, convs

            get_details_btn.click(
                user_details_handler,
                inputs=detail_user_id,
                outputs=[user_details_md, user_convs_table],
            )

            # Live monitor
            def refresh_live():
                df = self._recent_convs_df(limit=50)
                ts = datetime.now().strftime('%H:%M:%S')
                return df, f"_Last updated at {ts}_", self.analytics.get_recent_image_paths()

            manual_refresh_btn.click(refresh_live, outputs=[live_table, live_last_refresh, gallery])
            live_timer.tick(refresh_live,           outputs=[live_table, live_last_refresh, gallery])
            auto_toggle.change(
                lambda active: gr.update(active=active),
                inputs=auto_toggle, outputs=live_timer,
            )

            # Conversations & export
            apply_filters_btn.click(
                lambda e, df, dt, t: self._filtered_convs_df(e, df, dt, t),
                inputs=[filter_email, filter_from, filter_to, filter_type],
                outputs=convs_table,
            )

            def export_handler(email, date_from, date_to, conv_type):
                path = self.exporter.export_to_csv(email, date_from, date_to, conv_type)
                if not path:
                    return gr.update(value=None), "❌ No conversations match these filters."
                return gr.update(value=path), f"✅ Exported to `{path}`"

            export_btn.click(
                export_handler,
                inputs=[filter_email, filter_from, filter_to, filter_type],
                outputs=[export_file, export_status],
            )

        return demo

    def launch(self, share: bool = False):
        demo = self.create_interface()
        demo.launch(
            share=share,
            theme=gr.themes.Base(),
            server_name="127.0.0.1",
            server_port=7861,
            show_error=True,
        )