#!/usr/bin/env python3
"""
Check service account capabilities and attempt to send email
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def check_service_account():
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        
        print(f"Service Account Email: {credentials.service_account_email}")
        print(f"Project ID: {credentials.project_id}")
        
        # Try to build Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Test basic access
        profile = service.users().getProfile(userId='me').execute()
        print(f"Gmail access successful: {profile.get('emailAddress')}")
        
    except Exception as error:
        print(f"Error: {error}")
        print("\nNote: Service accounts need domain-wide delegation for Gmail access")
        print("Alternative: Use OAuth2 flow or configure domain delegation")

if __name__ == '__main__':
    check_service_account()