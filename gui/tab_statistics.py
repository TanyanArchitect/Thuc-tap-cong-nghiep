# file: gui/tab_statistics.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
from collections import Counter
import os

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from pdf_report import PDFReport 

class StatisticsTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app 

        self.create_widgets()

    def create_widgets(self):
        stats_control_frame = ttk.Frame(self, style="App.TFrame")
        stats_control_frame.pack(fill='x')
        
        self.app.export_pdf_button = ttk.Button(stats_control_frame, text="Xuất Báo cáo PDF...", command=self.export_to_pdf, style="App.TButton", state="disabled")
        self.app.export_pdf_button.pack(side=tk.LEFT, anchor='w', pady=5)
        
        ttk.Label(self, text="* Biểu đồ sẽ được tạo/cập nhật khi bạn dừng quét.", style="App.TLabel").pack(anchor='w', fill='x', pady=5)
        
        self.stats_main_frame = ttk.Frame(self, style="App.TFrame")
        self.stats_main_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        top_charts_pane = ttk.PanedWindow(self.stats_main_frame, orient=tk.HORIZONTAL)
        top_charts_pane.pack(fill=tk.BOTH, expand=True)
        
        self.app.stats_pie_frame = ttk.Frame(top_charts_pane, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        top_charts_pane.add(self.app.stats_pie_frame, weight=40) 
        
        right_bar_frame = ttk.Frame(top_charts_pane, style="App.TFrame")
        top_charts_pane.add(right_bar_frame, weight=60)
        
        right_pane_vertical = ttk.PanedWindow(right_bar_frame, orient=tk.VERTICAL)
        right_pane_vertical.pack(fill=tk.BOTH, expand=True)
        
        self.app.stats_bar_ip_frame = ttk.Frame(right_pane_vertical, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        right_pane_vertical.add(self.app.stats_bar_ip_frame, weight=50)
        self.app.stats_bar_ports_frame = ttk.Frame(right_pane_vertical, style="White.TFrame", relief=tk.RIDGE, borderwidth=2)
        right_pane_vertical.add(self.app.stats_bar_ports_frame, weight=50)

    def _process_statistics(self):
        ip_counter = Counter()
        port_counter = Counter()
        proto_counter = Counter()
        alert_counter = Counter()

        for pkt in self.app.all_packets_data:
            tag = pkt.get('tag', 'normal') # Dùng .get để tránh lỗi nếu thiếu key
            if tag == 'danger':
                alert_counter['Nguy hiểm (Tấn công)'] += 1
            elif tag == 'anomaly':
                alert_counter['Bất thường (Thống kê)'] += 1
            
            proto_counter[pkt.get('proto_name', 'Other')] += 1
            
            if 'IP' in pkt['parsed_layers']:
                ip_counter[pkt['parsed_layers']['IP']['src']] += 1
                ip_counter[pkt['parsed_layers']['IP']['dst']] += 1
            if 'TCP' in pkt['parsed_layers']:
                port_counter[f"{pkt['parsed_layers']['TCP']['dport']}/TCP"] += 1
            elif 'UDP' in pkt['parsed_layers']:
                port_counter[f"{pkt['parsed_layers']['UDP']['dport']}/UDP"] += 1
        
        return ip_counter, port_counter, proto_counter, alert_counter

    def export_to_pdf(self):
        self.app.status_var.set("Đang chuẩn bị xuất PDF...")
        if not self.app.all_packets_data:
            messagebox.showerror("Lỗi", "Không có dữ liệu để xuất. Hãy chạy một phiên quét trước.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Lưu Báo cáo PDF",
            initialfile=f"TANetAI_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not file_path:
            self.app.status_var.set("Đã hủy xuất PDF.")
            return

        self.app.status_var.set("Đang xử lý dữ liệu báo cáo...")
        
        try:
            ip_counter, port_counter, proto_counter, alert_counter = self._process_statistics()
            total_packets = len(self.app.all_packets_data)
            total_alerts = sum(alert_counter.values())
            
            # (SỬA LỖI QUAN TRỌNG) Gọi hàm của chính class này (self), không phải self.app
            if not self.app.charts:
                self.update_statistics_tab()

            chart_files = []
            # Lưu ảnh với DPI cao
            if self.app.charts.get('pie_chart'):
                self.app.charts['pie_chart'].savefig("pie_chart.png", bbox_inches='tight', dpi=150)
                chart_files.append("pie_chart.png")
            if self.app.charts.get('ip_chart'):
                self.app.charts['ip_chart'].savefig("ip_chart.png", bbox_inches='tight', dpi=150)
                chart_files.append("ip_chart.png")
            if self.app.charts.get('port_chart'):
                self.app.charts['port_chart'].savefig("port_chart.png", bbox_inches='tight', dpi=150)
                chart_files.append("port_chart.png")

            alert_data = []
            for pkt in self.app.all_packets_data:
                tag = pkt.get('tag', 'normal')
                if tag in ['danger', 'anomaly']:
                    reason = ""
                    if pkt.get('rule_analysis'): reason = pkt['rule_analysis']
                    elif pkt.get('behavior_analysis'): reason = pkt['behavior_analysis'].replace("\n", " ").replace("     ", " ")
                    elif pkt.get('prediction') == -1 and self.app.ai_detector: 
                        reason = self.app.ai_detector.explain_anomaly(pkt['features'])
                    
                    alert_data.append({
                        "id": pkt['id'],
                        "time": pkt.get('time', 'N/A'), # Dùng .get để tránh lỗi
                        "summary": pkt['summary'],
                        "reason": reason
                    })
            
            pdf = PDFReport()
            pdf.set_auto_page_break(True, margin=15)
            pdf.add_page()
            
            pdf.chapter_title("Tóm tắt Phiên quét")
            summary_content = (
                f"Tên chương trình: TANetAI (v{self.app.CURRENT_VERSION})\n"
                f"Tác giả: Tấn Lai Hoàng\n"
                f"Giao diện quét: {self.app.iface_var.get()}\n\n"
                f"Tổng số gói tin đã phân tích: {total_packets}\n"
                f"Tổng số cảnh báo đã phát hiện: {total_alerts}\n\n"
                f"Phân loại Cảnh báo:\n"
                f"  - MỨC ĐỘ NGUY HIỂM (Đỏ): {alert_counter.get('Nguy hiểm (Tấn công)', 0)}\n"
                f"  - Mức độ Bất thường (Vàng): {alert_counter.get('Bất thường (Thống kê)', 0)}"
            )
            pdf.chapter_body(summary_content)
            
            pdf.add_page()
            pdf.chapter_title("Thống kê Trực quan")
            pdf.add_charts(chart_files)
            
            if alert_data:
                pdf.add_page()
                pdf.chapter_title(f"Chi tiết {len(alert_data)} Cảnh báo")
                pdf.add_alerts_table(alert_data)
            
            pdf.output(file_path)
            
            for f in chart_files:
                if os.path.exists(f): os.remove(f)
            messagebox.showinfo("Hoàn tất", f"Đã xuất báo cáo thành công!\nĐã lưu tại: {file_path}")
            self.app.status_var.set("Xuất PDF hoàn tất.")
        except Exception as e:
            print(f"LỖI XUẤT PDF: {e}")
            messagebox.showerror("Lỗi", f"Không thể xuất PDF: {e}")
            self.app.status_var.set(f"Xuất PDF thất bại: {e}")
            for f in ["pie_chart.png", "ip_chart.png", "port_chart.png"]:
                if os.path.exists(f): os.remove(f)

    def clear_charts(self):
        for widget in self.app.chart_widgets:
            widget.destroy()
        self.app.chart_widgets = []
        self.app.charts = {} 
        
    def _create_bar_chart(self, parent_frame, data, title, xlabel, ylabel):
        try:
            labels = list(data.keys())
            values = list(data.values())
            
            fig = Figure(figsize=(5, 3), dpi=100, facecolor=self.app.chart_facecolor)
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.app.chart_facecolor)
            ax.tick_params(colors=self.app.chart_textcolor, labelsize=8)
            ax.xaxis.label.set_color(self.app.chart_textcolor)
            ax.yaxis.label.set_color(self.app.chart_textcolor)
            ax.title.set_color(self.app.chart_textcolor)

            ax.bar(labels, values, color=self.app.colors_dark['header'])
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.app.chart_widgets.append(widget)
            return fig
        except Exception as e:
            print(f"Lỗi vẽ biểu đồ cột: {e}")
            return None

    def _create_pie_chart(self, parent_frame, data, title):
        try:
            labels = list(data.keys())
            values = list(data.values())
            total = sum(values)

            legend_labels = [f"{l} ({v/total*100:.1f}%)" for l, v in zip(labels, values)]

            fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.app.chart_facecolor)
            ax = fig.add_subplot(111)
            
            # Tắt autopct
            wedges, texts = ax.pie(values, startangle=90)
            
            ax.axis('equal')
            ax.set_title(title, color=self.app.chart_textcolor)
            
            ax.legend(wedges, legend_labels,
                      title="Giao thức",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1),
                      facecolor=self.app.chart_facecolor,
                      labelcolor=self.app.chart_textcolor)
            
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.app.chart_widgets.append(widget)
            return fig
        except Exception as e:
            print(f"Lỗi vẽ biểu đồ tròn: {e}")
            return None

    def update_statistics_tab(self):
        self.app.status_var.set("Đang tạo báo cáo thống kê...")
        if not self.app.all_packets_data:
            self.app.status_var.set("Tạo báo cáo thất bại: Không có dữ liệu.")
            return

        self.clear_charts()
        
        # Bắt lỗi nếu _process_statistics gặp vấn đề
        try:
            ip_counter, port_counter, proto_counter, alert_counter = self._process_statistics()
            
            self.app.charts['pie_chart'] = self._create_pie_chart(self.app.stats_pie_frame, proto_counter, "Phân loại Giao thức")
            
            top_5_ips = dict(ip_counter.most_common(5))
            self.app.charts['ip_chart'] = self._create_bar_chart(self.app.stats_bar_ip_frame, top_5_ips, "Top 5 IP Hoạt động (Nguồn + Đích)", "Địa chỉ IP", "Số gói tin")
            
            top_5_ports = dict(port_counter.most_common(5))
            self.app.charts['port_chart'] = self._create_bar_chart(self.app.stats_bar_ports_frame, top_5_ports, "Top 5 Dịch vụ/Cổng (Đích)", "Cổng / Giao thức", "Số lần")

            self.app.status_var.set("Tạo báo cáo thống kê hoàn tất.")
        except Exception as e:
            print(f"Lỗi tạo thống kê: {e}")
            self.app.status_var.set(f"Lỗi tạo thống kê: {e}")