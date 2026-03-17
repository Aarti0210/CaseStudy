#!/usr/bin/env python3
"""
Environment Manager CLI
Interactive command-line tool for managing environment variables
"""

import os
import secrets
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.env_manager import EnvManager

def show_current_env():
    """Show current environment configuration"""
    print("🔍 Current Environment Configuration")
    print("=" * 40)
    EnvManager.print_all_configs()

def set_variable(name: str, value: str = None):
    """Set environment variable"""
    if value is None:
        # Generate value for certain variables
        if name in ['SECRET_KEY', 'JWT_SECRET_KEY']:
            value = secrets.token_urlsafe(32)
            print(f"🔑 Generated secure {name}")
        else:
            print("❌ Value required for this variable")
            return False
    
    # Set environment variable
    os.environ[name] = value
    print(f"✅ Set {name} = {value[:20]}{'...' if len(value) > 20 else ''}")
    
    return True

def add_variable(name: str, value: str):
    """Add variable to .env file"""
    env_file = '.env'
    
    # Read existing .env
    existing_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            existing_lines = f.readlines()
    
    # Check if variable already exists
    var_line = f"{name}={value}\n"
    updated = False
    
    for i, line in enumerate(existing_lines):
        if line.startswith(f"{name}="):
            existing_lines[i] = var_line
            updated = True
            break
    
    if not updated:
        existing_lines.append(var_line)
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.writelines(existing_lines)
    
    print(f"✅ Added to .env: {name}={value[:20]}{'...' if len(value) > 20 else ''}")

def list_variables():
    """List all environment variables"""
    print("📋 Environment Variables")
    print("=" * 25)
    
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    print(f"  {key}: {value[:30]}{'...' if len(value) > 30 else ''}")
    else:
        print("⚠️  .env file not found")

def generate_all_secrets():
    """Generate all required secrets"""
    print("🔑 Generating Security Keys")
    print("=" * 30)
    
    secrets_dict = {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'JWT_SECRET_KEY': secrets.token_urlsafe(32),
        'FLASK_SECRET_KEY': secrets.token_hex(32),  # Alternative
    }
    
    for name, value in secrets_dict.items():
        print(f"{name}: {value}")
    
    # Add to .env
    for name, value in secrets_dict.items():
        add_variable(name, value)
    
    print("\n✅ All security keys generated and added to .env")

def validate_environment():
    """Validate current environment"""
    print("🔍 Validating Environment")
    print("=" * 30)
    
    try:
        required = EnvManager.validate_required()
        missing = [key for key, exists in required.items() if not exists]
        
        if missing:
            print("❌ Missing required variables:")
            for var in missing:
                print(f"  - {var}")
        else:
            print("✅ All required variables are set")
        
        # Check security
        security = EnvManager.get_security_config()
        if len(security['secret_key']) < 32:
            print("⚠️  SECRET_KEY is too short (< 32 characters)")
        if len(security['jwt_secret_key']) < 32:
            print("⚠️  JWT_SECRET_KEY is too short (< 32 characters)")
        
        # Check database
        db_config = EnvManager.get_database_config()
        if not db_config['url']:
            print("⚠️  DATABASE_URL is not set")
        else:
            print("✅ Database URL is configured")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Environment Manager CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current environment')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set environment variable')
    set_parser.add_argument('name', help='Variable name')
    set_parser.add_argument('--value', help='Variable value')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add variable to .env')
    add_parser.add_argument('name', help='Variable name')
    add_parser.add_argument('value', help='Variable value')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all environment variables')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate security keys')
    gen_parser.add_argument('--all', action='store_true', help='Generate all required secrets')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate environment')
    
    args = parser.parse_args()
    
    if args.command == 'show':
        show_current_env()
    elif args.command == 'set':
        set_variable(args.name, args.value)
    elif args.command == 'add':
        add_variable(args.name, args.value)
    elif args.command == 'list':
        list_variables()
    elif args.command == 'generate':
        if args.all:
            generate_all_secrets()
        else:
            print("Use --all to generate all required secrets")
    elif args.command == 'validate':
        validate_environment()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
