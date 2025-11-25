"""
Console UI - Beautiful colored console output
"""

import sys
import time
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)


class ConsoleUI:
    """Beautiful colored console UI"""
    
    # Color schemes
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    DEBUG = Fore.MAGENTA
    TIMESTAMP = Fore.BLACK + Style.BRIGHT
    BANNER = Fore.CYAN + Style.BRIGHT
    
    @staticmethod
    def print_banner():
        """Print ASCII banner"""
        banner = f"""{Fore.CYAN + Style.BRIGHT}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ███╗   ██╗███████╗ ██████╗ ██╗  ██╗███████╗███████╗ ██████╗██████╗  ██████╗║
║  ████╗  ██║██╔════╝██╔═══██╗╚██╗██╔╝██╔════╝██╔════╝██╔════╝██╔══██╗██╔═══██╗
║  ██╔██╗ ██║█████╗  ██║   ██║ ╚███╔╝ ███████╗█████╗  ██║     ██████╔╝██║   ██║║
║  ██║╚██╗██║██╔══╝  ██║   ██║ ██╔██╗ ╚════██║██╔══╝  ██║     ██╔══██╗██║   ██║║
║  ██║ ╚████║███████╗╚██████╔╝██╔╝ ██╗███████║███████╗╚██████╗██████╔╝╚██████╔╝║
║  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝╚═════╝  ╚═════╝ ║
║                                                                              ║
║                    Telegram Security Automation Bot v1.4.0                  ║
║                          Professional Edition                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(banner)
    
    @staticmethod
    def timestamp():
        """Get formatted timestamp"""
        return f"{ConsoleUI.TIMESTAMP}[{datetime.now().strftime('%H:%M:%S')}]{Style.RESET_ALL}"
    
    @staticmethod
    def success(message):
        """Print success message"""
        print(f"{ConsoleUI.timestamp()} {ConsoleUI.SUCCESS}✓{Style.RESET_ALL} {message}")
    
    @staticmethod
    def error(message):
        """Print error message"""
        print(f"{ConsoleUI.timestamp()} {ConsoleUI.ERROR}✗{Style.RESET_ALL} {message}")
    
    @staticmethod
    def warning(message):
        """Print warning message"""
        print(f"{ConsoleUI.timestamp()} {ConsoleUI.WARNING}⚠{Style.RESET_ALL} {message}")
    
    @staticmethod
    def info(message):
        """Print info message"""
        print(f"{ConsoleUI.timestamp()} {ConsoleUI.INFO}ℹ{Style.RESET_ALL} {message}")
    
    @staticmethod
    def debug(message):
        """Print debug message"""
        print(f"{ConsoleUI.timestamp()} {ConsoleUI.DEBUG}◆{Style.RESET_ALL} {message}")
    
    @staticmethod
    def loading(message, duration=0.5):
        """Print loading message with animated dots"""
        sys.stdout.write(f"{ConsoleUI.timestamp()} {ConsoleUI.INFO}⟳{Style.RESET_ALL} {message}")
        sys.stdout.flush()
        
        for _ in range(3):
            time.sleep(duration / 3)
            sys.stdout.write(".")
            sys.stdout.flush()
        
        print()
    
    @staticmethod
    def section(title):
        """Print section header"""
        print(f"\n{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}\n")
    
    @staticmethod
    def table_row(label, value, color=Fore.WHITE):
        """Print a table row"""
        print(f"  {Fore.WHITE}{label:<30}{Style.RESET_ALL} {color}{value}{Style.RESET_ALL}")
    
    @staticmethod
    def separator():
        """Print separator line"""
        print(f"{Fore.BLACK + Style.BRIGHT}{'─' * 80}{Style.RESET_ALL}")


# Convenience functions
ui = ConsoleUI()
