#!/usr/bin/env python3
"""
Simple Email Sender - Uses existing token or provides setup instructions
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email_with_existing_token():
    """Send email using existing OAuth token"""

    # Check for existing token
    if not os.path.exists('token.json'):
        print("❌ No authentication token found!")
        print("\n🔧 SETUP REQUIRED:")
        print("   1. Run the OAuth setup script first to authenticate")
        print("   2. Or manually create token.json with valid OAuth credentials")
        return False

    try:
        # Load existing credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())

            # Save refreshed token
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ Token refreshed successfully")

        elif not creds or not creds.valid:
            print("❌ Invalid credentials in token.json")
            print("   Please run OAuth setup again to get fresh credentials")
            return False

        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Get user info
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile.get('emailAddress')
        print(f"✅ Authenticated as: {sender_email}")

        # Email details
        recipients = ['api@fantasypros.com', 'rodric@fantasypros.com']

        # Read email content
        if not os.path.exists('fantasypros_api_email.txt'):
            print("❌ Email content file not found: fantasypros_api_email.txt")
            return False

        with open('fantasypros_api_email.txt', 'r') as f:
            email_content = f.read()

        # Parse content
        lines = email_content.split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])

        print(f"\n📧 Email Details:")
        print(f"   Subject: {subject}")
        print(f"   Recipients: {', '.join(recipients)}")
        print(f"   From: {sender_email}")

        # Create message
        message = MIMEMultipart()
        message['from'] = sender_email
        message['to'] = ', '.join(recipients)
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Encode and send
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        email_message = {'raw': raw_message}

        print(f"\n🚀 Sending email to FantasyPros...")
        result = service.users().messages().send(userId='me', body=email_message).execute()

        print(f"\n🎉 EMAIL SENT SUCCESSFULLY!")
        print(f"📝 Message ID: {result['id']}")
        print(f"📧 Sent to: {', '.join(recipients)}")
        print(f"📨 Subject: {subject}")

        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Check internet connection")
        print("   2. Verify token.json is valid")
        print("   3. Run OAuth setup again if token is corrupted")
        return False

def show_manual_setup_instructions():
    """Show instructions for manual OAuth setup"""
    print("\n" + "="*60)
    print("🔧 MANUAL OAUTH SETUP INSTRUCTIONS")
    print("="*60)
    print("\nIf automated setup doesn't work, follow these steps:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/apis/credentials")

    print("\n2. Find your OAuth client and add redirect URIs:")
    print("   - http://localhost")
    print("   - http://localhost:8080")

    print("\n3. Generate authorization URL manually:")
    print("   Use oauth_credentials.json to create OAuth flow")

    print("\n4. Complete browser authorization")

    print("\n5. Save token.json with OAuth credentials")

    print("\n💡 Once token.json exists, this script will work automatically!")
    print("="*60)

if __name__ == '__main__':
    print("📧 Simple FantasyPros Email Sender")
    print("="*40)

    # Attempt to send email
    success = send_email_with_existing_token()

    if not success:
        show_manual_setup_instructions()

        print(f"\n📋 Current files status:")
        print(f"   oauth_credentials.json: {'✅ Found' if os.path.exists('oauth_credentials.json') else '❌ Missing'}")
        print(f"   token.json: {'✅ Found' if os.path.exists('token.json') else '❌ Missing'}")
        print(f"   fantasypros_api_email.txt: {'✅ Found' if os.path.exists('fantasypros_api_email.txt') else '❌ Missing'}")

    else:
        print(f"\n✅ Email system is working perfectly!")
        print(f"🔮 Future emails can be sent by just running this script.")