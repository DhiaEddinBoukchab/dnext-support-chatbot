"""
Admin dashboard - Gradio interface for administrators.
Follows SOLID principles: this module is responsible only for admin UI & orchestration,
delegating persistence and business logic to repository and services.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import json

import gradio as gr
import pandas as pd

from database import DatabaseRepository
from auth_service import AuthenticationService
from models import UserStatus


logger = logging.getLogger(__name__)


class AdminDashboard:
    """
    Admin Dashboard - SRP: Handles admin interface only.
    It provides:
    - Real-time monitoring of conversations (auto-refresh)
    - Offline analytics (filters, exports, statistics)
    """

    def __init__(self, db_repository: DatabaseRepository, auth_service: AuthenticationService):
        """Initialize admin dashboard"""
        self.db = db_repository
        self.auth = auth_service
        self.is_authenticated = False

    # ==================== AUTH ====================

    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate admin user"""
        if self.auth.verify_admin(username, password):
            self.is_authenticated = True
            logger.info(f"Admin logged in: {username}")
            return True, "✅ Authentication successful!"

        logger.warning(f"Failed admin login attempt: {username}")
        return False, "❌ Invalid credentials"

    # ==================== DATAFRAME BUILDERS ====================

    def get_users_dataframe(self) -> pd.DataFrame:
        """Get users as DataFrame for display"""
        users = self.db.get_all_users(limit=1000)

        if not users:
            return pd.DataFrame(columns=['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login'])

        data: List[dict] = []
        for user in users:
            data.append(
                {
                    'ID': user.user_id,
                    'Email': user.email,
                    'Name': user.full_name,
                    'Status': user.status.value,
                    'Total Queries': user.total_queries,
                    'Created': user.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                }
            )

        return pd.DataFrame(data)

    def _build_conversations_rows(self, conversations, include_user: bool = True) -> List[dict]:
        """Internal helper to build conversation rows for DataFrames."""
        rows: List[dict] = []
        for conv, user in conversations:
            rows.append(
                {
                    'ID': conv.conversation_id,
                    'User' if include_user else 'User ID': user.email if include_user else conv.user_id,
                    'Message': conv.message[:100] + '...' if len(conv.message) > 100 else conv.message,
                    'Response': conv.response[:100] + '...' if len(conv.response) > 100 else conv.response,
                    'Type': conv.conversation_type,
                    'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Response Time (ms)': conv.response_time_ms or 'N/A',
                }
            )
        return rows

    def get_conversations_dataframe(self, user_id: Optional[int] = None, limit: int = 100) -> pd.DataFrame:
        """
        Get conversations as DataFrame.
        When user_id is provided, returns last `limit` conversations for that user.
        Otherwise returns most recent `limit` conversations across all users.
        """
        if user_id:
            conversations = self.db.get_user_conversations(user_id, limit=limit)
            data: List[dict] = []
            for conv in conversations:
                data.append(
                    {
                        'ID': conv.conversation_id,
                        'User ID': conv.user_id,
                        'Message': conv.message[:100] + '...' if len(conv.message) > 100 else conv.message,
                        'Response': conv.response[:100] + '...' if len(conv.response) > 100 else conv.response,
                        'Type': conv.conversation_type,
                        'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Response Time (ms)': conv.response_time_ms or 'N/A',
                    }
                )
        else:
            recent = self.db.get_recent_conversations(limit=limit)
            data = self._build_conversations_rows(recent, include_user=True)

        if not data:
            return pd.DataFrame(
                columns=['ID', 'User' if not user_id else 'User ID', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)']
            )

        return pd.DataFrame(data)

    def get_filtered_conversations_dataframe(
        self,
        user_email: str,
        date_from_str: str,
        date_to_str: str,
        conversation_type: str,
    ) -> pd.DataFrame:
        """
        Get conversations filtered by user email (contains), date range and type.
        Used for offline analytics and exports.
        """
        date_from: Optional[datetime] = None
        date_to: Optional[datetime] = None

        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date_from format: {date_from_str}")

        if date_to_str:
            try:
                # include full day by setting time to 23:59:59
                date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
                date_to = date_to.replace(hour=23, minute=59, second=59)
            except ValueError:
                logger.warning(f"Invalid date_to format: {date_to_str}")

        conv_type = conversation_type or None
        conversations = self.db.get_conversations_filtered(
            user_email=user_email or None,
            date_from=date_from,
            date_to=date_to,
            conversation_type=conv_type,
            limit=500,
        )

        rows = self._build_conversations_rows(conversations, include_user=True)
        if not rows:
            return pd.DataFrame(
                columns=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)']
            )

        return pd.DataFrame(rows)

    # ==================== STATISTICS & ANALYTICS ====================

    def get_statistics_display(self) -> str:
        """Get formatted statistics"""
        stats = self.db.get_statistics()

        if not stats:
            return "No statistics available"

        return f"""
## 📊 System Overview

**Users**
- Total Users: {stats.get('total_users', 0)}
- Active Users (7 days): {stats.get('active_users_7d', 0)}

**Conversations**
- Total Conversations: {stats.get('total_conversations', 0)}
- Today's Conversations: {stats.get('conversations_today', 0)}
- Avg Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms
        """

    def get_timeseries_dataframe(self, days: int = 14) -> pd.DataFrame:
        """Build a DataFrame of conversations per day for the last `days` days."""
        series = self.db.get_conversations_timeseries(days=days)
        if not series:
            return pd.DataFrame({"date": [], "conversations": []})

        dates = [str(day) for day, _ in series]
        counts = [count for _, count in series]
        return pd.DataFrame({"date": dates, "conversations": counts})

    def get_recent_image_attachments(self, limit: int = 20) -> List[str]:
        """
        Get file paths for the most recent image attachments across conversations.
        This powers a lightweight gallery in the admin dashboard so admins can
        visually inspect what users have uploaded.
        """
        recent = self.db.get_recent_conversations(limit=200)
        image_paths: List[str] = []

        for conversation, _user in recent:
            if not getattr(conversation, "attachments", None):
                continue
            try:
                items = json.loads(conversation.attachments)
            except Exception as e:
                logger.warning(f"Failed to parse attachments JSON: {e}")
                continue

            for item in items:
                if item.get("type") == "image" and item.get("path"):
                    image_paths.append(item["path"])
                    if len(image_paths) >= limit:
                        return image_paths

        return image_paths

    # ==================== USER DETAIL ====================

    def get_user_details(self, user_id: int) -> str:
        """Get detailed user information"""
        if not user_id:
            return "Please enter a user ID"

        user = self.db.get_user_by_id(user_id)
        if not user:
            return f"❌ User with ID {user_id} not found"

        conversations = self.db.get_user_conversations(user_id, limit=10)

        details = f"""
## 👤 User Details

**Basic Information**
- User ID: {user.user_id}
- Email: {user.email}
- Full Name: {user.full_name}
- Status: {user.status.value}

**Activity**
- Total Queries: {user.total_queries}
- Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}

**Recent Conversations:** {len(conversations)}
        """

        return details

    def update_user_status(self, user_id: int, new_status: str) -> str:
        """Update user status"""
        if not user_id:
            return "Please enter a user ID"

        user = self.db.get_user_by_id(user_id)
        if not user:
            return f"❌ User with ID {user_id} not found"

        try:
            status = UserStatus(new_status.lower())
            self.db.update_user_status(user_id, status)
            return f"✅ User {user_id} status updated to {status.value}"
        except ValueError:
            return f"❌ Invalid status: {new_status}"

    # ==================== EXPORT ====================

    def export_conversations_to_csv(
        self,
        user_email: str,
        date_from: str,
        date_to: str,
        conversation_type: str,
    ) -> Optional[str]:
        """
        Export filtered conversations to a CSV file and return its path.
        This allows offline analysis and long-term archiving.
        """
        df = self.get_filtered_conversations_dataframe(user_email, date_from, date_to, conversation_type)
        if df.empty:
            return None

        exports_dir = Path("exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = (user_email or "all").replace("@", "_").replace(".", "_")
        filename = exports_dir / f"conversations_{safe_email}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding="utf-8")
        logger.info(f"Exported {len(df)} conversations to {filename}")
        return str(filename)

    # ==================== UI ====================

    def create_interface(self) -> gr.Blocks:
        """Create admin dashboard interface"""

        # Note: theme is passed at launch time (Gradio 6+ recommendation),
        # so we keep Blocks simple here for maximum compatibility.
        with gr.Blocks(title="Admin Dashboard") as demo:

            # Authentication state
            auth_state = gr.State(False)

            # ---------- LOGIN ----------
            with gr.Column(visible=True) as login_section:
                gr.Markdown("## 🔐 Admin Login")
                username_input = gr.Textbox(label="Username", placeholder="admin")
                password_input = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login", variant="primary")
                login_status = gr.Markdown("")

            # ---------- DASHBOARD ----------
            with gr.Column(visible=False) as dashboard_section:
                gr.Markdown("## 🎛️ Admin Dashboard - Dnext Support Chatbot")

                with gr.Tabs():
                    # Statistics Tab
                    with gr.Tab("📊 Statistics"):
                        stats_display = gr.Markdown("")
                        # Minimal arguments to keep compatibility across Gradio versions
                        stats_timeseries = gr.LinePlot(
                            value=pd.DataFrame({"date": [], "conversations": []}),
                            x="date",
                            y="conversations",
                            title="Conversations per day (last 14 days)",
                        )
                        refresh_stats_btn = gr.Button("🔄 Refresh Statistics")

                    # Users Tab
                    with gr.Tab("👥 Users"):
                        users_table = gr.Dataframe(
                            headers=['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login'],
                            wrap=True,
                        )
                        refresh_users_btn = gr.Button("🔄 Refresh Users")

                        gr.Markdown("### User Management")
                        with gr.Row():
                            user_id_input = gr.Number(label="User ID", precision=0)
                            user_status_input = gr.Dropdown(
                                choices=["active", "inactive", "blocked"],
                                label="New Status",
                            )
                        update_status_btn = gr.Button("Update Status")
                        status_update_msg = gr.Markdown("")

                    # User Details Tab
                    with gr.Tab("🔍 User Details"):
                        detail_user_id = gr.Number(label="User ID", precision=0)
                        get_details_btn = gr.Button("Get Details")
                        user_details_display = gr.Markdown("")

                        gr.Markdown("### User's Conversation History")
                        user_conversations_table = gr.Dataframe(
                            headers=['ID', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
                            wrap=True,
                        )

                    # Live Monitor Tab
                    with gr.Tab("📡 Live Monitor"):
                        gr.Markdown(
                            "Real-time view of the latest conversations. "
                            "Use auto-refresh to monitor activity while the chatbot is running."
                        )
                        live_conversations_table = gr.Dataframe(
                            headers=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
                            wrap=True,
                        )
                        live_last_refresh = gr.Markdown("")
                        attachments_gallery = gr.Gallery(
                            label="Recent images",
                            columns=4,
                            rows=1,
                            height="auto",
                        )
                        with gr.Row():
                            auto_refresh_toggle = gr.Checkbox(
                                value=True, label="Auto-refresh every 5 seconds"
                            )
                            manual_refresh_btn = gr.Button("Refresh now")
                        live_timer = gr.Timer(value=5.0, active=True)

                    # All Conversations & Export Tab
                    with gr.Tab("💬 Conversations & Export"):
                        gr.Markdown("Filter and export conversations for offline analysis.")

                        with gr.Row():
                            filter_email = gr.Textbox(
                                label="User email contains", placeholder="user@domain.com (optional)"
                            )
                            filter_from = gr.Textbox(
                                label="From date (YYYY-MM-DD)", placeholder="2026-01-01 (optional)"
                            )
                            filter_to = gr.Textbox(
                                label="To date (YYYY-MM-DD)", placeholder="2026-12-31 (optional)"
                            )
                            filter_type = gr.Dropdown(
                                choices=["", "TECHNICAL", "CASUAL"],
                                label="Conversation type",
                                value="",
                            )

                        with gr.Row():
                            apply_filters_btn = gr.Button("Apply filters")
                            export_btn = gr.Button("Export to CSV")

                        conversations_table = gr.Dataframe(
                            headers=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
                            wrap=True,
                        )
                        export_status = gr.Markdown("")
                        export_file = gr.File(label="Download CSV", interactive=False)

            # ---------- EVENT HANDLERS ----------

            def login_handler(username, password):
                success, message = self.authenticate_admin(username, password)
                if success:
                    stats_md = self.get_statistics_display()
                    stats_df = self.get_timeseries_dataframe(days=14)
                    return {
                        login_section: gr.update(visible=False),
                        dashboard_section: gr.update(visible=True),
                        login_status: message,
                        auth_state: True,
                        stats_display: stats_md,
                        stats_timeseries: stats_df,
                        users_table: self.get_users_dataframe(),
                        conversations_table: self.get_conversations_dataframe(limit=100),
                        live_conversations_table: self.get_conversations_dataframe(limit=50),
                        live_last_refresh: f"_Last updated at {datetime.now().strftime('%H:%M:%S')}_",
                        attachments_gallery: self.get_recent_image_attachments(),
                    }
                return {
                    login_status: message,
                    auth_state: False,
                }

            login_btn.click(
                login_handler,
                inputs=[username_input, password_input],
                outputs=[
                    login_section,
                    dashboard_section,
                    login_status,
                    auth_state,
                    stats_display,
                    stats_timeseries,
                    users_table,
                    conversations_table,
                    live_conversations_table,
                    live_last_refresh,
                    attachments_gallery,
                ],
            )

            # ----- Statistics -----
            def refresh_stats():
                return self.get_statistics_display(), self.get_timeseries_dataframe(days=14)

            refresh_stats_btn.click(
                refresh_stats,
                outputs=[stats_display, stats_timeseries],
            )

            # ----- Users -----
            refresh_users_btn.click(
                lambda: self.get_users_dataframe(),
                outputs=users_table,
            )

            update_status_btn.click(
                self.update_user_status,
                inputs=[user_id_input, user_status_input],
                outputs=status_update_msg,
            )

            # ----- User details -----
            def get_user_details_handler(user_id):
                details = self.get_user_details(int(user_id) if user_id else 0)
                conversations = self.get_conversations_dataframe(
                    int(user_id) if user_id else None, limit=100
                )
                # For the user details tab we only show that user's conversations, without email column
                if not conversations.empty:
                    conversations = conversations.drop(columns=['User']) if 'User' in conversations.columns else conversations
                return details, conversations

            get_details_btn.click(
                get_user_details_handler,
                inputs=detail_user_id,
                outputs=[user_details_display, user_conversations_table],
            )

            # ----- Live monitor -----
            def refresh_live_conversations():
                df = self.get_conversations_dataframe(limit=50)
                ts = datetime.now().strftime("%H:%M:%S")
                images = self.get_recent_image_attachments()
                return df, f"_Last updated at {ts}_", images

            manual_refresh_btn.click(
                refresh_live_conversations,
                outputs=[live_conversations_table, live_last_refresh, attachments_gallery],
            )

            def toggle_timer(active: bool):
                return gr.update(active=active)

            auto_refresh_toggle.change(
                toggle_timer,
                inputs=auto_refresh_toggle,
                outputs=live_timer,
            )

            live_timer.tick(
                refresh_live_conversations,
                outputs=[live_conversations_table, live_last_refresh, attachments_gallery],
            )

            # ----- Conversations & export -----
            def apply_filters(email, date_from, date_to, conv_type):
                return self.get_filtered_conversations_dataframe(email, date_from, date_to, conv_type)

            apply_filters_btn.click(
                apply_filters,
                inputs=[filter_email, filter_from, filter_to, filter_type],
                outputs=conversations_table,
            )

            def export_handler(email, date_from, date_to, conv_type):
                path = self.export_conversations_to_csv(email, date_from, date_to, conv_type)
                if not path:
                    return gr.update(value=None), "❌ No conversations matching these filters."
                return gr.update(value=path), f"✅ Exported conversations to `{path}`"

            export_btn.click(
                export_handler,
                inputs=[filter_email, filter_from, filter_to, filter_type],
                outputs=[export_file, export_status],
            )

        return demo

    def launch(self, share: bool = False):
        """Launch admin dashboard"""
        demo = self.create_interface()
        demo.launch(
            share=share,
            theme=gr.themes.Base(),
            server_name="127.0.0.1",  # Only localhost access
            server_port=7861,  # Different port from main chatbot
            show_error=True,
        )