import platform
import psutil
import socket
import os
from datetime import datetime

def get_system_info():
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")

def get_cpu_info():
    print("="*40, "CPU Info", "="*40)
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    print(f"Max Frequency: {psutil.cpu_freq().max:.2f}Mhz")
    print(f"Min Frequency: {psutil.cpu_freq().min:.2f}Mhz")
    print(f"Current Frequency: {psutil.cpu_freq().current:.2f}Mhz")
    print(f"CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

def get_memory_info():
    print("="*40, "Memory Information", "="*40)
    svmem = psutil.virtual_memory()
    print(f"Total: {svmem.total / (1024 ** 3):.2f} GB")
    print(f"Available: {svmem.available / (1024 ** 3):.2f} GB")
    print(f"Used: {svmem.used / (1024 ** 3):.2f} GB")
    print(f"Percentage: {svmem.percent}%")

def get_disk_info():
    print("="*40, "Disk Information", "="*40)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        print(f"  Total Size: {partition_usage.total / (1024 ** 3):.2f} GB")
        print(f"  Used: {partition_usage.used / (1024 ** 3):.2f} GB")
        print(f"  Free: {partition_usage.free / (1024 ** 3):.2f} GB")
        print(f"  Percentage: {partition_usage.percent}%")
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {disk_io.read_bytes / (1024 ** 3):.2f} GB")
    print(f"Total write: {disk_io.write_bytes / (1024 ** 3):.2f} GB")

def get_network_info():
    print("="*40, "Network Information", "="*40)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB")
    print(f"Total Bytes Received: {net_io.bytes_recv / (1024 ** 2):.2f} MB")

def get_boot_time():
    print("="*40, "Boot Time", "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

if __name__ == "__main__":
    get_system_info()
    get_cpu_info()
    get_memory_info()
    get_disk_info()
    get_network_info()
    get_boot_time()
    input("Press Enter to exit...")