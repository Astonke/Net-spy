from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils import get_devices, save_device, remove_device, toggle_device,get_all_devices,rmd,restore
from .process_manager import start_monitoring, stop_monitoring, is_monitoring

import csv

def disable_device(request):
    if request.method == "POST":
        ip_to_disable = request.POST.get("ip_address")

        if ip_to_disable:
            # Read all devices from devices.csv
            with open('devices.csv', 'r') as file:
                reader = csv.reader(file)
                devices = list(reader)

            # Write all devices except the one to be disabled back to devices.csv
            with open('devices.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for device in devices:
                    if device[0] != ip_to_disable:  # Assuming IP is in the first column
                        writer.writerow(device)

            # Append the removed device to temp.csv
            with open('temp.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                for device in devices:
                    if device[0] == ip_to_disable:
                        writer.writerow(device)

            return redirect('devices')  # Redirect back to the devices page
    return redirect('devices')  # If no IP is found or invalid request


def devices_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        ip = request.POST.get('ip')
        description = request.POST.get('description')

        if action == 'add':
            save_device(ip, description)
        elif action == 'remove':
            #remove_device(ip)
            rmd(ip)
        elif action == 'enable':
            toggle_device(ip, 'enabled')
            restore(ip,description)
        elif action == 'disable':
            toggle_device(ip, 'disabled')
            remove_device(ip)
        elif action == 'arm':
            message = start_monitoring()
        elif action == 'disarm':
            message = stop_monitoring()
        
        return redirect('devices')
    if request.method == 'GET':
        devices = get_all_devices()
        monitoring_state = "Running" if is_monitoring() else "Stopped"
        return render(request, 'devices.html', {'devices': devices, 'monitoring_state': monitoring_state})


def enable_device(request):
    """Enable a device by moving it from temp.csv to devices.csv."""
    if request.method == "POST":
        ip_address = request.POST.get("ip_address")

        # Step 1: Read temp.csv to find the device
        device_to_enable = None
        temp_devices = []
        with open(TEMP_CSV, "r") as temp_file:
            reader = csv.reader(temp_file)
            for row in reader:
                if row[0] == ip_address:  # Match IP address
                    device_to_enable = row  # Found the device
                temp_devices.append(row)  # Keep all rows

        if device_to_enable is None:
            return JsonResponse({"error": "Device not found in temp.csv"}, status=400)

        # Step 2: Check if the device already exists in devices.csv
        with open(DEVICES_CSV, "r") as devices_file:
            reader = csv.reader(devices_file)
            existing_devices = [row for row in reader]

        if device_to_enable in existing_devices:
            return JsonResponse({"message": "Device is already enabled."}, status=200)

        # Step 3: Write the device back to devices.csv
        with open(DEVICES_CSV, "a", newline="") as devices_file:
            writer = csv.writer(devices_file)
            writer.writerow(device_to_enable)

        # Optional: Provide success feedback
        return redirect("devices")

    return JsonResponse({"error": "Invalid request method"}, status=405)

import os
import signal
import subprocess
from django.http import JsonResponse
from django.shortcuts import render

# Path to your monitoring script
MONITOR_SCRIPT = "app2.py"

# Global variable to keep track of the process
monitor_process = None


def toggle_monitor(request):
    """Toggle the monitoring process on or off."""
    global monitor_process

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "start":
            if monitor_process is None or monitor_process.poll() is not None:  # Process not running
                try:
                    monitor_process = subprocess.Popen(
                        ["python", MONITOR_SCRIPT],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    return JsonResponse({"status": "Monitoring started"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to start monitoring: {e}"}, status=500)
            else:
                return JsonResponse({"message": "Monitoring is already running"}, status=200)

        elif action == "stop":
            if monitor_process and monitor_process.poll() is None:  # Process running
                try:
                    os.kill(monitor_process.pid, signal.SIGTERM)
                    monitor_process = None
                    return JsonResponse({"status": "Monitoring stopped"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to stop monitoring: {e}"}, status=500)
            else:
                return JsonResponse({"message": "Monitoring is not running"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)
