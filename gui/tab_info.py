# file: gui/tab_info.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser # (MỚI) Để mở trình duyệt
from app_utils import VERSION_HISTORY

class AboutTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app 
        self.create_widgets()

    def open_link(self, url):
        """Hàm mở liên kết trong trình duyệt mặc định."""
        webbrowser.open_new(url)

    def create_widgets(self):
        about_frame = ttk.Frame(self, style="App.TFrame")
        about_frame.pack(fill='x', padx=10)
        
        # --- Về Chương trình ---
        ttk.Label(about_frame, text="Về Chương trình", font=("Arial", 14, "bold"), style="App.TLabel").pack(anchor='w', pady=5)
        
        about_text = f"Tên chương trình: TANetAI\n"
        about_text += f"Phiên bản: {self.app.CURRENT_VERSION}\n\n"
        about_text += "Đây là đồ án tốt nghiệp của tôi tại khoa CNTT chuyên ngành An ninh mạng,\n"
        about_text += "Trường Đại học Ngoại ngữ - Tin học Thành phố Hồ Chí Minh (HUFLIT)."
        
        ttk.Label(about_frame, text=about_text, style="App.TLabel", justify=tk.LEFT, font=("Arial", 11)).pack(anchor='w', pady=5, padx=10)
        
        # --- Về Tác giả (Được tách ra để làm link) ---
        ttk.Label(about_frame, text="Về Tác giả", font=("Arial", 14, "bold"), style="App.TLabel").pack(anchor='w', pady=(20, 5))
        
        # Dòng Tên
        ttk.Label(about_frame, text="Tác giả: Tấn Lai Hoàng", style="App.TLabel", font=("Arial", 11)).pack(anchor='w', padx=10)

        # Dòng Email (Có link)
        email_frame = ttk.Frame(about_frame, style="App.TFrame")
        email_frame.pack(anchor='w', padx=10)
        ttk.Label(email_frame, text="Email: ", style="App.TLabel", font=("Arial", 11)).pack(side=tk.LEFT)
        
        # Link Email
        lbl_email = tk.Label(email_frame, text="tanlaihoang.work@gmail.com", font=("Arial", 11, "underline"), fg="blue", cursor="hand2", bg="#F0F0F0")
        lbl_email.pack(side=tk.LEFT)
        # Khi click sẽ mở trình gửi mail mặc định
        lbl_email.bind("<Button-1>", lambda e: self.open_link("mailto:tanlaihoang.work@gmail.com"))

        # Dòng GitHub (Có link)
        github_frame = ttk.Frame(about_frame, style="App.TFrame")
        github_frame.pack(anchor='w', padx=10)
        ttk.Label(github_frame, text="GitHub: ", style="App.TLabel", font=("Arial", 11)).pack(side=tk.LEFT)
        
        # Link GitHub
        lbl_github = tk.Label(github_frame, text="https://github.com/TanyanArchitect", font=("Arial", 11, "underline"), fg="blue", cursor="hand2", bg="#F0F0F0")
        lbl_github.pack(side=tk.LEFT)
        # Khi click sẽ mở trình duyệt
        lbl_github.bind("<Button-1>", lambda e: self.open_link("https://github.com/TanyanArchitect"))

        # Lời cảm ơn
        thanks_text = "\nCảm ơn bạn đã sử dụng và vui lòng liên hệ tôi qua email nếu có vấn đề\n" \
                      "về chương trình hoặc gợi ý cải thiện."
        ttk.Label(about_frame, text=thanks_text, style="App.TLabel", justify=tk.LEFT, font=("Arial", 11)).pack(anchor='w', padx=10)
        
        # (MỚI) Lưu tham chiếu để cập nhật màu nền khi đổi theme
        self.link_labels = [lbl_email, lbl_github]

    def update_theme_colors(self, bg_color, fg_color):
        """Hàm này sẽ được gọi từ main.py khi đổi theme"""
        for lbl in self.link_labels:
            lbl.config(bg=bg_color, fg="#4da6ff" if bg_color != "#F0F0F0" else "blue") # Xanh sáng hơn nếu nền tối

class VersionsTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app 
        self.create_widgets()

    def create_widgets(self):
        version_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        version_pane.pack(fill=tk.BOTH, expand=True)

        version_list_frame = ttk.Frame(version_pane, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        version_pane.add(version_list_frame, weight=30)
        
        ttk.Label(version_list_frame, text="Lịch sử Phiên bản", font=("Arial", 12, "bold"), style="White.TLabel").pack(pady=5)
        cols = ('version',)
        self.app.version_tree = ttk.Treeview(version_list_frame, columns=cols, show='headings')
        self.app.version_tree.heading('version', text='Phiên bản')
        self.app.version_tree.column('version', width=150, anchor='w')
        
        ver_scroll = ttk.Scrollbar(version_list_frame, orient="vertical", command=self.app.version_tree.yview)
        self.app.version_tree.configure(yscrollcommand=ver_scroll.set)
        ver_scroll.pack(side='right', fill='y')
        self.app.version_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.app.version_tree.bind('<<TreeviewSelect>>', self.on_version_select)
        
        for ver in VERSION_HISTORY.keys(): 
            self.app.version_tree.insert('', 'end', values=(ver,))
            
        version_detail_frame = ttk.Frame(version_pane, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        version_pane.add(version_detail_frame, weight=70)

        ttk.Label(version_detail_frame, text="Chi tiết Cập nhật", font=("Arial", 12, "bold"), style="White.TLabel").pack(pady=5)
        self.app.version_details_text = scrolledtext.ScrolledText(version_detail_frame, wrap=tk.WORD, width=70, height=20, font=("Arial", 11), state='disabled')
        self.app.version_details_text.pack(fill='both', expand=True, padx=5, pady=5)

    def on_version_select(self, event):
        selected_items = self.app.version_tree.selection()
        if not selected_items: return
        selected_item = selected_items[0]
        item_values = self.app.version_tree.item(selected_item, 'values')
        if not item_values: return
        version_key = item_values[0]
        
        details = VERSION_HISTORY.get(version_key, "Không tìm thấy thông tin.")
        
        self.app.version_details_text.config(state='normal')
        self.app.version_details_text.delete('1.0', tk.END)
        self.app.version_details_text.insert('1.0', details)
        self.app.version_details_text.config(state='disabled')