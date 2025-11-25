# Firebase Integration Setup Guide

## Overview
This bot now includes Firebase Realtime Database integration to store and manage chat history for all users.

## Features
- ✅ Automatic chat history logging for all user messages
- ✅ Each user has their own folder in the database
- ✅ View chat history with `/history` command
- ✅ Clear chat history with `/clear_history` command
- ✅ Track all commands and messages

## Firebase Setup Instructions

### 1. Firebase Project Setup
Your `google-services.json` file is already in the project directory. This file contains:
- Project ID: `allhack-c2c4b`
- API Key: `AIzaSyCS5EAOGwhKU_PdIDSw0ZOa4BKa2NtsBoU`
- Database URL: `https://allhack-c2c4b-default-rtdb.firebaseio.com`

### 2. Enable Firebase Realtime Database
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `allhack-c2c4b`
3. Click on "Realtime Database" in the left menu
4. Click "Create Database"
5. Choose a location (e.g., us-central1)
6. Start in **test mode** for development (you can secure it later)

### 3. Database Rules (Important!)
For the bot to work, you need to set proper database rules:

Go to the "Rules" tab in Firebase Realtime Database and use these rules:

```json
{
  "rules": {
    "users": {
      "$user_id": {
        ".read": true,
        ".write": true
      }
    }
  }
}
```

**For production**, use more secure rules:
```json
{
  "rules": {
    "users": {
      "$user_id": {
        ".read": "auth != null && auth.uid == $user_id",
        ".write": "auth != null && auth.uid == $user_id"
      }
    }
  }
}
```

### 4. Database Structure
The bot creates the following structure in Firebase:

```
users/
  ├── {user_id}/
  │   ├── info/
  │   │   ├── user_id: 123456789
  │   │   ├── username: "john_doe"
  │   │   └── last_seen: "2025-11-24T08:43:06"
  │   └── messages/
  │       ├── {timestamp_key}/
  │       │   ├── user_id: 123456789
  │       │   ├── username: "john_doe"
  │       │   ├── message: "/start"
  │       │   ├── command: "/start"
  │       │   └── timestamp: "2025-11-24T08:43:06"
  │       └── {timestamp_key}/
  │           └── ...
```

## Usage

### View Chat History
Users can view their chat history by sending:
```
/history
```

This will show:
- Total message count
- Last 20 messages
- Timestamp for each message
- Command used (if any)

### Clear Chat History
Users can delete their entire chat history:
```
/clear_history
```

### Disable Chat History
To disable chat history logging, edit `config.py`:
```python
ENABLE_CHAT_HISTORY = False
```

## Configuration

### config.py Settings
```python
# Firebase Configuration
FIREBASE_CONFIG_PATH = "google-services.json"
ENABLE_CHAT_HISTORY = True  # Set to False to disable chat history logging
```

## Troubleshooting

### Error: "Firebase initialization failed"
- Make sure `google-services.json` exists in the project directory
- Check that the file is valid JSON
- Verify your internet connection

### Error: "Permission denied"
- Check your Firebase Database Rules
- Make sure the database is created and active
- Verify the API key is correct

### Messages not saving
- Check Firebase Console to see if database is receiving data
- Look at bot logs for any error messages
- Verify `ENABLE_CHAT_HISTORY = True` in config.py

## Security Recommendations

1. **Use Environment Variables**: Store sensitive data in environment variables
2. **Secure Database Rules**: Use authentication for production
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Data Retention**: Set up automatic data deletion for old messages
5. **Encryption**: Consider encrypting sensitive message data

## API Limits

Firebase Realtime Database free tier includes:
- 1 GB stored data
- 10 GB/month downloaded data
- 100 simultaneous connections

For most Telegram bots, this should be sufficient.

## Support

If you encounter any issues:
1. Check the bot logs for error messages
2. Verify Firebase Console shows the database is active
3. Test with a simple `/start` command
4. Check that messages appear in Firebase Console

## Next Steps

1. ✅ Firebase is integrated
2. ✅ Chat history is being saved
3. ✅ Users can view their history
4. 🔄 Consider adding analytics
5. 🔄 Add admin commands to view all users
6. 🔄 Implement data export functionality
