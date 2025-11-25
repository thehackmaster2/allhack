"""
Example Plugin - Shows how to create a custom plugin
"""

from core.plugin_manager import Plugin


class ExamplePlugin(Plugin):
    """Example plugin demonstrating the plugin system"""
    
    name = "Example Plugin"
    description = "A simple example plugin that responds with a greeting"
    enabled = True
    
    async def run(self, update, context):
        """Execute the plugin"""
        await update.message.reply_text(
            "👋 Hello! This is an example plugin.\n\n"
            "You can create your own plugins by:\n"
            "1. Creating a .py file in the plugins/ folder\n"
            "2. Importing Plugin from core.plugin_manager\n"
            "3. Creating a class that inherits from Plugin\n"
            "4. Implementing the run() method\n\n"
            "Your plugin will be automatically loaded on bot startup!"
        )
