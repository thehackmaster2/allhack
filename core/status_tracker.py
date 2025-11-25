"""
Status Tracker - Track bot statistics and performance
"""

import time
import psutil
import threading
from datetime import datetime, timedelta


class StatusTracker:
    def __init__(self):
        self.start_time = time.time()
        self.version = "1.4.0"
        self.tasks_completed = 0
        self.running_tasks = {}
        self.lock = threading.Lock()
    
    def get_uptime(self):
        """Get bot uptime as a formatted string"""
        uptime_seconds = time.time() - self.start_time
        uptime = timedelta(seconds=int(uptime_seconds))
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_memory_usage(self):
        """Get current memory usage percentage"""
        try:
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()
            mem_mb = mem_info.rss / 1024 / 1024
            return mem_percent, mem_mb
        except:
            return 0.0, 0.0
    
    def add_task(self, task_id, task_name):
        """Add a running task"""
        with self.lock:
            self.running_tasks[task_id] = {
                'name': task_name,
                'start_time': time.time()
            }
    
    def remove_task(self, task_id):
        """Remove a completed task"""
        with self.lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            self.tasks_completed += 1
    
    def get_running_tasks(self):
        """Get list of currently running tasks"""
        with self.lock:
            tasks = []
            for task_id, task_info in self.running_tasks.items():
                runtime = time.time() - task_info['start_time']
                tasks.append({
                    'id': task_id,
                    'name': task_info['name'],
                    'runtime': runtime
                })
            return tasks
    
    def get_status_report(self):
        """Get formatted status report"""
        uptime = self.get_uptime()
        cpu = self.get_cpu_usage()
        mem_percent, mem_mb = self.get_memory_usage()
        running_tasks = self.get_running_tasks()
        
        report = f"🤖 **NeoxSecBot Status Report**\n\n"
        report += f"**Version:** {self.version}\n"
        report += f"**Uptime:** {uptime}\n"
        report += f"**CPU Usage:** {cpu:.1f}%\n"
        report += f"**RAM Usage:** {mem_percent:.1f}% ({mem_mb:.1f} MB)\n"
        report += f"**Tasks Completed:** {self.tasks_completed}\n"
        report += f"**Running Tasks:** {len(running_tasks)}\n\n"
        
        if running_tasks:
            report += "**Active Tasks:**\n"
            for task in running_tasks:
                runtime = timedelta(seconds=int(task['runtime']))
                report += f"  • {task['name']} (running {runtime})\n"
        else:
            report += "**Active Tasks:** None\n"
        
        report += f"\n**Status:** ✅ Operational"
        
        return report


# Global status tracker
_status_tracker = None


def get_status_tracker():
    """Get or create the global status tracker"""
    global _status_tracker
    if _status_tracker is None:
        _status_tracker = StatusTracker()
    return _status_tracker
