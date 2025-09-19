#!/usr/bin/env python3
"""
Gmail API Email Sender
Sends the FantasyPros API support email
"""

import os
import base64
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate using service account and return Gmail service object"""
    if not os.path.exists('credentials.json'):
        print("ERROR: credentials.json not found!")
        print("Please place the service account credentials file in this directory.")
        return None
    
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        
        # The service account email will be used as the sender
        service = build('gmail', 'v1', credentials=credentials)
        return service, credentials.service_account_email
        
    except Exception as error:
        print(f'Authentication error: {error}')
        return None, None

def create_message(sender, to, subject, body):
    """Create email message"""
    message = MIMEText(body)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, user_id, message):
    """Send email via Gmail API"""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message sent successfully! Message ID: {message["id"]}')
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def main():
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
    print(f"Using service account: {sender_email}")
    
    # Create and send message
    message = create_message(
        sender=sender_email,
        to='api@fantasypros.com',
        subject=subject,
        body=body
    )
    
    print("Sending email to api@fantasypros.com...")
    send_email(service, 'me', message)

if __name__ == '__main__':
    main()