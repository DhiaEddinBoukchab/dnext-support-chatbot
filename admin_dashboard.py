"""
Admin dashboard - Gradio interface for administrators
Following SRP: Only responsible for admin UI
"""

import gradio as gr
from typing import List, Tuple
import pandas as pd
from datetime import datetime
import logging

from database import DatabaseRepository
from auth_service import AuthenticationService
from models import UserStatus


logger = logging.getLogger(__name__)


class AdminDashboard:
    """
    Admin Dashboard - SRP: Handles admin interface only
    """
    
    def __init__(self, db_repository: DatabaseRepository, auth_service: AuthenticationService):
        """Initialize admin dashboard"""
        self.db = db_repository
        self.auth = auth_service
        self.is_authenticated = False
    
    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate admin user"""
        if self.auth.verify_admin(username, password):
            self.is_authenticated = True
            logger.info(f"Admin logged in: {username}")
            return True, "✅ Authentication successful!"
        
        logger.warning(f"Failed admin login attempt: {username}")
        return False, "❌ Invalid credentials"
    
    def get_users_dataframe(self) -> pd.DataFrame:
        """Get users as DataFrame for display"""
        users = self.db.get_all_users(limit=1000)
        
        if not users:
            return pd.DataFrame(columns=['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login'])
        
        data = []
        for user in users:
            data.append({
                'ID': user.user_id,
                'Email': user.email,
                'Name': user.full_name,
                'Status': user.status.value,
                'Total Queries': user.total_queries,
                'Created': user.created_at.strftime('%Y-%m-%d %H:%M'),
                'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            })
        
        return pd.DataFrame(data)
    
    def get_conversations_dataframe(self, user_id: int = None) -> pd.DataFrame:
        """Get conversations as DataFrame"""
        if user_id:
            conversations = self.db.get_user_conversations(user_id, limit=100)
            data = []
            for conv in conversations:
                data.append({
                    'ID': conv.conversation_id,
                    'User ID': conv.user_id,
                    'Message': conv.message[:100] + '...' if len(conv.message) > 100 else conv.message,
                    'Response': conv.response[:100] + '...' if len(conv.response) > 100 else conv.response,
                    'Type': conv.conversation_type,
                    'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Response Time (ms)': conv.response_time_ms or 'N/A'
                })
        else:
            recent = self.db.get_recent_conversations(limit=100)
            data = []
            for conv, user in recent:
                data.append({
                    'ID': conv.conversation_id,
                    'User': user.email,
                    'Message': conv.message[:100] + '...' if len(conv.message) > 100 else conv.message,
                    'Response': conv.response[:100] + '...' if len(conv.response) > 100 else conv.response,
                    'Type': conv.conversation_type,
                    'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Response Time (ms)': conv.response_time_ms or 'N/A'
                })
        
        if not data:
            return pd.DataFrame(columns=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'])
        
        return pd.DataFrame(data)
    
    def get_statistics_display(self) -> str:
        """Get formatted statistics"""
        stats = self.db.get_statistics()
        
        if not stats:
            return "No statistics available"
        
        return f"""
## 📊 System Statistics

**Users**
- Total Users: {stats.get('total_users', 0)}
- Active Users (7 days): {stats.get('active_users_7d', 0)}

**Conversations**
- Total Conversations: {stats.get('total_conversations', 0)}
- Today's Conversations: {stats.get('conversations_today', 0)}
- Avg Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms
        """
    
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
    
    def create_interface(self) -> gr.Blocks:
        """Create admin dashboard interface"""
        
        with gr.Blocks(theme=gr.themes.Base(), title="Admin Dashboard") as demo:
            
            # Authentication state
            auth_state = gr.State(False)
            
            with gr.Column(visible=True) as login_section:
                gr.Markdown("# 🔐 Admin Login")
                username_input = gr.Textbox(label="Username", placeholder="admin")
                password_input = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login", variant="primary")
                login_status = gr.Markdown("")
            
            with gr.Column(visible=False) as dashboard_section:
                gr.Markdown("# 🎛️ Admin Dashboard - Dnext Support Chatbot")
                
                with gr.Tabs():
                    # Statistics Tab
                    with gr.Tab("📊 Statistics"):
                        stats_display = gr.Markdown("")
                        refresh_stats_btn = gr.Button("🔄 Refresh Statistics")
                    
                    # Users Tab
                    with gr.Tab("👥 Users"):
                        users_table = gr.Dataframe(
                            headers=['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login'],
                            wrap=True
                        )
                        refresh_users_btn = gr.Button("🔄 Refresh Users")
                        
                        gr.Markdown("### User Management")
                        with gr.Row():
                            user_id_input = gr.Number(label="User ID", precision=0)
                            user_status_input = gr.Dropdown(
                                choices=["active", "inactive", "blocked"],
                                label="New Status"
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
                            wrap=True
                        )
                    
                    # All Conversations Tab
                    with gr.Tab("💬 All Conversations"):
                        conversations_table = gr.Dataframe(
                            headers=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
                            wrap=True
                        )
                        refresh_conversations_btn = gr.Button("🔄 Refresh Conversations")
            
            # Event handlers
            def login_handler(username, password):
                success, message = self.authenticate_admin(username, password)
                if success:
                    return {
                        login_section: gr.update(visible=False),
                        dashboard_section: gr.update(visible=True),
                        login_status: message,
                        auth_state: True,
                        stats_display: self.get_statistics_display(),
                        users_table: self.get_users_dataframe(),
                        conversations_table: self.get_conversations_dataframe()
                    }
                return {
                    login_status: message,
                    auth_state: False
                }
            
            login_btn.click(
                login_handler,
                inputs=[username_input, password_input],
                outputs=[login_section, dashboard_section, login_status, auth_state,
                        stats_display, users_table, conversations_table]
            )
            
            # Refresh handlers
            refresh_stats_btn.click(
                lambda: self.get_statistics_display(),
                outputs=stats_display
            )
            
            refresh_users_btn.click(
                lambda: self.get_users_dataframe(),
                outputs=users_table
            )
            
            refresh_conversations_btn.click(
                lambda: self.get_conversations_dataframe(),
                outputs=conversations_table
            )
            
            update_status_btn.click(
                self.update_user_status,
                inputs=[user_id_input, user_status_input],
                outputs=status_update_msg
            )
            
            def get_user_details_handler(user_id):
                details = self.get_user_details(int(user_id) if user_id else 0)
                conversations = self.get_conversations_dataframe(int(user_id) if user_id else None)
                return details, conversations
            
            get_details_btn.click(
                get_user_details_handler,
                inputs=detail_user_id,
                outputs=[user_details_display, user_conversations_table]
            )
        
        return demo
    
    def launch(self, share: bool = False):
        """Launch admin dashboard"""
        demo = self.create_interface()
        demo.launch(
            share=share,
            server_name="127.0.0.1",  # Only localhost access
            server_port=7861,  # Different port from main chatbot
            show_error=True
        )