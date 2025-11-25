# NeoxSecBot - Quick Start Guide

## 🚀 Quick Installation (Windows)

### Step 1: Install Python
1. Download Python 3.8+ from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation: Open PowerShell and run `python --version`

### Step 2: Install Dependencies
Open PowerShell in the NeoxSecBot folder and run:
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Bot Token
1. Create a Telegram bot:
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. Edit `config.py`:
   - Open config.py in a text editor
   - Replace `BOT_TOKEN = "..."` with your actual token
   - Save the file

### Step 4: Run the Bot
**Option A: Using the batch file**
```
Double-click start.bat
```

**Option B: Using PowerShell**
```powershell
python bot.py
```

### Step 5: Test the Bot
1. Open Telegram
2. Search for your bot by username
3. Send `/start` to see all commands

## 🔧 Optional: Install Additional Tools

For enhanced functionality, install these tools:

### nmap (Port Scanning)
1. Download from https://nmap.org/download.html
2. Install with default options
3. Add to PATH if not automatic

### whois (WHOIS Lookup)
**Option A: Chocolatey**
```powershell
choco install whois
```

**Option B: Manual**
Download from https://docs.microsoft.com/en-us/sysinternals/downloads/whois

### dig (DNS Queries)
**Option A: BIND Tools**
Download from https://www.isc.org/download/

**Option B: Use built-in fallback**
The bot will use Python's socket library if dig is not available

## 🔑 Optional: API Keys

### VirusTotal (Malware Analysis)
1. Sign up at https://www.virustotal.com/
2. Get API key from your account
3. Add to `config.py`: `VIRUSTOTAL_API_KEY = "your_key"`

### Have I Been Pwned (Leak Checking)
1. Get API key from https://haveibeenpwned.com/API/Key
2. Add to `config.py`: `HIBP_API_KEY = "your_key"`

## 📝 Example Commands

Once the bot is running, try these commands in Telegram:

```
/start                          - Show welcome message
/whois google.com              - WHOIS lookup
/dns google.com                - DNS records
/subdomains example.com        - Find subdomains
/scan http://example.com       - Web security scan
/quickdir http://example.com   - Quick directory scan
/decode base64 SGVsbG8gV29ybGQ= - Decode base64
/hashid 5d41402abc4b2a76b9719d911017c592 - Identify hash
/leak test@example.com         - Check for breaches
```

## ⚠️ Important Notes

1. **Legal Use Only**: Only scan systems you own or have permission to test
2. **Rate Limiting**: Some commands may be slow due to API rate limits
3. **Firewall**: Windows Firewall may ask for permission - allow it
4. **Antivirus**: Some security software may flag the bot - this is normal for security tools

## 🐛 Troubleshooting

**Bot won't start:**
- Check bot token in config.py
- Verify Python is in PATH: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**Commands not working:**
- Check bot logs in the console
- Verify target format (include http:// for URLs)
- Some features require API keys

**"Module not found" error:**
- Run from the NeoxSecBot directory
- Reinstall dependencies

## 📞 Need Help?

Check the full README.md for detailed documentation.

---

**Ready to start? Run `start.bat` or `python bot.py`!**
