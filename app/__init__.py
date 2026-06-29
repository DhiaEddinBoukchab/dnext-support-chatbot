"""
app package - exposes ChatbotApp without importing the full UI stack eagerly.

Usage in main.py:
    from app import ChatbotApp
"""

__all__ = ["ChatbotApp"]


def __getattr__(name):
    if name == "ChatbotApp":
        from app.chatbot_app import ChatbotApp

        return ChatbotApp
    raise AttributeError(f"module 'app' has no attribute {name!r}")
