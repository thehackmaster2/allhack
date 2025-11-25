"""
NeoxSecBot Configuration
"""

# Telegram Bot Token
BOT_TOKEN = "8398817549:AAFF5dvH6UscSp7U7jzzP3wjo5AmQZZ5HYU"

# Results folder (DEPRECATED - Using Firebase now)
# All data is saved to Firebase Realtime Database
# No local storage is used
RESULTS_FOLDER = "results/"  # Only used for temporary files during processing

# API Keys (optional, add your own)
VIRUSTOTAL_API_KEY = ""  # Get from https://www.virustotal.com/
HIBP_API_KEY = ""  # Get from https://haveibeenpwned.com/API/Key

# Scan configurations
NMAP_TIMEOUT = 300  # seconds
HTTP_TIMEOUT = 10  # seconds
MAX_THREADS = 10

# Wordlists
DIRFINDER_WORDLIST = "wordlists/common.txt"
SUBDOMAIN_WORDLIST = "wordlists/subdomains.txt"

# Cracking wordlists directory
WORDLIST_DIR = "C:/Users/neox/Desktop/Ps/"

# Default credentials for login checker
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "12345"),
    ("root", "root"),
    ("root", "toor"),
    ("administrator", "administrator"),
    ("test", "test"),
    ("guest", "guest"),
]

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Firebase Configuration
FIREBASE_CONFIG_PATH = "google-services.json"
ENABLE_CHAT_HISTORY = True  # Set to False to disable chat history logging
SAVE_TO_FIREBASE_ONLY = True  # Set to True to save all data to Firebase (no local files)
