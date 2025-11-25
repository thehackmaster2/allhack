"""
Login Page Security Checker
"""

import aiohttp
import asyncio
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup


class LoginCheckerModule:
    def __init__(self, results_folder: str):
        self.results_folder = results_folder
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
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
    
    async def detect_login_page(self, target: str) -> Dict[str, any]:
        """Detect if page is a login page"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            is_login = False
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    html = await resp.text()
                    
                    # Check for login indicators
                    login_indicators = [
                        r'<input[^>]*type=["\']password["\']',
                        r'<form[^>]*login',
                        r'<input[^>]*name=["\']username["\']',
                        r'<input[^>]*name=["\']email["\']',
                        r'<input[^>]*name=["\']user["\']',
                        r'<button[^>]*login',
                        r'sign\s*in',
                        r'log\s*in',
                    ]
                    
                    found_indicators = []
                    for pattern in login_indicators:
                        if re.search(pattern, html, re.IGNORECASE):
                            found_indicators.append(pattern)
                            is_login = True
                    
                    if is_login:
                        results.append("✓ Login page detected!")
                        results.append(f"\nFound {len(found_indicators)} login indicators:")
                        for indicator in found_indicators:
                            results.append(f"  - Pattern: {indicator}")
                    else:
                        results.append("✗ No login page detected")
            
            output = "\n".join(results)
            
            return {
                'status': 'success',
                'is_login': is_login,
                'output': output,
                'indicators': len(found_indicators)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def check_csrf_protection(self, target: str) -> Dict[str, any]:
        """Check for CSRF token in login form"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            has_csrf = False
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    html = await resp.text()
                    
                    # Check for CSRF tokens
                    csrf_patterns = [
                        r'<input[^>]*name=["\']csrf[^"\']*["\']',
                        r'<input[^>]*name=["\']_token["\']',
                        r'<input[^>]*name=["\']authenticity_token["\']',
                        r'<meta[^>]*name=["\']csrf-token["\']',
                    ]
                    
                    found_tokens = []
                    for pattern in csrf_patterns:
                        matches = re.findall(pattern, html, re.IGNORECASE)
                        if matches:
                            found_tokens.extend(matches)
                            has_csrf = True
                    
                    if has_csrf:
                        results.append("✓ CSRF protection detected")
                        results.append(f"\nFound {len(found_tokens)} CSRF token(s):")
                        for token in found_tokens[:5]:  # Limit output
                            results.append(f"  {token[:100]}...")
                    else:
                        results.append("⚠️  WARNING: No CSRF token detected!")
                        results.append("  The login form may be vulnerable to CSRF attacks")
            
            output = "\n".join(results)
            
            return {
                'status': 'success',
                'has_csrf': has_csrf,
                'output': output
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def test_default_credentials(self, target: str, 
                                       credentials: List[Tuple[str, str]]) -> Dict[str, any]:
        """Test common default credentials"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            results.append(f"Testing {len(credentials)} credential pairs...\n")
            
            # First, get the login form
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    html = await resp.text()
                    
                    # Try to find form action and input names
                    form_action = target
                    username_field = 'username'
                    password_field = 'password'
                    
                    # Parse form
                    form_match = re.search(r'<form[^>]*action=["\']([^"\']*)["\']', html, re.IGNORECASE)
                    if form_match:
                        form_action = urljoin(target, form_match.group(1))
                    
                    # Find username field
                    user_match = re.search(r'<input[^>]*name=["\']([^"\']*user[^"\']*)["\']', html, re.IGNORECASE)
                    if user_match:
                        username_field = user_match.group(1)
                    
                    # Find password field
                    pass_match = re.search(r'<input[^>]*type=["\']password["\'][^>]*name=["\']([^"\']*)["\']', html, re.IGNORECASE)
                    if pass_match:
                        password_field = pass_match.group(1)
                    
                    results.append(f"Form action: {form_action}")
                    results.append(f"Username field: {username_field}")
                    results.append(f"Password field: {password_field}\n")
                
                # Test credentials
                tested = 0
                for username, password in credentials:
                    if tested >= 5:  # Limit to prevent abuse
                        results.append(f"\n⚠️  Stopped after {tested} attempts to prevent lockout")
                        break
                    
                    data = {
                        username_field: username,
                        password_field: password
                    }
                    
                    try:
                        async with session.post(form_action, data=data,
                                               timeout=aiohttp.ClientTimeout(total=10),
                                               headers={'User-Agent': self.user_agent},
                                               allow_redirects=False) as resp:
                            status = resp.status
                            
                            # Check for successful login indicators
                            if status in [302, 301, 303]:  # Redirect might indicate success
                                location = resp.headers.get('Location', '')
                                if 'dashboard' in location.lower() or 'admin' in location.lower():
                                    results.append(f"⚠️  POSSIBLE SUCCESS: {username}:{password} (redirect to {location})")
                                else:
                                    results.append(f"  Tested: {username}:{password} - Redirect to {location}")
                            elif status == 200:
                                results.append(f"  Tested: {username}:{password} - No redirect (likely failed)")
                            else:
                                results.append(f"  Tested: {username}:{password} - Status {status}")
                            
                            tested += 1
                            await asyncio.sleep(1)  # Rate limiting
                    except:
                        results.append(f"  Tested: {username}:{password} - Connection error")
                        tested += 1
            
            results.append(f"\n✓ Tested {tested} credential pairs")
            results.append("Note: Manual verification required for any potential matches")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'login_check.txt', output)
            
            return {
                'status': 'success',
                'output': output,
                'tested': tested,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def check_rate_limiting(self, target: str) -> Dict[str, any]:
        """Check for rate limiting on login attempts"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            results.append("Testing for rate limiting...\n")
            
            # Make multiple rapid requests
            num_requests = 10
            response_times = []
            statuses = []
            
            async with aiohttp.ClientSession() as session:
                for i in range(num_requests):
                    start_time = asyncio.get_event_loop().time()
                    try:
                        async with session.post(target, 
                                               data={'username': 'test', 'password': 'test'},
                                               timeout=aiohttp.ClientTimeout(total=10),
                                               headers={'User-Agent': self.user_agent},
                                               allow_redirects=False) as resp:
                            elapsed = asyncio.get_event_loop().time() - start_time
                            response_times.append(elapsed)
                            statuses.append(resp.status)
                    except:
                        response_times.append(0)
                        statuses.append(0)
                    
                    await asyncio.sleep(0.1)  # Small delay between requests
            
            # Analyze results
            results.append(f"Made {num_requests} requests:")
            for i, (status, time) in enumerate(zip(statuses, response_times), 1):
                results.append(f"  Request {i}: Status {status}, Time {time:.2f}s")
            
            # Check for rate limiting indicators
            has_rate_limit = False
            if 429 in statuses:  # Too Many Requests
                has_rate_limit = True
                results.append("\n✓ Rate limiting detected (HTTP 429)")
            elif any(t > 5 for t in response_times):
                results.append("\n⚠️  Possible rate limiting (slow responses detected)")
            else:
                results.append("\n⚠️  WARNING: No obvious rate limiting detected!")
                results.append("  The login form may be vulnerable to brute force attacks")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'login_check.txt', output)
            
            return {
                'status': 'success',
                'has_rate_limit': has_rate_limit,
                'output': output,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def full_check(self, target: str, credentials: List[Tuple[str, str]]) -> Dict[str, any]:
        """Run all login security checks"""
        results = []
        
        results.append("=== LOGIN PAGE DETECTION ===")
        r = await self.detect_login_page(target)
        results.append(r.get('output', r.get('message', '')))
        
        if r.get('is_login'):
            results.append("\n\n=== CSRF PROTECTION ===")
            r = await self.check_csrf_protection(target)
            results.append(r.get('output', r.get('message', '')))
            
            results.append("\n\n=== RATE LIMITING ===")
            r = await self.check_rate_limiting(target)
            results.append(r.get('output', r.get('message', '')))
            
            results.append("\n\n=== DEFAULT CREDENTIALS TEST ===")
            r = await self.test_default_credentials(target, credentials)
            results.append(r.get('output', r.get('message', '')))
        
        output = "\n".join(results)
        filepath = self._save_result(target, 'login_full_check.txt', output)
        
        return {
            'status': 'success',
            'output': output,
            'file': filepath
        }


# Export functions
async def check_login(target: str, results_folder: str, 
                     credentials: List[Tuple[str, str]]) -> Dict[str, any]:
    module = LoginCheckerModule(results_folder)
    return await module.full_check(target, credentials)
