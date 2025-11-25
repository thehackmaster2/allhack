"""
Firebase Manager for NeoxSecBot
Handles all Firebase Realtime Database operations for chat history
"""

import json
import os
from datetime import datetime
import requests
from typing import Dict, List, Optional


class FirebaseManager:
    """Manages Firebase Realtime Database operations"""
    
    def __init__(self, config_path: str = "google-services.json"):
        """Initialize Firebase Manager with google-services.json"""
        self.config_path = config_path
        self.project_id = None
        self.api_key = None
        self.database_url = None
        
        self._load_config()
    
    def _load_config(self):
        """Load Firebase configuration from google-services.json"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.project_id = config['project_info']['project_id']
            self.api_key = config['client'][0]['api_key'][0]['current_key']
            
            # Construct Firebase Realtime Database URL
            self.database_url = f"https://{self.project_id}-default-rtdb.firebaseio.com"
            
            print(f"✅ Firebase initialized: {self.project_id}")
        except Exception as e:
            print(f"❌ Error loading Firebase config: {e}")
            raise
    
    def save_message(self, user_id: int, username: str, message: str, command: str = None) -> bool:
        """
        Save a message to Firebase under the user's ID
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            message: Message text
            command: Command used (if any)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().isoformat()
            
            message_data = {
                'user_id': user_id,
                'username': username or 'Unknown',
                'message': message,
                'command': command,
                'timestamp': timestamp
            }
            
            # Create path: /users/{user_id}/messages/{timestamp_key}
            timestamp_key = timestamp.replace(':', '-').replace('.', '-')
            url = f"{self.database_url}/users/{user_id}/messages/{timestamp_key}.json?auth={self.api_key}"
            
            response = requests.put(url, json=message_data, timeout=10)
            
            if response.status_code == 200:
                # Also update user info
                self._update_user_info(user_id, username)
                return True
            else:
                print(f"❌ Firebase save failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving message to Firebase: {e}")
            return False
    
    def _update_user_info(self, user_id: int, username: str):
        """Update user information (last seen, username)"""
        try:
            user_info = {
                'user_id': user_id,
                'username': username or 'Unknown',
                'last_seen': datetime.now().isoformat()
            }
            
            url = f"{self.database_url}/users/{user_id}/info.json?auth={self.api_key}"
            requests.put(url, json=user_info, timeout=10)
        except Exception as e:
            print(f"❌ Error updating user info: {e}")
    
    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get chat history for a user
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        try:
            url = f"{self.database_url}/users/{user_id}/messages.json?auth={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    return []
                
                # Convert to list and sort by timestamp
                messages = []
                for key, msg in data.items():
                    messages.append(msg)
                
                # Sort by timestamp (newest first)
                messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Limit results
                return messages[:limit]
            else:
                print(f"❌ Firebase get failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting history from Firebase: {e}")
            return []
    
    def get_all_users(self) -> List[Dict]:
        """Get list of all users who have interacted with the bot"""
        try:
            url = f"{self.database_url}/users.json?auth={self.api_key}&shallow=true"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    return []
                
                user_ids = list(data.keys())
                users = []
                
                for user_id in user_ids:
                    info_url = f"{self.database_url}/users/{user_id}/info.json?auth={self.api_key}"
                    info_response = requests.get(info_url, timeout=10)
                    
                    if info_response.status_code == 200:
                        user_info = info_response.json()
                        if user_info:
                            users.append(user_info)
                
                return users
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error getting users from Firebase: {e}")
            return []
    
    def delete_user_history(self, user_id: int) -> bool:
        """Delete all history for a user"""
        try:
            url = f"{self.database_url}/users/{user_id}/messages.json?auth={self.api_key}"
            response = requests.delete(url, timeout=10)
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error deleting history: {e}")
            return False
    
    def get_message_count(self, user_id: int) -> int:
        """Get total message count for a user"""
        try:
            url = f"{self.database_url}/users/{user_id}/messages.json?auth={self.api_key}&shallow=true"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return len(data) if data else 0
            else:
                return 0
        except Exception as e:
            print(f"❌ Error getting message count: {e}")
            return 0
    
    def save_scan_result(self, user_id: int, username: str, scan_type: str, 
                        target: str, result_data: str) -> bool:
        """
        Save scan results to Firebase under user's ID
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            scan_type: Type of scan (recon, webscan, dir, etc.)
            target: Target that was scanned
            result_data: Scan results/output
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().isoformat()
            timestamp_key = timestamp.replace(':', '-').replace('.', '-')
            
            scan_data = {
                'user_id': user_id,
                'username': username or 'Unknown',
                'scan_type': scan_type,
                'target': target,
                'result': result_data,
                'timestamp': timestamp
            }
            
            # Save to: /users/{user_id}/scans/{scan_type}/{timestamp_key}
            url = f"{self.database_url}/users/{user_id}/scans/{scan_type}/{timestamp_key}.json?auth={self.api_key}"
            
            response = requests.put(url, json=scan_data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Saved {scan_type} scan for user {user_id}")
                return True
            else:
                print(f"❌ Firebase save failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving scan result: {e}")
            return False
    
    def get_user_scans(self, user_id: int, scan_type: str = None, limit: int = 20) -> List[Dict]:
        """
        Get scan results for a user
        
        Args:
            user_id: Telegram user ID
            scan_type: Optional filter by scan type
            limit: Maximum number of results
        
        Returns:
            List of scan dictionaries
        """
        try:
            if scan_type:
                url = f"{self.database_url}/users/{user_id}/scans/{scan_type}.json?auth={self.api_key}"
            else:
                url = f"{self.database_url}/users/{user_id}/scans.json?auth={self.api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    return []
                
                # Flatten nested structure if needed
                scans = []
                if scan_type:
                    # Data is already flat
                    for key, scan in data.items():
                        scans.append(scan)
                else:
                    # Data has scan_type level
                    for stype, scans_dict in data.items():
                        if isinstance(scans_dict, dict):
                            for key, scan in scans_dict.items():
                                scans.append(scan)
                
                # Sort by timestamp (newest first)
                scans.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                return scans[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error getting scans: {e}")
            return []
    
    def save_file_data(self, user_id: int, username: str, file_type: str,
                      filename: str, file_data: bytes) -> Optional[str]:
        """
        Save file data to Firebase (base64 encoded)
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            file_type: Type of file (report, crack_result, etc.)
            filename: Original filename
            file_data: File content as bytes
        
        Returns:
            str: Firebase path if successful, None otherwise
        """
        try:
            import base64
            timestamp = datetime.now().isoformat()
            timestamp_key = timestamp.replace(':', '-').replace('.', '-')
            
            # Encode file data to base64
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            file_info = {
                'user_id': user_id,
                'username': username or 'Unknown',
                'file_type': file_type,
                'filename': filename,
                'data': encoded_data,
                'timestamp': timestamp,
                'size_bytes': len(file_data)
            }
            
            # Save to: /users/{user_id}/files/{file_type}/{timestamp_key}
            url = f"{self.database_url}/users/{user_id}/files/{file_type}/{timestamp_key}.json?auth={self.api_key}"
            
            response = requests.put(url, json=file_info, timeout=30)
            
            if response.status_code == 200:
                firebase_path = f"/users/{user_id}/files/{file_type}/{timestamp_key}"
                print(f"✅ Saved file to Firebase: {firebase_path}")
                return firebase_path
            else:
                print(f"❌ Firebase file save failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None
    
    def get_user_files(self, user_id: int, file_type: str = None) -> List[Dict]:
        """Get files for a user"""
        try:
            if file_type:
                url = f"{self.database_url}/users/{user_id}/files/{file_type}.json?auth={self.api_key}"
            else:
                url = f"{self.database_url}/users/{user_id}/files.json?auth={self.api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data:
                    return []
                
                files = []
                if file_type:
                    for key, file_info in data.items():
                        # Don't include the large data field in list
                        file_meta = {k: v for k, v in file_info.items() if k != 'data'}
                        file_meta['firebase_key'] = key
                        files.append(file_meta)
                else:
                    for ftype, files_dict in data.items():
                        if isinstance(files_dict, dict):
                            for key, file_info in files_dict.items():
                                file_meta = {k: v for k, v in file_info.items() if k != 'data'}
                                file_meta['firebase_key'] = key
                                files.append(file_meta)
                
                # Sort by timestamp
                files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                return files
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error getting files: {e}")
            return []
    
    def delete_all_user_data(self, user_id: int) -> bool:
        """Delete ALL data for a user (messages, scans, files)"""
        try:
            url = f"{self.database_url}/users/{user_id}.json?auth={self.api_key}"
            response = requests.delete(url, timeout=10)
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error deleting user data: {e}")
            return False
    
    def get_wordlist(self, wordlist_name: str) -> List[str]:
        """
        Get wordlist from Firebase
        
        Args:
            wordlist_name: Name of the wordlist (without .txt extension)
        
        Returns:
            List of passwords/words
        """
        try:
            url = f"{self.database_url}/wordlists/{wordlist_name}/passwords.json?auth={self.api_key}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and isinstance(data, list):
                    print(f"✅ Loaded wordlist '{wordlist_name}' ({len(data)} passwords)")
                    return data
                else:
                    print(f"❌ Wordlist '{wordlist_name}' is empty or invalid")
                    return []
            else:
                print(f"❌ Wordlist '{wordlist_name}' not found in Firebase")
                return []
                
        except Exception as e:
            print(f"❌ Error loading wordlist: {e}")
            return []
    
    def list_wordlists(self) -> List[str]:
        """
        List all available wordlists in Firebase
        
        Returns:
            List of wordlist names
        """
        try:
            url = f"{self.database_url}/wordlists.json?auth={self.api_key}&shallow=true"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    wordlists = list(data.keys())
                    print(f"✅ Found {len(wordlists)} wordlists in Firebase")
                    return wordlists
                else:
                    return []
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error listing wordlists: {e}")
            return []
    
    def get_wordlist_info(self, wordlist_name: str) -> Optional[Dict]:
        """
        Get information about a wordlist (without loading all passwords)
        
        Args:
            wordlist_name: Name of the wordlist
        
        Returns:
            Dict with wordlist info (filename, count)
        """
        try:
            url = f"{self.database_url}/wordlists/{wordlist_name}.json?auth={self.api_key}&shallow=true"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    # Get count
                    count_url = f"{self.database_url}/wordlists/{wordlist_name}/count.json?auth={self.api_key}"
                    count_response = requests.get(count_url, timeout=10)
                    count = count_response.json() if count_response.status_code == 200 else 0
                    
                    return {
                        'name': wordlist_name,
                        'count': count
                    }
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting wordlist info: {e}")
            return None
