# file: pdf_report.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import datetime
from fpdf import FPDF, XPos, YPos
from fpdf.fonts import FontFace 
from app_utils import resource_path

class PDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.add_font("DejaVu", "", resource_path("fonts/DejaVuSans.ttf"))
            self.add_font("DejaVu", "B", resource_path("fonts/DejaVuSans-Bold.ttf"))
            self.add_font("DejaVu", "I", resource_path("fonts/DejaVuSans-Oblique.ttf"))
            self.add_font("DejaVu", "BI", resource_path("fonts/DejaVuSans-BoldOblique.ttf"))
            self.set_font("DejaVu", size=10)
        except Exception as e:
            print(f"LỖI FONT: Không thể tải font. {e}")
            self.set_font("Arial", size=10)

    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Báo cáo Phân tích Mạng - TANetAI", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 5, f"Tạo lúc: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Trang {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title):
        self.set_font("DejaVu", "B", 14)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True, align="L")
        self.ln(5)

    def chapter_body(self, content):
        self.set_font("DejaVu", "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, content)
        self.ln()

    def add_charts(self, chart_files):
        try:
            if "pie_chart.png" in chart_files:
                if self.get_y() > 150: self.add_page()
                self.set_font("DejaVu", "B", 11)
                self.cell(0, 10, "1. Phân loại Giao thức", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.image("pie_chart.png", x=20, w=170) 
                self.ln(5)

            if "ip_chart.png" in chart_files:
                if self.get_y() > 180: self.add_page()
                self.set_font("DejaVu", "B", 11)
                self.cell(0, 10, "2. Top 5 IP Hoạt động", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.image("ip_chart.png", x=20, w=170)
                self.ln(5)
            
            if "port_chart.png" in chart_files:
                if self.get_y() > 180: self.add_page()
                self.set_font("DejaVu", "B", 11)
                self.cell(0, 10, "3. Top 5 Dịch vụ/Cổng", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.image("port_chart.png", x=20, w=170)
                self.ln(10)
            
        except Exception as e:
            print(f"Lỗi khi chèn ảnh biểu đồ: {e}")
            self.chapter_body("[Không thể tải biểu đồ]")

    def add_alerts_table(self, alert_data):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(0, 0, 0)
        
        # (MỚI) Thêm cột "Thời gian"
        headings = ("ID", "Thời gian", "Tóm tắt Gói tin", "Lý do Phát hiện")
        data = []
        for item in alert_data:
            data.append((
                str(item['id']),
                str(item['time']), # Thêm dữ liệu thời gian
                item['summary'],
                item['reason']
            ))

        header_style = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=(50, 50, 50), family="DejaVu")

        with self.table(
            # (CẬP NHẬT) Điều chỉnh độ rộng cột: ID(15), Time(25), Summary(60), Reason(90) = Tổng 190
            col_widths=(15, 25, 60, 90),
            text_align=("CENTER", "CENTER", "LEFT", "LEFT"),
            headings_style=header_style
        ) as table:
            table.row(headings)
            for data_row in data:
                table.row(data_row)