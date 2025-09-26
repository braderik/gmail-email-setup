# Automated Gmail Sender Guide

## Overview

The `automated_gmail_sender.py` script provides a streamlined way to send emails via Gmail API with minimal setup after the initial OAuth authorization. This guide will help you get it running.

## Quick Start

### Method 1: Using the Helper Script (Recommended)

```bash
python3 run_automated_sender.py
```

This script will:
- Check for all required files
- Show setup instructions if files are missing
- Run the automated sender if everything is ready

### Method 2: Direct Execution

```bash
python3 automated_gmail_sender.py
```

## Setup Requirements

The automated sender needs these files to work:

### Required Files

1. **`oauth_credentials.json`** - OAuth2 client credentials from Google Cloud Console
2. **`fantasypros_api_email.txt`** - Email content to send

### Optional Files

- **`token.json`** - Saved OAuth tokens (created automatically after first authentication)

## First-Time Setup

### Step 1: Create OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Credentials**
3. Click **Create Credentials > OAuth 2.0 Client ID**
4. Choose **Desktop Application**
5. Download the credentials file
6. Rename it to `oauth_credentials.json`

### Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** user type (for personal use)
3. Fill in required fields:
   - **App name:** `Personal Gmail Sender` (or your choice)
   - **User support email:** Your email address
   - **Developer contact:** Your email address
4. Add your Gmail address to **Test users**

### Step 3: Enable Gmail API

1. Go to **APIs & Services > Library**
2. Search for "Gmail API"
3. Click and **Enable** it

### Step 4: Create Email Content

```bash
cp fantasypros_api_email.txt.example fantasypros_api_email.txt
```

Edit the content with your details:
- Replace `[Your Name]` with your actual name
- Verify the API key is correct
- Customize the message as needed

## Running the Script

### First Run (One-time OAuth Setup)

```bash
python3 automated_gmail_sender.py
```

The script will:
1. Check for existing authentication tokens
2. If none found, start the OAuth flow
3. Display an authorization URL
4. Wait for you to complete the browser authorization
5. Save the tokens for future use
6. Send the email

**Expected Output:**
```
🤖 Automated Gmail Sender for FantasyPros API Request
============================================================
🔐 No valid credentials - one-time OAuth setup required

💡 This is a one-time setup. After completion, all future
   emails will be sent automatically without browser interaction!

🔐 Starting automated OAuth flow...
🌐 Started local server on http://localhost:8080

============================================================
🔑 AUTOMATED OAUTH SETUP REQUIRED
============================================================

⚠️  ONE-TIME SETUP NEEDED:
1. Open this URL in your browser:
   https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...

2. Complete the Google authorization
3. The page will redirect and show 'Authorization Successful!'
4. This script will automatically continue...
```

### Subsequent Runs (Fully Automated)

After the first setup, running the script again will:
1. Use saved tokens automatically
2. Send the email immediately
3. No browser interaction needed

**Expected Output:**
```
🤖 Automated Gmail Sender for FantasyPros API Request
============================================================
✅ Valid credentials found - ready for automated sending!

📧 FantasyPros Email Sender - Automated Mode
==================================================
✅ Using existing valid credentials
✅ Authenticated as: your-email@gmail.com

📤 Preparing email:
   📨 Subject: FantasyPros API Key Activation Request
   👥 Recipients: api@fantasypros.com, rodric@fantasypros.com

🚀 Sending email...

🎉 SUCCESS! Email sent successfully!
```

## Troubleshooting

### Missing Files Error

```
❌ ERROR: oauth_credentials.json not found!
```

**Solution:** Follow Step 1 in the setup guide above.

### Invalid Credentials Error

```
❌ Failed to refresh credentials: ...
```

**Solution:** Delete `token.json` and run the script again to re-authenticate.

### Browser Authorization Issues

**Problem:** The OAuth URL doesn't work or shows an error.

**Solutions:**
1. Make sure you've configured the OAuth consent screen
2. Add your email as a test user
3. Verify that Gmail API is enabled
4. Check that the redirect URI includes `http://localhost:8080`

### Permission Denied

```
❌ Failed to send email: Permission denied
```

**Solutions:**
1. Verify your Gmail API scopes include `gmail.send`
2. Make sure you completed the OAuth consent properly
3. Check that the authenticated account has permission to send emails

## Security Notes

⚠️ **Important:** Never commit these files to version control:
- `oauth_credentials.json` - Contains client secrets
- `token.json` - Contains access tokens
- `fantasypros_api_email.txt` - May contain personal information

The `.gitignore` file should exclude these files automatically.

## How It Works

1. **Authentication Check:** Script checks for existing valid tokens
2. **Token Refresh:** If tokens are expired but refreshable, they're automatically refreshed
3. **OAuth Flow:** If no valid tokens exist, launches one-time OAuth setup
4. **Email Sending:** Once authenticated, reads email content and sends to recipients
5. **Success Confirmation:** Displays confirmation with message details

## Files Created

After successful setup, you'll have:
- `oauth_credentials.json` - Your OAuth client credentials
- `token.json` - Saved authentication tokens (auto-created)
- `fantasypros_api_email.txt` - Your email content

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the console output for specific error messages
3. Verify all setup steps were completed correctly
4. Consider running `python3 run_automated_sender.py` for guided setup