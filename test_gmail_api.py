#!/usr/bin/env python3
"""
Test Gmail API access with service account
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def test_gmail_api():
    """Test Gmail API access"""
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)

        # Build Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        # Try to get user profile
        try:
            profile = service.users().getProfile(userId='me').execute()
            print(f"Successfully accessed Gmail API!")
            print(f"Email: {profile.get('emailAddress')}")
            print(f"Messages total: {profile.get('messagesTotal')}")
            print(f"Threads total: {profile.get('threadsTotal')}")
            return True
        except Exception as e:
            print(f"Failed to access Gmail profile: {e}")

            # Try to list labels instead
            try:
                labels = service.users().labels().list(userId='me').execute()
                print(f"Successfully accessed Gmail labels API!")
                print(f"Found {len(labels.get('labels', []))} labels")
                return True
            except Exception as e2:
                print(f"Failed to access Gmail labels: {e2}")
                return False

    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return False

if __name__ == '__main__':
    test_gmail_api()