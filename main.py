"""
main.py — application entry point.
Replaces the old monolithic app.py.
Run with:  python main.py
"""

import logging

from config import Config
from database import DatabaseRepository
from auth_service import AuthenticationService
from app import ChatbotApp
from app.ui_styles import LAUNCH_CSS

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("🚀 Starting Customer AI Assistant")
    print("=" * 60)

    try:
        db   = DatabaseRepository("data/chatbot.db")
        auth = AuthenticationService(db)

        db.create_admin("admin", "admin123")
        logger.info("✅ Default admin created (username: admin, password: admin123)")
        logger.info("⚠️  IMPORTANT: Change the admin password in production!")

        app  = ChatbotApp(db, auth)
        demo = app.create_interface()

        print("\n" + "=" * 60)
        print("✅ Chatbot is ready!")
        print("📊 Admin dashboard : run admin_launcher.py")
        print("🔍 LangSmith tracing enabled")
        print("⚡ Session-grouped sidebar")
        print("🧠 Full conversation memory per session")
        print("📎 Multi-file upload support")
        print("=" * 60)

        demo.launch(
            share=True,
            server_name=Config.SERVER_NAME,
            server_port=Config.SERVER_PORT,
            show_error=True,
            css=LAUNCH_CSS,
        )

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()