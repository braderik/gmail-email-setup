# OAuth Redirect URI Mismatch - Fix Instructions

## 🚨 PROBLEM DESCRIPTION
The `automated_gmail_sender.py` script fails with **Error 400: redirect_uri_mismatch** because:
- Your code uses `http://localhost:8080` as the redirect URI
- Your Google Cloud Console OAuth client doesn't have this URI in its authorized list

## ✅ QUICK FIX - Option 1: Add Redirect URIs (Recommended)

### Step 1: Access Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Make sure you're in the correct project
3. Navigate to **APIs & Services** → **Credentials**

### Step 2: Find Your OAuth Client
1. Look for your OAuth 2.0 Client ID
2. It might be named something like: `Web client 1` or have an ID like `147969369327-r81lgbd42o188cno7lj22845kmprvv6b`
3. Click the **pencil icon** (Edit) next to it

### Step 3: Add Redirect URIs
1. Scroll down to **Authorized redirect URIs**
2. Click **+ ADD URI**
3. Add these URIs exactly (one at a time):
   ```
   http://localhost:8080
   http://localhost:8081
   http://localhost:8082
   http://localhost:9090
   ```
   
   ⚠️ **IMPORTANT**: 
   - Include `http://` - this is required!
   - Use `localhost`, not `127.0.0.1`
   - No trailing slashes

### Step 4: Save Changes
1. Click **SAVE** at the bottom
2. Wait **1-2 minutes** for changes to propagate
3. Return to your terminal and complete the OAuth authorization

## 🔄 ALTERNATIVE FIX - Option 2: Desktop Application

### Step 1: Create New OAuth Client
1. In Google Cloud Console → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth 2.0 Client ID**
3. Choose **Application type**: **Desktop application**
4. Name it: `Gmail Email Sender`
5. Click **CREATE**

### Step 2: Download and Replace
1. Click **DOWNLOAD** to get the JSON file
2. Rename it to `oauth_credentials.json`
3. Replace your existing `oauth_credentials.json`
4. Restart the script

**Advantage**: Desktop applications don't need redirect URIs!

## ⚡ TROUBLESHOOTING

### If you still get redirect_uri_mismatch:
1. **Double-check the URIs**: Make sure they're exactly `http://localhost:8080` (with http://)
2. **Wait longer**: Changes can take up to 5 minutes to propagate
3. **Clear browser cache**: Or try an incognito window
4. **Check project**: Ensure you're editing the OAuth client in the correct Google Cloud project

### If ports are busy:
The working script tries multiple ports automatically:
- 8080 (primary)
- 8081 (fallback)
- 8082 (fallback)
- 9090 (fallback)

### Common mistakes:
❌ `localhost:8080` (missing protocol)
❌ `https://localhost:8080` (wrong protocol)
❌ `http://127.0.0.1:8080` (IP instead of localhost)
❌ `http://localhost:8080/` (trailing slash)

✅ `http://localhost:8080` (correct)

## 🛡️ SECURITY CONSIDERATIONS

These redirect URIs are safe because:
- They only work on `localhost` (your computer)
- They're only used during the OAuth flow
- No external access is possible
- The authorization code is only valid once

## 🔍 VERIFICATION STEPS

After making changes:
1. Run `automated_gmail_sender_working.py`
2. Check that it says: `🌐 OAuth server started successfully on http://localhost:XXXX`
3. The browser should open automatically
4. Complete Google authorization
5. You should see: `✅ Authorization Successful!`

## 📞 STILL NEED HELP?

If you're still having issues:

1. **Check Google Cloud Console errors**: Look for any red error messages
2. **Verify Gmail API is enabled**: APIs & Services → Library → Gmail API → Enable
3. **Try the desktop application approach**: Often simpler and more reliable
4. **Use manual fallback**: Copy/paste the authorization URL if browser doesn't open

## 🚀 SUCCESS INDICATORS

You know it's working when you see:
```
✅ OAuth setup completed! Credentials saved.
🎉 Future emails will now send automatically!
```

After this one-time setup, your `token.json` file will be created and future email sending will be completely automated!