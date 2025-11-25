"""
Reconnaissance Module - Real OSINT and Network Scanning
"""

import subprocess
import asyncio
import os
import socket
import re
from datetime import datetime
import aiohttp
from typing import Dict, List, Optional


class ReconModule:
    def __init__(self, results_folder: str):
        self.results_folder = results_folder
    
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
    
    async def run_whois(self, target: str) -> Dict[str, str]:
        """Run real WHOIS lookup"""
        try:
            # Clean target (remove http/https)
            clean_target = re.sub(r'^https?://', '', target).split('/')[0]
            
            process = await asyncio.create_subprocess_exec(
                'whois', clean_target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            output = stdout.decode('utf-8', errors='ignore')
            
            if not output or stderr:
                return {
                    'status': 'error',
                    'message': f'WHOIS failed: {stderr.decode()}',
                    'output': ''
                }
            
            # Save results
            filepath = self._save_result(target, 'recon.txt', f"WHOIS Results:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except asyncio.TimeoutError:
            return {'status': 'error', 'message': 'WHOIS timeout', 'output': ''}
        except FileNotFoundError:
            return {'status': 'error', 'message': 'whois command not found. Install with: apt install whois', 'output': ''}
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def run_dns(self, target: str) -> Dict[str, str]:
        """Run real DNS lookup using dig"""
        try:
            clean_target = re.sub(r'^https?://', '', target).split('/')[0]
            
            results = []
            
            # A records
            for record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']:
                process = await asyncio.create_subprocess_exec(
                    'dig', clean_target, record_type, '+short',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                output = stdout.decode('utf-8', errors='ignore').strip()
                
                if output:
                    results.append(f"{record_type} Records:\n{output}\n")
            
            full_output = "\n".join(results)
            
            if not full_output:
                # Fallback to socket DNS
                try:
                    ip = socket.gethostbyname(clean_target)
                    full_output = f"A Record (via socket):\n{ip}\n"
                except:
                    pass
            
            filepath = self._save_result(target, 'recon.txt', f"DNS Results:\n{full_output}")
            
            return {
                'status': 'success',
                'output': full_output if full_output else 'No DNS records found',
                'file': filepath
            }
        except FileNotFoundError:
            # Fallback to socket
            try:
                clean_target = re.sub(r'^https?://', '', target).split('/')[0]
                ip = socket.gethostbyname(clean_target)
                output = f"A Record:\n{ip}\n"
                filepath = self._save_result(target, 'recon.txt', f"DNS Results:\n{output}")
                return {'status': 'success', 'output': output, 'file': filepath}
            except Exception as e:
                return {'status': 'error', 'message': str(e), 'output': ''}
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def run_subdomains(self, target: str) -> Dict[str, str]:
        """Enumerate subdomains using crt.sh and DNS queries"""
        try:
            clean_target = re.sub(r'^https?://', '', target).split('/')[0]
            subdomains = set()
            
            # Method 1: crt.sh certificate transparency
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://crt.sh/?q=%.{clean_target}&output=json"
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for entry in data:
                                name = entry.get('name_value', '')
                                for subdomain in name.split('\n'):
                                    subdomain = subdomain.strip().lower()
                                    if subdomain and clean_target in subdomain:
                                        subdomains.add(subdomain)
            except Exception as e:
                pass
            
            # Method 2: Common subdomain bruteforce
            common_subs = ['www', 'mail', 'ftp', 'admin', 'webmail', 'smtp', 'pop', 'ns1', 'ns2', 
                          'cpanel', 'whm', 'blog', 'dev', 'staging', 'api', 'test', 'portal']
            
            for sub in common_subs:
                try:
                    full_domain = f"{sub}.{clean_target}"
                    ip = socket.gethostbyname(full_domain)
                    subdomains.add(f"{full_domain} -> {ip}")
                except:
                    pass
            
            output = "\n".join(sorted(subdomains)) if subdomains else "No subdomains found"
            filepath = self._save_result(target, 'recon.txt', f"Subdomain Enumeration:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'count': len(subdomains),
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def run_ports(self, target: str) -> Dict[str, str]:
        """Run real port scan using nmap"""
        try:
            clean_target = re.sub(r'^https?://', '', target).split('/')[0]
            
            # Try to resolve to IP
            try:
                ip = socket.gethostbyname(clean_target)
            except:
                ip = clean_target
            
            # Run nmap
            process = await asyncio.create_subprocess_exec(
                'nmap', '-Pn', '-sV', '--top-ports', '100', '-T4', ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            
            output = stdout.decode('utf-8', errors='ignore')
            
            if not output or 'command not found' in output.lower():
                # Fallback to basic socket scan
                output = await self._socket_port_scan(ip)
            
            filepath = self._save_result(target, 'recon.txt', f"Port Scan Results:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except asyncio.TimeoutError:
            return {'status': 'error', 'message': 'Port scan timeout', 'output': ''}
        except FileNotFoundError:
            # Fallback to socket scan
            try:
                clean_target = re.sub(r'^https?://', '', target).split('/')[0]
                ip = socket.gethostbyname(clean_target)
                output = await self._socket_port_scan(ip)
                filepath = self._save_result(target, 'recon.txt', f"Port Scan Results:\n{output}")
                return {'status': 'success', 'output': output, 'file': filepath}
            except Exception as e:
                return {'status': 'error', 'message': str(e), 'output': ''}
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}
    
    async def _socket_port_scan(self, ip: str) -> str:
        """Fallback port scanner using sockets"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(f"{port}/tcp open")
                sock.close()
            except:
                pass
        
        if open_ports:
            return f"Open ports on {ip}:\n" + "\n".join(open_ports)
        return f"No open ports found on {ip} (common ports checked)"
    
    async def run_techscan(self, target: str) -> Dict[str, str]:
        """Detect web technologies"""
        try:
            if not target.startswith('http'):
                target = f"http://{target}"
            
            results = []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=10), 
                                      allow_redirects=True) as resp:
                    headers = resp.headers
                    html = await resp.text()
                    
                    # Server detection
                    if 'Server' in headers:
                        results.append(f"Server: {headers['Server']}")
                    
                    # Technology detection
                    if 'X-Powered-By' in headers:
                        results.append(f"Powered By: {headers['X-Powered-By']}")
                    
                    # Framework detection
                    if 'wordpress' in html.lower():
                        results.append("CMS: WordPress detected")
                    if 'joomla' in html.lower():
                        results.append("CMS: Joomla detected")
                    if 'drupal' in html.lower():
                        results.append("CMS: Drupal detected")
                    
                    # JavaScript frameworks
                    if 'react' in html.lower():
                        results.append("Framework: React.js detected")
                    if 'angular' in html.lower():
                        results.append("Framework: Angular detected")
                    if 'vue' in html.lower():
                        results.append("Framework: Vue.js detected")
                    
                    # Other headers
                    for header in ['X-AspNet-Version', 'X-AspNetMvc-Version', 'X-Frame-Options', 
                                  'X-Content-Type-Options', 'Strict-Transport-Security']:
                        if header in headers:
                            results.append(f"{header}: {headers[header]}")
            
            output = "\n".join(results) if results else "No technologies detected"
            filepath = self._save_result(target, 'recon.txt', f"Technology Scan:\n{output}")
            
            return {
                'status': 'success',
                'output': output,
                'file': filepath
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'output': ''}


# Export functions
async def run_whois(target: str, results_folder: str) -> Dict[str, str]:
    module = ReconModule(results_folder)
    return await module.run_whois(target)

async def run_dns(target: str, results_folder: str) -> Dict[str, str]:
    module = ReconModule(results_folder)
    return await module.run_dns(target)

async def run_subdomains(target: str, results_folder: str) -> Dict[str, str]:
    module = ReconModule(results_folder)
    return await module.run_subdomains(target)

async def run_ports(target: str, results_folder: str) -> Dict[str, str]:
    module = ReconModule(results_folder)
    return await module.run_ports(target)

async def run_techscan(target: str, results_folder: str) -> Dict[str, str]:
    module = ReconModule(results_folder)
    return await module.run_techscan(target)
