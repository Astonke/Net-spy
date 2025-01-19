import csv
from csv import *
from encron.tools import find_file

DEVICES_CSV = find_file('devices.csv')
TEMP_CSV = find_file('temp.csv')

def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        return [row for row in reader]

def write_csv(file_path, data):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def get_devices():
    return read_csv(DEVICES_CSV)

def get_all_devices():
    return read_csv(TEMP_CSV)

def save_device(ip, description):
    devices = get_devices()
    all_devices = get_all_devices()
    devices.append([ip, description, 'enabled'])
    all_devices.append([ip, description, 'enabled'])
    write_csv(DEVICES_CSV, devices)
    write_csv(TEMP_CSV, all_devices)

def restore(ip,description):
    devices = get_devices()
    all_devices = get_all_devices()
    devices.append([ip, description, 'enabled'])
    #all_devices.append([ip, description, 'enabled'])
    write_csv(DEVICES_CSV, devices)

def remove_device(ip):
    devices = [row for row in get_all_devices() if row[0] != ip]
    write_csv(DEVICES_CSV, devices)

def rmd(ip):
    devices = [row for row in get_all_devices() if row[0] != ip]
    write_csv(DEVICES_CSV, devices)
    write_csv(TEMP_CSV,devices)

def toggle_device(ip, status):
    devices = get_all_devices()
    for device in devices:
        if device[0] == ip:
            device[2] = status
    write_csv(TEMP_CSV, devices)
