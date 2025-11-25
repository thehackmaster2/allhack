"""
Login Test Module - Security Testing for Login Pages
⚠️ EDUCATIONAL USE ONLY - Authorized Testing Only

Features:
- SQL Injection Testing (Safe Mode)
- Weak Login Page Analysis
- Sensitive File Discovery
- Directory Fingerprinting
"""

import aiohttp
import asyncio
import os
import re
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class LoginTester:
    def __init__(self, results_folder: str):
        self.results_folder = results_folder
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.findings = []
        
        # SQL Injection payloads (safe mode - detection only)
        self.sqli_payloads = [
            "' OR '1'='1",
            "\" OR \"1\"=\"1",
            "OR 1=1--",
            "' OR ''='",
            "admin' --",
            "' OR 1=1--",
            "admin'/*",
            "' UNION SELECT NULL--",
            "1' AND '1'='1",
        ]
        
        # Sensitive files to check
        self.sensitive_files = [
            "cre.txt",
            "credentials.txt",
            "pass.txt",
            "passwd",
            "admin.txt",
            "backup.zip",
            "users.txt",
            "password.txt",
            ".env",
            "config.php",
            "config.old",
            "database.sql",
            "db.sql",
            "dump.sql",
            "login.txt",
            "passwords.txt",
            "users.sql",
            "backup.sql",
            ".git/config",
            "wp-config.php",
            "config.inc.php",
        ]
        
        # Common credential directories
        self.credential_dirs = [
            "/admin/",
            "/admins/",
            "/login/",
            "/backup/",
            "/old/",
            "/test/",
            "/dev/",
            "/debug/",
            "/config/",
            "/private/",
            "/secret/",
            "/credentials/",
        ]
    
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
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"Login Security Test Report\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {target}\n")
            f.write(f"{'='*60}\n\n")
            f.write(content)
        return filepath
    
    async def test_sql_injection(self, url: str, form_details: Dict) -> List[Dict]:
        """Test for SQL injection vulnerabilities (safe mode)"""
        vulnerabilities = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for payload in self.sqli_payloads:
                    try:
                        # Build test data
                        data = {
                            form_details.get('username_field', 'username'): payload,
                            form_details.get('password_field', 'password'): 'test123'
                        }
                        
                        # Add hidden fields
                        data.update(form_details.get('extra_fields', {}))
                        
                        # Send request
                        async with session.post(
                            form_details.get('form_url', url),
                            data=data,
                            headers={'User-Agent': self.user_agent},
                            timeout=aiohttp.ClientTimeout(total=10),
                            allow_redirects=True
                        ) as resp:
                            text = await resp.text()
                            status = resp.status
                            
                            # Check for SQL error messages
                            sql_errors = [
                                'sql syntax',
                                'mysql_fetch',
                                'mysql error',
                                'ora-',
                                'postgresql',
                                'sqlite',
                                'syntax error',
                                'unclosed quotation',
                                'quoted string',
                                'database error',
                            ]
                            
                            text_lower = text.lower()
                            for error in sql_errors:
                                if error in text_lower:
                                    vulnerabilities.append({
                                        'type': 'SQL Injection',
                                        'payload': payload,
                                        'evidence': f'SQL error detected: {error}',
                                        'severity': 'HIGH'
                                    })
                                    break
                            
                            # Check for unexpected success
                            if status == 200 and 'welcome' in text_lower or 'dashboard' in text_lower:
                                vulnerabilities.append({
                                    'type': 'SQL Injection',
                                    'payload': payload,
                                    'evidence': 'Possible authentication bypass',
                                    'severity': 'CRITICAL'
                                })
                        
                        await asyncio.sleep(0.2)  # Rate limiting
                    
                    except Exception:
                        continue
        
        except Exception as e:
            self.findings.append(f"SQL injection test error: {str(e)}")
        
        return vulnerabilities
    
    async def analyze_page_source(self, url: str) -> List[Dict]:
        """Analyze page source for hardcoded credentials and secrets"""
        findings = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': self.user_agent},
                                      timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    html = await resp.text()
                    
                    # Check for hardcoded credentials in HTML
                    patterns = {
                        'Hardcoded Password': r'password\s*[:=]\s*["\']([^"\']+)["\']',
                        'Hardcoded Username': r'username\s*[:=]\s*["\']([^"\']+)["\']',
                        'API Key': r'api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
                        'Secret Token': r'secret\s*[:=]\s*["\']([^"\']+)["\']',
                        'Database Password': r'db[_-]?pass(?:word)?\s*[:=]\s*["\']([^"\']+)["\']',
                    }
                    
                    for name, pattern in patterns.items():
                        matches = re.findall(pattern, html, re.IGNORECASE)
                        for match in matches:
                            if len(match) > 3 and match not in ['password', 'username', 'admin']:
                                findings.append({
                                    'type': name,
                                    'evidence': f'Found: {match}',
                                    'severity': 'HIGH'
                                })
                    
                    # Check for commented credentials
                    comment_pattern = r'<!--.*?(password|username|admin|secret).*?-->'
                    comments = re.findall(comment_pattern, html, re.IGNORECASE | re.DOTALL)
                    if comments:
                        findings.append({
                            'type': 'Commented Credentials',
                            'evidence': f'Found {len(comments)} suspicious comments',
                            'severity': 'MEDIUM'
                        })
                    
                    # Check for debug mode
                    if 'debug' in html.lower() and ('true' in html.lower() or '1' in html):
                        findings.append({
                            'type': 'Debug Mode',
                            'evidence': 'Debug mode appears to be enabled',
                            'severity': 'MEDIUM'
                        })
        
        except Exception as e:
            self.findings.append(f"Page analysis error: {str(e)}")
        
        return findings
    
    async def discover_sensitive_files(self, url: str) -> List[Dict]:
        """Discover sensitive files on the server"""
        found_files = []
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        try:
            async with aiohttp.ClientSession() as session:
                for filename in self.sensitive_files:
                    try:
                        test_url = urljoin(base_url, filename)
                        
                        async with session.get(
                            test_url,
                            headers={'User-Agent': self.user_agent},
                            timeout=aiohttp.ClientTimeout(total=5),
                            allow_redirects=False
                        ) as resp:
                            if resp.status == 200:
                                content_type = resp.headers.get('Content-Type', '')
                                size = resp.headers.get('Content-Length', 'unknown')
                                
                                found_files.append({
                                    'type': 'Sensitive File',
                                    'file': filename,
                                    'url': test_url,
                                    'status': resp.status,
                                    'size': size,
                                    'content_type': content_type,
                                    'severity': 'CRITICAL'
                                })
                        
                        await asyncio.sleep(0.1)
                    
                    except Exception:
                        continue
        
        except Exception as e:
            self.findings.append(f"File discovery error: {str(e)}")
        
        return found_files
    
    async def fingerprint_directories(self, url: str) -> List[Dict]:
        """Fingerprint common credential directories"""
        found_dirs = []
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        try:
            async with aiohttp.ClientSession() as session:
                for directory in self.credential_dirs:
                    try:
                        test_url = urljoin(base_url, directory)
                        
                        async with session.get(
                            test_url,
                            headers={'User-Agent': self.user_agent},
                            timeout=aiohttp.ClientTimeout(total=5),
                            allow_redirects=False
                        ) as resp:
                            if resp.status in [200, 403, 401]:
                                found_dirs.append({
                                    'type': 'Directory Found',
                                    'directory': directory,
                                    'url': test_url,
                                    'status': resp.status,
                                    'severity': 'MEDIUM' if resp.status == 200 else 'LOW'
                                })
                        
                        await asyncio.sleep(0.1)
                    
                    except Exception:
                        continue
        
        except Exception as e:
            self.findings.append(f"Directory fingerprinting error: {str(e)}")
        
        return found_dirs
    
    async def get_form_details(self, url: str) -> Dict:
        """Get login form details for testing"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': self.user_agent},
                                      timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    form = soup.find('form')
                    if not form:
                        return {}
                    
                    action = form.get('action', '')
                    form_url = urljoin(url, action) if action else url
                    
                    inputs = form.find_all('input')
                    username_field = None
                    password_field = None
                    extra_fields = {}
                    
                    for inp in inputs:
                        name = inp.get('name', '')
                        inp_type = inp.get('type', '').lower()
                        value = inp.get('value', '')
                        
                        if inp_type == 'password':
                            password_field = name
                        elif inp_type in ['text', 'email'] or 'user' in name.lower():
                            if not username_field:
                                username_field = name
                        elif inp_type == 'hidden':
                            extra_fields[name] = value
                    
                    return {
                        'form_url': form_url,
                        'username_field': username_field or 'username',
                        'password_field': password_field or 'password',
                        'extra_fields': extra_fields
                    }
        except Exception:
            return {}
    
    async def run_security_test(self, url: str, progress_callback=None) -> Dict:
        """Run complete security test on login page"""
        try:
            results = []
            all_findings = []
            
            results.append("🔒 Login Security Test Started")
            results.append(f"Target: {url}\n")
            
            # Get form details
            if progress_callback:
                await progress_callback("Analyzing login form...")
            
            form_details = await self.get_form_details(url)
            
            if form_details:
                results.append(f"✓ Login form detected")
                results.append(f"  Form URL: {form_details.get('form_url')}")
                results.append(f"  Username field: {form_details.get('username_field')}")
                results.append(f"  Password field: {form_details.get('password_field')}\n")
            
            # Test 1: SQL Injection
            if progress_callback:
                await progress_callback("Testing for SQL injection...")
            
            results.append("📋 SQL Injection Testing...")
            sqli_vulns = await self.test_sql_injection(url, form_details)
            
            if sqli_vulns:
                results.append(f"  ⚠️ Found {len(sqli_vulns)} potential SQL injection points!")
                for vuln in sqli_vulns:
                    results.append(f"    - {vuln['evidence']}")
                    all_findings.append(vuln)
            else:
                results.append("  ✓ No SQL injection vulnerabilities detected")
            results.append("")
            
            # Test 2: Page Source Analysis
            if progress_callback:
                await progress_callback("Analyzing page source...")
            
            results.append("📋 Page Source Analysis...")
            source_findings = await self.analyze_page_source(url)
            
            if source_findings:
                results.append(f"  ⚠️ Found {len(source_findings)} security issues!")
                for finding in source_findings:
                    results.append(f"    - {finding['type']}: {finding['evidence']}")
                    all_findings.append(finding)
            else:
                results.append("  ✓ No hardcoded credentials found")
            results.append("")
            
            # Test 3: Sensitive File Discovery
            if progress_callback:
                await progress_callback("Scanning for sensitive files...")
            
            results.append("📋 Sensitive File Discovery...")
            files = await self.discover_sensitive_files(url)
            
            if files:
                results.append(f"  ⚠️ Found {len(files)} sensitive files!")
                for file in files:
                    results.append(f"    - {file['file']} ({file['status']}) - {file['url']}")
                    all_findings.append(file)
            else:
                results.append("  ✓ No sensitive files found")
            results.append("")
            
            # Test 4: Directory Fingerprinting
            if progress_callback:
                await progress_callback("Fingerprinting directories...")
            
            results.append("📋 Directory Fingerprinting...")
            dirs = await self.fingerprint_directories(url)
            
            if dirs:
                results.append(f"  ℹ️ Found {len(dirs)} directories:")
                for directory in dirs:
                    results.append(f"    - {directory['directory']} ({directory['status']})")
                    all_findings.append(directory)
            else:
                results.append("  ✓ No common directories found")
            results.append("")
            
            # Summary
            critical = len([f for f in all_findings if f.get('severity') == 'CRITICAL'])
            high = len([f for f in all_findings if f.get('severity') == 'HIGH'])
            medium = len([f for f in all_findings if f.get('severity') == 'MEDIUM'])
            low = len([f for f in all_findings if f.get('severity') == 'LOW'])
            
            results.append("="*40)
            results.append("📊 SECURITY SUMMARY")
            results.append("="*40)
            results.append(f"Total Findings: {len(all_findings)}")
            if critical > 0:
                results.append(f"🔴 Critical: {critical}")
            if high > 0:
                results.append(f"🟠 High: {high}")
            if medium > 0:
                results.append(f"🟡 Medium: {medium}")
            if low > 0:
                results.append(f"🟢 Low: {low}")
            
            if len(all_findings) == 0:
                results.append("\n✅ No major security issues detected!")
            else:
                results.append("\n⚠️ Security issues found - review recommended!")
            
            output = "\n".join(results)
            
            # Save detailed report
            filepath = self._save_result(url, 'login_test_report.txt', output)
            
            # Save leaked files if any
            if files:
                leaks_content = "\n".join([f"{f['file']}: {f['url']}" for f in files])
                self._save_result(url, 'login_test_leaks.txt', leaks_content)
            
            return {
                'status': 'success',
                'output': output,
                'findings': all_findings,
                'file': filepath,
                'summary': {
                    'total': len(all_findings),
                    'critical': critical,
                    'high': high,
                    'medium': medium,
                    'low': low
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Export function
async def test_login_security(url: str, results_folder: str, 
                              progress_callback=None) -> Dict:
    """Test login page security - Educational/Authorized use only"""
    tester = LoginTester(results_folder)
    return await tester.run_security_test(url, progress_callback)
