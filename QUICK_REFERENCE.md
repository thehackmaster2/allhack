# Quick Reference - NeoxSecBot Commands

## 🚀 Quick Start
```
1. /start          - See all commands
2. /whois google.com - Try a scan
3. /scans          - View your results
4. /history        - View your chat history
```

## 📋 All Commands (27 Total)

### 🔍 Reconnaissance (6)
```
/recon <target>       - Full recon (WHOIS+DNS+subdomains+ports+tech)
/whois <domain>       - Domain registration info
/dns <domain>         - DNS records (A, MX, NS, TXT, etc.)
/subdomains <domain>  - Find subdomains
/ports <target>       - Scan open ports
/tech <url>           - Detect web technologies
```

### 🌐 Web Security (1)
```
/scan <url>           - Full vulnerability scan (XSS, SQLi, headers)
```

### 📁 Directory Discovery (2)
```
/dir <url>            - Full directory enumeration
/quickdir <url>       - Quick common paths scan
```

### 🔑 Login Testing (1)
```
/login <url>          - Check login security (CSRF, rate limiting)
```

### 📊 Reporting (1)
```
/report <target>      - Generate PDF security report
```

### 🦠 Malware Analysis (2)
```
/hash <file_hash>     - Lookup hash (VirusTotal, MalwareBazaar)
/analyze <file_path>  - Analyze file (strings, metadata)
```

### 🏴 CTF Tools (4)
```
/decode <method> <text>  - Decode (base64/hex/rot13/auto)
/encode <method> <text>  - Encode (base64/hex/rot13)
/hashid <hash>           - Identify hash type
/caesar <text>           - Bruteforce Caesar cipher
```

### 💧 Breach Checking (2)
```
/leak <email>         - Check email in breaches (HIBP)
/pwned <password>     - Check if password compromised
```

### 🔓 Password Cracking (2)
```
/login_crack <url> <username>  - Brute force login
/zip_crack                     - Crack ZIP (upload file)
```

### 📜 Firebase & Data (3)
```
/history              - View your chat messages
/scans [type]         - View scan results (filter optional)
/clear_history        - Delete your chat history
```

### ⚙️ Bot Info (3)
```
/start                - Show all commands (detailed)
/help                 - Same as /start
/about                - Bot features and info
```

## 💡 Usage Examples

### Example 1: Domain Reconnaissance
```
/whois example.com
/dns example.com
/subdomains example.com
/scans whois          ← View all WHOIS results
```

### Example 2: Web Security Testing
```
/scan https://example.com
/dir https://example.com
/login https://example.com/login
/scans scan           ← View all scan results
```

### Example 3: CTF Challenge
```
/decode base64 SGVsbG8gV29ybGQ=
/hashid 5d41402abc4b2a76b9719d911017c592
/caesar Uryyb Jbeyq
```

### Example 4: Data Management
```
/history              ← See all your commands
/scans                ← See all your scans
/scans whois          ← Filter by type
/clear_history        ← Delete everything
```

## 🔥 Pro Tips

1. **Filter scan results by type:**
   ```
   /scans whois      ← Only WHOIS scans
   /scans dns        ← Only DNS scans
   /scans scan       ← Only web scans
   ```

2. **All data is saved to Firebase:**
   - Every scan result is stored
   - Access anytime with `/scans`
   - Organized by your user ID
   - No data lost when bot restarts

3. **Quick testing workflow:**
   ```
   /whois target.com     ← Quick info
   /dns target.com       ← DNS records
   /tech target.com      ← Technologies
   /scans                ← Review all results
   ```

4. **Privacy:**
   - Only you can see your data
   - Delete anytime with `/clear_history`
   - All data in your Firebase account

## 📊 Firebase Database Structure
```
users/
  └── {your_user_id}/
      ├── messages/     ← Chat history
      ├── scans/        ← All scan results
      │   ├── whois/
      │   ├── dns/
      │   ├── scan/
      │   └── ...
      └── files/        ← Reports, etc.
```

## ⚠️ Important Notes

**Legal:**
- ✅ Use only on authorized targets
- ✅ Get permission before testing
- ✅ Educational purposes only
- ❌ Don't use for illegal activities

**Best Practices:**
- Always check `/help` for latest commands
- Use `/scans` to review past results
- Use `/history` to track your activity
- Clear old data with `/clear_history`

## 🎯 Most Used Commands

**Top 10:**
1. `/start` - See all commands
2. `/whois <domain>` - Quick domain info
3. `/dns <domain>` - DNS records
4. `/scan <url>` - Web security scan
5. `/scans` - View your results
6. `/history` - View your activity
7. `/decode base64 <text>` - Decode base64
8. `/leak <email>` - Check breaches
9. `/tech <url>` - Detect technologies
10. `/about` - Bot information

## 🚀 Getting Started

**First Time Users:**
```bash
1. Send: /start
   → Read the full command list

2. Send: /whois google.com
   → Try your first scan

3. Send: /scans
   → See your saved results

4. Send: /about
   → Learn about all features
```

**Regular Users:**
```bash
/scans              ← Check recent scans
/history            ← Check recent activity
/whois <target>     ← Quick recon
/scan <url>         ← Security scan
```

## 📱 Mobile-Friendly Commands

Short commands for mobile:
```
/whois domain.com
/dns domain.com
/tech url.com
/scans
/history
```

## 🎓 Learning Path

**Beginner:**
1. `/start` - Learn commands
2. `/whois` - Try reconnaissance
3. `/scans` - View results

**Intermediate:**
4. `/scan` - Web security
5. `/dir` - Directory discovery
6. `/decode` - CTF tools

**Advanced:**
7. `/login_crack` - Password testing
8. `/report` - Generate reports
9. Custom workflows

---

**Need Help?** Send `/help` anytime!
**Questions?** Send `/about` for details!
**View Data?** Send `/scans` or `/history`!
