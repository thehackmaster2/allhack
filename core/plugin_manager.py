"""
Plugin System - Dynamic plugin loading and management
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any


class Plugin:
    """Base plugin class"""
    name = "BasePlugin"
    description = "Base plugin class"
    enabled = True
    
    async def run(self, update, context):
        """Plugin execution method"""
        raise NotImplementedError("Plugin must implement run() method")


class PluginManager:
    """Manage bot plugins"""
    
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.enabled_plugins: Dict[str, bool] = {}
        
        # Create plugin directory
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = os.path.join(plugin_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Plugins directory\n")
    
    def load_plugins(self):
        """Load all plugins from the plugin directory"""
        if self.plugin_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(os.path.abspath(self.plugin_dir)))
        
        loaded_count = 0
        
        # Scan plugin directory
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                
                try:
                    # Import the plugin module
                    module_name = f"{os.path.basename(self.plugin_dir)}.{plugin_name}"
                    module = importlib.import_module(module_name)
                    
                    # Find plugin class
                    plugin_class = None
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                            plugin_class = obj
                            break
                    
                    if plugin_class:
                        # Instantiate plugin
                        plugin_instance = plugin_class()
                        self.plugins[plugin_name] = plugin_instance
                        self.enabled_plugins[plugin_name] = getattr(plugin_instance, 'enabled', True)
                        loaded_count += 1
                        print(f"  ✓ Loaded plugin: {plugin_instance.name}")
                    else:
                        print(f"  ✗ No valid plugin class found in {filename}")
                
                except Exception as e:
                    print(f"  ✗ Failed to load {filename}: {e}")
        
        return loaded_count
    
    def get_plugin(self, plugin_name):
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)
    
    def is_enabled(self, plugin_name):
        """Check if a plugin is enabled"""
        return self.enabled_plugins.get(plugin_name, False)
    
    def enable_plugin(self, plugin_name):
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.enabled_plugins[plugin_name] = True
            return True
        return False
    
    def disable_plugin(self, plugin_name):
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.enabled_plugins[plugin_name] = False
            return True
        return False
    
    def get_enabled_plugins(self):
        """Get list of enabled plugins"""
        return [
            (name, plugin) for name, plugin in self.plugins.items()
            if self.enabled_plugins.get(name, False)
        ]
    
    def get_all_plugins(self):
        """Get list of all plugins with their status"""
        result = []
        for name, plugin in self.plugins.items():
            result.append({
                'name': plugin.name,
                'description': plugin.description,
                'enabled': self.enabled_plugins.get(name, False),
                'module': name
            })
        return result


# Global plugin manager
_plugin_manager = None


def get_plugin_manager():
    """Get or create the global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
