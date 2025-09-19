#!/usr/bin/env python3
"""
Service Account Gmail Sender
Sends emails using service account credentials with domain-wide delegation
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail_service_account(user_email):
    """Authenticate using service account with domain-wide delegation"""
    if not os.path.exists('credentials.json'):
        print("ERROR: credentials.json not found!")
        return None
    
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        
        # Delegate to the user email for domain-wide delegation
        delegated_credentials = credentials.with_subject(user_email)
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=delegated_credentials)
        return service, user_email
        
    except Exception as error:
        print(f'Service account authentication error: {error}')
        print("Note: This requires domain-wide delegation to be configured")
        return None, None

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
    # Use the service account email as sender
    sender_email = 'claude-code-gmal@gen-lang-client-0867150174.iam.gserviceaccount.com'
    
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
    
    # Try to authenticate with service account
    result = authenticate_gmail_service_account(sender_email)
    if not result or result[0] is None:
        print("Service account authentication failed.")
        print("Falling back to direct service account email sending...")
        
        # Try direct service account approach
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES)
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create and send message
            message = create_message(
                sender=sender_email,
                recipients=recipients,
                subject=subject,
                body=body
            )
            
            print(f"Attempting to send email from: {sender_email}")
            print(f"To: {', '.join(recipients)}")
            send_email(service, 'me', message)
            
        except Exception as error:
            print(f"Direct service account sending failed: {error}")
            print("\nThis is expected - service accounts need additional configuration for Gmail.")
            print("The OAuth2 approach is recommended for personal Gmail accounts.")
        return
    
    service, sender_email = result
    print(f"Authenticated as service account: {sender_email}")
    
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