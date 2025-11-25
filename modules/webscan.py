"""
Web Vulnerability Scanner - Real Security Testing
"""

import aiohttp
import asyncio
import re
import os
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin, urlparse


class WebScanModule:
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
    
    async def scan_headers(self, target: str) -> Dict[str, any]:
        """Check for missing security headers"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            security_headers = {
                'Strict-Transport-Security': 'HSTS not set - Site vulnerable to protocol downgrade attacks',
                'X-Frame-Options': 'X-Frame-Options not set - Clickjacking possible',
                'X-Content-Type-Options': 'X-Content-Type-Options not set - MIME sniffing possible',
                'Content-Security-Policy': 'CSP not set - XSS protection reduced',
                'X-XSS-Protection': 'X-XSS-Protection not set',
                'Referrer-Policy': 'Referrer-Policy not set - Information leakage possible',
                'Permissions-Policy': 'Permissions-Policy not set'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    headers = resp.headers
                    
                    results.append(f"Status Code: {resp.status}")
                    results.append(f"\nPresent Headers:")
                    for key, value in headers.items():
                        results.append(f"  {key}: {value}")
                    
                    results.append(f"\n\nSecurity Analysis:")
                    missing_count = 0
                    for header, warning in security_headers.items():
                        if header not in headers:
                            results.append(f"  ⚠️  {warning}")
                            missing_count += 1
                        else:
                            results.append(f"  ✓ {header}: {headers[header]}")
                    
                    # Check for information disclosure
                    if 'Server' in headers:
                        results.append(f"\n  ℹ️  Server header reveals: {headers['Server']}")
                    if 'X-Powered-By' in headers:
                        results.append(f"  ℹ️  X-Powered-By reveals: {headers['X-Powered-By']}")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'webscan.txt', f"Security Headers Scan:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'missing_headers': missing_count,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def scan_cookies(self, target: str) -> Dict[str, any]:
        """Analyze cookie security"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    
                    if not resp.cookies:
                        results.append("No cookies set by the server")
                    else:
                        results.append(f"Found {len(resp.cookies)} cookie(s):\n")
                        
                        for cookie in resp.cookies.values():
                            results.append(f"Cookie: {cookie.key}")
                            results.append(f"  Value: {cookie.value[:50]}..." if len(cookie.value) > 50 else f"  Value: {cookie.value}")
                            
                            # Security checks
                            issues = []
                            if not cookie.get('secure'):
                                issues.append("⚠️  Secure flag not set - Can be transmitted over HTTP")
                            if not cookie.get('httponly'):
                                issues.append("⚠️  HttpOnly flag not set - Accessible via JavaScript (XSS risk)")
                            if not cookie.get('samesite'):
                                issues.append("⚠️  SameSite not set - CSRF attacks possible")
                            
                            if issues:
                                results.append("  Issues:")
                                for issue in issues:
                                    results.append(f"    {issue}")
                            else:
                                results.append("  ✓ Cookie appears secure")
                            results.append("")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'webscan.txt', f"Cookie Security Scan:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def test_xss(self, target: str) -> Dict[str, any]:
        """Test for XSS reflection"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            payloads = [
                '<script>alert(1)</script>',
                '"><script>alert(1)</script>',
                '<img src=x onerror=alert(1)>',
                'javascript:alert(1)',
                '<svg/onload=alert(1)>'
            ]
            
            # Test in URL parameters
            test_param = 'xss_test'
            reflected = []
            
            async with aiohttp.ClientSession() as session:
                for payload in payloads:
                    test_url = f"{target}?{test_param}={payload}"
                    try:
                        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10),
                                              headers={'User-Agent': self.user_agent},
                                              allow_redirects=False) as resp:
                            html = await resp.text()
                            
                            # Check if payload is reflected in response
                            if payload in html:
                                reflected.append(f"⚠️  Payload reflected: {payload}")
                                results.append(f"Potential XSS found with payload: {payload}")
                                results.append(f"  URL: {test_url}")
                                results.append(f"  Payload found in response body\n")
                    except:
                        pass
            
            if not reflected:
                results.append("✓ No XSS reflection detected in basic tests")
                results.append("Note: This is a basic test. Manual testing recommended.")
            else:
                results.append(f"\n⚠️  WARNING: {len(reflected)} potential XSS vulnerabilities found!")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'webscan.txt', f"XSS Test Results:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'vulnerabilities': len(reflected),
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def test_sqli(self, target: str) -> Dict[str, any]:
        """Test for SQL injection (boolean-based)"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            payloads = [
                ("' OR '1'='1", "true_condition"),
                ("' OR '1'='2", "false_condition"),
                ("' AND '1'='1", "true_and"),
                ("' AND '1'='2", "false_and"),
                ("1' OR '1'='1", "numeric_true"),
                ("1' OR '1'='2", "numeric_false"),
            ]
            
            test_param = 'id'
            responses = {}
            
            async with aiohttp.ClientSession() as session:
                # Get baseline
                try:
                    async with session.get(f"{target}?{test_param}=1", 
                                          timeout=aiohttp.ClientTimeout(total=10),
                                          headers={'User-Agent': self.user_agent}) as resp:
                        baseline_length = len(await resp.text())
                        baseline_status = resp.status
                except:
                    baseline_length = 0
                    baseline_status = 0
                
                # Test payloads
                for payload, ptype in payloads:
                    test_url = f"{target}?{test_param}={payload}"
                    try:
                        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10),
                                              headers={'User-Agent': self.user_agent},
                                              allow_redirects=False) as resp:
                            content = await resp.text()
                            responses[ptype] = {
                                'length': len(content),
                                'status': resp.status,
                                'payload': payload
                            }
                    except:
                        pass
            
            # Analyze responses
            vulnerabilities = []
            
            # Check for boolean-based SQLi
            if 'true_condition' in responses and 'false_condition' in responses:
                true_len = responses['true_condition']['length']
                false_len = responses['false_condition']['length']
                
                if true_len != false_len and abs(true_len - false_len) > 100:
                    vulnerabilities.append("⚠️  Possible Boolean-based SQL Injection detected!")
                    vulnerabilities.append(f"  True condition response: {true_len} bytes")
                    vulnerabilities.append(f"  False condition response: {false_len} bytes")
            
            # Check for error-based
            for ptype, data in responses.items():
                if data['status'] == 500:
                    vulnerabilities.append(f"⚠️  Server error (500) with payload: {data['payload']}")
            
            if vulnerabilities:
                results.extend(vulnerabilities)
                results.append(f"\n⚠️  WARNING: Potential SQL injection indicators found!")
            else:
                results.append("✓ No obvious SQL injection vulnerabilities detected")
                results.append("Note: This is a basic test. Manual testing recommended.")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'webscan.txt', f"SQL Injection Test:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'vulnerabilities': len(vulnerabilities),
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def scan_robots(self, target: str) -> Dict[str, any]:
        """Parse robots.txt"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            parsed = urlparse(target)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            results = []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10),
                                      headers={'User-Agent': self.user_agent}) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        results.append(f"robots.txt found at: {robots_url}\n")
                        results.append("Content:")
                        results.append(content)
                        
                        # Extract interesting paths
                        disallowed = re.findall(r'Disallow:\s*(.+)', content, re.IGNORECASE)
                        if disallowed:
                            results.append(f"\n\nDisallowed paths ({len(disallowed)}):")
                            for path in disallowed[:20]:  # Limit output
                                results.append(f"  {path.strip()}")
                    else:
                        results.append(f"robots.txt not found (Status: {resp.status})")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'webscan.txt', f"robots.txt Analysis:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def full_scan(self, target: str) -> Dict[str, any]:
        """Run all web scans"""
        results = []
        
        results.append("=== SECURITY HEADERS ===")
        r = await self.scan_headers(target)
        results.append(r.get('output', r.get('message', '')))
        
        results.append("\n\n=== COOKIE SECURITY ===")
        r = await self.scan_cookies(target)
        results.append(r.get('output', r.get('message', '')))
        
        results.append("\n\n=== XSS TESTING ===")
        r = await self.test_xss(target)
        results.append(r.get('output', r.get('message', '')))
        
        results.append("\n\n=== SQL INJECTION TESTING ===")
        r = await self.test_sqli(target)
        results.append(r.get('output', r.get('message', '')))
        
        results.append("\n\n=== ROBOTS.TXT ===")
        r = await self.scan_robots(target)
        results.append(r.get('output', r.get('message', '')))
        
        output = "\n".join(results)
        filepath = self._save_result(target, 'webscan_full.txt', output)
        
        return {
            'status': 'success',
            'output': output,
            'file': filepath
        }


# Export functions
async def scan_target(target: str, results_folder: str) -> Dict[str, any]:
    module = WebScanModule(results_folder)
    return await module.full_scan(target)
