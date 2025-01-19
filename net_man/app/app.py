import csv
import platform
import subprocess
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
from typing import List, Tuple
from encron.tools import find_file

class DeviceMonitor:
    def __init__(self, csv_file: str, phone_number: str, email_address: str):
        self.devices = self._load_devices(csv_file)
        self.phone_number = phone_number
        self.email_address = email_address
        
        # Email configuration - Replace with your SMTP server details
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "astonmwendwa254@gmail.com"
        self.smtp_password = "dcjq eqvz fomk vmci"
        
        # SMS configuration - Using TextBelt as an example (get an API key from textbelt.com)
        self.sms_api_key = '2f9cd8eea625cb9de30eca56b3b44ccdce040e81wbxbdjLOHxRpgeHRId8YkCt7f'
        self.sms_api_url = 'https://textbelt.com/text'

    def _load_devices(self, csv_file: str) -> List[Tuple[str, str]]:
        """Load devices from CSV file."""
        devices = []
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    ip_address, name = row
                    devices.append((ip_address.strip(), name.strip()))
        return devices

    def ping(self, ip_address: str) -> bool:
        """
        Enhanced ping function that checks for both successful ping and destination unreachable messages.
        Returns True only if the device is definitely online.
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip_address]
        
        try:
            # Capture both stdout and stderr
            output = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5  # Add timeout to prevent hanging
            )
            
            # Check for common "destination unreachable" messages in both stdout and stderr
            unreachable_messages = [
                "destination host unreachable",
                "destination unreachable",
                "100% packet loss",
                "request timed out",
                "0 received"
            ]
            
            output_lower = (output.stdout + output.stderr).lower()
            
            # If any unreachable message is found, consider the device offline
            for msg in unreachable_messages:
                if msg in output_lower:
                    return False
            
            # Check if ping was successful
            return output.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"Ping timeout for {ip_address}")
            return False
        except subprocess.CalledProcessError:
            print(f"Ping failed for {ip_address}")
            return False
        except Exception as e:
            print(f"Error while pinging {ip_address}: {str(e)}")
            return False
    
    def pig(self, ip_address: str) -> bool:
        """Ping an IP address and return True if device is online."""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip_address]
        
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    def send_email_alert(self, message: str):
        """Send email alert."""
        try:
            msg = MIMEText(message)
            msg['Subject'] = 'Device Offline Alert'
            msg['From'] = self.smtp_username
            msg['To'] = self.email_address

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_sms_alert(self, message: str):
        """Send SMS alert using TextBelt."""
        try:
            resp = requests.post(self.sms_api_url, {
                'phone': self.phone_number,
                'message': message,
                'key': self.sms_api_key,
            })
            
            if not resp.json()['success']:
                print(f"Failed to send SMS: {resp.json()}")
                
        except Exception as e:
            print(f"Failed to send SMS: {e}")

    def monitor_devices(self):
        """Main monitoring loop."""
        print("Starting device monitoring...")
        
        while True:
            for ip_address, name in self.devices:
                if not self.ping(ip_address):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    alert_message = f"Device {name} ({ip_address}) is offline at {timestamp}"
                    
                    print(alert_message)
                    self.send_email_alert(alert_message)
                    #self.send_sms_alert(alert_message)
                else:
                    print(f"device {name} online [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            time.sleep(5)  # Wait 5 seconds before next check

def main():
    # Replace these with your actual values
    csv_file = find_file("devices.csv")
    phone_number = "+254702162058"
    email_address = "crashcoders6@gmail.com"
    
    monitor = DeviceMonitor(csv_file, phone_number, email_address)
    monitor.monitor_devices()

if __name__ == "__main__":
    main()
