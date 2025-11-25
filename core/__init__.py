"""
Core System - NeoxSecBot v1.4.0
"""

from .instance_lock import acquire_lock, release_lock
from .crash_handler import install_crash_handler, get_crash_handler
from .status_tracker import get_status_tracker
from .console_ui import ui, ConsoleUI
from .plugin_manager import get_plugin_manager, Plugin

__all__ = [
    'acquire_lock',
    'release_lock',
    'install_crash_handler',
    'get_crash_handler',
    'get_status_tracker',
    'ui',
    'ConsoleUI',
    'get_plugin_manager',
    'Plugin'
]
