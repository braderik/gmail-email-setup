# OAuth Consent Screen Setup

## For Testing/Personal Use (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **OAuth consent screen**
3. Choose **External** user type
4. Fill in required fields:

### Required Fields:
- **App name:** `Personal Gmail Sender`
- **User support email:** Your email address
- **Developer contact information:** Your email address

### Optional Fields (leave blank for testing):
- Application home page: (leave empty)
- Application privacy policy link: (leave empty) 
- Application terms of service link: (leave empty)
- Authorized domains: (leave empty)

### Test Users Section:
- Add your Gmail address to **Test users**
- This allows you to use the app while it's in "Testing" mode

## Why This Works:
- Apps in "Testing" mode don't require domain verification
- Only test users (you) can authorize the app
- No public URLs needed for personal use
- Gmail API access will work immediately

## After Setup:
The OAuth URL will work and you can complete the email sending process.

## Note:
If you plan to distribute this publicly later, you'll need proper domain verification and privacy policy URLs.