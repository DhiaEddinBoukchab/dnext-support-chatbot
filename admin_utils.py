"""
Admin utilities for managing the system via command line
"""

import argparse
from database import DatabaseRepository
from models import UserStatus


def create_admin(username: str, password: str):
    """Create a new admin user"""
    db = DatabaseRepository()
    admin_id = db.create_admin(username, password)
    
    if admin_id:
        print(f"✅ Admin user '{username}' created successfully!")
    else:
        print(f"❌ Admin user '{username}' already exists!")


def list_users():
    """List all users"""
    db = DatabaseRepository()
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
    """Block a user"""
    db = DatabaseRepository()
    user = db.get_user_by_id(user_id)
    
    if not user:
        print(f"❌ User with ID {user_id} not found!")
        return
    
    db.update_user_status(user_id, UserStatus.BLOCKED)
    print(f"✅ User {user.email} (ID: {user_id}) has been blocked!")


def unblock_user(user_id: int):
    """Unblock a user"""
    db = DatabaseRepository()
    user = db.get_user_by_id(user_id)
    
    if not user:
        print(f"❌ User with ID {user_id} not found!")
        return
    
    db.update_user_status(user_id, UserStatus.ACTIVE)
    print(f"✅ User {user.email} (ID: {user_id}) has been unblocked!")


def show_stats():
    """Show system statistics"""
    db = DatabaseRepository()
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
    """Export conversations to CSV"""
    import csv
    from datetime import datetime
    
    db = DatabaseRepository()
    
    if user_email:
        user = db.get_user_by_email(user_email)
        if not user:
            print(f"❌ User {user_email} not found!")
            return
        
        conversations = db.get_user_conversations(user.user_id, limit=10000)
        filename = f"conversations_{user.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        recent = db.get_recent_conversations(limit=10000)
        conversations = [conv for conv, _ in recent]
        filename = f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'User ID', 'Message', 'Response', 'Type', 'Timestamp', 'Response Time (ms)'])
        
        for conv in conversations:
            writer.writerow([
                conv.conversation_id,
                conv.user_id,
                conv.message,
                conv.response,
                conv.conversation_type,
                conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                conv.response_time_ms or 'N/A'
            ])
    
    print(f"✅ Exported {len(conversations)} conversations to {filename}")


def delete_conversations(user_ids: list):
    """Delete conversations for specified users"""
    db = DatabaseRepository()
    total_deleted = 0
    
    for user_id in user_ids:
        user = db.get_user_by_id(user_id)
        
        if not user:
            print(f"⚠️  User ID {user_id} not found!")
            continue
        
        deleted_count = db.delete_user_conversations(user_id)
        total_deleted += deleted_count
        print(f"✅ Deleted {deleted_count} conversations for user {user_id} ({user.email})")
    
    print(f"\n📊 Total conversations deleted: {total_deleted}")


def delete_users(user_ids: list):
    """Delete users and all their conversations"""
    db = DatabaseRepository()
    
    print("\n⚠️  WARNING: This will permanently delete users and all their conversations!")
    confirmation = input(f"Are you sure you want to delete users {user_ids}? Type 'yes' to confirm: ")
    
    if confirmation.lower() != 'yes':
        print("❌ Deletion cancelled.")
        return
    
    total_deleted = 0
    for user_id in user_ids:
        user = db.get_user_by_id(user_id)
        
        if not user:
            print(f"⚠️  User ID {user_id} not found!")
            continue
        
        success = db.delete_user(user_id)
        if success:
            total_deleted += 1
            print(f"✅ Deleted user {user_id} ({user.email}) and all their conversations")
        else:
            print(f"❌ Failed to delete user {user_id}")
    
    print(f"\n📊 Total users deleted: {total_deleted}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Admin utilities for Dnext Chatbot')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create admin
    create_admin_parser = subparsers.add_parser('create-admin', help='Create admin user')
    create_admin_parser.add_argument('username', help='Admin username')
    create_admin_parser.add_argument('password', help='Admin password')
    
    # List users
    subparsers.add_parser('list-users', help='List all users')
    
    # Block user
    block_parser = subparsers.add_parser('block-user', help='Block a user')
    block_parser.add_argument('user_id', type=int, help='User ID to block')
    
    # Unblock user
    unblock_parser = subparsers.add_parser('unblock-user', help='Unblock a user')
    unblock_parser.add_argument('user_id', type=int, help='User ID to unblock')
    
    # Show stats
    subparsers.add_parser('stats', help='Show system statistics')
    
    # Export conversations
    export_parser = subparsers.add_parser('export', help='Export conversations to CSV')
    export_parser.add_argument('--email', help='User email (optional, exports all if not provided)')
    
    # Delete conversations
    delete_parser = subparsers.add_parser('delete-conversations', help='Delete conversations for specified users')
    delete_parser.add_argument('user_ids', nargs='+', type=int, help='User IDs to delete conversations for')
    
    # Delete users
    delete_user_parser = subparsers.add_parser('delete-user', help='Delete users and all their conversations')
    delete_user_parser.add_argument('user_ids', nargs='+', type=int, help='User IDs to delete')
    
    args = parser.parse_args()
    
    if args.command == 'create-admin':
        create_admin(args.username, args.password)
    elif args.command == 'list-users':
        list_users()
    elif args.command == 'block-user':
        block_user(args.user_id)
    elif args.command == 'unblock-user':
        unblock_user(args.user_id)
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'export':
        export_conversations(args.email)
    elif args.command == 'delete-conversations':
        delete_conversations(args.user_ids)
    elif args.command == 'delete-user':
        delete_users(args.user_ids)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()