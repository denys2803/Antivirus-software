import platform
import psutil
import socket
# import os

import time

def get_system_info():
    info = {}
    
    # Basic OS information
    info['OS'] = platform.system()
    info['OS Release'] = platform.release()
    info['OS Version'] = platform.version()
    info['Architecture'] = platform.architecture()
    info['Machine'] = platform.machine()
    info['Processor'] = platform.processor()
    
    # CPU information
    info['CPU Cores (Physical)'] = psutil.cpu_count(logical=False)
    info['CPU Cores (Logical)'] = psutil.cpu_count(logical=True)
    info['CPU Frequency'] = psutil.cpu_freq()
    
    # Memory information
    mem = psutil.virtual_memory()
    info['Total Memory'] = f"{mem.total / (1024**3):.2f} GB"
    info['Available Memory'] = f"{mem.available / (1024**3):.2f} GB"
    info['Used Memory'] = f"{mem.used / (1024**3):.2f} GB"
    info['Memory Percentage'] = f"{mem.percent}%"
    
    # Swap memory
    swap = psutil.swap_memory()
    info['Total Swap'] = f"{swap.total / (1024**3):.2f} GB"
    info['Used Swap'] = f"{swap.used / (1024**3):.2f} GB"
    info['Swap Percentage'] = f"{swap.percent}%"
    
    # Disk information
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info[partition.device] = {
                'Mountpoint': partition.mountpoint,
                'File System': partition.fstype,
                'Total': f"{usage.total / (1024**3):.2f} GB",
                'Used': f"{usage.used / (1024**3):.2f} GB",
                'Free': f"{usage.free / (1024**3):.2f} GB",
                'Percentage': f"{usage.percent}%"
            }
        except PermissionError:
            continue
    info['Disks'] = disk_info
    
    # Network information
    hostname = socket.gethostname()
    info['Hostname'] = hostname
    info['IP Addresses'] = {}
    net_if_addrs = psutil.net_if_addrs()
    for interface, addrs in net_if_addrs.items():
        info['IP Addresses'][interface] = [addr.address for addr in addrs if addr.family.name == 'AF_INET']
    
    # Boot time
    boot_time = psutil.boot_time()
    info['Boot Time'] = psutil.datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
    
    # Users
    users = psutil.users()
    info['Logged Users'] = [user.name for user in users]
    
    # Processes (summary)
    info['Total Processes'] = len(psutil.pids())
    
    return info

if __name__ == "__main__":
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    # print(system_info)