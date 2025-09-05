import platform
import psutil
import socket
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter.font import Font
import webbrowser
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class SystemInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Information Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg='#f0f0f0')
        
        # Custom fonts
        self.title_font = Font(family="Segoe UI", size=12, weight="bold")
        self.button_font = Font(family="Segoe UI", size=10)
        self.mono_font = Font(family="Consolas", size=10)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=self.button_font, padding=5)
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=self.button_font, padding=[10, 5])
        self.style.map('TButton', 
                      foreground=[('pressed', 'white'), ('active', 'white')],
                      background=[('pressed', '#0066cc'), ('active', '#0066cc')])
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="System Information Dashboard", 
            font=self.title_font,
            background='#f0f0f0'
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Add refresh and quit buttons
        self.button_frame = ttk.Frame(self.header_frame)
        self.button_frame.pack(side=tk.RIGHT)
        
        self.refresh_btn = ttk.Button(
            self.button_frame, 
            text="🔄 Refresh All", 
            command=self.refresh_all,
            style='TButton'
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = ttk.Button(
            self.button_frame, 
            text="🚪 Quit", 
            command=self.on_close,
            style='TButton'
        )
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_summary_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_disk_tab()
        self.create_network_tab()
        self.create_process_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initialize data
        self.refresh_all()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_summary_tab(self):
        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="Summary")
        
        # Summary output
        self.summary_output = scrolledtext.ScrolledText(
            self.summary_tab,
            wrap=tk.WORD,
            font=self.mono_font,
            bg='white',
            padx=10,
            pady=10
        )
        self.summary_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quick stats frame
        self.quick_stats_frame = ttk.Frame(self.summary_tab)
        self.quick_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cpu_usage_var = tk.StringVar()
        self.mem_usage_var = tk.StringVar()
        self.disk_usage_var = tk.StringVar()
        
        ttk.Label(self.quick_stats_frame, text="CPU Usage:").pack(side=tk.LEFT, padx=5)
        ttk.Label(self.quick_stats_frame, textvariable=self.cpu_usage_var, font=self.mono_font).pack(side=tk.LEFT)
        
        ttk.Label(self.quick_stats_frame, text="Memory Usage:").pack(side=tk.LEFT, padx=10)
        ttk.Label(self.quick_stats_frame, textvariable=self.mem_usage_var, font=self.mono_font).pack(side=tk.LEFT)
        
        ttk.Label(self.quick_stats_frame, text="Disk Usage:").pack(side=tk.LEFT, padx=10)
        ttk.Label(self.quick_stats_frame, textvariable=self.disk_usage_var, font=self.mono_font).pack(side=tk.LEFT)
    
    def create_cpu_tab(self):
        self.cpu_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cpu_tab, text="CPU")
        
        # CPU info frame
        self.cpu_info_frame = ttk.Frame(self.cpu_tab)
        self.cpu_info_frame.pack(fill=tk.X, pady=5)
        
        self.cpu_output = scrolledtext.ScrolledText(
            self.cpu_info_frame,
            wrap=tk.WORD,
            font=self.mono_font,
            height=10,
            bg='white',
            padx=10,
            pady=10
        )
        self.cpu_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # CPU usage graph
        self.cpu_graph_frame = ttk.Frame(self.cpu_tab)
        self.cpu_graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.cpu_ax.set_title('CPU Usage (%)')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlabel('Time')
        self.cpu_ax.set_ylabel('Usage %')
        self.cpu_lines = []
        
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.cpu_graph_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # CPU core buttons
        self.core_buttons_frame = ttk.Frame(self.cpu_tab)
        self.core_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.core_vars = []
        for i in range(psutil.cpu_count()):
            var = tk.IntVar(value=1)
            self.core_vars.append(var)
            cb = ttk.Checkbutton(
                self.core_buttons_frame,
                text=f"Core {i}",
                variable=var,
                onvalue=1,
                offvalue=0
            )
            cb.pack(side=tk.LEFT, padx=5)
    
    def create_memory_tab(self):
        self.memory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_tab, text="Memory")
        
        # Memory info
        self.mem_output = scrolledtext.ScrolledText(
            self.memory_tab,
            wrap=tk.WORD,
            font=self.mono_font,
            height=8,
            bg='white',
            padx=10,
            pady=10
        )
        self.mem_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory usage graph
        self.mem_graph_frame = ttk.Frame(self.memory_tab)
        self.mem_graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.mem_fig, self.mem_ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.mem_ax.set_title('Memory Usage')
        self.mem_ax.set_ylim(0, 100)
        self.mem_ax.set_xlabel('Time')
        self.mem_ax.set_ylabel('Usage %')
        self.mem_line, = self.mem_ax.plot([], [], 'r-')
        
        self.mem_canvas = FigureCanvasTkAgg(self.mem_fig, master=self.mem_graph_frame)
        self.mem_canvas.draw()
        self.mem_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Swap memory info
        self.swap_output = scrolledtext.ScrolledText(
            self.memory_tab,
            wrap=tk.WORD,
            font=self.mono_font,
            height=4,
            bg='white',
            padx=10,
            pady=10
        )
        self.swap_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_disk_tab(self):
        self.disk_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.disk_tab, text="Disk")
        
        # Disk info
        self.disk_output = scrolledtext.ScrolledText(
            self.disk_tab,
            wrap=tk.WORD,
            font=self.mono_font,
            height=10,
            bg='white',
            padx=10,
            pady=10
        )
        self.disk_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Disk usage graph
        self.disk_graph_frame = ttk.Frame(self.disk_tab)
        self.disk_graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.disk_fig, self.disk_ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.disk_ax.set_title('Disk Usage')
        self.disk_ax.set_ylim(0, 100)
        self.disk_ax.set_xlabel('Time')
        self.disk_ax.set_ylabel('Usage %')
        self.disk_lines = []
        
        self.disk_canvas = FigureCanvasTkAgg(self.disk_fig, master=self.disk_graph_frame)
        self.disk_canvas.draw()
        self.disk_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_network_tab(self):
        self.network_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.network_tab, text="Network")
        
        # Network info
        self.net_output = scrolledtext.ScrolledText(
            self.network_tab,
            wrap=tk.WORD,
            font=self.mono_font,
            height=10,
            bg='white',
            padx=10,
            pady=10
        )
        self.net_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Network traffic graph
        self.net_graph_frame = ttk.Frame(self.network_tab)
        self.net_graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.net_fig, (self.net_ax1, self.net_ax2) = plt.subplots(2, 1, figsize=(8, 4), dpi=100)
        self.net_ax1.set_title('Network Traffic')
        self.net_ax1.set_ylabel('Sent (MB)')
        self.net_ax2.set_ylabel('Received (MB)')
        self.net_sent_line, = self.net_ax1.plot([], [], 'b-')
        self.net_recv_line, = self.net_ax2.plot([], [], 'g-')
        
        self.net_canvas = FigureCanvasTkAgg(self.net_fig, master=self.net_graph_frame)
        self.net_canvas.draw()
        self.net_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_process_tab(self):
        self.process_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.process_tab, text="Processes")
        
        # Treeview for processes
        self.process_tree = ttk.Treeview(
            self.process_tab,
            columns=('pid', 'name', 'cpu', 'memory', 'status'),
            show='headings'
        )
        
        self.process_tree.heading('pid', text='PID')
        self.process_tree.heading('name', text='Name')
        self.process_tree.heading('cpu', text='CPU %')
        self.process_tree.heading('memory', text='Memory %')
        self.process_tree.heading('status', text='Status')
        
        self.process_tree.column('pid', width=80, anchor=tk.CENTER)
        self.process_tree.column('name', width=200, anchor=tk.W)
        self.process_tree.column('cpu', width=80, anchor=tk.CENTER)
        self.process_tree.column('memory', width=80, anchor=tk.CENTER)
        self.process_tree.column('status', width=100, anchor=tk.CENTER)
        
        self.process_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Process control buttons
        self.process_btn_frame = ttk.Frame(self.process_tab)
        self.process_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            self.process_btn_frame,
            text="Refresh",
            command=self.update_process_list
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.process_btn_frame,
            text="Kill Process",
            command=self.kill_selected_process
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.process_btn_frame,
            text="Details",
            command=self.show_process_details
        ).pack(side=tk.LEFT, padx=5)
        
        # Sort options
        self.sort_var = tk.StringVar(value='cpu')
        ttk.Label(self.process_btn_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        ttk.OptionMenu(
            self.process_btn_frame,
            self.sort_var,
            'cpu',
            'cpu',
            'memory',
            'name',
            'pid',
            command=lambda _: self.update_process_list()
        ).pack(side=tk.LEFT)
    
    def refresh_all(self):
        self.status_var.set("Refreshing data...")
        self.root.update()
        
        self.get_system_info()
        self.get_cpu_info()
        self.get_memory_info()
        self.get_disk_info()
        self.get_network_info()
        self.update_process_list()
        
        self.status_var.set("Data refreshed at " + datetime.now().strftime("%H:%M:%S"))
    
    def get_system_info(self):
        self.summary_output.delete('1.0', tk.END)
        
        uname = platform.uname()
        self.summary_output.insert(tk.END, "=== System Information ===\n", 'header')
        self.summary_output.insert(tk.END, f"{'System:':<15}{uname.system}\n")
        self.summary_output.insert(tk.END, f"{'Node Name:':<15}{uname.node}\n")
        self.summary_output.insert(tk.END, f"{'Release:':<15}{uname.release}\n")
        self.summary_output.insert(tk.END, f"{'Version:':<15}{uname.version}\n")
        self.summary_output.insert(tk.END, f"{'Machine:':<15}{uname.machine}\n")
        self.summary_output.insert(tk.END, f"{'Processor:':<15}{uname.processor}\n\n")
        
        # Boot time
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        self.summary_output.insert(tk.END, "=== Boot Time ===\n", 'header')
        self.summary_output.insert(tk.END, f"Last boot: {bt.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.summary_output.insert(tk.END, f"Uptime: {str(datetime.now() - bt).split('.')[0]}\n\n")
        
        # Users
        self.summary_output.insert(tk.END, "=== Users ===\n", 'header')
        users = psutil.users()
        for user in users:
            self.summary_output.insert(tk.END, 
                f"User: {user.name} (Terminal: {user.terminal}, Host: {user.host}, Started: {datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')})\n")
    
    def get_cpu_info(self):
        self.cpu_output.delete('1.0', tk.END)
        
        self.cpu_output.insert(tk.END, "=== CPU Information ===\n", 'header')
        self.cpu_output.insert(tk.END, f"{'Physical cores:':<20}{psutil.cpu_count(logical=False)}\n")
        self.cpu_output.insert(tk.END, f"{'Total cores:':<20}{psutil.cpu_count(logical=True)}\n")
        
        freq = psutil.cpu_freq()
        self.cpu_output.insert(tk.END, f"{'Max Frequency:':<20}{freq.max:.2f} MHz\n")
        self.cpu_output.insert(tk.END, f"{'Min Frequency:':<20}{freq.min:.2f} MHz\n")
        self.cpu_output.insert(tk.END, f"{'Current Frequency:':<20}{freq.current:.2f} MHz\n\n")
        
        self.cpu_output.insert(tk.END, "=== CPU Usage ===\n", 'header')
        usage = psutil.cpu_percent(percpu=True, interval=1)
        total_usage = psutil.cpu_percent()
        
        self.cpu_usage_var.set(f"{total_usage:.1f}%")
        
        for i, percentage in enumerate(usage):
            self.cpu_output.insert(tk.END, f"Core {i}: {percentage}%\n")
        
        self.cpu_output.insert(tk.END, f"\nTotal CPU Usage: {total_usage}%\n")
        
        # CPU stats
        stats = psutil.cpu_stats()
        self.cpu_output.insert(tk.END, "\n=== CPU Stats ===\n", 'header')
        self.cpu_output.insert(tk.END, f"{'Context switches:':<20}{stats.ctx_switches}\n")
        self.cpu_output.insert(tk.END, f"{'Interrupts:':<20}{stats.interrupts}\n")
        self.cpu_output.insert(tk.END, f"{'Soft interrupts:':<20}{stats.soft_interrupts}\n")
        self.cpu_output.insert(tk.END, f"{'Syscalls:':<20}{stats.syscalls}\n")
    
    def get_memory_info(self):
        self.mem_output.delete('1.0', tk.END)
        self.swap_output.delete('1.0', tk.END)
        
        # Virtual memory
        svmem = psutil.virtual_memory()
        self.mem_output.insert(tk.END, "=== Memory Information ===\n", 'header')
        self.mem_output.insert(tk.END, f"{'Total:':<15}{svmem.total / (1024 ** 3):.2f} GB\n")
        self.mem_output.insert(tk.END, f"{'Available:':<15}{svmem.available / (1024 ** 3):.2f} GB\n")
        self.mem_output.insert(tk.END, f"{'Used:':<15}{svmem.used / (1024 ** 3):.2f} GB\n")
        self.mem_output.insert(tk.END, f"{'Percentage:':<15}{svmem.percent}%\n")
        
        self.mem_usage_var.set(f"{svmem.percent:.1f}%")
        
        # Swap memory
        swap = psutil.swap_memory()
        self.swap_output.insert(tk.END, "=== Swap Memory ===\n", 'header')
        self.swap_output.insert(tk.END, f"{'Total:':<15}{swap.total / (1024 ** 3):.2f} GB\n")
        self.swap_output.insert(tk.END, f"{'Used:':<15}{swap.used / (1024 ** 3):.2f} GB\n")
        self.swap_output.insert(tk.END, f"{'Free:':<15}{swap.free / (1024 ** 3):.2f} GB\n")
        self.swap_output.insert(tk.END, f"{'Percentage:':<15}{swap.percent}%\n")
    
    def get_disk_info(self):
        self.disk_output.delete('1.0', tk.END)
        
        partitions = psutil.disk_partitions()
        self.disk_output.insert(tk.END, "=== Disk Information ===\n", 'header')
        
        total_disk_usage = 0
        partition_count = 0
        
        for partition in partitions:
            self.disk_output.insert(tk.END, f"\n=== Device: {partition.device} ===\n", 'subheader')
            self.disk_output.insert(tk.END, f"{'Mountpoint:':<15}{partition.mountpoint}\n")
            self.disk_output.insert(tk.END, f"{'File system:':<15}{partition.fstype}\n")
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_output.insert(tk.END, f"{'Total:':<15}{usage.total / (1024 ** 3):.2f} GB\n")
                self.disk_output.insert(tk.END, f"{'Used:':<15}{usage.used / (1024 ** 3):.2f} GB\n")
                self.disk_output.insert(tk.END, f"{'Free:':<15}{usage.free / (1024 ** 3):.2f} GB\n")
                self.disk_output.insert(tk.END, f"{'Usage:':<15}{usage.percent}%\n")
                
                total_disk_usage += usage.percent
                partition_count += 1
            except PermissionError:
                self.disk_output.insert(tk.END, "Access denied\n")
                continue
        
        if partition_count > 0:
            avg_disk_usage = total_disk_usage / partition_count
            self.disk_usage_var.set(f"{avg_disk_usage:.1f}%")
        
        # Disk IO
        disk_io = psutil.disk_io_counters()
        self.disk_output.insert(tk.END, "\n=== Disk I/O ===\n", 'header')
        self.disk_output.insert(tk.END, f"{'Read count:':<15}{disk_io.read_count}\n")
        self.disk_output.insert(tk.END, f"{'Write count:':<15}{disk_io.write_count}\n")
        self.disk_output.insert(tk.END, f"{'Read bytes:':<15}{disk_io.read_bytes / (1024 ** 3):.2f} GB\n")
        self.disk_output.insert(tk.END, f"{'Write bytes:':<15}{disk_io.write_bytes / (1024 ** 3):.2f} GB\n")
    
    def get_network_info(self):
        self.net_output.delete('1.0', tk.END)
        
        if_addrs = psutil.net_if_addrs()
        self.net_output.insert(tk.END, "=== Network Information ===\n", 'header')
        
        for interface_name, interface_addresses in if_addrs.items():
            self.net_output.insert(tk.END, f"\n=== Interface: {interface_name} ===\n", 'subheader')
            
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    self.net_output.insert(tk.END, f"{'IP Address:':<15}{address.address}\n")
                    self.net_output.insert(tk.END, f"{'Netmask:':<15}{address.netmask}\n")
                    if address.broadcast:
                        self.net_output.insert(tk.END, f"{'Broadcast:':<15}{address.broadcast}\n")
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    self.net_output.insert(tk.END, f"{'MAC Address:':<15}{address.address}\n")
                    self.net_output.insert(tk.END, f"{'Netmask:':<15}{address.netmask}\n")
                    if address.broadcast:
                        self.net_output.insert(tk.END, f"{'Broadcast:':<15}{address.broadcast}\n")
        
        net_io = psutil.net_io_counters()
        self.net_output.insert(tk.END, "\n=== Network I/O ===\n", 'header')
        self.net_output.insert(tk.END, f"{'Bytes sent:':<15}{net_io.bytes_sent / (1024 ** 2):.2f} MB\n")
        self.net_output.insert(tk.END, f"{'Bytes recv:':<15}{net_io.bytes_recv / (1024 ** 2):.2f} MB\n")
        self.net_output.insert(tk.END, f"{'Packets sent:':<15}{net_io.packets_sent}\n")
        self.net_output.insert(tk.END, f"{'Packets recv:':<15}{net_io.packets_recv}\n")
        self.net_output.insert(tk.END, f"{'Errors in:':<15}{net_io.errin}\n")
        self.net_output.insert(tk.END, f"{'Errors out:':<15}{net_io.errout}\n")
        self.net_output.insert(tk.END, f"{'Drops in:':<15}{net_io.dropin}\n")
        self.net_output.insert(tk.END, f"{'Drops out:':<15}{net_io.dropout}\n")
    
    def update_process_list(self):
        for row in self.process_tree.get_children():
            self.process_tree.delete(row)
        
        sort_by = self.sort_var.get()
        reverse = True if sort_by in ['cpu', 'memory'] else False
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append((
                    proc.info['pid'],
                    proc.info['name'],
                    proc.info['cpu_percent'],
                    proc.info['memory_percent'],
                    proc.info['status']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort processes
        if sort_by == 'pid':
            processes.sort(key=lambda x: x[0], reverse=reverse)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x[1].lower(), reverse=reverse)
        elif sort_by == 'cpu':
            processes.sort(key=lambda x: x[2], reverse=reverse)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x[3], reverse=reverse)
        elif sort_by == 'status':
            processes.sort(key=lambda x: x[4], reverse=reverse)
        
        # Add to treeview
        for proc in processes[:100]:  # Limit to top 100
            self.process_tree.insert('', tk.END, values=proc)
    
    def kill_selected_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No process selected")
            return
        
        item = self.process_tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Kill process {name} (PID: {pid})?"):
            try:
                p = psutil.Process(pid)
                p.terminate()
                time.sleep(0.5)
                self.update_process_list()
                messagebox.showinfo("Success", f"Process {name} terminated")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process: {e}")
    
    def show_process_details(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No process selected")
            return
        
        item = self.process_tree.item(selected[0])
        pid = item['values'][0]
        
        try:
            p = psutil.Process(pid)
            with p.oneshot():
                details = (
                    f"=== Process Details ===\n"
                    f"PID: {p.pid}\n"
                    f"Name: {p.name()}\n"
                    f"Status: {p.status()}\n"
                    f"CPU %: {p.cpu_percent():.1f}\n"
                    f"Memory %: {p.memory_percent():.1f}\n"
                    f"Memory RSS: {p.memory_info().rss / (1024 ** 2):.2f} MB\n"
                    f"Memory VMS: {p.memory_info().vms / (1024 ** 2):.2f} MB\n"
                    f"Threads: {p.num_threads()}\n"
                    f"Create Time: {datetime.fromtimestamp(p.create_time()).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Exe: {p.exe()}\n"
                    f"Working Dir: {p.cwd()}\n"
                    f"Command Line: {' '.join(p.cmdline())}\n"
                )
                
                messagebox.showinfo("Process Details", details)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get process details: {e}")
    
    def monitor_system(self):
        cpu_data = [[] for _ in range(psutil.cpu_count())]
        mem_data = []
        disk_data = [[] for _ in range(len(psutil.disk_partitions()))]
        net_sent_data = []
        net_recv_data = []
        
        timestamps = []
        max_points = 60  # Keep last 60 data points
        
        while self.monitoring:
            try:
                # Get current time
                now = time.time()
                timestamps.append(now)
                
                # CPU monitoring
                cpu_percent = psutil.cpu_percent(percpu=True)
                for i, percent in enumerate(cpu_percent):
                    cpu_data[i].append(percent)
                
                # Memory monitoring
                mem_percent = psutil.virtual_memory().percent
                mem_data.append(mem_percent)
                
                # Disk monitoring
                partitions = psutil.disk_partitions()
                for i, part in enumerate(partitions):
                    try:
                        usage = psutil.disk_usage(part.mountpoint).percent
                        disk_data[i].append(usage)
                    except:
                        disk_data[i].append(0)
                
                # Network monitoring
                net_io = psutil.net_io_counters()
                net_sent_data.append(net_io.bytes_sent / (1024 ** 2))
                net_recv_data.append(net_io.bytes_recv / (1024 ** 2))
                
                # Trim data to max_points
                if len(timestamps) > max_points:
                    timestamps.pop(0)
                    for i in range(len(cpu_data)):
                        cpu_data[i].pop(0)
                    mem_data.pop(0)
                    for i in range(len(disk_data)):
                        disk_data[i].pop(0)
                    net_sent_data.pop(0)
                    net_recv_data.pop(0)
                
                # Update CPU graph
                self.cpu_ax.clear()
                self.cpu_ax.set_title('CPU Usage (%)')
                self.cpu_ax.set_ylim(0, 100)
                
                for i, data in enumerate(cpu_data):
                    if self.core_vars[i].get():
                        self.cpu_ax.plot(timestamps, data, label=f'Core {i}')
                
                self.cpu_ax.legend(loc='upper right')
                self.cpu_canvas.draw()
                
                # Update Memory graph
                self.mem_ax.clear()
                self.mem_ax.set_title('Memory Usage (%)')
                self.mem_ax.set_ylim(0, 100)
                self.mem_ax.plot(timestamps, mem_data, 'r-')
                self.mem_canvas.draw()
                
                # Update Disk graph
                self.disk_ax.clear()
                self.disk_ax.set_title('Disk Usage (%)')
                self.disk_ax.set_ylim(0, 100)
                
                for i, data in enumerate(disk_data):
                    if i < len(partitions):
                        self.disk_ax.plot(timestamps, data, label=partitions[i].device)
                
                self.disk_ax.legend(loc='upper right')
                self.disk_canvas.draw()
                
                # Update Network graph
                self.net_ax1.clear()
                self.net_ax2.clear()
                self.net_ax1.set_title('Network Traffic')
                self.net_ax1.plot(timestamps, net_sent_data, 'b-', label='Sent')
                self.net_ax2.plot(timestamps, net_recv_data, 'g-', label='Received')
                self.net_ax1.legend()
                self.net_ax2.legend()
                self.net_canvas.draw()
                
                # Update status
                self.status_var.set(f"Monitoring... Last update: {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def on_close(self):
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemInfoApp(root)
    root.mainloop()