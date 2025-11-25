"""
Instance Lock System - Prevents multiple bot instances
"""

import os
import sys
import time
import atexit


class InstanceLock:
    def __init__(self, lock_dir="results/lock"):
        self.lock_dir = lock_dir
        self.lock_file = os.path.join(lock_dir, "instance.lock")
        self.locked = False
    
    def acquire(self):
        """Acquire the instance lock"""
        # Create lock directory
        os.makedirs(self.lock_dir, exist_ok=True)
        
        # Check if lock exists
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process is still running
                if self._is_process_running(pid):
                    print(f"\n❌ ERROR: Another instance is already running (PID: {pid})")
                    print(f"   Lock file: {self.lock_file}")
                    print(f"\n   If you're sure no other instance is running, delete:")
                    print(f"   {os.path.abspath(self.lock_file)}\n")
                    return False
                else:
                    # Stale lock file, remove it
                    os.remove(self.lock_file)
            except Exception:
                # Invalid lock file, remove it
                try:
                    os.remove(self.lock_file)
                except:
                    pass
        
        # Create lock file with current PID
        try:
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            self.locked = True
            
            # Register cleanup on exit
            atexit.register(self.release)
            return True
        except Exception as e:
            print(f"❌ Failed to create lock file: {e}")
            return False
    
    def release(self):
        """Release the instance lock"""
        if self.locked and os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
                self.locked = False
            except:
                pass
    
    def _is_process_running(self, pid):
        """Check if a process with given PID is running"""
        try:
            if sys.platform == 'win32':
                import subprocess
                result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {pid}'],
                    capture_output=True,
                    text=True
                )
                return str(pid) in result.stdout
            else:
                # Unix-like systems
                os.kill(pid, 0)
                return True
        except:
            return False


# Global instance
_instance_lock = None


def acquire_lock():
    """Acquire the global instance lock"""
    global _instance_lock
    _instance_lock = InstanceLock()
    return _instance_lock.acquire()


def release_lock():
    """Release the global instance lock"""
    global _instance_lock
    if _instance_lock:
        _instance_lock.release()
