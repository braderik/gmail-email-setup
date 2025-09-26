#!/usr/bin/env python3
"""
Automated Gmail Email Sender - WORKING VERSION with OAuth Fix
Fixed redirect URI mismatch with multiple port fallbacks and better error handling
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
from googleapiclient.errors import HttpError
import http.server
import socketserver
import urllib.parse
import threading
import time
import webbrowser

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Multiple ports to try for OAuth callback (fixes redirect_uri_mismatch)
OAUTH_PORTS = [8080, 8081, 8082, 9090]

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback"""
    def __init__(self, *args, **kwargs):
        self.auth_code = None
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

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
                success_html = '''
                    <html>
                    <head><title>OAuth Authorization Successful</title></head>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">✅ Authorization Successful!</h1>
                    <p>Your Gmail email system is now authenticated and ready to use.</p>
                    <p><strong>You can safely close this browser window.</strong></p>
                    <p style="font-size: 14px; color: gray;">This window will automatically close in 5 seconds...</p>
                    <script>setTimeout(function(){window.close();}, 5000);</script>
                    </body>
                    </html>
                '''
                self.wfile.write(success_html.encode('utf-8'))

                # Store the code globally
                global received_auth_code
                received_auth_code = self.auth_code
            elif 'error' in params:
                error = params['error'][0]
                print(f"❌ OAuth error: {error}")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = f'''
                    <html>
                    <head><title>OAuth Authorization Error</title></head>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Authorization Error</h1>
                    <p>Error: {error}</p>
                    <p>Please try the authorization process again.</p>
                    </body>
                    </html>
                '''
                self.wfile.write(error_html.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = '''
                    <html>
                    <head><title>OAuth Authorization Error</title></head>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Error</h1>
                    <p>No authorization code received.</p>
                    <p>Please try the authorization process again.</p>
                    </body>
                    </html>
                '''
                self.wfile.write(error_html.encode('utf-8'))
        else:
            # Handle other requests (like favicon)
            self.send_response(404)
            self.end_headers()

def start_local_server(port):
    """Start local server to receive OAuth callback on specific port"""
    try:
        with socketserver.TCPServer(("", port), OAuthHandler) as httpd:
            print(f"🌐 OAuth server started successfully on http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"⚠️  Port {port} is already in use")
            return False
        else:
            print(f"❌ Failed to start server on port {port}: {e}")
            return False
    except Exception as e:
        print(f"❌ Server error on port {port}: {e}")
        return False

def find_available_port():
    """Find an available port from our list of OAuth ports"""
    for port in OAUTH_PORTS:
        try:
            with socketserver.TCPServer(("", port), None) as test_server:
                print(f"✅ Port {port} is available")
                return port
        except OSError:
            print(f"⚠️  Port {port} is already in use, trying next...")
            continue
    
    print("❌ No available ports found from the OAuth port list")
    return None

def show_redirect_uri_instructions(port):
    """Show instructions for fixing redirect URI mismatch"""
    print(f"\n{'🔧 REDIRECT URI SETUP INSTRUCTIONS'}")
    print(f"{'='*60}")
    print(f"\n⚠️  If you get 'Error 400: redirect_uri_mismatch', follow these steps:")
    print(f"\n1. 🌐 Go to Google Cloud Console:")
    print(f"   https://console.cloud.google.com/apis/credentials")
    print(f"\n2. 🔍 Find your OAuth 2.0 Client ID")
    print(f"\n3. ✏️  Click 'Edit' on your OAuth client")
    print(f"\n4. ➕ Under 'Authorized redirect URIs', click '+ ADD URI'")
    print(f"\n5. 📝 Add exactly: http://localhost:{port}")
    print(f"   (Include 'http://' - this is required!)")
    print(f"\n6. 💾 Click 'SAVE'")
    print(f"\n7. 🔄 Wait 1-2 minutes for changes to propagate")
    print(f"\n8. 🔁 Re-run this script")
    print(f"\n💡 TIP: Add all these URIs to avoid future issues:")
    for p in OAUTH_PORTS:
        print(f"   • http://localhost:{p}")
    print(f"\n{'='*60}")

def authenticate_gmail_automated():
    """Automated Gmail authentication with improved error handling"""
    creds = None

    # Check for existing valid token
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            if creds and creds.valid:
                print("✅ Using existing valid credentials")
                return creds
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                    print("✅ Credentials refreshed successfully")
                    return creds
                except Exception as e:
                    print(f"❌ Failed to refresh credentials: {e}")
                    print("🔄 Will attempt new OAuth flow...")
                    creds = None
        except Exception as e:
            print(f"⚠️  Error loading existing credentials: {e}")
            print("🔄 Will attempt new OAuth flow...")
            creds = None

    # Need new authorization
    if not creds or not creds.valid:
        if not os.path.exists('oauth_credentials.json'):
            print("❌ ERROR: oauth_credentials.json not found!")
            print("\n📋 Required file missing:")
            print("   • oauth_credentials.json - Download from Google Cloud Console")
            print("\n🔗 Get it here: https://console.cloud.google.com/apis/credentials")
            return None

        print("🔐 Starting OAuth flow with improved error handling...")

        # Find available port
        port = find_available_port()
        if not port:
            print("❌ Cannot find an available port for OAuth callback")
            print("\n🛠️  Manual solution:")
            print("   1. Check what's using ports 8080-8082, 9090")
            print("   2. Stop those services temporarily")
            print("   3. Re-run this script")
            return None

        # Setup global variables
        global received_auth_code
        received_auth_code = None

        # Start local server in background
        server_thread = threading.Thread(target=start_local_server, args=(port,), daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(2)

        try:
            # Create OAuth flow with dynamic redirect URI
            flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
            flow.redirect_uri = f'http://localhost:{port}'

            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                prompt='consent', 
                access_type='offline',
                include_granted_scopes='true'
            )

            print(f"\n{'='*60}")
            print("🔑 OAUTH SETUP REQUIRED")
            print(f"{'='*60}")
            print(f"\n🌐 OAuth server running on port {port}")
            print(f"\n⚠️  ONE-TIME SETUP NEEDED:")
            print(f"1. 🌍 Opening browser automatically...")
            print(f"   If it doesn't open, copy this URL:")
            print(f"   {auth_url}")
            print(f"\n2. 🔐 Complete the Google authorization")
            print(f"3. ✅ Page will show 'Authorization Successful!'")
            print(f"4. 🤖 This script will automatically continue...")
            print(f"\n💡 After this setup, future emails will send automatically!")
            print(f"{'='*60}\n")

            # Try to open browser automatically
            try:
                webbrowser.open(auth_url)
                print("🌍 Browser opened automatically")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print("📋 Please copy and paste the URL above into your browser")

            # Wait for authorization code with progress indicator
            timeout = 300  # 5 minutes
            start_time = time.time()
            dots = 0

            print("\n⏳ Waiting for authorization", end="", flush=True)
            
            while received_auth_code is None and (time.time() - start_time) < timeout:
                time.sleep(1)
                dots = (dots + 1) % 4
                print(f"\r⏳ Waiting for authorization{'.' * dots}{' ' * (3-dots)}", end="", flush=True)

            print()  # New line after progress indicator

            if received_auth_code is None:
                print("❌ Timeout waiting for authorization (5 minutes)")
                show_redirect_uri_instructions(port)
                return None

            # Exchange code for credentials
            print("🔄 Exchanging authorization code for access token...")
            try:
                flow.fetch_token(code=received_auth_code)
                creds = flow.credentials

                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

                print("✅ OAuth setup completed! Credentials saved.")
                print("🎉 Future emails will now send automatically!")
                return creds

            except Exception as e:
                print(f"❌ Failed to exchange authorization code: {e}")
                
                # Check for specific redirect URI error
                if "redirect_uri_mismatch" in str(e).lower():
                    print("\n🔍 DETECTED: redirect_uri_mismatch error")
                    show_redirect_uri_instructions(port)
                
                return None

        except FileNotFoundError:
            print("❌ oauth_credentials.json file not found!")
            print("📥 Download it from Google Cloud Console > APIs & Services > Credentials")
            return None
        except Exception as e:
            print(f"❌ OAuth flow error: {e}")
            
            # Check for specific redirect URI error
            if "redirect_uri_mismatch" in str(e).lower():
                print("\n🔍 DETECTED: redirect_uri_mismatch error")
                show_redirect_uri_instructions(port)
            
            return None

def send_fantasypros_email():
    """Send FantasyPros API key request email"""
    print("📧 FantasyPros Email Sender - WORKING VERSION")
    print("="*50)

    # Authenticate
    creds = authenticate_gmail_automated()
    if not creds:
        print("❌ Authentication failed - cannot send email")
        print("\n🛠️  Troubleshooting steps:")
        print("   1. Check oauth_credentials.json exists")
        print("   2. Verify redirect URIs in Google Cloud Console")
        print("   3. Make sure no firewall blocks localhost ports")
        return False

    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Get user profile
        print("🔍 Getting user profile...")
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile.get('emailAddress')
        print(f"✅ Authenticated as: {sender_email}")

        # Recipients
        recipients = ['api@fantasypros.com', 'rodric@fantasypros.com']

        # Read email content
        if not os.path.exists('fantasypros_api_email.txt'):
            print("❌ Email content file not found: fantasypros_api_email.txt")
            print("\n📝 Please create this file with your email content")
            return False

        print("📖 Reading email content...")
        with open('fantasypros_api_email.txt', 'r') as f:
            email_content = f.read()

        # Parse email content
        lines = email_content.split('\n')
        if not lines:
            print("❌ Email content file is empty")
            return False
            
        subject = lines[0].replace('Subject: ', '') if lines[0].startswith('Subject: ') else 'FantasyPros API Key Request'
        body = '\n'.join(lines[2:]) if len(lines) > 2 else '\n'.join(lines[1:])

        print(f"\n📤 Preparing email:")
        print(f"   📨 Subject: {subject}")
        print(f"   👥 Recipients: {', '.join(recipients)}")
        print(f"   📝 Body length: {len(body)} characters")

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
        print(f"👤 Sent from: {sender_email}")
        print(f"\n✅ FantasyPros API key activation request has been sent!")

        return True

    except HttpError as e:
        print(f"❌ Gmail API error: {e}")
        if e.resp.status == 403:
            print("🔒 Permission denied - check Gmail API is enabled")
        elif e.resp.status == 401:
            print("🔑 Authentication failed - token may be invalid")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Check internet connection")
        print("   2. Verify Gmail API is enabled in Google Cloud Console")
        print("   3. Ensure token.json is valid")
        print("   4. Try deleting token.json and re-authenticating")
        return False

def check_credentials_status():
    """Check if we already have valid credentials"""
    print("🔍 Checking credential status...")
    
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.valid:
                print("✅ Valid credentials found - ready for automated sending!")
                return True
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Credentials exist but expired - will auto-refresh")
                return True
            else:
                print("⚠️  Credentials exist but are invalid")
                return False
        except Exception as e:
            print(f"⚠️  Credentials file exists but corrupted: {e}")
            return False

    print("🔐 No valid credentials - one-time OAuth setup required")
    return False

def show_manual_fallback_instructions():
    """Show manual OAuth instructions if automated flow fails"""
    print(f"\n{'🛠️  MANUAL OAUTH FALLBACK'}")
    print(f"{'='*60}")
    print(f"\nIf the automated OAuth flow fails, try these manual steps:")
    print(f"\n1. 🌐 Go to Google Cloud Console:")
    print(f"   https://console.cloud.google.com/apis/credentials")
    print(f"\n2. 🔍 Create new OAuth 2.0 Client ID:")
    print(f"   • Application type: Desktop application")
    print(f"   • Name: Gmail Email Sender")
    print(f"\n3. 📥 Download the JSON file as 'oauth_credentials.json'")
    print(f"\n4. 🔄 Re-run this script")
    print(f"\n5. ✅ The desktop app type doesn't require redirect URIs!")
    print(f"\n{'='*60}")

if __name__ == '__main__':
    print("🤖 Automated Gmail Sender for FantasyPros API Request - WORKING VERSION")
    print("="*70)
    print("🛠️  This version includes OAuth redirect URI mismatch fixes")
    print("="*70)

    # Check prerequisite files
    print("\n📋 Checking prerequisite files...")
    missing_files = []
    
    if not os.path.exists('oauth_credentials.json'):
        missing_files.append('oauth_credentials.json')
    
    if not os.path.exists('fantasypros_api_email.txt'):
        missing_files.append('fantasypros_api_email.txt')
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print(f"\n📥 Please ensure these files exist before running:")
        for file in missing_files:
            print(f"   • {file}")
        if 'oauth_credentials.json' in missing_files:
            print(f"\n🔗 Get oauth_credentials.json from:")
            print(f"   https://console.cloud.google.com/apis/credentials")
        exit(1)
    else:
        print("✅ All prerequisite files found")

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
        print(f"   3. Test your API key when you receive it")
        print(f"\n🔮 Future use: Just run this script - no browser needed!")
    else:
        print(f"\n❌ Email sending failed. Check the error messages above.")
        show_manual_fallback_instructions()
        print(f"\n🆘 Need help? Check the fix_oauth_redirect_instructions.md file")