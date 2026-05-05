"""
CLI tool for managing API keys for MCP server
Run this script to generate, revoke, and list API keys
"""

import argparse
import sys
from auth import key_manager


def generate_key(args):
    """Generate a new API key"""
    key = key_manager.generate_key(
        colleague_name=args.name,
        expires_in_days=args.expires
    )
    
    print("\n" + "="*60)
    print("API Key Generated Successfully!")
    print("="*60)
    print(f"Colleague: {args.name}")
    print(f"API Key:   {key}")
    print("\nShare this key with your colleague. They will use it as:")
    print("  Authorization: Bearer " + key)
    print("\nExpiration:", f"{args.expires} days" if args.expires else "Never")
    print("="*60 + "\n")


def list_keys(args):
    """List all active API keys"""
    keys = key_manager.list_keys()
    
    if not keys:
        print("\nNo API keys found.\n")
        return
    
    print("\n" + "="*60)
    print("Active API Keys")
    print("="*60)
    
    for i, key_info in enumerate(keys, 1):
        print(f"\n{i}. {key_info['colleague']}")
        print(f"   Created: {key_info['created_at']}")
        print(f"   Expires: {key_info['expires_at'] or 'Never'}")
        print(f"   Last Used: {key_info['last_used'] or 'Never'}")
        print(f"   Usage Count: {key_info['usage_count']}")
        print(f"   Status: {'Active' if key_info['active'] else 'Revoked'}")
    
    print("\n" + "="*60 + "\n")


def revoke_key(args):
    """Revoke an API key"""
    key = args.key
    
    if key_manager.revoke_key(key):
        print(f"\nKey revoked successfully!\n")
    else:
        print(f"\nKey not found or already revoked.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Manage API keys for DNEXT MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a key for a colleague
  python manage_keys.py generate --name "john@example.com" --expires 30
  
  # List all keys
  python manage_keys.py list
  
  # Revoke a key
  python manage_keys.py revoke --key "dnext_xxxxx"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new API key")
    gen_parser.add_argument("--name", required=True, help="Colleague name or email")
    gen_parser.add_argument("--expires", type=int, default=None, 
                           help="Days until key expires (default: never)")
    gen_parser.set_defaults(func=generate_key)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.set_defaults(func=list_keys)
    
    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("--key", required=True, help="API key to revoke")
    revoke_parser.set_defaults(func=revoke_key)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
