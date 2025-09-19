#!/usr/bin/env python3
"""
Gmail OAuth2 Email Sender
Sends emails using OAuth2 personal Gmail account
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate using OAuth2 and return Gmail service object"""
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('oauth_credentials.json'):
                print("ERROR: oauth_credentials.json not found!")
                print("Please follow the OAuth2 setup guide to create OAuth2 client credentials.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
            # Use local server for OAuth flow
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Get user's email address
    profile = service.users().getProfile(userId='me').execute()
    sender_email = profile.get('emailAddress')
    
    return service, sender_email

def create_message(sender, recipients, subject, body):
    """Create email message with multiple recipients"""
    message = MIMEMultipart()
    message['from'] = sender
    message['to'] = ', '.join(recipients)
    message['subject'] = subject
    
    # Add body
    message.attach(MIMEText(body, 'plain'))
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, user_id, message):
    """Send email via Gmail API"""
    try:
        result = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message sent successfully! Message ID: {result["id"]}')
        return result
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def main():
    # Recipients for FantasyPros API support
    recipients = ['api@fantasypros.com', 'rodric@fantasypros.com']
    
    # Read the email content
    try:
        with open('fantasypros_api_email.txt', 'r') as f:
            email_content = f.read()
        
        # Extract subject and body
        lines = email_content.split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])  # Skip subject and empty line
        
    except FileNotFoundError:
        print("ERROR: fantasypros_api_email.txt not found!")
        return
    
    # Authenticate Gmail
    result = authenticate_gmail()
    if not result:
        return
    
    service, sender_email = result
    print(f"Authenticated as: {sender_email}")
    
    # Create and send message
    message = create_message(
        sender=sender_email,
        recipients=recipients,
        subject=subject,
        body=body
    )
    
    print(f"Sending email to: {', '.join(recipients)}")
    send_email(service, 'me', message)

if __name__ == '__main__':
    main()