# NeoxSecBot - Telegram Security Automation Bot

A comprehensive security testing and automation bot for Telegram with real penetration testing capabilities.

## 🚀 Features

### 🔍 Reconnaissance
- **WHOIS Lookup**: Real WHOIS queries using system whois command
- **DNS Enumeration**: Complete DNS record discovery (A, AAAA, MX, NS, TXT, CNAME)
- **Subdomain Discovery**: Certificate transparency + DNS bruteforce
- **Port Scanning**: Real nmap integration with socket fallback
- **Technology Detection**: Web framework and CMS identification

### 🌐 Web Security
- **Security Headers**: Check for missing security headers (HSTS, CSP, X-Frame-Options, etc.)
- **Cookie Analysis**: Secure, HttpOnly, and SameSite flag verification
- **XSS Testing**: Reflection-based XSS vulnerability detection
- **SQL Injection**: Boolean-based SQLi testing
- **robots.txt Analysis**: Parse and analyze robots.txt

### 📁 Directory Enumeration
- **Full Directory Scan**: Concurrent HTTP requests with custom wordlists
- **Quick Scan**: Fast common path discovery
- **Progress Tracking**: Real-time scan progress updates

### 🔑 Login Security
- **Login Detection**: Automatic login page identification
- **CSRF Protection**: Check for CSRF tokens
- **Default Credentials**: Test common username/password combinations
- **Rate Limiting**: Detect brute force protection

### 📊 Reporting
- **PDF Reports**: Professional security assessment reports using ReportLab
- **Text Reports**: Simple text-based summaries
- **Organized Results**: All results saved per target

### 🦠 Malware Analysis
- **Hash Calculation**: MD5, SHA1, SHA256 hashing
- **VirusTotal Integration**: Hash lookup via VT API
- **MalwareBazaar**: Free malware database queries
- **String Extraction**: Extract readable strings from binaries
- **Metadata Extraction**: File type detection and metadata

### 🏴 CTF Tools
- **Base64**: Encode/decode with URL-safe support
- **Hexadecimal**: Hex encoding/decoding
- **ROT13**: ROT13 cipher
- **Caesar Cipher**: Bruteforce all 26 shifts
- **Hash Identification**: Automatic hash type detection
- **Hash Calculation**: Generate multiple hash types
- **Steganography**: Basic embedded file detection

### 💧 Leak Checking
- **Email Breach Check**: Have I Been Pwned integration
- **Password Check**: Pwned Passwords API (k-anonymity)
- **Password Strength**: Comprehensive strength analysis
- **Local Database**: Support for local breach databases

### 📜 Chat History (Firebase)
- **Automatic Logging**: All user messages saved to Firebase Realtime Database
- **User Folders**: Each user has their own data folder
- **History Viewing**: View chat history with `/history` command
- **History Management**: Clear history with `/clear_history` command
- **Privacy**: Users can only access their own data

## 📦 Installation

### Prerequisites
```bash
# Windows (PowerShell)
# Install Python 3.8+ from python.org

# Optional tools for enhanced functionality:
# - nmap: https://nmap.org/download.html
# - whois: Install via chocolatey or manual download
```

### Setup
```bash
# Clone or navigate to the project directory
cd NeoxSecBot

# Install Python dependencies
pip install -r requirements.txt

# Configure the bot
# Edit config.py and add your bot token and API keys
```

