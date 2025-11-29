# file: main.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import sys
import os
import json
import ctypes 
import traceback
import datetime 

import matplotlib
matplotlib.use("TkAgg")

from scapy.all import Ether, IP, TCP, UDP, ICMP, ARP

from app_utils import (
    resource_path, MODEL_PATH, STATS_PATH, CONFIG_FILE, ICON_FILE, TRANSLATION_MAP
)
from network_manager import NetworkManager
from anomaly_detector import AnomalyDetector
from behavioral_analyzer import BehavioralAnalyzer

from gui.tab_monitor import MonitorTab
from gui.tab_statistics import StatisticsTab
from gui.tab_settings import SettingsTab
from gui.tab_info import AboutTab, VersionsTab

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

CURRENT_VERSION = "16.2" 

class ThemeToggle(tk.Canvas):
    def __init__(self, parent, command=None, width=60, height=30, bg_color="#f0f0f0"):
        super().__init__(parent, width=width+2, height=height+2, bg=bg_color, highlightthickness=0)
        self.command = command
        self.is_on = False 
        self.on_color = "#4cd964"  
        self.off_color = "#cccccc" 
        self.handle_color = "#ffffff"
        self.width = width
        self.height = height
        self.bg_rect = self.create_line(16, 16, 46, 16, width=28, capstyle=tk.ROUND, fill=self.off_color)
        self.handle_radius = 13
        self.handle = self.create_oval(3, 3, 29, 29, fill=self.handle_color, outline="")
        
        # (SỬA LỖI) Dùng mã Unicode
        self.icon_text = self.create_text(16, 16, text="\u2600", font=("Segoe UI Emoji", 12)) 
        
        self.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.animate()
        if self.command:
            self.command()

    def animate(self):
        if self.is_on:
            self.itemconfig(self.bg_rect, fill=self.on_color)
            self.coords(self.handle, 33, 3, 59, 29) 
            self.coords(self.icon_text, 46, 16)    
            self.itemconfig(self.icon_text, text="\U0001F319") 
        else:
            self.itemconfig(self.bg_rect, fill=self.off_color)
            self.coords(self.handle, 3, 3, 29, 29) 
            self.coords(self.icon_text, 16, 16)
            self.itemconfig(self.icon_text, text="\u2600") 
            
    def set_bg(self, color):
        self.config(bg=color)


