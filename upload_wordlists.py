"""
Upload Wordlists to Firebase
This script uploads all wordlist files from C:/Users/neox/Desktop/Ps/ to Firebase
"""

import os
import sys
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from firebase_manager import FirebaseManager

def upload_wordlists_to_firebase():
    """Upload all wordlist files to Firebase"""
    
    wordlist_dir = "C:/Users/neox/Desktop/Ps/"
    
    print("=" * 50)
    print("Firebase Wordlist Uploader")
    print("=" * 50)
    print()
    
    # Initialize Firebase
    try:
        firebase = FirebaseManager("google-services.json")
        print(f"[+] Connected to Firebase: {firebase.project_id}")
        print()
    except Exception as e:
        print(f"[-] Error connecting to Firebase: {e}")
        return
    
    # Check if directory exists
    if not os.path.exists(wordlist_dir):
        print(f"[-] Wordlist directory not found: {wordlist_dir}")
        return
    
    # Get all .txt files
    wordlist_files = [f for f in os.listdir(wordlist_dir) if f.endswith('.txt')]
    
    if not wordlist_files:
        print(f"[-] No .txt files found in {wordlist_dir}")
        return
    
    print(f"[+] Found {len(wordlist_files)} wordlist files")
    print()
    
    # Upload each wordlist
    for filename in wordlist_files:
        filepath = os.path.join(wordlist_dir, filename)
        
        try:
            # Read file
            print(f"[*] Uploading: {filename}...", end=" ")
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Clean and prepare data
            passwords = [line.strip() for line in lines if line.strip()]
            
            # Upload to Firebase
            wordlist_data = {
                'filename': filename,
                'count': len(passwords),
                'passwords': passwords[:10000]  # Limit to 10k passwords per file for Firebase
            }
            
            # Save to /wordlists/{filename}
            url = f"{firebase.database_url}/wordlists/{filename.replace('.txt', '')}.json?auth={firebase.api_key}"
            
            import requests
            response = requests.put(url, json=wordlist_data, timeout=30)
            
            if response.status_code == 200:
                print(f"[+] OK ({len(passwords)} passwords)")
            else:
                print(f"[-] Failed: {response.status_code}")
                
        except Exception as e:
            print(f"[-] Error: {e}")
    
    print()
    print("=" * 50)
    print("[+] Upload complete!")
    print()
    print("[*] Wordlists are now available in Firebase:")
    print("    /wordlists/{wordlist_name}/passwords")
    print()

if __name__ == "__main__":
    upload_wordlists_to_firebase()
