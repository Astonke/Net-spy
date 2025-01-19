import csv
import platform
import subprocess
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import requests
from typing import List, Tuple, Dict
from encron.tools import find_file
from twilio.rest import Client
from encron.tools import find_file
from threading import Thread

from playsound import playsound as play

class DeviceMonitor:
    def __init__(self, csv_file: str, phone_number: str, email_address: str):
        # First load devices before setting up other configurations
        self.devices = self.load_devices(csv_file)  # Changed from _load_devices to load_devices
        self.phone_number = phone_number
        self.email_address = email_address
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "astonmwendwa254@gmail.com"
        self.smtp_password = "dcjq eqvz fomk vmci"
        
        # Twilio configuration
        self.twilio_account_sid = 'AC271665660485457621c7eed08921b9eb'
        self.twilio_auth_token = 'fcdac2844bfc425f5d1fb40321971822'
        self.twilio_from_number = '+18786886089'
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        # Twilio endpoints
        self.twilio_sms_endpoint = "https://demo.twilio.com/welcome/sms/reply/"
        self.twilio_voice_endpoint = "https://demo.twilio.com/welcome/voice/"
        
        # Initialize the last notification time tracker
        self.last_sms_time: Dict[str, datetime] = {}
        self.last_call_time: Dict[str, datetime] = {}

    def load_devices(self, csv_file: str) -> List[Tuple[str, str]]:  # Removed underscore
        """Load devices from CSV file."""
        devices = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3:
                        ip_address,name,state = row
                        devices.append((ip_address.strip(), name.strip()))
            return devices
        except Exception as e:
            raise Exception(f"Error loading devices from CSV: {str(e)}")

    def ping(self, ip_address: str) -> bool:
        """Enhanced ping function that checks for both successful ping and destination unreachable messages."""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip_address]
        
        try:
            output = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            unreachable_messages = [
                "destination host unreachable",
                "destination unreachable",
                "100% packet loss",
                "request timed out",
                "0 received"
            ]
            
            output_lower = (output.stdout + output.stderr).lower()
            
            for msg in unreachable_messages:
                if msg in output_lower:
                    return False
            
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
                print("Email alert sent successfully")
                
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_sms_alert(self, message: str):
        """Send SMS alert using Twilio demo endpoint."""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from_number,
                to=self.phone_number,
                status_callback=self.twilio_sms_endpoint
            )
            print(f"SMS sent successfully: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

    def make_voice_call(self, message: str):
        """Make voice call using Twilio demo endpoint."""
        try:
            call = self.twilio_client.calls.create(
                twiml=f'<Response><Say>{message}</Say></Response>',
                from_=self.twilio_from_number,
                to=self.phone_number,
                status_callback=self.twilio_voice_endpoint
            )
            print(f"Voice call initiated: {call.sid}")
        except Exception as e:
            print(f"Failed to make voice call: {e}")

    def can_send_sms(self, device_id: str) -> bool:
        """Check if enough time has elapsed since the last SMS."""
        if device_id not in self.last_sms_time:
            return True
        time_elapsed = datetime.now() - self.last_sms_time[device_id]
        return time_elapsed >= timedelta(hours=1)

    def can_make_call(self, device_id: str) -> bool:
        """Check if enough time has elapsed since the last call."""
        if device_id not in self.last_call_time:
            return True
        time_elapsed = datetime.now() - self.last_call_time[device_id]
        return time_elapsed >= timedelta(hours=1)

    def monitor_devices(self):
        """Main monitoring loop with SMS and voice call notifications."""
        print("Starting device monitoring...")
        
        device_states = {ip: True for ip, _ in self.devices}
        
        while True:
            for ip_address, name in self.devices:
                device_id = f"{name}_{ip_address}"
                is_online = self.ping(ip_address)
                
                if not is_online:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    alert_message = f"Device {name} ({ip_address}) is offline at {timestamp}"
                    print(alert_message)
                    
                    #self.send_email_alert(alert_message)
                    
                    if self.can_send_sms(device_id):
                        #self.send_sms_alert(alert_message)
                        self.send_email_alert(alert_message)
                        self.last_sms_time[device_id] = datetime.now()
                        print(f"SMS alert sent for {name}. Next SMS will be sent after 1 hour.")
                        
                        if self.can_make_call(device_id):
                            #self.make_voice_call(alert_message)
                            play(find_file('sec.mp3'))
                            self.last_call_time[device_id] = datetime.now()
                            #print(f"Voice call initiated for {name}. Next call will be made after 1 hour.")
                    else:
                        time_since_last = datetime.now() - self.last_sms_time[device_id]
                        minutes_left = int(60 - (time_since_last.total_seconds() / 60))
                        print(f"Skipping notifications for {name} - {minutes_left} minutes until next alert")
                    
                    device_states[ip_address] = False
                else:
                    print(f"Device {name} online [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                    
                    if not device_states[ip_address]:
                        recovery_message = f"Device {name} ({ip_address}) is back online at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        print(recovery_message)
                        #self.send_email_alert(recovery_message)
                        
                        if self.can_send_sms(device_id):
                            #self.send_sms_alert(recovery_message)
                            self.send_email_alert(recovery_message)
                            #self.make_voice_call(recovery_message)
                            self.last_sms_time[device_id] = datetime.now()
                            self.last_call_time[device_id] = datetime.now()
                    
                    device_states[ip_address] = True
                    
            time.sleep(5)

def main():
    try:
        csv_file = find_file("devices.csv")
        phone_number = "+254702162058"
        email_address = "crashcoders6@gmail.com"
        
        print("\nNetwork Device Monitor Starting...")
        print(f"Loading device list from: {csv_file}")
        print(f"Notifications will be sent to:")
        #print(f"  - SMS: {phone_number}")
        print(f"  - Email: {email_address}\n")
        
        try:
            monitor = DeviceMonitor(csv_file, phone_number, email_address)
            print("Successfully initialized device monitor\n")
        except Exception as e:
            print(f"Failed to initialize device monitor: {str(e)}")
            return
        
        print("\nStarting monitoring loop...")
        print("Press Ctrl+C to stop the monitor\n")
        monitor.monitor_devices()
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except FileNotFoundError:
        print(f"\nError: Could not find devices.csv file")
        print("Please ensure devices.csv exists in the current directory")
        print("Format should be: ip_address,name_identifier (one per line)")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        print("\nNetwork Device Monitor stopped")

if __name__ == "__main__":
    print("\n=== Network Device Monitor ===\n")
    main()