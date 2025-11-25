"""
Directory and File Finder - Real Directory Bruteforce
"""

import aiohttp
import asyncio
import os
import re
from datetime import datetime
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse


class DirFinderModule:
    def __init__(self, results_folder: str):
        self.results_folder = results_folder
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.found_paths = set()
    
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
            f.write(f"Directory Scan Results\n")
            f.write(f"Target: {target}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(content)
        return filepath
    
    def _get_default_wordlist(self) -> List[str]:
        """Generate default wordlist if no file exists"""
        return [
            # Common directories
            'admin', 'administrator', 'login', 'wp-admin', 'phpmyadmin',
            'dashboard', 'cpanel', 'panel', 'control', 'manage',
            'backup', 'backups', 'old', 'new', 'test', 'dev', 'staging',
            'api', 'v1', 'v2', 'rest', 'graphql',
            'uploads', 'files', 'images', 'img', 'assets', 'static',
            'css', 'js', 'javascript', 'scripts', 'style',
            'includes', 'inc', 'lib', 'libraries', 'vendor',
            'config', 'configuration', 'settings', 'setup',
            'install', 'installation', 'installer',
            'database', 'db', 'sql', 'mysql',
            'temp', 'tmp', 'cache', 'logs', 'log',
            'download', 'downloads', 'upload',
            'user', 'users', 'account', 'accounts',
            'profile', 'profiles', 'member', 'members',
            'public', 'private', 'secret', 'hidden',
            'docs', 'documentation', 'doc', 'help',
            'blog', 'news', 'forum', 'forums',
            'shop', 'store', 'cart', 'checkout',
            'search', 'find', 'query',
            
            # Common files
            'robots.txt', 'sitemap.xml', 'humans.txt',
            '.htaccess', '.htpasswd', '.env', '.git',
            'web.config', 'config.php', 'configuration.php',
            'settings.php', 'database.php', 'db.php',
            'index.php', 'index.html', 'index.htm',
            'admin.php', 'login.php', 'logout.php',
            'readme.txt', 'README.md', 'LICENSE',
            'changelog.txt', 'CHANGELOG.md',
            'phpinfo.php', 'info.php', 'test.php',
            'backup.sql', 'dump.sql', 'database.sql',
            'backup.zip', 'backup.tar.gz', 'site.zip',
            '.git/HEAD', '.git/config', '.svn/entries',
            'composer.json', 'package.json', 'package-lock.json',
            'yarn.lock', 'Gemfile', 'requirements.txt',
        ]
    
    async def _check_path(self, session: aiohttp.ClientSession, base_url: str, 
                         path: str, semaphore: asyncio.Semaphore) -> Dict[str, any]:
        """Check if a path exists"""
        async with semaphore:
            url = urljoin(base_url, path)
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5),
                                      headers={'User-Agent': self.user_agent},
                                      allow_redirects=False) as resp:
                    return {
                        'path': path,
                        'url': url,
                        'status': resp.status,
                        'size': resp.content_length or 0,
                        'found': resp.status in [200, 201, 204, 301, 302, 307, 308, 401, 403]
                    }
            except asyncio.TimeoutError:
                return {'path': path, 'url': url, 'status': 0, 'size': 0, 'found': False}
            except:
                return {'path': path, 'url': url, 'status': 0, 'size': 0, 'found': False}
    
    async def scan_directories(self, target: str, wordlist_path: str = None, 
                              max_concurrent: int = 20) -> Dict[str, any]:
        """Scan for directories and files"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            # Ensure target ends with /
            if not target.endswith('/'):
                target += '/'
            
            # Load wordlist
            wordlist = []
            if wordlist_path and os.path.exists(wordlist_path):
                with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                    wordlist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            else:
                wordlist = self._get_default_wordlist()
            
            results = []
            found_items = []
            
            results.append(f"Starting directory scan on: {target}")
            results.append(f"Wordlist size: {len(wordlist)} entries")
            results.append(f"Max concurrent requests: {max_concurrent}\n")
            
            # Create semaphore for rate limiting
            semaphore = asyncio.Semaphore(max_concurrent)
            
            # Scan paths
            async with aiohttp.ClientSession() as session:
                tasks = [self._check_path(session, target, path, semaphore) 
                        for path in wordlist]
                
                # Process results as they complete
                completed = 0
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    completed += 1
                    
                    if result['found']:
                        status = result['status']
                        size = result['size']
                        path = result['path']
                        url = result['url']
                        
                        # Determine status description
                        status_desc = {
                            200: 'OK',
                            201: 'Created',
                            204: 'No Content',
                            301: 'Moved Permanently',
                            302: 'Found (Redirect)',
                            307: 'Temporary Redirect',
                            308: 'Permanent Redirect',
                            401: 'Unauthorized',
                            403: 'Forbidden'
                        }.get(status, str(status))
                        
                        entry = f"[{status}] [{size:>8} bytes] {path}"
                        found_items.append(entry)
                        self.found_paths.add(url)
                    
                    # Progress indicator (every 10%)
                    if completed % max(1, len(wordlist) // 10) == 0:
                        progress = (completed / len(wordlist)) * 100
                        results.append(f"Progress: {progress:.0f}% ({completed}/{len(wordlist)})")
            
            # Sort and format results
            found_items.sort()
            
            results.append(f"\n{'='*60}")
            results.append(f"Scan Complete!")
            results.append(f"Found {len(found_items)} accessible paths:\n")
            
            if found_items:
                results.extend(found_items)
            else:
                results.append("No accessible paths found with the current wordlist.")
            
            output = "\n".join(results)
            filepath = self._save_result(target, 'dirs.txt', output)
            
            return {
                'status': 'success',
                'output': output,
                'found_count': len(found_items),
                'total_checked': len(wordlist),
                'file': filepath,
                'found_paths': list(self.found_paths)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def quick_scan(self, target: str) -> Dict[str, any]:
        """Quick scan with minimal wordlist"""
        quick_list = [
            'admin', 'login', 'wp-admin', 'phpmyadmin', 'dashboard',
            'robots.txt', 'sitemap.xml', '.git', '.env',
            'backup', 'config', 'api', 'uploads',
            'index.php', 'admin.php', 'login.php',
            '.htaccess', 'web.config', 'phpinfo.php'
        ]
        
        if not target.startswith('http'):
            target = f"http://{target}"
        if not target.endswith('/'):
            target += '/'
        
        results = []
        found_items = []
        
        semaphore = asyncio.Semaphore(10)
        
        async with aiohttp.ClientSession() as session:
            tasks = [self._check_path(session, target, path, semaphore) 
                    for path in quick_list]
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result['found']:
                    entry = f"[{result['status']}] {result['path']}"
                    found_items.append(entry)
        
        results.append(f"Quick scan results for: {target}\n")
        if found_items:
            results.append(f"Found {len(found_items)} items:")
            results.extend(sorted(found_items))
        else:
            results.append("No common paths found.")
        
        output = "\n".join(results)
        filepath = self._save_result(target, 'dirs_quick.txt', output)
        
        return {
            'status': 'success',
            'output': output,
            'found_count': len(found_items),
            'file': filepath
        }


# Export functions
async def scan_directories(target: str, results_folder: str, 
                          wordlist_path: str = None) -> Dict[str, any]:
    module = DirFinderModule(results_folder)
    return await module.scan_directories(target, wordlist_path)

async def quick_scan(target: str, results_folder: str) -> Dict[str, any]:
    module = DirFinderModule(results_folder)
    return await module.quick_scan(target)
