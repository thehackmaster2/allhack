# NeoxSecBot - Single-File Deployment Guide

## 🎯 Overview

Your bot is now **ONE SINGLE FILE** (`bot.py`) with:
- ✅ All 27+ commands in one file
- ✅ Firebase integration built-in
- ✅ Web dashboard for admin control
- ✅ Ready for Render.com deployment
- ✅ No module dependencies

---

## 📁 Project Structure

```
NeoxSecBot/
├── bot.py                    # Single file with everything
├── requirements.txt          # Python dependencies
├── google-services.json      # Firebase config
├── templates/
│   └── index.html           # Admin dashboard
├── README.md                # This file
└── .gitignore               # Git ignore file
```

**That's it! Only 5 files needed!**

---

## 🚀 Local Setup

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Configure Firebase**

1. Place your `google-services.json` in the root directory
2. Enable Firebase Realtime Database in Firebase Console
3. Set database rules (see FIREBASE_SETUP.md)

### **Step 3: Set Environment Variables**

Create `.env` file:
```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_PASSWORD=your_admin_password
PORT=5000
```

### **Step 4: Run the Bot**

```bash
python bot.py
```

**That's it!** Bot is running with web dashboard at `http://localhost:5000`

---

## 🌐 Deploy to Render.com

### **Step 1: Push to GitHub**

```bash
git init
git add bot.py requirements.txt google-services.json templates/
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/neoxsecbot.git
git push -u origin main
```

### **Step 2: Create Render Web Service**

1. Go to https://render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: neoxsecbot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free

### **Step 3: Set Environment Variables**

In Render dashboard, add:
```
BOT_TOKEN = your_telegram_bot_token
ADMIN_PASSWORD = your_admin_password
PORT = 10000
```

### **Step 4: Deploy**

Click "Create Web Service" and Render will:
1. Clone your repository
2. Run `pip install -r requirements.txt`
3. Run `python bot.py`
4. Bot starts automatically!

---

## 🎨 Admin Dashboard

Access at: `https://your-app.onrender.com/`

**Features:**
- 📊 Real-time statistics
- 👥 User management
- 🔍 View user activity
- 🗑️ Delete user data
- 📥 Export data
- 🔄 Auto-refresh every 30s

**Default Password:** Set in environment variable `ADMIN_PASSWORD`

---

## 📋 Bot Commands (All in bot.py)

### **Reconnaissance (6 commands)**
- `/recon` - Full reconnaissance
- `/whois` - WHOIS lookup
- `/dns` - DNS enumeration
- `/subdomains` - Subdomain discovery
- `/ports` - Port scanning
- `/tech` - Technology detection

### **Web Security (1 command)**
- `/scan` - Web vulnerability scan

### **Directory Discovery (2 commands)**
- `/dir` - Full directory scan
- `/quickdir` - Quick directory scan

### **Login Testing (1 command)**
- `/login` - Login security check

### **Reporting (1 command)**
- `/report` - Generate PDF report

### **Malware Analysis (2 commands)**
- `/hash` - Hash lookup
- `/analyze` - File analysis

### **CTF Tools (4 commands)**
- `/decode` - Decode text
- `/encode` - Encode text
- `/hashid` - Identify hash type
- `/caesar` - Caesar cipher

### **Breach Checking (2 commands)**
- `/leak` - Email breach check
- `/pwned` - Password breach check

### **Password Cracking (2 commands)**
- `/login_crack` - Login brute force
- `/zip_crack` - ZIP cracking

### **Firebase & Data (3 commands)**
- `/history` - View chat history
- `/scans` - View scan results
- `/clear_history` - Delete history

### **Bot Info (3 commands)**
- `/start` - Welcome message
- `/help` - Show help
- `/about` - About bot

**Total: 27 commands in ONE file!**

---

## 🔧 Configuration

### **In bot.py:**

```python
class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_token_here")
    FIREBASE_CONFIG_PATH = "google-services.json"
    ENABLE_CHAT_HISTORY = True
    SAVE_TO_FIREBASE_ONLY = True
    WEB_PORT = int(os.getenv("PORT", 5000))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
```

---

## 🔒 Security

### **Environment Variables (Never commit these!)**
- `BOT_TOKEN` - Telegram bot token
- `ADMIN_PASSWORD` - Dashboard password
- `VIRUSTOTAL_API_KEY` - Optional
- `HIBP_API_KEY` - Optional

### **.gitignore:**
```
.env
google-services.json
__pycache__/
*.pyc
```

---

## 📊 Firebase Structure

```json
{
  "users": {
    "123456789": {
      "info": {...},
      "messages": {...},
      "scans": {...}
    }
  },
  "wordlists": {
    "ps": {...},
    "Pu": {...},
    "user": {...}
  }
}
```

---

## ✅ Deployment Checklist

- [ ] Create `bot.py` (single file)
- [ ] Create `requirements.txt`
- [ ] Add `google-services.json`
- [ ] Create `templates/index.html`
- [ ] Test locally: `python bot.py`
- [ ] Push to GitHub
- [ ] Create Render web service
- [ ] Set environment variables
- [ ] Deploy and test

---

## 🎯 Benefits of Single-File Design

| Feature | Multi-File | Single-File |
|---------|-----------|-------------|
| **Files** | 50+ files | 1 file |
| **Deployment** | Complex | Simple |
| **Dependencies** | Many modules | Minimal |
| **Maintenance** | Hard | Easy |
| **Portability** | Difficult | Copy & paste |
| **Debugging** | Multiple files | One file |

---

## 🆘 Troubleshooting

### **Bot not starting:**
```bash
# Check logs
python bot.py

# Check environment variables
echo $BOT_TOKEN
```

### **Dashboard not loading:**
```bash
# Check port
netstat -an | grep 5000

# Check Flask
pip install Flask
```

### **Firebase errors:**
```bash
# Verify google-services.json exists
ls google-services.json

# Check Firebase Console
# Enable Realtime Database
```

---

## 📚 Documentation

- **bot.py** - All code in one file
- **index.html** - Admin dashboard
- **requirements.txt** - Python dependencies
- **README.md** - This file

---

## 🎉 Summary

**Your bot is now:**
- ✅ **ONE single file** (bot.py)
- ✅ **Easy to deploy** (just run python bot.py)
- ✅ **Works on Render** (automatic deployment)
- ✅ **Has admin dashboard** (web interface)
- ✅ **Firebase integrated** (cloud storage)
- ✅ **27+ commands** (all security tools)

**Deployment is as simple as:**
```bash
pip install -r requirements.txt
python bot.py
```

**That's it!** 🚀
