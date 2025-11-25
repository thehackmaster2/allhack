"""
CTF Tools Module - Encoding/Decoding and Crypto Analysis
"""

import base64
import binascii
import hashlib
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
import subprocess


class CTFModule:
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
    
    def base64_decode(self, text: str) -> Dict[str, str]:
        """Decode base64"""
        try:
            # Try standard base64
            decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
            return {
                'status': 'success',
                'method': 'base64',
                'result': decoded
            }
        except:
            try:
                # Try URL-safe base64
                decoded = base64.urlsafe_b64decode(text).decode('utf-8', errors='ignore')
                return {
                    'status': 'success',
                    'method': 'base64_urlsafe',
                    'result': decoded
                }
            except:
                return {
                    'status': 'error',
                    'message': 'Invalid base64 string'
                }
    
    def base64_encode(self, text: str) -> Dict[str, str]:
        """Encode to base64"""
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return {
                'status': 'success',
                'method': 'base64',
                'result': encoded
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def hex_decode(self, text: str) -> Dict[str, str]:
        """Decode hexadecimal"""
        try:
            # Remove spaces and common prefixes
            text = text.replace(' ', '').replace('0x', '').replace('\\x', '')
            decoded = bytes.fromhex(text).decode('utf-8', errors='ignore')
            return {
                'status': 'success',
                'method': 'hex',
                'result': decoded
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def hex_encode(self, text: str) -> Dict[str, str]:
        """Encode to hexadecimal"""
        try:
            encoded = text.encode('utf-8').hex()
            return {
                'status': 'success',
                'method': 'hex',
                'result': encoded
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def rot13(self, text: str) -> Dict[str, str]:
        """ROT13 cipher"""
        try:
            import codecs
            result = codecs.encode(text, 'rot_13')
            return {
                'status': 'success',
                'method': 'rot13',
                'result': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def caesar_bruteforce(self, text: str) -> Dict[str, List[Tuple[int, str]]]:
        """Brute force all Caesar cipher shifts"""
        try:
            results = []
            for shift in range(26):
                decoded = ''
                for char in text:
                    if char.isalpha():
                        ascii_offset = 65 if char.isupper() else 97
                        decoded += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
                    else:
                        decoded += char
                results.append((shift, decoded))
            
            return {
                'status': 'success',
                'method': 'caesar_bruteforce',
                'results': results
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def identify_hash(self, hash_string: str) -> Dict[str, str]:
        """Identify hash type based on length and format"""
        hash_string = hash_string.strip()
        length = len(hash_string)
        
        hash_types = []
        
        if length == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_string):
            hash_types.append('MD5')
        if length == 40 and re.match(r'^[a-fA-F0-9]{40}$', hash_string):
            hash_types.append('SHA1')
        if length == 64 and re.match(r'^[a-fA-F0-9]{64}$', hash_string):
            hash_types.append('SHA256')
        if length == 128 and re.match(r'^[a-fA-F0-9]{128}$', hash_string):
            hash_types.append('SHA512')
        if length == 16 and re.match(r'^[a-fA-F0-9]{16}$', hash_string):
            hash_types.append('MySQL (old)')
        if hash_string.startswith('$2a$') or hash_string.startswith('$2b$') or hash_string.startswith('$2y$'):
            hash_types.append('bcrypt')
        if hash_string.startswith('$6$'):
            hash_types.append('SHA512crypt')
        if hash_string.startswith('$5$'):
            hash_types.append('SHA256crypt')
        if hash_string.startswith('$1$'):
            hash_types.append('MD5crypt')
        
        if not hash_types:
            hash_types.append('Unknown')
        
        return {
            'status': 'success',
            'hash': hash_string,
            'length': length,
            'possible_types': hash_types
        }
    
    def calculate_hash(self, text: str) -> Dict[str, str]:
        """Calculate various hashes of input"""
        try:
            data = text.encode('utf-8')
            
            return {
                'status': 'success',
                'md5': hashlib.md5(data).hexdigest(),
                'sha1': hashlib.sha1(data).hexdigest(),
                'sha256': hashlib.sha256(data).hexdigest(),
                'sha512': hashlib.sha512(data).hexdigest()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def extract_metadata(self, filepath: str) -> Dict[str, any]:
        """Extract metadata from file using exiftool if available"""
        try:
            # Try using exiftool
            try:
                result = subprocess.run(['exiftool', filepath], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                if result.returncode == 0:
                    return {
                        'status': 'success',
                        'method': 'exiftool',
                        'output': result.stdout
                    }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Fallback to basic metadata
            stat = os.stat(filepath)
            metadata = {
                'filename': os.path.basename(filepath),
                'size': f"{stat.st_size} bytes",
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Try to read file header
            with open(filepath, 'rb') as f:
                header = f.read(16)
                metadata['header_hex'] = header.hex()
            
            output = '\n'.join([f"{k}: {v}" for k, v in metadata.items()])
            
            return {
                'status': 'success',
                'method': 'basic',
                'output': output
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def check_steganography(self, filepath: str) -> Dict[str, str]:
        """Basic steganography checks"""
        try:
            results = []
            
            # Check file size anomalies
            stat = os.stat(filepath)
            results.append(f"File size: {stat.st_size} bytes")
            
            # Check for embedded files (basic)
            with open(filepath, 'rb') as f:
                content = f.read()
                
                # Look for common file signatures
                signatures = {
                    b'PK\x03\x04': 'ZIP archive',
                    b'\x89PNG': 'PNG image',
                    b'\xff\xd8\xff': 'JPEG image',
                    b'GIF8': 'GIF image',
                    b'%PDF': 'PDF document',
                    b'MZ': 'PE executable',
                }
                
                found_signatures = []
                for sig, desc in signatures.items():
                    count = content.count(sig)
                    if count > 1:
                        found_signatures.append(f"Multiple {desc} signatures found ({count})")
                    elif count == 1 and sig not in content[:100]:
                        found_signatures.append(f"{desc} signature found in middle of file")
                
                if found_signatures:
                    results.append("\n⚠️  Potential hidden files detected:")
                    results.extend([f"  - {s}" for s in found_signatures])
                else:
                    results.append("\n✓ No obvious embedded files detected")
            
            # Check for strings
            strings = []
            current = b''
            with open(filepath, 'rb') as f:
                for byte in f.read():
                    if 32 <= byte <= 126:
                        current += bytes([byte])
                    else:
                        if len(current) >= 10:
                            strings.append(current.decode('ascii', errors='ignore'))
                        current = b''
            
            if strings:
                results.append(f"\nFound {len(strings)} readable strings")
                results.append("Sample strings:")
                for s in strings[:5]:
                    results.append(f"  {s[:50]}...")
            
            return {
                'status': 'success',
                'output': '\n'.join(results)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def auto_decode(self, text: str) -> Dict[str, any]:
        """Try to automatically decode text using multiple methods"""
        results = []
        
        # Try base64
        b64_result = self.base64_decode(text)
        if b64_result['status'] == 'success':
            results.append(f"Base64: {b64_result['result']}")
        
        # Try hex
        hex_result = self.hex_decode(text)
        if hex_result['status'] == 'success':
            results.append(f"Hex: {hex_result['result']}")
        
        # Try ROT13
        rot_result = self.rot13(text)
        if rot_result['status'] == 'success':
            results.append(f"ROT13: {rot_result['result']}")
        
        # Check if it's a hash
        hash_id = self.identify_hash(text)
        if hash_id['possible_types'] != ['Unknown']:
            results.append(f"Possible hash types: {', '.join(hash_id['possible_types'])}")
        
        return {
            'status': 'success',
            'results': results if results else ['No successful decoding methods found']
        }


# Export functions
async def decode_text(text: str, method: str, results_folder: str) -> Dict[str, str]:
    module = CTFModule(results_folder)
    
    if method == 'base64':
        return module.base64_decode(text)
    elif method == 'hex':
        return module.hex_decode(text)
    elif method == 'rot13':
        return module.rot13(text)
    elif method == 'caesar':
        return module.caesar_bruteforce(text)
    elif method == 'auto':
        return module.auto_decode(text)
    else:
        return {'status': 'error', 'message': 'Unknown decoding method'}

async def encode_text(text: str, method: str, results_folder: str) -> Dict[str, str]:
    module = CTFModule(results_folder)
    
    if method == 'base64':
        return module.base64_encode(text)
    elif method == 'hex':
        return module.hex_encode(text)
    elif method == 'rot13':
        return module.rot13(text)
    else:
        return {'status': 'error', 'message': 'Unknown encoding method'}

async def identify_hash(hash_string: str, results_folder: str) -> Dict[str, str]:
    module = CTFModule(results_folder)
    return module.identify_hash(hash_string)

async def calculate_hash(text: str, results_folder: str) -> Dict[str, str]:
    module = CTFModule(results_folder)
    return module.calculate_hash(text)

async def extract_metadata(filepath: str, results_folder: str) -> Dict[str, any]:
    module = CTFModule(results_folder)
    return module.extract_metadata(filepath)

async def check_stego(filepath: str, results_folder: str) -> Dict[str, str]:
    module = CTFModule(results_folder)
    return module.check_steganography(filepath)
