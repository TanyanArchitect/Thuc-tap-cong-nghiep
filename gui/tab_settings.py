# file: gui/tab_settings.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class SettingsTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app 
        self.create_widgets()

    def create_widgets(self):
        settings_frame = ttk.Frame(self, style="App.TFrame")
        settings_frame.pack(fill='x')

        def create_setting_entry(parent, text, key):
            frame = ttk.Frame(parent, style="App.TFrame")
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=text, style="App.TLabel", width=40).pack(side=tk.LEFT, padx=5)
            self.app.config_vars[key] = tk.IntVar(value=self.app.config.get(key, 0))
            entry = ttk.Spinbox(frame, from_=0, to=999999, width=10, 
                                textvariable=self.app.config_vars[key],
                                background=self.app.colors_light['text_bg'])
            entry.pack(side=tk.LEFT, padx=5)
            return frame

        ttk.Label(settings_frame, text="AI Thống kê (Isolation Forest)", font=("Arial", 11, "bold"), style="App.TLabel").pack(fill='x', pady=5)
        create_setting_entry(settings_frame, "Số gói tin để huấn luyện:", "training_packets")
        
        ttk.Label(settings_frame, text="AI Hành vi (Phát hiện Tấn công)", font=("Arial", 11, "bold"), style="App.TLabel").pack(fill='x', pady=(15, 5))
        f1 = create_setting_entry(settings_frame, "Phát hiện Quét Cổng (Số cổng):", "portscan_count")
        create_setting_entry(f1, "Trong (giây):", "portscan_window")
        
        f2 = create_setting_entry(settings_frame, "Phát hiện Quét Mạng (Số máy chủ):", "hostscan_count")
        create_setting_entry(f2, "Trong (giây):", "hostscan_window")

        f3 = create_setting_entry(settings_frame, "Phát hiện Tấn công Lũ lụt (Số gói tin):", "flood_count")
        create_setting_entry(f3, "Trong (giây):", "flood_window")
        
        save_button = ttk.Button(self, text="Lưu Cài đặt", command=self.app.save_config, style="App.TButton")
        save_button.pack(pady=20, anchor='w', padx=5)