### Configuration
Edit `config.py`:
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
VIRUSTOTAL_API_KEY = "YOUR_VT_API_KEY"  # Optional
HIBP_API_KEY = "YOUR_HIBP_API_KEY"  # Optional
```

### Firebase Setup (for Chat History)
1. Your `google-services.json` is already in the project
2. Go to [Firebase Console](https://console.firebase.google.com/)
3. Select your project: `allhack-c2c4b`
4. Enable "Realtime Database"
5. Set database rules (see `FIREBASE_SETUP.md` for details)

For detailed Firebase setup instructions, see **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)**

## 🎮 Usage

### Start the Bot
```bash
python bot.py
```

### Telegram Commands

#### Basic Commands
- `/start` - Welcome message and command list
- `/help` - Show all available commands
- `/about` - About the bot

#### Reconnaissance
- `/recon <target>` - Full reconnaissance scan
- `/whois <domain>` - WHOIS lookup
- `/dns <domain>` - DNS enumeration
- `/subdomains <domain>` - Subdomain discovery
- `/ports <target>` - Port scanning
- `/tech <url>` - Technology detection

#### Web Security
- `/scan <url>` - Full web vulnerability scan
- `/headers <url>` - Security headers check
- `/cookies <url>` - Cookie security analysis
- `/xss <url>` - XSS testing
- `/sqli <url>` - SQL injection testing
- `/robots <url>` - robots.txt analysis

#### Directory Enumeration
- `/dir <url>` - Full directory scan
- `/quickdir <url>` - Quick directory scan

#### Login Security
- `/login <url>` - Login page security check

#### Reporting
- `/report <target>` - Generate PDF report

#### Malware Analysis
- `/hash <file_hash>` - Hash lookup
- `/analyze <file_path>` - File analysis
- `/strings <file_path>` - Extract strings

#### CTF Tools
- `/decode <method> <text>` - Decode text (base64/hex/rot13/auto)
- `/encode <method> <text>` - Encode text (base64/hex/rot13)
- `/hashid <hash>` - Identify hash type
- `/caesar <text>` - Caesar cipher bruteforce
- `/stego <file_path>` - Basic stego check

#### Leak Checking
- `/leak <email>` - Check email breaches
- `/pwned <password>` - Check password breaches

#### Chat History
- `/history` - View your chat history
- `/clear_history` - Delete your chat history

## 📁 Project Structure

```
NeoxSecBot/
│
├── bot.py                 # Main bot file with command handlers
├── config.py              # Configuration (tokens, API keys)
├── firebase_manager.py    # Firebase Realtime Database integration
├── google-services.json   # Firebase configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── FIREBASE_SETUP.md     # Firebase setup guide
│
├── modules/              # All functional modules
│   ├── recon.py          # Reconnaissance tools
│   ├── webscan.py        # Web vulnerability scanner
│   ├── dirfinder.py      # Directory enumeration
│   ├── loginchecker.py   # Login security testing
│   ├── reportgen.py      # PDF/text report generation
│   ├── malware.py        # Malware analysis
│   ├── ctf.py            # CTF tools and crypto
│   └── leakcheck.py      # Breach checking
│
└── results/              # Scan results (auto-created)
    └── <target>/         # Per-target results
```

## 🔒 Security & Legal

### ⚠️ IMPORTANT DISCLAIMER

This tool is designed for **EDUCATIONAL PURPOSES** and **AUTHORIZED SECURITY TESTING ONLY**.

**You MUST:**
- ✅ Obtain explicit written permission before testing any system
- ✅ Only use on systems you own or have authorization to test
- ✅ Comply with all applicable laws and regulations
- ✅ Use responsibly and ethically

**You MUST NOT:**
- ❌ Use this tool for illegal activities
- ❌ Test systems without authorization
- ❌ Use for malicious purposes
- ❌ Violate any laws or regulations

**The developers are NOT responsible for any misuse of this tool.**

## 🛠️ Advanced Configuration

### Custom Wordlists
Create custom wordlists for directory scanning:
```
wordlists/common.txt
wordlists/subdomains.txt
```

### API Keys
For enhanced functionality, obtain API keys:
- **VirusTotal**: https://www.virustotal.com/
- **Have I Been Pwned**: https://haveibeenpwned.com/API/Key

### Default Credentials
Edit `config.py` to customize default credential testing:
```python
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("root", "toor"),
    # Add more...
]
```

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't start:**
- Check your bot token in `config.py`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**WHOIS/DNS/Port scanning not working:**
- Install system tools: `whois`, `dig`, `nmap`
- The bot will use fallback methods if tools are unavailable

**API features not working:**
- Verify API keys in `config.py`
- Check API rate limits

## 📝 Development

### Adding New Modules
1. Create module in `modules/` directory
2. Implement async functions
3. Add command handler in `bot.py`
4. Update help text

### Module Template
```python
async def my_function(target: str, results_folder: str) -> Dict[str, any]:
    try:
        # Your code here
        return {
            'status': 'success',
            'output': 'results',
            'file': 'path/to/results'
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is provided for educational purposes. Use at your own risk.

## 👨‍💻 Author

**NeoxSec Team**
- Version: 1.0.0
- Contact: [Your contact info]

## 🙏 Acknowledgments

- python-telegram-bot library
- Have I Been Pwned API
- VirusTotal API
- All open-source security tools used

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally!**
