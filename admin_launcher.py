"""
Admin Dashboard Launcher - Separate script to run admin interface
Run this on localhost only for security
"""

import logging
from database import DatabaseRepository
from auth_service import AuthenticationService
from admin_dashboard import AdminDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """Launch admin dashboard"""
    print("=" * 60)
    print("🎛️ Starting Admin Dashboard")
    print("=" * 60)
    print("⚠️ SECURITY: This runs on localhost only!")
    print("=" * 60)
    
    try:
        # Initialize services
        db_repository = DatabaseRepository("data/chatbot.db")
        auth_service = AuthenticationService(db_repository)
        
        # Create admin dashboard
        admin_dashboard = AdminDashboard(db_repository, auth_service)
        
        print("\n" + "=" * 60)
        print("✅ Admin Dashboard Ready!")
        print("🌐 Access: http://127.0.0.1:7861")
        print("👤 Default Login: admin / admin123")
        print("⚠️ Change default password immediately!")
        print("=" * 60 + "\n")
        
        # Launch (localhost only, no sharing)
        admin_dashboard.launch(share=False)
        
    except Exception as e:
        logger.error(f"Failed to start admin dashboard: {e}")
        raise


if __name__ == "__main__":
    main()