"""
Admin CLI utilities for managing the system via command line.
Run with:  python -m admin_dashboard.utils <command>
           OR: python admin_dashboard/utils.py <command>

Available commands:
  create-admin <username> <password>
  list-users
  block-user <user_id>
  unblock-user <user_id>
  stats
  export [--email user@example.com]
  delete-conversations <user_id> [<user_id> ...]
  delete-user <user_id> [<user_id> ...]
"""

import argparse
import csv
import logging
from datetime import datetime

from database import DatabaseRepository
from models import UserStatus

logger = logging.getLogger(__name__)


def _get_db() -> DatabaseRepository:
    return DatabaseRepository("data/chatbot.db")


# ── Commands ──────────────────────────────────────────────────────────────────

def create_admin(username: str, password: str):
    db = _get_db()
    if db.create_admin(username, password):
        print(f"✅ Admin user '{username}' created successfully!")
    else:
        print(f"❌ Admin user '{username}' already exists!")


def list_users():
    db    = _get_db()
    users = db.get_all_users(limit=1000)
    print("\n" + "=" * 80)
    print(f"Total Users: {len(users)}")
    print("=" * 80)
    for user in users:
        print(f"\nID: {user.user_id}")
        print(f"Email: {user.email}")
        print(f"Name: {user.full_name}")
        print(f"Status: {user.status.value}")
        print(f"Total Queries: {user.total_queries}")
        print(f"Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        print("-" * 80)


def block_user(user_id: int):
    db   = _get_db()
    user = db.get_user_by_id(user_id)
    if not user:
        print(f"❌ User with ID {user_id} not found!")
        return
    db.update_user_status(user_id, UserStatus.BLOCKED)
    print(f"✅ User {user.email} (ID: {user_id}) has been blocked!")


def unblock_user(user_id: int):
    db   = _get_db()
    user = db.get_user_by_id(user_id)
    if not user:
        print(f"❌ User with ID {user_id} not found!")
        return
    db.update_user_status(user_id, UserStatus.ACTIVE)
    print(f"✅ User {user.email} (ID: {user_id}) has been unblocked!")


def show_stats():
    db    = _get_db()
    stats = db.get_statistics()
    print("\n" + "=" * 60)
    print("📊 SYSTEM STATISTICS")
    print("=" * 60)
    print(f"\nUsers:")
    print(f"  - Total: {stats.get('total_users', 0)}")
    print(f"  - Active (7 days): {stats.get('active_users_7d', 0)}")
    print(f"\nConversations:")
    print(f"  - Total: {stats.get('total_conversations', 0)}")
    print(f"  - Today: {stats.get('conversations_today', 0)}")
    print(f"  - Avg Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms")
    print("=" * 60 + "\n")


def export_conversations(user_email: str = None):
    db = _get_db()
    if user_email:
        user = db.get_user_by_email(user_email)
        if not user:
            print(f"❌ User {user_email} not found!")
            return
        conversations = db.get_user_conversations(user.user_id, limit=10000)
        filename = f"conversations_{user.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        recent        = db.get_recent_conversations(limit=10000)
        conversations = [conv for conv, _ in recent]
        filename      = f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'User ID', 'Message', 'Response', 'Type', 'Timestamp', 'Response Time (ms)'])
        for conv in conversations:
            writer.writerow([
                conv.conversation_id, conv.user_id,
                conv.message, conv.response,
                conv.conversation_type,
                conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                conv.response_time_ms or 'N/A',
            ])
    print(f"✅ Exported {len(conversations)} conversations to {filename}")


def delete_conversations(user_ids: list):
    db = _get_db()
    total = 0
    for user_id in user_ids:
        user = db.get_user_by_id(user_id)
        if not user:
            print(f"⚠️  User ID {user_id} not found!")
            continue
        count  = db.delete_user_conversations(user_id)
        total += count
        print(f"✅ Deleted {count} conversations for user {user_id} ({user.email})")
    print(f"\n📊 Total conversations deleted: {total}")


def delete_users(user_ids: list):
    db = _get_db()
    print("\n⚠️  WARNING: This permanently deletes users and all their conversations!")
    confirm = input(f"Delete users {user_ids}? Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled.")
        return
    total = 0
    for user_id in user_ids:
        user = db.get_user_by_id(user_id)
        if not user:
            print(f"⚠️  User ID {user_id} not found!")
            continue
        if db.delete_user(user_id):
            total += 1
            print(f"✅ Deleted user {user_id} ({user.email})")
        else:
            print(f"❌ Failed to delete user {user_id}")
    print(f"\n📊 Total users deleted: {total}")


# ── CLI parser ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Admin CLI for Dnext Chatbot')
    sub    = parser.add_subparsers(dest='command', help='Available commands')

    p = sub.add_parser('create-admin', help='Create admin user')
    p.add_argument('username'); p.add_argument('password')

    sub.add_parser('list-users', help='List all users')

    p = sub.add_parser('block-user',   help='Block a user')
    p.add_argument('user_id', type=int)

    p = sub.add_parser('unblock-user', help='Unblock a user')
    p.add_argument('user_id', type=int)

    sub.add_parser('stats', help='Show system statistics')

    p = sub.add_parser('export', help='Export conversations to CSV')
    p.add_argument('--email', help='Filter by user email (optional)')

    p = sub.add_parser('delete-conversations', help='Delete conversations for users')
    p.add_argument('user_ids', nargs='+', type=int)

    p = sub.add_parser('delete-user', help='Delete users and their conversations')
    p.add_argument('user_ids', nargs='+', type=int)

    args = parser.parse_args()

    commands = {
        'create-admin':        lambda: create_admin(args.username, args.password),
        'list-users':          list_users,
        'block-user':          lambda: block_user(args.user_id),
        'unblock-user':        lambda: unblock_user(args.user_id),
        'stats':               show_stats,
        'export':              lambda: export_conversations(getattr(args, 'email', None)),
        'delete-conversations':lambda: delete_conversations(args.user_ids),
        'delete-user':         lambda: delete_users(args.user_ids),
    }

    if args.command in commands:
        commands[args.command]()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()