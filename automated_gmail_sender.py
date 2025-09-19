#!/usr/bin/env python3
"""
Automated Gmail Email Sender - No Browser Required
Uses saved OAuth tokens for automated email sending
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import http.server
import socketserver
import urllib.parse
import threading
import time

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback"""
    def __init__(self, *args, **kwargs):
        self.auth_code = None
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith('/?'):
            # Parse the authorization code from the callback
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if 'code' in params:
                self.auth_code = params['code'][0]
                print(f"✅ Received authorization code: {self.auth_code[:20]}...")

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html>
                    <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window. The email system is now authenticated.</p>
                    <script>setTimeout(function(){window.close();}, 3000);</script>
                    </body>
                    </html>
                ''')

                # Store the code globally
                global received_auth_code
                received_auth_code = self.auth_code
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No authorization code received</h1></body></html>')
        else:
            super().do_GET()

def start_local_server():
    """Start local server to receive OAuth callback"""
    PORT = 8080

    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        print(f"🌐 Started local server on http://localhost:{PORT}")
        httpd.serve_forever()

def authenticate_gmail_automated():
    """Automated Gmail authentication"""
    creds = None

    # Check for existing valid token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if creds and creds.valid:
            print("✅ Using existing valid credentials")
            return creds
        elif creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials")
            try:
                creds.refresh(Request())
                # Save refreshed credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("✅ Credentials refreshed successfully")
                return creds
            except Exception as e:
                print(f"❌ Failed to refresh credentials: {e}")
                creds = None

    # Need new authorization
    if not creds or not creds.valid:
        if not os.path.exists('oauth_credentials.json'):
            print("❌ ERROR: oauth_credentials.json not found!")
            return None

        print("🔐 Starting automated OAuth flow...")

        # Start local server in background
        global received_auth_code
        received_auth_code = None

        server_thread = threading.Thread(target=start_local_server, daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(1)

        # Create OAuth flow with localhost:8080 redirect
        flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
        flow.redirect_uri = 'http://localhost:8080'

        # Generate authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

        print(f"\n{'='*60}")
        print("🔑 AUTOMATED OAUTH SETUP REQUIRED")
        print(f"{'='*60}")
        print(f"\n⚠️  ONE-TIME SETUP NEEDED:")
        print(f"1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print(f"\n2. Complete the Google authorization")
        print(f"3. The page will redirect and show 'Authorization Successful!'")
        print(f"4. This script will automatically continue...")
        print(f"\n🤖 After this setup, future emails will send automatically!")
        print(f"{'='*60}\n")

        # Wait for authorization code
        timeout = 300  # 5 minutes
        start_time = time.time()

        while received_auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)

        if received_auth_code is None:
            print("❌ Timeout waiting for authorization")
            return None

        # Exchange code for credentials
        try:
            flow.fetch_token(code=received_auth_code)
            creds = flow.credentials

            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

            print("✅ OAuth setup completed! Credentials saved.")
            return creds

        except Exception as e:
            print(f"❌ Failed to exchange authorization code: {e}")
            return None

def send_fantasypros_email():
    """Send FantasyPros API key request email"""
    print("📧 FantasyPros Email Sender - Automated Mode")
    print("="*50)

    # Authenticate
    creds = authenticate_gmail_automated()
    if not creds:
        print("❌ Authentication failed")
        return False

    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Get user profile
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile.get('emailAddress')
        print(f"✅ Authenticated as: {sender_email}")

        # Recipients
        recipients = ['api@fantasypros.com', 'rodric@fantasypros.com']

        # Read email content
        if not os.path.exists('fantasypros_api_email.txt'):
            print("❌ Email content file not found: fantasypros_api_email.txt")
            return False

        with open('fantasypros_api_email.txt', 'r') as f:
            email_content = f.read()

        # Parse email content
        lines = email_content.split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])

        print(f"\n📤 Preparing email:")
        print(f"   📨 Subject: {subject}")
        print(f"   👥 Recipients: {', '.join(recipients)}")

        # Create email message
        message = MIMEMultipart()
        message['from'] = sender_email
        message['to'] = ', '.join(recipients)
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        email_message = {'raw': raw_message}

        # Send email
        print(f"\n🚀 Sending email...")
        result = service.users().messages().send(userId='me', body=email_message).execute()

        print(f"\n🎉 SUCCESS! Email sent successfully!")
        print(f"📧 Recipients: {', '.join(recipients)}")
        print(f"📝 Message ID: {result['id']}")
        print(f"📨 Subject: {subject}")
        print(f"\n✅ FantasyPros API key activation request has been sent!")

        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def check_credentials_status():
    """Check if we already have valid credentials"""
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.valid:
                print("✅ Valid credentials found - ready for automated sending!")
                return True
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Credentials exist but expired - will auto-refresh")
                return True
        except Exception as e:
            print(f"⚠️  Credentials file exists but invalid: {e}")

    print("🔐 No valid credentials - one-time OAuth setup required")
    return False

if __name__ == '__main__':
    print("🤖 Automated Gmail Sender for FantasyPros API Request")
    print("="*60)

    # Check credential status
    has_creds = check_credentials_status()

    if not has_creds:
        print("\n💡 This is a one-time setup. After completion, all future")
        print("   emails will be sent automatically without browser interaction!")

    # Send email
    success = send_fantasypros_email()

    if success:
        print(f"\n🎯 Next steps:")
        print(f"   1. FantasyPros will receive your API key activation request")
        print(f"   2. They should respond with activation confirmation")
        print(f"   3. Test your API key: N6mAz6LiGQ2DerrVMLDlw5sxTQoG32P73CWkDwZ7")
        print(f"\n🔮 Future use: Just run this script - no browser needed!")
    else:
        print(f"\n❌ Email sending failed. Check the error messages above.")