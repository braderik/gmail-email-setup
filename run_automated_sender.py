#!/usr/bin/env python3
"""
Run Script for Automated Gmail Sender
Provides helpful setup guidance and runs the automated sender
"""

import os
import sys

def check_setup():
    """Check if all required files are present"""
    required_files = {
        'oauth_credentials.json': 'OAuth2 client credentials from Google Cloud Console',
        'fantasypros_api_email.txt': 'Email content to send to FantasyPros'
    }
    
    optional_files = {
        'token.json': 'Saved OAuth tokens (created after first authentication)'
    }
    
    print("🔍 Checking setup requirements...")
    print("=" * 50)
    
    missing_files = []
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing ({description})")
            missing_files.append(file)
    
    for file, description in optional_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"ℹ️  {file} - Not found ({description})")
    
    return missing_files

def show_setup_instructions():
    """Display setup instructions"""
    print("\n" + "=" * 60)
    print("🔧 SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\n1. Create OAuth2 Credentials:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Navigate to APIs & Services > Credentials")
    print("   - Create OAuth 2.0 Client ID (Desktop Application)")
    print("   - Download as 'oauth_credentials.json'")
    
    print("\n2. Create Email Content:")
    print("   - Copy fantasypros_api_email.txt.example to fantasypros_api_email.txt")
    print("   - Edit the content with your details")
    
    print("\n3. Configure OAuth Consent Screen:")
    print("   - Follow instructions in oauth_consent_setup.md")
    print("   - Add your email as a test user")
    
    print("\n4. Run the script again:")
    print("   python3 automated_gmail_sender.py")
    
    print("\n💡 After first-time setup, future runs will be automatic!")

def main():
    print("🚀 Automated Gmail Sender Setup & Runner")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('automated_gmail_sender.py'):
        print("❌ Error: automated_gmail_sender.py not found in current directory")
        print("   Please run this script from the gmail-email-setup directory")
        return 1
    
    # Check setup
    missing_files = check_setup()
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required file(s)")
        show_setup_instructions()
        
        # Show example files
        print(f"\n📋 Example files available:")
        for file in missing_files:
            example_file = f"{file}.example"
            if os.path.exists(example_file):
                print(f"   cp {example_file} {file}")
        
        return 1
    
    # All files present, run the automated sender
    print("\n✅ All required files present!")
    print("🚀 Running automated_gmail_sender.py...")
    print("=" * 50)
    
    # Import and run the automated sender
    try:
        os.system('python3 automated_gmail_sender.py')
    except KeyboardInterrupt:
        print("\n⏹️  Script interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running script: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())