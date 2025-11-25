"""
ZIP Password Cracker Module - Telegram-Integrated Version
⚠️ EDUCATIONAL USE ONLY - Authorized Files Only

Replicates exact behavior of reference ZIP cracker with Telegram integration:
- Threading with Event-based control
- Real-time progress updates
- Attempts/time/speed tracking
- Clean thread termination
"""

import os
import time
import pyzipper
from threading import Thread, Event
from datetime import datetime
from typing import Dict, Optional, Callable
import asyncio


class ZipCracker:
    """ZIP password cracker with threading and progress tracking"""
    
    def __init__(self, zip_path: str, wordlist_path: str, results_folder: str):
        self.zip_path = zip_path
        self.wordlist_path = wordlist_path
        self.results_folder = results_folder
        
        # Threading control
        self.stop_event = Event()
        self.progress_thread = None
        
        # Statistics
        self.attempts = 0
        self.start_time = None
        self.found_password = None
        
        # Progress callback for Telegram
        self.progress_callback = None
        self.last_progress_time = 0
    
    def set_progress_callback(self, callback: Callable):
        """Set async callback for progress updates"""
        self.progress_callback = callback
    
    def show_progress(self):
        """Progress thread - shows real-time statistics"""
        while not self.stop_event.is_set():
            if self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    speed = self.attempts / elapsed
                    
                    # Format progress message
                    progress_msg = (
                        f"[+] Attempts: {self.attempts} | "
                        f"Time: {int(elapsed)}s | "
                        f"Speed: {speed:.1f} pwd/s"
                    )
                    
                    # Send to Telegram if callback exists and enough time passed
                    current_time = time.time()
                    if self.progress_callback and (current_time - self.last_progress_time) >= 2.5:
                        try:
                            # Schedule callback in event loop
                            asyncio.run_coroutine_threadsafe(
                                self.progress_callback(progress_msg),
                                asyncio.get_event_loop()
                            )
                            self.last_progress_time = current_time
                        except:
                            pass
            
            # Sleep briefly
            time.sleep(0.5)
    
    def crack(self) -> Dict[str, any]:
        """
        Main cracking function - exact replica of reference script behavior
        """
        try:
            # Validate files
            if not os.path.exists(self.zip_path):
                return {
                    'status': 'error',
                    'message': f'ZIP file not found: {self.zip_path}'
                }
            
            if not os.path.exists(self.wordlist_path):
                return {
                    'status': 'error',
                    'message': f'Wordlist not found: {self.wordlist_path}'
                }
            
            # Start timing
            self.start_time = time.time()
            
            # Start progress thread
            self.progress_thread = Thread(target=self.show_progress, daemon=True)
            self.progress_thread.start()
            
            # Open ZIP file
            try:
                zip_file = pyzipper.AESZipFile(self.zip_path)
            except Exception as e:
                self.stop_event.set()
                if self.progress_thread:
                    self.progress_thread.join(timeout=1)
                return {
                    'status': 'error',
                    'message': f'Failed to open ZIP file: {str(e)}'
                }
            
            # Open wordlist and crack
            found = False
            
            try:
                with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
                    for line in wordlist:
                        if self.stop_event.is_set():
                            break
                        
                        password = line.strip()
                        if not password:
                            continue
                        
                        self.attempts += 1
                        
                        try:
                            # Attempt extraction with password
                            zip_file.setpassword(password.encode('utf-8'))
                            
                            # Try to extract first file to test password
                            zip_file.testzip()
                            
                            # If we get here, password is correct!
                            self.found_password = password
                            found = True
                            self.stop_event.set()
                            break
                        
                        except (RuntimeError, pyzipper.BadZipFile, pyzipper.LargeZipFile):
                            # Wrong password, continue
                            continue
                        except Exception:
                            # Other error, continue
                            continue
            
            finally:
                # Clean up
                zip_file.close()
                self.stop_event.set()
                
                # Wait for progress thread to finish
                if self.progress_thread and self.progress_thread.is_alive():
                    self.progress_thread.join(timeout=2)
            
            # Calculate final statistics
            elapsed_time = time.time() - self.start_time
            speed = self.attempts / elapsed_time if elapsed_time > 0 else 0
            
            # Prepare result
            if found:
                # Extract files
                extract_path = self._extract_zip(self.found_password)
                
                # Save report
                report_content = self._generate_report(
                    found=True,
                    password=self.found_password,
                    attempts=self.attempts,
                    time_elapsed=elapsed_time,
                    speed=speed,
                    extract_path=extract_path
                )
                
                report_file = self._save_report(report_content)
                
                return {
                    'status': 'success',
                    'found': True,
                    'password': self.found_password,
                    'attempts': self.attempts,
                    'time': elapsed_time,
                    'speed': speed,
                    'extract_path': extract_path,
                    'report_file': report_file
                }
            else:
                # Not found
                report_content = self._generate_report(
                    found=False,
                    attempts=self.attempts,
                    time_elapsed=elapsed_time,
                    speed=speed
                )
                
                report_file = self._save_report(report_content)
                
                return {
                    'status': 'success',
                    'found': False,
                    'attempts': self.attempts,
                    'time': elapsed_time,
                    'speed': speed,
                    'report_file': report_file
                }
        
        except Exception as e:
            # Ensure cleanup
            self.stop_event.set()
            if self.progress_thread and self.progress_thread.is_alive():
                self.progress_thread.join(timeout=2)
            
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _extract_zip(self, password: str) -> Optional[str]:
        """Extract ZIP contents with found password"""
        try:
            # Create extraction directory
            extract_dir = os.path.join(
                self.results_folder,
                f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extract
            with pyzipper.AESZipFile(self.zip_path) as zf:
                zf.setpassword(password.encode('utf-8'))
                zf.extractall(extract_dir)
            
            return extract_dir
        except Exception:
            return None
    
    def _generate_report(self, found: bool, attempts: int, time_elapsed: float, 
                        speed: float, password: str = None, extract_path: str = None) -> str:
        """Generate cracking report"""
        report = []
        report.append("="*60)
        report.append("ZIP PASSWORD CRACKING REPORT")
        report.append("="*60)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"ZIP File: {self.zip_path}")
        report.append(f"Wordlist: {self.wordlist_path}")
        report.append("")
        report.append("RESULTS:")
        report.append("-"*60)
        
        if found:
            report.append(f"✅ PASSWORD FOUND!")
            report.append(f"Password: {password}")
            report.append(f"Attempts: {attempts}")
            report.append(f"Time: {time_elapsed:.2f} seconds")
            report.append(f"Speed: {speed:.1f} passwords/second")
            if extract_path:
                report.append(f"Extracted to: {extract_path}")
        else:
            report.append(f"❌ PASSWORD NOT FOUND")
            report.append(f"Attempts: {attempts}")
            report.append(f"Time: {time_elapsed:.2f} seconds")
            report.append(f"Speed: {speed:.1f} passwords/second")
        
        report.append("="*60)
        
        return "\n".join(report)
    
    def _save_report(self, content: str) -> str:
        """Save report to file"""
        try:
            os.makedirs(self.results_folder, exist_ok=True)
            report_file = os.path.join(
                self.results_folder,
                f"zipcrack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return report_file
        except Exception:
            return None


def get_largest_wordlist(wordlist_dir: str) -> Optional[str]:
    """Get the largest wordlist file from directory"""
    try:
        if not os.path.exists(wordlist_dir):
            return None
        
        wordlists = []
        for file in os.listdir(wordlist_dir):
            filepath = os.path.join(wordlist_dir, file)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                wordlists.append((filepath, size))
        
        if not wordlists:
            return None
        
        # Sort by size and return largest
        wordlists.sort(key=lambda x: x[1], reverse=True)
        return wordlists[0][0]
    
    except Exception:
        return None


def get_wordlist_by_size(wordlist_dir: str, size: str) -> Optional[str]:
    """Get wordlist by size category (small/medium/big)"""
    try:
        if not os.path.exists(wordlist_dir):
            return None
        
        wordlists = []
        for file in os.listdir(wordlist_dir):
            filepath = os.path.join(wordlist_dir, file)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                wordlists.append((filepath, file_size))
        
        if not wordlists:
            return None
        
        # Sort by size
        wordlists.sort(key=lambda x: x[1])
        
        # Select based on size category
        if size == 'small':
            return wordlists[0][0]
        elif size == 'medium':
            idx = len(wordlists) // 2
            return wordlists[idx][0]
        elif size == 'big':
            return wordlists[-1][0]
        else:
            return wordlists[-1][0]  # Default to biggest
    
    except Exception:
        return None


async def crack_zip(zip_path: str, wordlist_path: str, results_folder: str,
                   progress_callback: Optional[Callable] = None) -> Dict[str, any]:
    """
    Crack ZIP password - Telegram-integrated version
    
    Args:
        zip_path: Path to ZIP file
        wordlist_path: Path to wordlist
        results_folder: Where to save results
        progress_callback: Async callback for progress updates
    
    Returns:
        Dict with status, found, password, attempts, time, speed
    """
    # Create cracker instance
    cracker = ZipCracker(zip_path, wordlist_path, results_folder)
    
    # Set progress callback
    if progress_callback:
        cracker.set_progress_callback(progress_callback)
    
    # Run cracking in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cracker.crack)
    
    return result


async def crack_zip_auto_wordlist(zip_path: str, wordlist_dir: str, 
                                  results_folder: str, wordlist_size: str = 'big',
                                  progress_callback: Optional[Callable] = None) -> Dict[str, any]:
    """
    Crack ZIP with automatic wordlist selection
    
    Args:
        zip_path: Path to ZIP file
        wordlist_dir: Directory containing wordlists
        results_folder: Where to save results
        wordlist_size: 'small', 'medium', or 'big'
        progress_callback: Async callback for progress updates
    
    Returns:
        Dict with status, found, password, attempts, time, speed
    """
    # Select wordlist
    if wordlist_size in ['small', 'medium', 'big']:
        wordlist_path = get_wordlist_by_size(wordlist_dir, wordlist_size)
    else:
        wordlist_path = get_largest_wordlist(wordlist_dir)
    
    if not wordlist_path:
        return {
            'status': 'error',
            'message': f'No wordlists found in {wordlist_dir}'
        }
    
    # Crack
    return await crack_zip(zip_path, wordlist_path, results_folder, progress_callback)
