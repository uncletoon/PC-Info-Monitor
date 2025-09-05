import platform
import psutil
import socket
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque

class AdvancedSystemMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced System Information Monitor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Data storage for real-time monitoring
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        self.disk_history = deque(maxlen=60)
        
        # Monitoring flags
        self.monitoring = False
        self.monitor_thread = None
        
        self.create_widgets()
        self.setup_plots()
        
    def configure_styles(self):
        # Configure ttk styles for dark theme
        self.style.configure('Title.TLabel', 
                           background='#2b2b2b', 
                           foreground='#ffffff',
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Heading.TLabel',
                           background='#3c3c3c',
                           foreground='#ffffff',
                           font=('Arial', 12, 'bold'))
        
        self.style.configure('Info.TLabel',
                           background='#3c3c3c',
                           foreground='#e0e0e0',
                           font=('Arial', 10))
        
        self.style.configure('Custom.TFrame',
                           background='#3c3c3c',
                           relief='raised',
                           borderwidth=2)
        
        self.style.configure('Custom.TNotebook',
                           background='#2b2b2b',
                           tabposition='n')
        
        self.style.configure('Custom.TNotebook.Tab',
                           background='#404040',
                           foreground='#ffffff',
                           padding=[20, 10])
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced System Monitor", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = tk.Button(control_frame, text="Start Monitoring", 
                                  command=self.start_monitoring,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                  relief='flat', padx=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Monitoring", 
                                 command=self.stop_monitoring,
                                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                                 relief='flat', padx=20, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="Refresh Static Info", 
                                    command=self.refresh_static_info,
                                    bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                    relief='flat', padx=20)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Stopped", 
                                   bg='#2b2b2b', fg='#ff9800', font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_overview_tab()
        self.create_performance_tab()
        self.create_system_tab()
        self.create_network_tab()
        self.create_processes_tab()
        
    def create_overview_tab(self):
        # Overview tab
        overview_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(overview_frame, text="Overview")
        
        # Create grid layout
        overview_frame.grid_rowconfigure(1, weight=1)
        overview_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Quick stats frame
        stats_frame = ttk.LabelFrame(overview_frame, text="Quick Statistics", 
                                   style='Custom.TFrame')
        stats_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        self.quick_stats = {}
        stats_labels = ['CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Speed']
        for i, label in enumerate(stats_labels):
            ttk.Label(stats_frame, text=f"{label}:", style='Heading.TLabel').grid(
                row=0, column=i*2, padx=10, pady=5, sticky='w')
            self.quick_stats[label] = ttk.Label(stats_frame, text="N/A", style='Info.TLabel')
            self.quick_stats[label].grid(row=0, column=i*2+1, padx=10, pady=5, sticky='w')
        
        # System info frame
        sys_info_frame = ttk.LabelFrame(overview_frame, text="System Information", 
                                      style='Custom.TFrame')
        sys_info_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        self.sys_info_text = scrolledtext.ScrolledText(sys_info_frame, 
                                                      height=15, width=40,
                                                      bg='#404040', fg='#ffffff',
                                                      font=('Consolas', 9))
        self.sys_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Hardware info frame
        hw_info_frame = ttk.LabelFrame(overview_frame, text="Hardware Information", 
                                     style='Custom.TFrame')
        hw_info_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        self.hw_info_text = scrolledtext.ScrolledText(hw_info_frame, 
                                                     height=15, width=40,
                                                     bg='#404040', fg='#ffffff',
                                                     font=('Consolas', 9))
        self.hw_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_performance_tab(self):
        # Performance monitoring tab
        perf_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(perf_frame, text="Performance")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor='#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, perf_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_system_tab(self):
        # System details tab
        system_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(system_frame, text="System Details")
        
        # Create paned window for better layout
        paned = ttk.PanedWindow(system_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Disk information
        disk_frame = ttk.LabelFrame(paned, text="Disk Information", style='Custom.TFrame')
        paned.add(disk_frame, weight=1)
        
        self.disk_tree = ttk.Treeview(disk_frame, columns=('Size', 'Used', 'Free', 'Usage%'), show='tree headings')
        self.disk_tree.heading('#0', text='Drive')
        self.disk_tree.heading('Size', text='Size (GB)')
        self.disk_tree.heading('Used', text='Used (GB)')
        self.disk_tree.heading('Free', text='Free (GB)')
        self.disk_tree.heading('Usage%', text='Usage %')
        self.disk_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right frame - Memory details
        mem_frame = ttk.LabelFrame(paned, text="Memory Details", style='Custom.TFrame')
        paned.add(mem_frame, weight=1)
        
        self.mem_text = scrolledtext.ScrolledText(mem_frame, 
                                                 bg='#404040', fg='#ffffff',
                                                 font=('Consolas', 9))
        self.mem_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_network_tab(self):
        # Network information tab
        network_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(network_frame, text="Network")
        
        # Network interfaces tree
        self.net_tree = ttk.Treeview(network_frame, columns=('Type', 'Address', 'Netmask'), show='tree headings')
        self.net_tree.heading('#0', text='Interface')
        self.net_tree.heading('Type', text='Type')
        self.net_tree.heading('Address', text='Address')
        self.net_tree.heading('Netmask', text='Netmask')
        self.net_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_processes_tab(self):
        # Process information tab
        proc_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(proc_frame, text="Processes")
        
        # Control frame
        proc_control = ttk.Frame(proc_frame)
        proc_control.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(proc_control, text="Sort by:", style='Heading.TLabel').pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="cpu")
        sort_combo = ttk.Combobox(proc_control, textvariable=self.sort_var, 
                                 values=['cpu', 'memory', 'name', 'pid'])
        sort_combo.pack(side=tk.LEFT, padx=5)
        
        refresh_proc_btn = tk.Button(proc_control, text="Refresh Processes", 
                                   command=self.refresh_processes,
                                   bg='#9C27B0', fg='white', font=('Arial', 9),
                                   relief='flat')
        refresh_proc_btn.pack(side=tk.LEFT, padx=10)
        
        # Process tree
        self.proc_tree = ttk.Treeview(proc_frame, columns=('PID', 'CPU%', 'Memory%', 'Status'), show='tree headings')
        self.proc_tree.heading('#0', text='Process Name')
        self.proc_tree.heading('PID', text='PID')
        self.proc_tree.heading('CPU%', text='CPU %')
        self.proc_tree.heading('Memory%', text='Memory %')
        self.proc_tree.heading('Status', text='Status')
        
        # Scrollbar for process tree
        proc_scroll = ttk.Scrollbar(proc_frame, orient=tk.VERTICAL, command=self.proc_tree.yview)
        self.proc_tree.configure(yscrollcommand=proc_scroll.set)
        
        self.proc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        proc_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def setup_plots(self):
        # Clear and setup subplots
        self.fig.clear()
        
        # Create subplots with dark theme
        self.ax1 = self.fig.add_subplot(2, 2, 1, facecolor='#404040')
        self.ax2 = self.fig.add_subplot(2, 2, 2, facecolor='#404040')
        self.ax3 = self.fig.add_subplot(2, 2, 3, facecolor='#404040')
        self.ax4 = self.fig.add_subplot(2, 2, 4, facecolor='#404040')
        
        # Customize axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        self.ax1.set_title('CPU Usage (%)', color='white')
        self.ax2.set_title('Memory Usage (%)', color='white')
        self.ax3.set_title('Network I/O (MB/s)', color='white')
        self.ax4.set_title('Disk I/O (MB/s)', color='white')
        
        self.fig.tight_layout()
    
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="Status: Monitoring", fg='#4CAF50')
            
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg='#ff9800')
    
    def monitor_loop(self):
        prev_net = psutil.net_io_counters()
        prev_disk = psutil.disk_io_counters()
        
        while self.monitoring:
            try:
                # Get current stats
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                current_net = psutil.net_io_counters()
                
                # Handle case where disk_io_counters might return None
                current_disk = psutil.disk_io_counters()
                if current_disk is None:
                    current_disk = prev_disk
                
                # Calculate network speed (bytes per second)
                net_speed = ((current_net.bytes_sent + current_net.bytes_recv) - 
                           (prev_net.bytes_sent + prev_net.bytes_recv)) / (1024 * 1024)  # MB/s
                
                # Calculate disk speed
                if current_disk and prev_disk:
                    disk_speed = ((current_disk.read_bytes + current_disk.write_bytes) - 
                                (prev_disk.read_bytes + prev_disk.write_bytes)) / (1024 * 1024)  # MB/s
                else:
                    disk_speed = 0
                
                # Store data
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                self.network_history.append(max(0, net_speed))
                self.disk_history.append(max(0, disk_speed))
                
                # Update GUI in main thread
                self.root.after(0, self.update_gui, cpu_percent, memory.percent, net_speed)
                
                prev_net = current_net
                if current_disk:
                    prev_disk = current_disk
                
                time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def update_gui(self, cpu_percent, memory_percent, net_speed):
        # Update quick stats
        self.quick_stats['CPU Usage'].config(text=f"{cpu_percent:.1f}%")
        self.quick_stats['Memory Usage'].config(text=f"{memory_percent:.1f}%")
        
        # Update disk usage
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            self.quick_stats['Disk Usage'].config(text=f"{disk_percent:.1f}%")
        except:
            self.quick_stats['Disk Usage'].config(text="N/A")
        
        self.quick_stats['Network Speed'].config(text=f"{net_speed:.2f} MB/s")
        
        # Update plots
        self.update_plots()
    
    def update_plots(self):
        if len(self.cpu_history) > 1:
            # Clear and redraw plots
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
                ax.set_facecolor('#404040')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('white')
            
            # Plot data
            time_points = list(range(len(self.cpu_history)))
            
            self.ax1.plot(time_points, list(self.cpu_history), color='#ff6b6b', linewidth=2)
            self.ax1.set_title('CPU Usage (%)', color='white')
            self.ax1.set_ylim(0, 100)
            
            self.ax2.plot(time_points, list(self.memory_history), color='#4ecdc4', linewidth=2)
            self.ax2.set_title('Memory Usage (%)', color='white')
            self.ax2.set_ylim(0, 100)
            
            self.ax3.plot(time_points, list(self.network_history), color='#45b7d1', linewidth=2)
            self.ax3.set_title('Network I/O (MB/s)', color='white')
            
            self.ax4.plot(time_points, list(self.disk_history), color='#f9ca24', linewidth=2)
            self.ax4.set_title('Disk I/O (MB/s)', color='white')
            
            self.fig.tight_layout()
            self.canvas.draw()
    
    def refresh_static_info(self):
        # Update system information
        self.update_system_info()
        self.update_hardware_info()
        self.update_disk_info()
        self.update_memory_info()
        self.update_network_info()
        self.refresh_processes()
    
    def update_system_info(self):
        self.sys_info_text.delete('1.0', tk.END)
        
        info = []
        uname = platform.uname()
        info.append("=== SYSTEM INFORMATION ===")
        info.append(f"System: {uname.system}")
        info.append(f"Node Name: {uname.node}")
        info.append(f"Release: {uname.release}")
        info.append(f"Version: {uname.version}")
        info.append(f"Machine: {uname.machine}")
        info.append(f"Processor: {uname.processor}")
        info.append("")
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        info.append(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"Uptime: {str(uptime).split('.')[0]}")
        
        self.sys_info_text.insert(tk.END, '\n'.join(info))
    
    def update_hardware_info(self):
        self.hw_info_text.delete('1.0', tk.END)
        
        info = []
        info.append("=== HARDWARE INFORMATION ===")
        
        # CPU Info
        info.append(f"Physical cores: {psutil.cpu_count(logical=False)}")
        info.append(f"Total cores: {psutil.cpu_count(logical=True)}")
        
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            info.append(f"Max Frequency: {cpu_freq.max:.2f} MHz")
            info.append(f"Min Frequency: {cpu_freq.min:.2f} MHz")
            info.append(f"Current Frequency: {cpu_freq.current:.2f} MHz")
        
        info.append("")
        
        # Memory Info
        svmem = psutil.virtual_memory()
        info.append("=== MEMORY ===")
        info.append(f"Total: {svmem.total / (1024**3):.2f} GB")
        info.append(f"Available: {svmem.available / (1024**3):.2f} GB")
        info.append(f"Used: {svmem.used / (1024**3):.2f} GB")
        info.append(f"Percentage: {svmem.percent}%")
        
        # Swap memory
        swap = psutil.swap_memory()
        info.append("")
        info.append("=== SWAP ===")
        if swap.total > 0:
            info.append(f"Total: {swap.total / (1024**3):.2f} GB")
            info.append(f"Free: {swap.free / (1024**3):.2f} GB")
            info.append(f"Used: {swap.used / (1024**3):.2f} GB")
            info.append(f"Percentage: {swap.percent}%")
        else:
            info.append("No swap memory configured")
        
        self.hw_info_text.insert(tk.END, '\n'.join(info))
    
    def update_disk_info(self):
        # Clear disk tree
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_tree.insert('', 'end', 
                                    text=f"{partition.device} ({partition.fstype})",
                                    values=(
                                        f"{usage.total / (1024**3):.2f}",
                                        f"{usage.used / (1024**3):.2f}",
                                        f"{usage.free / (1024**3):.2f}",
                                        f"{(usage.used / usage.total) * 100:.1f}%"
                                    ))
            except PermissionError:
                continue
    
    def update_memory_info(self):
        self.mem_text.delete('1.0', tk.END)
        
        info = []
        svmem = psutil.virtual_memory()
        
        info.append("=== VIRTUAL MEMORY ===")
        info.append(f"Total: {svmem.total / (1024**3):.2f} GB")
        info.append(f"Available: {svmem.available / (1024**3):.2f} GB")
        info.append(f"Used: {svmem.used / (1024**3):.2f} GB")
        
        # Check if free attribute exists (not available on all systems)
        if hasattr(svmem, 'free'):
            info.append(f"Free: {svmem.free / (1024**3):.2f} GB")
        
        # Check if cached attribute exists (Linux-specific)
        if hasattr(svmem, 'cached'):
            info.append(f"Cached: {svmem.cached / (1024**3):.2f} GB")
        
        # Check if buffers attribute exists (Linux-specific)
        if hasattr(svmem, 'buffers'):
            info.append(f"Buffers: {svmem.buffers / (1024**3):.2f} GB")
        
        info.append(f"Percentage: {svmem.percent}%")
        
        # Add swap memory information
        swap = psutil.swap_memory()
        info.append("")
        info.append("=== SWAP MEMORY ===")
        if swap.total > 0:
            info.append(f"Total: {swap.total / (1024**3):.2f} GB")
            info.append(f"Used: {swap.used / (1024**3):.2f} GB")
            info.append(f"Free: {swap.free / (1024**3):.2f} GB")
            info.append(f"Percentage: {swap.percent}%")
        else:
            info.append("No swap memory configured")
        
        self.mem_text.insert(tk.END, '\n'.join(info))
    
    def update_network_info(self):
        # Clear network tree
        for item in self.net_tree.get_children():
            self.net_tree.delete(item)
        
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            interface_item = self.net_tree.insert('', 'end', text=interface_name)
            
            for address in interface_addresses:
                addr_type = str(address.family).split('.')[-1]
                self.net_tree.insert(interface_item, 'end', 
                                   text="",
                                   values=(
                                       addr_type,
                                       address.address,
                                       address.netmask or "N/A"
                                   ))
    
    def refresh_processes(self):
        # Clear process tree
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)
        
        try:
            # Get all processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            sort_key = self.sort_var.get()
            if sort_key == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            elif sort_key == 'memory':
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            elif sort_key == 'name':
                processes.sort(key=lambda x: x['name'] or '')
            elif sort_key == 'pid':
                processes.sort(key=lambda x: x['pid'] or 0)
            
            # Display top 50 processes
            for proc in processes[:50]:
                self.proc_tree.insert('', 'end',
                                    text=proc['name'] or 'N/A',
                                    values=(
                                        proc['pid'] or 'N/A',
                                        f"{proc['cpu_percent'] or 0:.1f}%",
                                        f"{proc['memory_percent'] or 0:.1f}%",
                                        proc['status'] or 'N/A'
                                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh processes: {e}")
    
    def run(self):
        # Initialize with static information
        self.refresh_static_info()
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = AdvancedSystemMonitor()
        app.run()
    except ImportError as e:
        if "matplotlib" in str(e):
            print("Please install matplotlib: pip install matplotlib")
        else:
            print(f"Import error: {e}")
    except Exception as e:
        print(f"Error running application: {e}")