class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"TANetAI (v{CURRENT_VERSION}) - Gateway Monitor")
        self.root.geometry("1300x800")
        
        self.CURRENT_VERSION = CURRENT_VERSION
        
        try:
            self.root.iconbitmap(ICON_FILE)
        except Exception as e:
            print(f"Không thể tải icon '{ICON_FILE}': {e}")

        self.net_manager = NetworkManager()
        self.ai_detector = None; self.behavior_analyzer = None
        self.packet_count = 0; self.all_packets_data = [] 
        self.sniff_thread = None; self.stop_sniff_event = threading.Event()
        self.message_queue = queue.Queue()
        self.config = {}; self.config_vars = {} 
        self.target_ips = set()
        
        self.current_theme = "light"
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') 
        
        self.filter_tcp_var = tk.BooleanVar(value=True)
        self.filter_udp_var = tk.BooleanVar(value=True)
        self.filter_icmp_var = tk.BooleanVar(value=True)
        self.filter_arp_var = tk.BooleanVar(value=True)
        self.filter_other_var = tk.BooleanVar(value=True)
        
        self.filter_danger_var = tk.BooleanVar(value=True)
        self.filter_anomaly_var = tk.BooleanVar(value=True)
        self.filter_normal_var = tk.BooleanVar(value=True)

        self.colors_light = {"bg": "#F0F0F0", "fg": "#000000", "frame_bg": "#FFFFFF", "text_bg": "#FFFFFF", "text_fg": "#000000", "header": "#00008B", "danger": "#FF0000", "anomaly": "#E69500", "normal_tree": "#505050", "button": "#E1E1E1", "disabled_fg": "#A0A0A0"}
        self.colors_dark = {"bg": "#2E2E2E", "fg": "#FFFFFF", "frame_bg": "#3C3C3C", "text_bg": "#1E1E1E", "text_fg": "#FFFFFF", "header": "#87CEFA", "danger": "#FF5252", "anomaly": "#FFD700", "normal_tree": "#C0C0C0", "button": "#505050", "disabled_fg": "#777777"}
        
        self.chart_widgets = []
        self.charts = {}

        self.load_config()
        self.create_widgets()
        self.setup_global_copy_paste()
        self.populate_interfaces() 
        self.apply_theme() 
        self.root.after(100, self.process_queue)
        
    def create_widgets(self):
        top_container = ttk.Frame(self.root)
        top_container.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.notebook = ttk.Notebook(top_container, style="App.TNotebook")
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.monitor_tab_instance = MonitorTab(self.notebook, self, style="App.TFrame", padding=5)
        self.statistics_tab = StatisticsTab(self.notebook, self, style="App.TFrame", padding=10) 
        self.settings_tab = SettingsTab(self.notebook, self, style="App.TFrame", padding=10)
        about_tab = AboutTab(self.notebook, self, style="App.TFrame", padding=10)
        versions_tab = VersionsTab(self.notebook, self, style="App.TFrame", padding=10) 
        
        self.notebook.add(self.monitor_tab_instance, text=' 📡 Giám sát ')
        self.notebook.add(self.statistics_tab, text=' 📊 Thống kê ')
        self.notebook.add(self.settings_tab, text=' ⚙️ Cài đặt ')
        self.notebook.add(about_tab, text=' ℹ️ Thông tin ')
        self.notebook.add(versions_tab, text=' 📜 Phiên bản ')
        
        self.notebook.bind("<<TtkNotebookTabChanged>>", self.on_tab_changed)
        
        self.bottom_bar = ttk.Frame(self.root, style="App.TFrame")
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng. Tải cấu hình thành công.")
        self.status_bar = ttk.Label(self.bottom_bar, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="5", style="Status.TLabel")
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.theme_switch = ThemeToggle(self.bottom_bar, command=self.toggle_theme)
        self.theme_switch.pack(side=tk.RIGHT, padx=(10, 0))

    def show_device_scanner(self):
        selected_iface_text = self.iface_var.get()
        if not selected_iface_text:
            messagebox.showwarning("Chưa chọn mạng", "Vui lòng chọn giao diện mạng trước khi quét.")
            return
        
        iface_name = self.interfaces[selected_iface_text]
        
        self.scan_window = tk.Toplevel(self.root)
        self.scan_window.title("Quét thiết bị trong mạng LAN")
        self.scan_window.geometry("500x600")
        
        try:
            self.scan_window.iconbitmap(ICON_FILE)
        except: pass
        
        input_frame = ttk.Frame(self.scan_window, padding=10)
        input_frame.pack(fill='x')
        ttk.Label(input_frame, text="Nhập dải mạng (ví dụ 192.168.1.0/24):").pack(side='left')
        self.ip_range_var = tk.StringVar(value="192.168.1.0/24") 
        ttk.Entry(input_frame, textvariable=self.ip_range_var, width=20).pack(side='left', padx=5)
        
        ttk.Button(input_frame, text="Bắt đầu Quét", command=lambda: self.run_arp_scan(iface_name)).pack(side='left', padx=5)
        
        list_frame = ttk.Frame(self.scan_window, padding=10)
        list_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        bottom_frame = ttk.Frame(self.scan_window, padding=10)
        bottom_frame.pack(fill='x')
        
        self.select_all_var = tk.BooleanVar()
        ttk.Checkbutton(bottom_frame, text="Chọn tất cả", variable=self.select_all_var, command=self.toggle_all_devices).pack(side='left')
        
        ttk.Button(bottom_frame, text="Giám sát các thiết bị đã chọn", command=self.apply_target_ips).pack(side='right')

        self.device_checkboxes = [] 

    def run_arp_scan(self, iface_name):
        ip_range = self.ip_range_var.get()
        self.status_var.set(f"Đang quét ARP trên {ip_range}...")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.device_checkboxes = []
        
        def scan_task():
            devices = self.net_manager.scan_network(ip_range, iface_name)
            self.root.after(0, lambda: self.display_scan_results(devices))
            
        threading.Thread(target=scan_task, daemon=True).start()

    def display_scan_results(self, devices):
        self.status_var.set(f"Quét hoàn tất. Tìm thấy {len(devices)} thiết bị.")
        
        if not devices:
            ttk.Label(self.scrollable_frame, text="Không tìm thấy thiết bị nào (hoặc lỗi quyền Admin).").pack(pady=5)
            return

        for dev in devices:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.scrollable_frame, text=f"IP: {dev['ip']} - MAC: {dev['mac']}", variable=var)
            chk.pack(anchor='w', pady=2)
            self.device_checkboxes.append((dev['ip'], var))

    def toggle_all_devices(self):
        state = self.select_all_var.get()
        for _, var in self.device_checkboxes:
            var.set(state)

    def apply_target_ips(self):
        self.target_ips = set()
        for ip, var in self.device_checkboxes:
            if var.get():
                self.target_ips.add(ip)
        
        count = len(self.target_ips)
        if count == 0:
            msg = "Bạn chưa chọn thiết bị nào.\nChương trình sẽ giám sát TOÀN BỘ lưu lượng (Mặc định)."
        else:
            msg = f"Đã chọn {count} thiết bị mục tiêu.\nChương trình sẽ CHỈ hiển thị gói tin liên quan đến các IP này."
        
        messagebox.showinfo("Cấu hình Giám sát", msg)
        self.scan_window.destroy()
        self.status_var.set(f"Sẵn sàng. Mục tiêu: {count if count > 0 else 'Toàn bộ'}")

    def setup_global_copy_paste(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Sao chép", command=self.copy_selection_global)
        self.root.bind_class("Treeview", "<Button-3>", self.show_context_menu)
        self.root.bind_class("Text", "<Button-3>", self.show_context_menu)
        self.root.bind_class("Entry", "<Button-3>", self.show_context_menu)
        self.root.bind_class("Treeview", "<Control-c>", self.copy_from_treeview_event)

    def show_context_menu(self, event):
        self.active_widget = event.widget
        self.context_menu.post(event.x_root, event.y_root)

    def copy_selection_global(self):
        try:
            widget = self.active_widget
            if isinstance(widget, ttk.Treeview):
                self.copy_treeview_data(widget)
            elif isinstance(widget, tk.Text):
                try:
                    text = widget.get("sel.first", "sel.last")
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                except: pass
            elif isinstance(widget, ttk.Entry) or isinstance(widget, tk.Entry):
                try:
                    text = widget.selection_get()
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                except: pass
        except Exception as e:
            print(f"Copy error: {e}")

    def copy_from_treeview_event(self, event):
        self.copy_treeview_data(event.widget)

    def copy_treeview_data(self, tree):
        selected_items = tree.selection()
        if not selected_items: return
        copied_text = ""
        for item_id in selected_items:
            values = tree.item(item_id, 'values')
            line = "\t".join(str(v) for v in values)
            copied_text += line + "\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(copied_text)
        self.root.update()

    def on_tab_changed(self, event):
        selected_tab_index = self.notebook.index(self.notebook.select())
        if selected_tab_index == 1:
            if not (self.sniff_thread and self.sniff_thread.is_alive()) and self.all_packets_data and not self.chart_widgets:
                self.statistics_tab.update_statistics_tab()
            elif not self.all_packets_data:
                self.status_var.set("Chuyển sang Tab Thống kê. Hãy quét để có dữ liệu.")
                self.statistics_tab.clear_charts()
                
    def on_version_select(self, event):
        pass 

    def open_advanced_filter(self):
        self.monitor_tab_instance.open_advanced_filter()

    def apply_and_close_filter(self):
        self.update_report_list()
        if self.filter_window:
            self.filter_window.destroy()

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f: self.config = json.load(f)
            print(f"Đã tải cấu hình từ {CONFIG_FILE}")
        except Exception as e:
            print(f"Không tìm thấy {CONFIG_FILE} hoặc file bị lỗi, sử dụng mặc định: {e}")
            self.config = {"training_packets": 3000, "portscan_count": 40, "portscan_window": 10, "hostscan_count": 40, "hostscan_window": 10, "flood_count": 2000, "flood_window": 2}
            self.save_config(show_message=False)

    def save_config(self, show_message=True):
        try:
            for key, var in self.config_vars.items(): self.config[key] = var.get()
            with open(CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=4)
            if show_message: messagebox.showinfo("Đã lưu", "Cài đặt đã được lưu thành công!\nCác thay đổi sẽ có hiệu lực ở lần quét tới.")
            self.status_var.set("Cài đặt đã được lưu.")
        except Exception as e:
            if show_message: messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {e}")

    def toggle_theme(self):
        if self.current_theme == "light": self.current_theme = "dark"
        else: self.current_theme = "light"
        self.apply_theme()
        
        if self.all_packets_data and hasattr(self, 'statistics_tab'):
            self.statistics_tab.update_statistics_tab()

    def apply_theme(self):
        colors = self.colors_dark if self.current_theme == "dark" else self.colors_light
        if self.current_theme == "dark":
            matplotlib.style.use('dark_background')
            self.chart_facecolor = colors["frame_bg"]
            self.chart_textcolor = colors["fg"]
        else:
            matplotlib.style.use('default')
            self.chart_facecolor = colors["frame_bg"]
            self.chart_textcolor = colors["fg"]

        self.root.config(bg=colors["bg"])
        self.style.configure("App.TFrame", background=colors["bg"]); self.style.configure("White.TFrame", background=colors["frame_bg"]); self.style.configure("App.TLabel", background=colors["bg"], foreground=colors["fg"]); self.style.configure("White.TLabel", background=colors["frame_bg"], foreground=colors["fg"]); self.style.configure("Status.TLabel", background=colors["button"], foreground=colors["fg"])
        self.style.configure("App.TButton", background=colors["button"], foreground=colors["fg"], font=("Arial", 10), borderwidth=1)
        self.style.map("App.TButton", background=[('active', colors["frame_bg"]), ('disabled', colors["bg"])], foreground=[('disabled', colors["disabled_fg"])])
        self.style.map("TCombobox", fieldbackground=[('readonly', colors["text_bg"])], foreground=[('readonly', colors["fg"])], selectbackground=[('readonly', colors["text_bg"])], selectforeground=[('readonly', colors["fg"])], arrowcolor=[('!disabled', colors["fg"])], background=[('!disabled', colors["button"])])
        self.root.option_add("*TCombobox*Listbox*Background", colors["text_bg"]); self.root.option_add("*TCombobox*Listbox*Foreground", colors["fg"]); self.root.option_add("*TCombobox*Listbox*SelectBackground", colors["header"]); self.root.option_add("*TCombobox*Listbox*SelectForeground", "#FFFFFF")
        self.style.configure("Treeview", background=colors["text_bg"], foreground=colors["text_fg"], fieldbackground=colors["text_bg"], font=("Arial", 10))
        self.style.configure("Treeview.Heading", background=colors["button"], foreground=colors["fg"], font=("Arial", 10, "bold"))
        self.style.map("Treeview", background=[('selected', colors["header"])], foreground=[('selected', "#FFFFFF")])
        
        if hasattr(self, 'report_tree'):
            self.report_tree.tag_configure('danger', foreground=colors["danger"])
            self.report_tree.tag_configure('anomaly', foreground=colors["anomaly"])
            self.report_tree.tag_configure('normal', foreground=colors["normal_tree"])
            
        if hasattr(self, 'details_text'):
            self.details_text.config(background=colors["text_bg"], foreground=colors["text_fg"]); self.details_text.tag_config("header", foreground=colors["header"]); self.details_text.tag_config("normal", foreground=colors["text_fg"])
            self.details_text.tag_config("danger", foreground=colors["danger"])
            self.details_text.tag_config("anomaly", foreground=colors["anomaly"])
        
        self.style.configure("App.TNotebook", background=colors["bg"]); self.style.configure("App.TNotebook.Tab", background=colors["button"], foreground=colors["fg"], padding=[10, 5])
        self.style.map("App.TNotebook.Tab", background=[("selected", colors["frame_bg"])], foreground=[("selected", colors["header"])])
        self.style.configure("TEntry", fieldbackground=colors["text_bg"], foreground=colors["text_fg"], insertcolor=colors["fg"])
        self.style.configure("White.TCheckbutton", background=colors["frame_bg"], foreground=colors["fg"])
        self.style.map("White.TCheckbutton", indicatorcolor=[('selected', colors["header"]), ('!selected', colors["text_fg"])])
        self.style.map("TSpinbox", fieldbackground=[('!disabled', colors["text_bg"])], foreground=[('!disabled', colors["text_fg"])], arrowcolor=[('!disabled', colors["text_fg"])], background=[('!disabled', colors["button"])])
        
        if hasattr(self, 'version_details_text'): self.version_details_text.config(background=colors["text_bg"], foreground=colors["text_fg"])
        
        if hasattr(self, 'bottom_bar'): self.style.configure("App.TFrame", background=colors["bg"])
        if hasattr(self, 'theme_switch'): self.theme_switch.set_bg(colors["bg"])
        
        if hasattr(self, 'about_tab_instance'):
            self.about_tab_instance.update_theme_colors(colors["bg"], colors["fg"])

    def parse_packet_to_dict(self, packet):
        layers = {}
        if packet.haslayer(Ether): layers['Ether'] = {"dst": packet[Ether].dst, "src": packet[Ether].src, "type": packet[Ether].type}
        if packet.haslayer(ARP): layers['ARP'] = {"op": packet[ARP].op, "psrc": packet[ARP].psrc, "pdst": packet[ARP].pdst}
        if packet.haslayer(IP): layers['IP'] = {"version": packet[IP].version, "ihl": packet[IP].ihl, "ttl": packet[IP].ttl, "proto": packet[IP].proto, "src": packet[IP].src, "dst": packet[IP].dst}
        if packet.haslayer(TCP): layers['TCP'] = {"sport": packet[TCP].sport, "dport": packet[TCP].dport, "seq": packet[TCP].seq, "ack": packet[TCP].ack, "flags": str(packet[TCP].flags), "window": packet[TCP].window}
        if packet.haslayer(UDP): layers['UDP'] = {"sport": packet[UDP].sport, "dport": packet[UDP].dport, "len": packet[UDP].len}
        if packet.haslayer(ICMP): layers['ICMP'] = {"type": packet[ICMP].type, "code": packet[ICMP].code, "id": packet[ICMP].id}
        return layers

    def parse_tcp_flags(self, flag_str):
        flags_map = {'F': 'FIN (Kết thúc)', 'S': 'SYN (Yêu cầu)', 'R': 'RST (Reset)', 'P': 'PSH (Đẩy dữ liệu)', 'A': 'ACK (Xác nhận)', 'U': 'URG (Khẩn)', 'E': 'ECE', 'C': 'CWR'}
        parts = [flags_map.get(f, f) for f in flag_str]
        return ", ".join(parts)
        
    def log_details(self, message, tag="normal", clear=False):
        self.details_text.config(state='normal')
        if clear: self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, message + "\n", (tag,))
        self.details_text.config(state='disabled')
        
    def populate_interfaces(self):
        self.interfaces = self.net_manager.list_interfaces()
        if not self.interfaces:
            self.status_var.set("Lỗi: Không tìm thấy giao diện mạng nào.")
            self.start_button.config(state='disabled')
            return
        self.iface_combo['values'] = list(self.interfaces.keys())
        self.iface_combo.current(0)
        self.status_var.set(f"Đã tải {len(self.interfaces)} giao diện. Sẵn sàng.")

    def clear_model(self):
        try:
            if os.path.exists(MODEL_PATH): os.remove(MODEL_PATH)
            if os.path.exists(STATS_PATH): os.remove(STATS_PATH)
            self.status_var.set("Đã xóa mô hình. Sẽ huấn luyện lại ở lần quét tới.")
        except Exception as e: self.status_var.set(f"Lỗi khi xóa mô hình: {e}")

    def start_scan(self):
        try:
            selected_display_name = self.iface_var.get()
            if not selected_display_name: 
                self.status_var.set("Lỗi: Vui lòng chọn một giao diện.")
                return

            self.selected_iface_name = self.interfaces[selected_display_name]
            self.load_config() 
            
            self.ai_detector = AnomalyDetector(n_packets_to_train=self.config.get('training_packets', 1000))
            self.behavior_analyzer = BehavioralAnalyzer(portscan_count=self.config.get('portscan_count', 20), portscan_window=self.config.get('portscan_window', 10), hostscan_count=self.config.get('hostscan_count', 20), hostscan_window=self.config.get('hostscan_window', 10), flood_count=self.config.get('flood_count', 500), flood_window=self.config.get('flood_window', 2))
            
            self.stop_sniff_event.clear(); self.packet_count = 0; self.all_packets_data = [] 
            
            for i in self.report_tree.get_children(): self.report_tree.delete(i)
            
            try:
                self.statistics_tab.clear_charts()
            except Exception as e:
                print(f"Lỗi xóa biểu đồ (bỏ qua): {e}")

            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.iface_combo.config(state='disabled')
            self.retrain_button.config(state='disabled')
            self.theme_switch.unbind("<Button-1>") 
            
            self.filter_button.config(state='disabled')
            self.search_entry.config(state='disabled')
            self.filter_anomaly_check.config(state='disabled')
            self.filter_normal_check.config(state='disabled')
            self.monitor_tab_instance.disable_danger_check()
            
            self.notebook.tab(1, state="disabled") 
            self.notebook.tab(2, state="disabled") 
            
            self.export_pdf_button.config(state='disabled')
            self.log_details("", clear=True) 
            
            if self.ai_detector.load_model(MODEL_PATH, STATS_PATH):
                self.status_var.set("Đã tải mô hình AI. Bắt đầu phát hiện.")
            else:
                self.status_var.set(f"Đang huấn luyện... (Sử dụng {self.config.get('training_packets', 1000)} gói)")
            
            self.sniff_thread = threading.Thread(target=self.run_scanner_thread, daemon=True)
            self.sniff_thread.start()

        except Exception as e:
            error_msg = f"Lỗi khi khởi động quét:\n{str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Lỗi Nghiêm Trọng", error_msg)
            self.on_scan_stopped()

    def run_scanner_thread(self):
        try:
            self.net_manager.start_sniffing(self.selected_iface_name, self.packet_callback, self.stop_sniff_event)
        except PermissionError as e: self.message_queue.put(("ERROR", str(e)))
        except Exception as e: self.message_queue.put(("ERROR", f"Lỗi không xác định: {e}"))
        finally: self.message_queue.put(("STOPPED", None))

    def packet_callback(self, packet):
        # (MỚI) Lấy thời gian
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        features = self.ai_detector._extract_features(packet)
        prediction = self.ai_detector.process_packet(packet)
        behavior_analysis = self.behavior_analyzer.process_packet(packet)
        parsed_layers = self.parse_packet_to_dict(packet)
        tag = 'normal'; rule_analysis = "" 
        proto_name = "Other"
        if packet.haslayer(TCP): proto_name = "TCP"
        elif packet.haslayer(UDP): proto_name = "UDP"
        elif packet.haslayer(ICMP): proto_name = "ICMP"
        elif packet.haslayer(ARP): proto_name = "ARP"
        if prediction == -1: tag = 'anomaly' 
        if behavior_analysis: tag = 'anomaly'
        if packet.haslayer(TCP) and packet[TCP].flags.R: rule_analysis = "LỖI PHẦN MỀM: Gói tin TCP Reset (RST) - Kết nối bị từ chối."; tag = 'anomaly'
        elif packet.haslayer(ICMP):
            icmp_type = packet[ICMP].type
            if icmp_type == 3: rule_analysis = "LỖI MẠNG: ICMP Destination Unreachable." 
            elif icmp_type == 11: rule_analysis = "LỖI MẠNG: ICMP Time Exceeded." 
            elif icmp_type == 5: rule_analysis = "CẢNH BÁO MẠNG: ICMP Redirect." 

        # (CẬP NHẬT) Logic gán Tag
        if behavior_analysis or rule_analysis:
            tag = 'danger'
        elif prediction == -1:
            tag = 'anomaly'

        # (CẬP NHẬT) Logic Lọc IP Mục tiêu
        if self.target_ips:
            src = parsed_layers.get('IP', {}).get('src', '') or parsed_layers.get('ARP', {}).get('psrc', '')
            dst = parsed_layers.get('IP', {}).get('dst', '') or parsed_layers.get('ARP', {}).get('pdst', '')
            if src not in self.target_ips and dst not in self.target_ips:
                return # Bỏ qua nếu không phải mục tiêu

        packet_data = {
            'summary': packet.summary(), 
            'parsed_layers': parsed_layers, 
            'features': features, 
            'prediction': prediction, 
            'tag': tag, 
            'rule_analysis': rule_analysis, 
            'behavior_analysis': behavior_analysis, 
            'proto_name': proto_name,
            'time': timestamp # Lưu thời gian
        }
        self.message_queue.put(("PACKET", packet_data))

    def _check_protocol_filter(self, proto_name):
        if proto_name == 'TCP' and not self.filter_tcp_var.get(): return False
        if proto_name == 'UDP' and not self.filter_udp_var.get(): return False
        if proto_name == 'ICMP' and not self.filter_icmp_var.get(): return False
        if proto_name == 'ARP' and not self.filter_arp_var.get(): return False
        if proto_name == 'Other' and not self.filter_other_var.get(): return False
        return True 

    def process_queue(self):
        try:
            while not self.message_queue.empty():
                msg_type, data = self.message_queue.get()
                if msg_type == "STOPPED": self.on_scan_stopped(); continue
                if msg_type == "ERROR": self.status_var.set(f"Lỗi nghiêm trọng: {data}"); self.on_scan_stopped(); continue
                
                if msg_type == "PACKET":
                    self.packet_count += 1
                    packet_data = data
                    packet_data['id'] = self.packet_count 
                    self.all_packets_data.append(packet_data)
                    
                    if self.packet_count % 50 == 0: 
                        if self.ai_detector and not self.ai_detector.is_trained:
                            train_target = self.config.get('training_packets', 1000)
                            self.status_var.set(f"Đang huấn luyện... ({self.packet_count}/{train_target})")
                            if self.ai_detector.just_trained:
                                self.status_var.set("Hoàn tất huấn luyện! Bắt đầu phát hiện.")
                                self.ai_detector.just_trained = False
                        else:
                             self.status_var.set(f"Đang quét... Đã phát hiện {self.packet_count} gói tin.")
        finally:
            self.root.after(100, self.process_queue)

    def stop_scan(self):
        if self.sniff_thread and self.sniff_thread.is_alive():
            self.status_var.set("Đang yêu cầu dừng quét...")
            self.stop_sniff_event.set()
            self.stop_button.config(state='disabled') 
            
            self.filter_button.config(state='normal'); self.search_entry.config(state='normal'); self.filter_anomaly_check.config(state='normal'); self.filter_normal_check.config(state='normal')
            self.monitor_tab_instance.enable_danger_check()
            
            self.notebook.tab(1, state="normal")
            self.notebook.tab(2, state="normal")
            self.export_pdf_button.config(state='normal')
            self.theme_switch.bind("<Button-1>", self.theme_switch.toggle)

    def on_scan_stopped(self):
        self.status_var.set(f"Đã dừng. Đang xử lý {self.packet_count} gói tin...")
        
        if self.ai_detector and not os.path.exists(MODEL_PATH):
            if self.ai_detector.is_trained:
                self.ai_detector.save_model(MODEL_PATH, STATS_PATH)
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.iface_combo.config(state='readonly')
        self.retrain_button.config(state='normal')
        self.theme_switch.bind("<Button-1>", self.theme_switch.toggle)
        
        self.filter_button.config(state='normal')
        self.search_entry.config(state='normal')
        self.filter_anomaly_check.config(state='normal')
        self.filter_normal_check.config(state='normal')
        self.monitor_tab_instance.enable_danger_check()
        
        self.notebook.tab(1, state="normal") 
        self.notebook.tab(2, state="normal") 
        
        self.export_pdf_button.config(state='normal')
        
        if self.sniff_thread: self.sniff_thread.join(timeout=1.0)
        self.sniff_thread = None
        
        if self.all_packets_data:
            self.status_var.set("Đang tải dữ liệu vào danh sách...")
            self.update_report_list() 
            self.status_var.set("Đang tạo biểu đồ thống kê...")
            self.statistics_tab.update_statistics_tab() 
            self.status_var.set(f"Hoàn tất! Đã phân tích {self.packet_count} gói tin. Sẵn sàng.")
        else:
            self.status_var.set("Đã dừng. Không có dữ liệu để báo cáo.")

    def update_report_list_if_stopped(self):
        if not (self.sniff_thread and self.sniff_thread.is_alive()):
            self.update_report_list()

    def update_report_list(self):
        self.log_details("", clear=True) 
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        search_term = self.search_var.get().lower()
        
        show_danger = self.filter_danger_var.get()
        show_anomaly = self.filter_anomaly_var.get()
        show_normal = self.filter_normal_var.get()
        
        count = 0
        for pkt in self.all_packets_data:
            tag = pkt['tag']
            
            if tag == 'danger' and not show_danger: continue
            if tag == 'anomaly' and not show_anomaly: continue
            if tag == 'normal' and not show_normal: continue
            
            if search_term and search_term not in pkt['summary'].lower():
                continue
            if not self._check_protocol_filter(pkt.get('proto_name', 'Other')):
                continue
            
            status_text = "Bình thường"
            if tag == 'danger': status_text = "NGUY HIỂM"
            elif tag == 'anomaly': status_text = "Bất thường"
            
            self.report_tree.insert(
                '', 'end', 
                values=(pkt['id'], pkt['time'], pkt['summary'], status_text),
                tags=(pkt['tag'],)
            )
            count += 1
        self.status_var.set(f"Đã lọc. Hiển thị {count} / {len(self.all_packets_data)} gói tin.")

    def on_packet_select(self, event):
        selected_items = self.report_tree.selection()
        if not selected_items: return
        selected_item = selected_items[0]
        item_values = self.report_tree.item(selected_item, 'values')
        if not item_values: return 
        packet_id = int(item_values[0])
        packet_data = None
        for pkt in self.all_packets_data:
            if pkt['id'] == packet_id:
                packet_data = pkt
                break
        if packet_data:
            self.log_details("", clear=True)
            self.log_details(f"--- CHI TIẾT GÓI TIN (ID: {packet_id}) ---", "header")
            self.log_details(f"Thời gian: {packet_data['time']}\n", "normal")
            
            parsed_data = packet_data['parsed_layers']
            for layer_name, fields in parsed_data.items():
                layer_display = TRANSLATION_MAP.get(layer_name, layer_name)
                self.log_details(f"\n--- {layer_display} ---", "header")
                for key, value in fields.items():
                    key_display = TRANSLATION_MAP.get(key, key)
                    value_display = str(value)
                    if key == 'proto': value_display = TRANSLATION_MAP.get(value, str(value))
                    elif key == 'flags': value_display = self.parse_tcp_flags(value)
                    elif layer_name == 'ICMP' and key == 'code': value_display = TRANSLATION_MAP.get((fields['type'], value), str(value))
                    self.log_details(f"{key_display:<30}\t: {value_display}", "normal")
            
            tag = packet_data['tag']
            if packet_data['rule_analysis']:
                self.log_details("\n--- PHÂN TÍCH QUY TẮC (Rule-Based) ---", "analysis_header")
                self.log_details(packet_data['rule_analysis'], "danger") 
            if packet_data['behavior_analysis']:
                self.log_details("\n--- PHÂN TÍCH HÀNH VI (AI) ---", "analysis_header")
                self.log_details(packet_data['behavior_analysis'], "danger")
            if packet_data['prediction'] == -1:
                self.log_details("\n--- PHÂN TÍCH THỐNG KÊ (AI) ---", "analysis_header")
                explanation = self.ai_detector.explain_anomaly(packet_data['features'])
                self.log_details(f"LÝ DO SUY ĐOÁN: {explanation}", tag) 
            elif tag == 'normal':
                self.log_details("\n--- PHÂN TÍCH THỐNG KÊ (AI) ---", "analysis_header")
                self.log_details("AI không phát hiện bất thường về mặt thống kê.", "normal")

if __name__ == "__main__":
    is_admin = False
    try:
        if sys.platform == 'win32':
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        else:
            is_admin = (os.geteuid() == 0)
    except Exception as e: print(f"Không thể kiểm tra quyền admin: {e}")

    root = tk.Tk()
    if not is_admin:
        root.title("Lỗi Quyền Truy Cập"); root.geometry("500x100")
        error_label = ttk.Label(root, text="LỖI: Vui lòng chạy với quyền Quản trị viên (Admin) hoặc sudo.", foreground="red", padding="20")
        error_label.pack()
    else:
        app = NetworkScannerApp(root)
    root.mainloop()