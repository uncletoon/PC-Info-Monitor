import platform
import psutil
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

# Create main GUI window
window = tk.Tk()
window.title("System Information Viewer")
window.geometry("800x600")

# Add a scrollable text box to display info
output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Consolas", 12))
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Helper to insert text into the text box
def display_output(text):
    output_box.insert(tk.END, text + '\n')
    output_box.see(tk.END)  # Auto scroll to bottom

# Redirected versions of your functions that print to GUI
def get_system_info():
    display_output("="*30 + " System Information " + "="*30)
    uname = platform.uname()
    display_output(f"System: {uname.system}")
    display_output(f"Node Name: {uname.node}")
    display_output(f"Release: {uname.release}")
    display_output(f"Version: {uname.version}")
    display_output(f"Machine: {uname.machine}")
    display_output(f"Processor: {uname.processor}")

def get_cpu_info():
    display_output("="*30 + " CPU Info " + "="*30)
    display_output(f"Physical cores: {psutil.cpu_count(logical=False)}")
    display_output(f"Total cores: {psutil.cpu_count(logical=True)}")
    display_output(f"Max Frequency: {psutil.cpu_freq().max:.2f} MHz")
    display_output(f"Min Frequency: {psutil.cpu_freq().min:.2f} MHz")
    display_output(f"Current Frequency: {psutil.cpu_freq().current:.2f} MHz")
    display_output(f"CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        display_output(f"Core {i}: {percentage}%")
    display_output(f"Total CPU Usage: {psutil.cpu_percent()}%")

def get_memory_info():
    display_output("="*30 + " Memory Information " + "="*30)
    svmem = psutil.virtual_memory()
    display_output(f"Total: {svmem.total / (1024 ** 3):.2f} GB")
    display_output(f"Available: {svmem.available / (1024 ** 3):.2f} GB")
    display_output(f"Used: {svmem.used / (1024 ** 3):.2f} GB")
    display_output(f"Percentage: {svmem.percent}%")

def get_disk_info():
    display_output("="*30 + " Disk Information " + "="*30)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        display_output(f"=== Device: {partition.device} ===")
        display_output(f"  Mountpoint: {partition.mountpoint}")
        display_output(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        display_output(f"  Total Size: {partition_usage.total / (1024 ** 3):.2f} GB")
        display_output(f"  Used: {partition_usage.used / (1024 ** 3):.2f} GB")
        display_output(f"  Free: {partition_usage.free / (1024 ** 3):.2f} GB")
        display_output(f"  Percentage: {partition_usage.percent}%")
    disk_io = psutil.disk_io_counters()
    display_output(f"Total read: {disk_io.read_bytes / (1024 ** 3):.2f} GB")
    display_output(f"Total write: {disk_io.write_bytes / (1024 ** 3):.2f} GB")

def get_network_info():
    display_output("="*30 + " Network Information " + "="*30)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            display_output(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                display_output(f"  IP Address: {address.address}")
                display_output(f"  Netmask: {address.netmask}")
                display_output(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                display_output(f"  MAC Address: {address.address}")
                display_output(f"  Netmask: {address.netmask}")
                display_output(f"  Broadcast MAC: {address.broadcast}")
    net_io = psutil.net_io_counters()
    display_output(f"Total Bytes Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB")
    display_output(f"Total Bytes Received: {net_io.bytes_recv / (1024 ** 2):.2f} MB")

def get_boot_time():
    display_output("="*30 + " Boot Time " + "="*30)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    display_output(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

# Create buttons for each info category
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(button_frame, text="System Info", command=get_system_info).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="CPU Info", command=get_cpu_info).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Memory Info", command=get_memory_info).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Disk Info", command=get_disk_info).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Network Info", command=get_network_info).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="Boot Time", command=get_boot_time).grid(row=0, column=5, padx=5)

# Clear button
tk.Button(window, text="Clear Output", command=lambda: output_box.delete('1.0', tk.END)).pack(pady=5)

# Start GUI loop
window.mainloop()
