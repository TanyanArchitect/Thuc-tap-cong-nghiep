# file: gui/tab_monitor.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel

class MonitorTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app 
        self.create_widgets()
        self.create_context_menu()

    def create_widgets(self):
        # A1. Khung điều khiển
        control_frame = ttk.Frame(self, style="App.TFrame")
        control_frame.pack(fill='x', pady=(0, 5))

        ttk.Label(control_frame, text="Chọn giao diện mạng:", style="App.TLabel").pack(side='left', padx=5)
        self.app.iface_var = tk.StringVar()
        self.app.iface_combo = ttk.Combobox(control_frame, textvariable=self.app.iface_var, width=30, state='readonly')
        self.app.iface_combo.pack(side='left', fill='x', expand=True, padx=5)
        
        # (MỚI) Nút Quét thiết bị LAN
        self.app.scan_lan_button = ttk.Button(control_frame, text="🔍 Quét thiết bị", command=self.app.show_device_scanner, style="App.TButton")
        self.app.scan_lan_button.pack(side='left', padx=5)

        self.app.start_button = ttk.Button(control_frame, text="Bắt đầu quét", command=self.app.start_scan, style="App.TButton")
        self.app.start_button.pack(side='left', padx=5)
        self.app.stop_button = ttk.Button(control_frame, text="Dừng quét", command=self.app.stop_scan, state='disabled', style="App.TButton")
        self.app.stop_button.pack(side='left', padx=5)
        self.app.retrain_button = ttk.Button(control_frame, text="Huấn luyện lại", command=self.app.clear_model, style="App.TButton")
        self.app.retrain_button.pack(side='left', padx=5)

        # A2. Khung Lọc
        filter_frame = ttk.Frame(self, style="White.TFrame", relief=tk.RIDGE, borderwidth=1)
        filter_frame.pack(fill='x', pady=5, padx=2)
        
        ttk.Label(filter_frame, text="Tìm kiếm:", style="White.TLabel").pack(side='left', padx=5)
        self.app.search_var = tk.StringVar()
        self.app.search_entry = ttk.Entry(filter_frame, textvariable=self.app.search_var, width=40)
        self.app.search_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        self.app.filter_danger_var = tk.BooleanVar(value=True)
        self.app.filter_danger_check = ttk.Checkbutton(filter_frame, text="Hiện Nguy hiểm", variable=self.app.filter_danger_var, style="White.TCheckbutton")
        self.app.filter_danger_check.pack(side='left', padx=5, pady=5)

        self.app.filter_anomaly_var = tk.BooleanVar(value=True)
        self.app.filter_anomaly_check = ttk.Checkbutton(filter_frame, text="Hiện Bất thường", variable=self.app.filter_anomaly_var, style="White.TCheckbutton")
        self.app.filter_anomaly_check.pack(side='left', padx=5, pady=5)
        
        self.app.filter_normal_var = tk.BooleanVar(value=True)
        self.app.filter_normal_check = ttk.Checkbutton(filter_frame, text="Hiện Bình thường", variable=self.app.filter_normal_var, style="White.TCheckbutton")
        self.app.filter_normal_check.pack(side='left', padx=5, pady=5)
        
        self.app.filter_button = ttk.Button(filter_frame, text="Lọc Nâng cao...", command=self.app.open_advanced_filter, style="App.TButton", state='disabled')
        self.app.filter_button.pack(side='right', padx=10, pady=5)

        self.app.search_entry.bind("<Return>", lambda e: self.app.update_report_list())
        self.app.filter_danger_check.config(command=self.app.update_report_list_if_stopped)
        self.app.filter_anomaly_check.config(command=self.app.update_report_list_if_stopped)
        self.app.filter_normal_check.config(command=self.app.update_report_list_if_stopped)

        # A3. Khung chính chia đôi
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Danh sách gói tin
        report_frame = ttk.Frame(main_pane, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        main_pane.add(report_frame, weight=50)
        ttk.Label(report_frame, text="Danh sách Gói tin", font=("Arial", 12, "bold"), style="White.TLabel").pack(pady=5)
        
        cols = ('id', 'time', 'summary', 'status')
        self.app.report_tree = ttk.Treeview(report_frame, columns=cols, show='headings')
        self.app.report_tree.heading('id', text='ID')
        self.app.report_tree.heading('time', text='Thời gian')
        self.app.report_tree.heading('summary', text='Tóm tắt')
        self.app.report_tree.heading('status', text='Trạng thái')
        
        self.app.report_tree.column('id', width=50, anchor='center')
        self.app.report_tree.column('time', width=100, anchor='center')
        self.app.report_tree.column('summary', width=450)
        self.app.report_tree.column('status', width=100, anchor='center')
        
        tree_scroll = ttk.Scrollbar(report_frame, orient="vertical", command=self.app.report_tree.yview)
        self.app.report_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side='right', fill='y')
        self.app.report_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.app.report_tree.bind('<<TreeviewSelect>>', self.app.on_packet_select)
        self.app.report_tree.bind("<Control-c>", self.copy_from_tree)

        # Chi tiết gói tin
        details_frame = ttk.Frame(main_pane, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        main_pane.add(details_frame, weight=50)
        ttk.Label(details_frame, text="Chi tiết Gói tin (Đã dịch)", font=("Arial", 12, "bold"), style="White.TLabel").pack(pady=5)
        
        self.app.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=70, height=20, font=("Courier New", 11), state='disabled')
        self.app.details_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.app.details_text.tag_config("header", font=("Arial", 11, "bold", "underline"))
        self.app.details_text.tag_config("analysis_header", font=("Arial", 11, "bold"), background="yellow", foreground="black")
        self.app.details_text.tag_config("normal")
        self.app.details_text.tag_config("anomaly", font=("Courier New", 11, "bold"))
        self.app.details_text.tag_config("danger", font=("Courier New", 11, "bold"))

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Sao chép (Copy)", command=self.copy_selection_context)
        self.app.report_tree.bind("<Button-3>", self.show_context_menu_tree)
        self.app.details_text.bind("<Button-3>", self.show_context_menu_text)

    def show_context_menu_tree(self, event):
        self.active_widget = "tree"
        item = self.app.report_tree.identify_row(event.y)
        if item:
            self.app.report_tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)

    def show_context_menu_text(self, event):
        self.active_widget = "text"
        self.context_menu.post(event.x_root, event.y_root)

    def copy_selection_context(self):
        if self.active_widget == "tree":
            self.copy_from_tree()
        elif self.active_widget == "text":
            try:
                text = self.app.details_text.get("sel.first", "sel.last")
                self.clipboard_clear()
                self.clipboard_append(text)
            except tk.TclError:
                pass

    def copy_from_tree(self, event=None):
        selected_items = self.app.report_tree.selection()
        if not selected_items:
            return
        copied_text = ""
        for item_id in selected_items:
            values = self.app.report_tree.item(item_id, 'values')
            line = "\t".join(str(v) for v in values)
            copied_text += line + "\n"
        self.clipboard_clear()
        self.clipboard_append(copied_text)
        self.update()

    # Các hàm trợ giúp bật/tắt nút
    def disable_danger_check(self):
        self.app.filter_danger_check.config(state='disabled')
        self.app.filter_anomaly_check.config(state='disabled')
        self.app.filter_normal_check.config(state='disabled')

    def enable_danger_check(self):
        self.app.filter_danger_check.config(state='normal')
        self.app.filter_anomaly_check.config(state='normal')
        self.app.filter_normal_check.config(state='normal')

    def open_advanced_filter(self):
        self.app.filter_window = Toplevel(self.app.root)
        self.app.filter_window.title("Lọc Nâng cao theo Giao thức")
        self.app.filter_window.transient(self.app.root)
        self.app.filter_window.grab_set() 
        
        colors = self.app.colors_dark if self.app.current_theme == "dark" else self.app.colors_light
        self.app.filter_window.config(bg=colors["bg"])
        
        frame = ttk.Frame(self.app.filter_window, style="App.TFrame", padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Vui lòng chọn các giao thức bạn muốn hiển thị:", style="App.TLabel").pack(pady=(0, 10))

        ttk.Checkbutton(frame, text="Giao thức TCP (Web, Email...)", variable=self.app.filter_tcp_var, style="App.TCheckbutton").pack(anchor='w', padx=10)
        ttk.Checkbutton(frame, text="Giao thức UDP (DNS, Game, Gọi...)", variable=self.app.filter_udp_var, style="App.TCheckbutton").pack(anchor='w', padx=10)
        ttk.Checkbutton(frame, text="Giao thức ICMP (Ping, Lỗi mạng)", variable=self.app.filter_icmp_var, style="App.TCheckbutton").pack(anchor='w', padx=10)
        ttk.Checkbutton(frame, text="Giao thức ARP (Tìm địa chỉ LAN)", variable=self.app.filter_arp_var, style="App.TCheckbutton").pack(anchor='w', padx=10)
        ttk.Checkbutton(frame, text="Các giao thức khác (IPv6, IGMP...)", variable=self.app.filter_other_var, style="App.TCheckbutton").pack(anchor='w', padx=10)

        button_frame = ttk.Frame(frame, style="App.TFrame")
        button_frame.pack(fill='x', pady=(20, 0))
        
        self.app.style.configure("App.TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        self.app.style.map("App.TCheckbutton", indicatorcolor=[('selected', colors["header"]), ('!selected', colors["text_fg"])])
        
        ttk.Button(button_frame, text="Thoát", command=self.app.filter_window.destroy, style="App.TButton").pack(side='right', padx=5)
        ttk.Button(button_frame, text="Áp dụng", command=self.app.apply_and_close_filter, style="App.TButton").pack(side='right', padx=5)