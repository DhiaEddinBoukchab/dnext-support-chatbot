"""
Script to activate all users in the database (set status to 'active').
"""
from database import DatabaseRepository
from models import UserStatus

def activate_all_users():
    db = DatabaseRepository()
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET status = ?", (UserStatus.ACTIVE.value,))
            conn.commit()
        print("All users set to ACTIVE.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    activate_all_users()
