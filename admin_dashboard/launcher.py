"""
Admin Dashboard Launcher.
Run with:  python -m admin_dashboard.launcher
           OR: python admin_dashboard/launcher.py
"""

import logging
from database import DatabaseRepository
from auth_service import AuthenticationService
from admin_dashboard.dashboard import AdminDashboard

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("🎛️  Starting Admin Dashboard")
    print("=" * 60)
    print("⚠️  SECURITY: This runs on localhost only!")
    print("=" * 60)

    try:
        db   = DatabaseRepository("data/chatbot.db")
        auth = AuthenticationService(db)
        admin = AdminDashboard(db, auth)

        print("\n" + "=" * 60)
        print("✅ Admin Dashboard Ready!")
        print("🌐 Access: http://127.0.0.1:7861")
        print("👤 Default Login: admin / admin123")
        print("⚠️  Change default password immediately!")
        print("=" * 60 + "\n")

        admin.launch(share=True)

    except Exception as e:
        logger.error(f"Failed to start admin dashboard: {e}")
        raise


if __name__ == "__main__":
    main()