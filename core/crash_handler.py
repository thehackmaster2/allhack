"""
Crash Handler - Auto-restart system with crash logging
"""

import os
import sys
import traceback
import time
from datetime import datetime


class CrashHandler:
    def __init__(self, log_dir="results/logs"):
        self.log_dir = log_dir
        self.crash_count = 0
        self.max_crashes = 5  # Max crashes before stopping auto-restart
        self.crash_window = 300  # 5 minutes
        self.crash_times = []
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
    
    def log_crash(self, exception, exc_info):
        """Log crash details to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.log_dir, f"crash_{timestamp}.log")
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"{'='*60}\n")
                f.write(f"CRASH LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                
                f.write(f"Exception Type: {type(exception).__name__}\n")
                f.write(f"Exception Message: {str(exception)}\n\n")
                
                f.write("Traceback:\n")
                f.write(''.join(traceback.format_exception(*exc_info)))
                
                f.write(f"\n{'='*60}\n")
                f.write(f"System Information:\n")
                f.write(f"{'='*60}\n")
                f.write(f"Python Version: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write(f"Working Directory: {os.getcwd()}\n")
            
            return log_file
        except Exception as e:
            print(f"Failed to write crash log: {e}")
            return None
    
    def should_restart(self):
        """Check if bot should auto-restart based on crash history"""
        current_time = time.time()
        
        # Remove old crash times outside the window
        self.crash_times = [t for t in self.crash_times if current_time - t < self.crash_window]
        
        # Add current crash
        self.crash_times.append(current_time)
        self.crash_count = len(self.crash_times)
        
        # Check if too many crashes in window
        if self.crash_count >= self.max_crashes:
            return False
        
        return True
    
    def handle_crash(self, exception, exc_info):
        """Handle a crash - log it and decide whether to restart"""
        print(f"\n{'='*60}")
        print(f"❌ CRASH DETECTED")
        print(f"{'='*60}")
        print(f"Error: {type(exception).__name__}: {str(exception)}")
        
        # Log the crash
        log_file = self.log_crash(exception, exc_info)
        if log_file:
            print(f"📝 Crash log saved: {log_file}")
        
        # Check if should restart
        if self.should_restart():
            print(f"\n🔄 Auto-restart enabled ({self.crash_count}/{self.max_crashes} crashes)")
            print(f"⏳ Restarting in 3 seconds...")
            time.sleep(3)
            return True
        else:
            print(f"\n⛔ Too many crashes ({self.crash_count} in {self.crash_window}s)")
            print(f"❌ Auto-restart disabled to prevent restart loop")
            print(f"📋 Check crash logs in: {self.log_dir}")
            return False


# Global crash handler
_crash_handler = None


def get_crash_handler():
    """Get or create the global crash handler"""
    global _crash_handler
    if _crash_handler is None:
        _crash_handler = CrashHandler()
    return _crash_handler


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    # Ignore KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    handler = get_crash_handler()
    should_restart = handler.handle_crash(exc_value, (exc_type, exc_value, exc_traceback))
    
    if should_restart:
        # Restart the bot
        restart_bot()
    else:
        sys.exit(1)


def restart_bot():
    """Restart the bot process"""
    print(f"\n🔄 Restarting bot...")
    
    try:
        # Get the current script path
        script = sys.argv[0]
        
        if sys.platform == 'win32':
            # Windows: Use start.bat if available
            import subprocess
            batch_file = os.path.join(os.path.dirname(script), 'start.bat')
            if os.path.exists(batch_file):
                subprocess.Popen([batch_file], shell=True)
            else:
                # Fallback to python restart
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Unix-like: Direct restart
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"❌ Failed to restart: {e}")
        sys.exit(1)


def install_crash_handler():
    """Install the global crash handler"""
    sys.excepthook = handle_exception
