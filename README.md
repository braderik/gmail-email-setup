# Gmail Email Setup

A collection of Python scripts for sending emails via Gmail API using multiple authentication methods.

## Features

- **Multiple Authentication Methods:**
  - OAuth2 with automatic local server
  - OAuth2 with manual code input
  - Service Account with domain delegation
  - Simple wrapper for existing tokens

- **Secure Implementation:**
  - Proper OAuth2 flow following Google standards
  - Token persistence and automatic refresh
  - Gmail send-only permissions

## Files Overview

### Main Scripts

- `send_gmail_oauth.py` - OAuth2 with automatic local server flow
- `send_gmail_manual_oauth.py` - OAuth2 with manual authorization code input
- `send_email_service_account.py` - Service account authentication with domain delegation
- `simple_email_sender.py` - Wrapper that uses existing tokens

### Testing & Utilities

- `test_gmail_api.py` - Test Gmail API access
- `check_service_account.py` - Verify service account setup
- `automated_gmail_sender.py` - Additional automation utilities

### Documentation

- `gmail_setup_instructions.txt` - Step-by-step setup guide
- `oauth_consent_setup.md` - OAuth consent screen configuration

## Prerequisites

1. **Python Dependencies:**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Google Cloud Project Setup:**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Create OAuth2 credentials or Service Account (depending on method)

## Setup Instructions

### Method 1: OAuth2 (Recommended for Personal Use)

1. **Create OAuth2 Credentials:**
   - Go to Google Cloud Console > APIs & Services > Credentials
   - Create OAuth 2.0 Client ID for Desktop Application
   - Download credentials as `oauth_credentials.json`

2. **Configure OAuth Consent Screen:**
   - Follow instructions in `oauth_consent_setup.md`
   - Add your email as a test user

3. **Run Authentication:**
   ```bash
   python3 send_gmail_oauth.py
   ```

### Method 2: Service Account (For Domain Delegation)

1. **Create Service Account:**
   - Google Cloud Console > IAM > Service Accounts
   - Create new service account
   - Download key as `credentials.json`

2. **Configure Domain Delegation:**
   - Enable domain-wide delegation
   - Add Gmail API scopes in admin console

3. **Run with Service Account:**
   ```bash
   python3 send_email_service_account.py
   ```

## Security Notes

⚠️ **IMPORTANT:** Never commit credential files to version control!

The following files contain sensitive information and should never be uploaded:
- `credentials.json` - Service account private keys
- `oauth_credentials.json` - OAuth client secrets
- `token.json` - Access/refresh tokens
- `fantasypros_api_email.txt` - Email content

Use environment variables for production deployments.

## Usage Example

```python
from send_gmail_oauth import authenticate_gmail, create_message, send_email

# Authenticate
service, sender_email = authenticate_gmail()

# Create message
recipients = ['user@example.com']
message = create_message(sender_email, recipients, 'Subject', 'Body')

# Send email
send_email(service, 'me', message)
```

## Testing

Test your setup with:
```bash
python3 test_gmail_api.py
```

## Troubleshooting

1. **Authentication Errors:**
   - Verify OAuth consent screen is configured
   - Check that test users are added
   - Ensure proper scopes are enabled

2. **Permission Denied:**
   - Verify Gmail API is enabled
   - Check service account domain delegation
   - Confirm proper IAM permissions

3. **Token Issues:**
   - Delete `token.json` and re-authenticate
   - Check token expiration and refresh logic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.