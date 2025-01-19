import subprocess

# Global variable to store the process
monitor_process = None

def start_monitoring():
    """Start the DeviceMonitor script."""
    global monitor_process
    if monitor_process is None or monitor_process.poll() is not None:
        monitor_process = subprocess.Popen(['python', 'app/app2.py'])
        return "Monitoring started"
    return "Monitoring already running"

def stop_monitoring():
    """Stop the DeviceMonitor script."""
    global monitor_process
    if monitor_process and monitor_process.poll() is None:
        monitor_process.terminate()
        monitor_process = None
        return "Monitoring stopped"
    return "Monitoring is not running"

def is_monitoring():
    """Check if the DeviceMonitor script is running."""
    return monitor_process is not None and monitor_process.poll() is None
