"""
Leak Checker Module - Check for breached credentials
"""

import aiohttp
import asyncio
import hashlib
import os
import re
from datetime import datetime
from typing import Dict, List


class LeakCheckModule:
    def __init__(self, results_folder: str, hibp_api_key: str = ""):
        self.results_folder = results_folder
        self.hibp_api_key = hibp_api_key
        self.user_agent = "NeoxSecBot"
    
    def _ensure_target_folder(self, target: str) -> str:
        """Create target-specific results folder"""
        safe_target = re.sub(r'[^\w\-.]', '_', target)
        target_path = os.path.join(self.results_folder, safe_target)
        os.makedirs(target_path, exist_ok=True)
        return target_path
    
    def _save_result(self, target: str, filename: str, content: str):
        """Save results to file"""
        target_path = self._ensure_target_folder(target)
        filepath = os.path.join(target_path, filename)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(content)
            f.write("\n")
        return filepath
    
    async def check_hibp_email(self, email: str) -> Dict[str, any]:
        """Check email against Have I Been Pwned API"""
        if not self.hibp_api_key:
            return {
                'status': 'error',
                'message': 'HIBP API key not configured. Get one from https://haveibeenpwned.com/API/Key'
            }
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                'hibp-api-key': self.hibp_api_key,
                'User-Agent': self.user_agent
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers,
                                      timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        breaches = await resp.json()
                        return {
                            'status': 'found',
                            'email': email,
                            'breach_count': len(breaches),
                            'breaches': breaches
                        }
                    elif resp.status == 404:
                        return {
                            'status': 'clean',
                            'email': email,
                            'message': 'No breaches found for this email'
                        }
                    elif resp.status == 429:
                        return {
                            'status': 'error',
                            'message': 'Rate limit exceeded. Please wait before trying again.'
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'HIBP API returned status {resp.status}'
                        }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def check_hibp_password(self, password: str) -> Dict[str, any]:
        """Check password against HIBP Pwned Passwords (k-anonymity)"""
        try:
            # Hash the password
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Query HIBP API with k-anonymity
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        
                        # Check if our suffix is in the results
                        for line in text.split('\n'):
                            if line.startswith(suffix):
                                count = int(line.split(':')[1].strip())
                                return {
                                    'status': 'pwned',
                                    'count': count,
                                    'message': f'⚠️  Password found in {count:,} breaches!'
                                }
                        
                        return {
                            'status': 'clean',
                            'message': '✓ Password not found in known breaches'
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'API returned status {resp.status}'
                        }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def check_dehashed(self, query: str) -> Dict[str, any]:
        """Check against DeHashed API (requires API key)"""
        # Note: DeHashed requires paid API access
        return {
            'status': 'not_implemented',
            'message': 'DeHashed integration requires paid API access'
        }
    
    async def check_local_database(self, email: str, db_path: str) -> Dict[str, any]:
        """Check against local breach database"""
        try:
            if not os.path.exists(db_path):
                return {
                    'status': 'error',
                    'message': f'Local database not found at {db_path}'
                }
            
            found_entries = []
            
            # Search in local database file
            with open(db_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if email.lower() in line.lower():
                        found_entries.append({
                            'line': line_num,
                            'content': line.strip()[:200]  # Limit length
                        })
                    
                    # Limit search to prevent excessive memory usage
                    if line_num > 1000000:
                        break
            
            if found_entries:
                return {
                    'status': 'found',
                    'email': email,
                    'count': len(found_entries),
                    'entries': found_entries[:10]  # Limit results
                }
            else:
                return {
                    'status': 'clean',
                    'email': email,
                    'message': 'Not found in local database'
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def check_email_full(self, email: str, local_db_path: str = None) -> Dict[str, any]:
        """Full email breach check"""
        try:
            results = []
            results.append(f"Checking email: {email}\n")
            
            # Validate email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return {
                    'status': 'error',
                    'message': 'Invalid email format'
                }
            
            # Check HIBP
            results.append("=== HAVE I BEEN PWNED ===")
            if self.hibp_api_key:
                hibp_result = await self.check_hibp_email(email)
                if hibp_result['status'] == 'found':
                    results.append(f"⚠️  EMAIL FOUND IN {hibp_result['breach_count']} BREACHES!")
                    results.append("\nBreached services:")
                    for breach in hibp_result['breaches'][:10]:  # Limit output
                        name = breach.get('Name', 'Unknown')
                        date = breach.get('BreachDate', 'Unknown')
                        results.append(f"  - {name} (Date: {date})")
                elif hibp_result['status'] == 'clean':
                    results.append("✓ Email not found in HIBP database")
                else:
                    results.append(f"Error: {hibp_result.get('message', 'Unknown error')}")
            else:
                results.append("⚠️  HIBP API key not configured")
                results.append("Get an API key from: https://haveibeenpwned.com/API/Key")
            
            # Check local database if provided
            if local_db_path:
                results.append("\n=== LOCAL DATABASE ===")
                local_result = await self.check_local_database(email, local_db_path)
                if local_result['status'] == 'found':
                    results.append(f"⚠️  Found {local_result['count']} entries in local database")
                elif local_result['status'] == 'clean':
                    results.append("✓ Not found in local database")
                else:
                    results.append(f"Error: {local_result.get('message', 'Unknown error')}")
            
            output = "\n".join(results)
            filepath = self._save_result(email, 'leak_check.txt', output)
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def check_password_strength(self, password: str) -> Dict[str, any]:
        """Analyze password strength"""
        try:
            results = []
            score = 0
            max_score = 10
            
            # Length check
            length = len(password)
            if length >= 12:
                score += 3
                results.append("✓ Length >= 12 characters (+3)")
            elif length >= 8:
                score += 2
                results.append("⚠️  Length >= 8 characters (+2)")
            else:
                results.append("✗ Length < 8 characters (0)")
            
            # Complexity checks
            if re.search(r'[a-z]', password):
                score += 1
                results.append("✓ Contains lowercase (+1)")
            else:
                results.append("✗ No lowercase letters")
            
            if re.search(r'[A-Z]', password):
                score += 1
                results.append("✓ Contains uppercase (+1)")
            else:
                results.append("✗ No uppercase letters")
            
            if re.search(r'[0-9]', password):
                score += 1
                results.append("✓ Contains numbers (+1)")
            else:
                results.append("✗ No numbers")
            
            if re.search(r'[^a-zA-Z0-9]', password):
                score += 2
                results.append("✓ Contains special characters (+2)")
            else:
                results.append("✗ No special characters")
            
            # Common patterns
            if re.search(r'(123|abc|password|qwerty)', password.lower()):
                score -= 2
                results.append("⚠️  Contains common pattern (-2)")
            
            # Check against HIBP
            results.append("\n=== BREACH CHECK ===")
            hibp_result = await self.check_hibp_password(password)
            if hibp_result['status'] == 'pwned':
                score = 0  # Pwned password = 0 score
                results.append(hibp_result['message'])
            elif hibp_result['status'] == 'clean':
                score += 2
                results.append(hibp_result['message'] + " (+2)")
            
            # Final score
            score = max(0, min(score, max_score))
            strength = 'Weak' if score < 4 else 'Medium' if score < 7 else 'Strong'
            
            results.insert(0, f"Password Strength: {strength} ({score}/{max_score})\n")
            
            return {
                'status': 'success',
                'score': score,
                'max_score': max_score,
                'strength': strength,
                'output': '\n'.join(results)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


# Export functions
async def check_email(email: str, results_folder: str, 
                     hibp_api_key: str = "", local_db_path: str = None) -> Dict[str, any]:
    module = LeakCheckModule(results_folder, hibp_api_key)
    return await module.check_email_full(email, local_db_path)

async def check_password(password: str, results_folder: str, 
                        hibp_api_key: str = "") -> Dict[str, any]:
    module = LeakCheckModule(results_folder, hibp_api_key)
    return await module.check_password_strength(password)
