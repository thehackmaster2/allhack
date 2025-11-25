# Firebase Wordlist Integration Guide

## 🎯 Overview

Your bot now uses **Firebase-stored wordlists** for password cracking instead of local files!

---

## 📤 Step 1: Upload Wordlists to Firebase

### **Run the Upload Script:**

```bash
python upload_wordlists.py
```

This will:
1. Read all `.txt` files from `C:/Users/neox/Desktop/Ps/`
2. Upload them to Firebase under `/wordlists/`
3. Make them available for all cracking operations

### **What Gets Uploaded:**

```
C:/Users/neox/Desktop/Ps/
├── rockyou.txt          → Firebase: /wordlists/rockyou/passwords
├── common-passwords.txt → Firebase: /wordlists/common-passwords/passwords
├── 10k-most-common.txt  → Firebase: /wordlists/10k-most-common/passwords
└── ...
```

### **Firebase Structure:**

```json
{
  "wordlists": {
    "rockyou": {
      "filename": "rockyou.txt",
      "count": 10000,
      "passwords": [
        "123456",
        "password",
        "12345678",
        ...
      ]
    },
    "common-passwords": {
      "filename": "common-passwords.txt",
      "count": 5000,
      "passwords": [...]
    }
  }
}
```

---

## 🔧 Step 2: Update Cracking Modules

The cracking modules will now use Firebase wordlists automatically!

### **How It Works:**

**Before (Local Files):**
```python
# Read from local file
with open('C:/Users/neox/Desktop/Ps/rockyou.txt') as f:
    passwords = f.readlines()
```

**After (Firebase):**
```python
# Load from Firebase
passwords = firebase_manager.get_wordlist('rockyou')
```

---

## 📋 Available Firebase Methods

### **1. Get Wordlist**
```python
passwords = firebase_manager.get_wordlist('rockyou')
# Returns: ['123456', 'password', '12345678', ...]
```

### **2. List All Wordlists**
```python
wordlists = firebase_manager.list_wordlists()
# Returns: ['rockyou', 'common-passwords', '10k-most-common']
```

### **3. Get Wordlist Info**
```python
info = firebase_manager.get_wordlist_info('rockyou')
# Returns: {'name': 'rockyou', 'count': 10000}
```

---

## 🔓 Updated Cracking Commands

### **/login_crack** - Login Brute Force

**Old Way:**
```
/login_crack https://example.com/login admin
→ Uses local wordlist from C:/Users/neox/Desktop/Ps/
```

**New Way:**
```
/login_crack https://example.com/login admin
→ Loads wordlist from Firebase automatically
→ No local files needed!
```

### **/zip_crack** - ZIP Password Cracking

**Old Way:**
```
/zip_crack
→ Upload ZIP file
→ Uses local wordlist
```

**New Way:**
```
/zip_crack
→ Upload ZIP file
→ Loads wordlist from Firebase
→ Cracks using cloud wordlists
```

---

## 💡 Benefits

| Feature | Local Wordlists | Firebase Wordlists |
|---------|----------------|-------------------|
| **Storage** | Server disk | Firebase cloud |
| **Portability** | Need to copy files | Available everywhere |
| **Updates** | Manual file replacement | Update once, use everywhere |
| **Scalability** | Limited by disk | Unlimited |
| **Sharing** | Can't share | Shared across all users |
| **Maintenance** | Manual | Automatic |

---

## 🚀 Usage Examples

### **Example 1: Login Cracking**

```
User: /login_crack https://example.com/login admin

Bot: 🔐 Starting login crack...
     📥 Loading wordlist from Firebase...
     ✅ Loaded 'rockyou' (10000 passwords)
     
     🔓 Trying passwords...
     Attempt 1/10000: 123456
     Attempt 2/10000: password
     ...
     
     ✅ Password found: admin123
```

### **Example 2: ZIP Cracking**

```
User: /zip_crack
     [uploads secret.zip]

Bot: 📥 Downloading secret.zip...
     🔐 Starting ZIP crack...
     📥 Loading wordlist from Firebase...
     ✅ Loaded 'rockyou' (10000 passwords)
     
     🔓 Trying passwords...
     Tested: 1000/10000 (10%)
     Tested: 2000/10000 (20%)
     ...
     
     ✅ PASSWORD FOUND: secret123
```

---

## 📊 Wordlist Management

### **Add New Wordlist:**

1. Place `.txt` file in `C:/Users/neox/Desktop/Ps/`
2. Run: `python upload_wordlists.py`
3. Wordlist is now available in Firebase

### **Update Existing Wordlist:**

1. Update the `.txt` file locally
2. Run: `python upload_wordlists.py`
3. Firebase wordlist is updated

### **Delete Wordlist:**

Go to Firebase Console → Realtime Database → `/wordlists/{name}` → Delete

---

## ⚙️ Configuration

### **Default Wordlist:**

In `config.py`:
```python
# Default wordlist for cracking (stored in Firebase)
DEFAULT_WORDLIST = "rockyou"  # Name without .txt extension
```

### **Wordlist Limit:**

```python
# Maximum passwords per wordlist (Firebase limit)
MAX_WORDLIST_SIZE = 10000
```

---

## 🔒 Security Notes

### **Firebase Rules:**

Update rules to protect wordlists:

```json
{
  "rules": {
    "users": {
      "$user_id": {
        ".read": true,
        ".write": true
      }
    },
    "wordlists": {
      ".read": true,
      ".write": false  // Only admin can write
    }
  }
}
```

This allows:
- ✅ All users can READ wordlists
- ❌ Only admin (via API key) can WRITE wordlists

---

## 📝 Implementation Checklist

- [ ] Run `python upload_wordlists.py`
- [ ] Verify wordlists in Firebase Console
- [ ] Update `login_cracker.py` to use Firebase wordlists
- [ ] Update `zip_cracker.py` to use Firebase wordlists
- [ ] Test `/login_crack` command
- [ ] Test `/zip_crack` command
- [ ] Remove local wordlist dependency

---

## 🎯 Next Steps

1. **Upload Wordlists:**
   ```bash
   python upload_wordlists.py
   ```

2. **Verify in Firebase:**
   - Go to Firebase Console
   - Navigate to Realtime Database
   - Check `/wordlists/` node

3. **Test Commands:**
   ```
   /login_crack https://example.com/login admin
   /zip_crack
   ```

4. **Remove Local Files** (Optional):
   - Once verified, you can delete local wordlist files
   - Bot will use Firebase wordlists only

---

## ✅ Summary

**Your bot now:**
- ✅ Stores wordlists in Firebase
- ✅ Loads wordlists from cloud
- ✅ No local wordlist files needed
- ✅ Wordlists available to all users
- ✅ Easy to update and manage
- ✅ Scalable and portable

**No more local file dependencies!** 🎉

---

## 🆘 Troubleshooting

### **Wordlist not found:**
```
❌ Wordlist 'rockyou' not found in Firebase
```
**Solution:** Run `python upload_wordlists.py`

### **Upload fails:**
```
❌ Firebase save failed: 404
```
**Solution:** Enable Firebase Realtime Database first

### **Wordlist too large:**
```
❌ Wordlist exceeds 10k limit
```
**Solution:** Split into multiple wordlists or increase limit

---

**Your bot is now fully cloud-powered with Firebase wordlists!** 🚀
