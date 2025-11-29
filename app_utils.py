# file: app_utils.py
# -*- coding: utf-8 -*-

import sys
import os

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối, hoạt động cho cả .py và .exe (PyInstaller) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Đường dẫn tệp tin
MODEL_PATH = resource_path("network_model.joblib")
STATS_PATH = resource_path("network_stats.json")
CONFIG_FILE = resource_path("config.json") 
ICON_FILE = resource_path("my_icon.ico")
FONT_DIR = resource_path("fonts")

# --- TỪ ĐIỂN DỊCH THUẬT GÓI TIN ---
TRANSLATION_MAP = {
    "Ether": "Lớp 2 - Liên kết (Ethernet)", "IP": "Lớp 3 - Mạng (IP)",
    "TCP": "Lớp 4 - Giao vận (TCP)", "UDP": "Lớp 4 - Giao vận (UDP)",
    "ICMP": "Lớp 3 - Kiểm soát (ICMP)", "ARP": "Lớp 2/3 - Phân giải (ARP)",
    "src": "Địa chỉ Nguồn", "dst": "Địa chỉ Đích",
    "type": "Loại", "version": "Phiên bản", "ihl": "Độ dài Tiêu đề IP",
    "tos": "Loại Dịch vụ", "len": "Tổng Chiều dài", "id": "Định danh",
    "flags": "Cờ (Flags)", "frag": "Phân mảnh", "ttl": "Thời gian sống (TTL)",
    "proto": "Giao thức cấp trên", "chksum": "Tổng kiểm tra (Checksum)", "options": "Tùy chọn",
    "sport": "Cổng Nguồn (Source Port)", "dport": "Cổng Đích (Dest Port)",
    "seq": "Số Thứ tự (Sequence)", "ack": "Số Xác nhận (Ack)",
    "dataofs": "Độ dài Tiêu đề TCP", "reserved": "Dự trữ", "window": "Kích thước Cửa sổ",
    "urgptr": "Con trỏ khẩn", 1: "ICMP", 6: "TCP", 17: "UDP",
    (3, "code"): "Loại ICMP (3)", (3, 0): "Lỗi Mạng (Không thể đến)",
    (3, 1): "Lỗi Máy chủ (Không thể đến)", (3, 2): "Lỗi Giao thức (Không thể đến)",
    (3, 3): "Lỗi Cổng (Không thể đến)", (5, "code"): "Loại ICMP (5 - Chuyển hướng)",
    (5, 0): "Chuyển hướng cho Mạng", (11, "code"): "Loại ICMP (11 - Hết giờ)",
    (11, 0): "Hết thời gian (TTL=0)"
}

# --- LỊCH SỬ PHIÊN BẢN ---
VERSION_HISTORY = {
    "16.2": "Ổn định hóa & Fix lỗi (Hiện tại)\n- Sửa lỗi hiển thị biểu đồ không cập nhật khi xuất PDF.\n- Khắc phục lỗi ký tự lạ (Emoji) gây crash trên một số máy Windows.\n- Tinh chỉnh giao diện quét thiết bị.",
    "16.1": "Sửa lỗi Giao diện & Icon\n- Cập nhật icon cho cửa sổ quét thiết bị.\n- Sửa lỗi cú pháp trong bộ lọc tìm kiếm.",
    "16.0": "Network Discovery (Hiện tại)\n- Thêm tính năng 'Quét thiết bị LAN' (ARP Scan).\n- Cho phép người dùng chọn các IP mục tiêu cụ thể để giám sát, giúp giảm tải và tập trung vào các máy quan trọng.",
    "15.1": "Phân loại Mối đe dọa (Red/Yellow)\n- Tách biệt khái niệm 'Nguy hiểm' (Đỏ - Tấn công rõ ràng) và 'Bất thường' (Vàng - Nghi vấn thống kê).\n- Cập nhật logic lọc, hiển thị màu sắc trên giao diện và trong báo cáo PDF.",
    "15.0": "Gateway Edition (Mô hình Router)\n- Cấu hình lại NetworkManager để bật chế độ Promiscuous (nghe lén) triệt để.\n- Tăng các ngưỡng AI trong config.json lên gấp 3-4 lần để phù hợp với lưu lượng lớn của cả hệ thống mạng.",
    "14.13": "Timestamp & Copy\n- Thêm cột 'Thời gian' (giờ:phút:giây) cho danh sách gói tin.\n- Thêm tính năng Copy/Paste toàn cục (Ctrl+C, Chuột phải) cho mọi nơi trong ứng dụng.",
    "14.12": "Sửa lỗi Mất Thanh Trạng Thái\n- Thay đổi thứ tự sắp xếp giao diện (Packing Order) để thanh trạng thái luôn hiển thị đè lên mọi Tab, không bị biến mất khi vẽ biểu đồ.",
    "14.11": "Bố cục PDF Dọc & Đồng bộ\n- Chuyển biểu đồ PDF sang xếp dọc (Vertical Stack) để hiển thị to và rõ hơn trên khổ giấy A4.\n- Đồng bộ hóa biến VERSION_HISTORY vào app_utils để tránh lỗi import.",
    "14.10": "Chế độ An toàn\n- Thêm cơ chế bắt lỗi (Error Trapping) cho nút Bắt đầu. Nếu có lỗi, chương trình sẽ hiện Popup thông báo thay vì bị đơ.\n- Sử dụng chỉ số Tab (Index) để điều khiển ổn định hơn.",
    "14.9.2": "Sửa lỗi Quét (Triệt để)\n- Sắp xếp lại thứ tự khởi tạo luồng quét để đảm bảo nó luôn chạy.\n- Thêm try-except cho việc xóa biểu đồ để tránh lỗi dừng chương trình âm thầm.",
    "14.9": "Sửa lỗi Layout\n- Khắc phục lỗi khoảng trắng lớn giữa Tab và thanh trạng thái do cấu hình pack sai.",
    "14.8": "Sắc nét (High DPI)\n- Bật chế độ High DPI Awareness. Giao diện trở nên sắc nét, không còn bị mờ hay răng cưa trên màn hình độ phân giải cao.",
    "14.7": "Giao diện Hiện đại\n- Chuyển nút 'Đổi Giao diện' xuống thanh trạng thái.\n- Thay nút bấm thường bằng nút công tắc trượt (Toggle Switch) hình Mặt trời/Mặt trăng tự vẽ.",
    "14.6": "Đồng bộ Theme\n- Biểu đồ tự động cập nhật màu sắc (Trắng/Đen) ngay khi người dùng đổi theme.",
    "14.5": "Dọn dẹp Code\n- Xóa bỏ hoàn toàn code cũ trong main.py để ép chương trình sử dụng logic mới từ thư mục gui/.\n- Khắc phục triệt để lỗi biểu đồ cũ vẫn hiển thị.",
    "14.4": "Sửa lỗi Biểu đồ (Chồng chéo)\n- Cập nhật logic biểu đồ tròn: ẩn hoàn toàn số liệu trên biểu đồ, đưa toàn bộ chi tiết (%) vào bảng chú thích (Legend).",
    "14.3": "Sửa lỗi PDF (AttributeError)\n- Sửa lỗi 'PDFReport object has no attribute style' bằng cách import đúng lớp FontFace.",
    "14.2": "Khôi phục Lịch sử Phiên bản\n- Khôi phục lại chi tiết toàn bộ lịch sử phiên bản trong Tab 'Phiên bản'.",
    "14.1": "Sửa lỗi Tái cấu trúc\n- Sửa lỗi 'AttributeError' cho CURRENT_VERSION khi truy cập từ các tab con.",
    "14.0": "Tái cấu trúc (Tách file)\n- Tách main_gui.py khổng lồ thành nhiều file nhỏ gọn (main.py, pdf_report.py, app_utils.py).\n- Chia code giao diện vào thư mục gui/ (tab_monitor.py, tab_statistics.py...).",
    "13.4": "Sửa lỗi PDF Tiếng Việt\n- Sửa lỗi font PDF bằng cách thêm 4 file font DejaVu vào thư mục dự án và đóng gói kèm. PDF giờ đây hỗ trợ Tiếng Việt đầy đủ.",
    "13.3": "Sửa lỗi Hiệu năng & PDF\n- Tắt chế độ hiển thị 'real-time' khi đang quét để chống đơ (crash) khi gặp lưu lượng lớn.\n- Danh sách gói tin chỉ hiển thị sau khi nhấn 'Dừng quét'.\n- Sửa lỗi font PDF (dejavuB).",
    "13.2": "Sửa lỗi Biểu đồ (Logic)\n- Biểu đồ tự động tạo khi dừng quét (không cần click).\n- Biểu đồ tròn dùng Chú giải (Legend) thay vì nhãn chồng chéo. Tinh chỉnh bố cục và kích thước biểu đồ.",
    "13.1": "Sửa lỗi Quan trọng (Quét & Icon)\n- Khôi phục dòng code khởi tạo luồng quét bị thiếu.\n- Sửa lỗi Icon 'Lông chim' mặc định bằng cách thêm root.iconbitmap và cập nhật lệnh PyInstaller.",
    "13.0": "Báo cáo Chuyên nghiệp (PDF)\n- Thêm nút 'Xuất Báo cáo PDF'.\n- Tích hợp thư viện fpdf2. Tạo báo cáo PDF chuyên nghiệp bao gồm Trang bìa, Biểu đồ nhúng, và Bảng chi tiết Cảnh báo.",
    "12.0": "Nâng cấp Trực quan (Biểu đồ)\n- Nâng cấp Tab Thống kê từ văn bản sang Biểu đồ trực quan.\n- Tích hợp thư viện matplotlib và Pillow vào giao diện Tkinter.",
    "11.3": "Sửa lỗi Trình cài đặt (Setup.exe)\n- Cập nhật script Setup.iss (Inno Setup), bỏ cờ /S (Silent) để tương thích với trình cài đặt Npcap miễn phí (yêu cầu tương tác người dùng).",
    "11.2": "Sẵn sàng Xuất xưởng (Fix Path)\n- Sửa lỗi đường dẫn (path) nghiêm trọng bằng hàm resource_path. Đảm bảo file .exe khi chạy có thể tìm thấy config.json và các tài nguyên đi kèm.",
    "11.1": "Cập nhật Nội dung (Tab Thông tin)\n- Cập nhật nội dung Tab 'Thông tin' với thông tin tác giả, tên chương trình 'TANetAI', email liên hệ và GitHub.\n- Phiên bản: Hiển thị phiên bản động.",
    "11.0": "Hoàn thiện (Thông tin)\n- Thêm Tab 'Thông tin' và Tab 'Phiên bản'.\n- Xây dựng giao diện xem lịch sử phiên bản dạng cây (Treeview) và chi tiết.",
    "10.1": "Sửa lỗi (Logic ID)\n- Sửa lỗi lặp lại ID gói tin (Race Condition) khi quét real-time bằng cách chuyển logic gán ID vào luồng giao diện.",
    "10.0": "Lọc Nâng cao\n- Nâng cấp Lọc: Nút 'Lọc / Tải lại' được đổi tên thành 'Lọc Nâng cao...'.\n- Chức năng: Khi nhấn, một cửa sổ mới (popup) sẽ xuất hiện, cho phép lọc chuyên sâu theo Giao thức (TCP, UDP, ICMP, ARP...).",
    "9.2": "Sửa lỗi (Nghiêm trọng)\n- Khắc phục lỗi crash khi khởi động do lỗi tham chiếu biến Tab (settings_tab).",
    "9.1": "Sửa lỗi (Nghiêm trọng)\n- Khắc phục lỗi nút 'Bắt đầu quét' không hoạt động (do mất code khởi tạo luồng).",
    "9.0": "Báo cáo (Tab Thống kê - Text)\n- Hoàn thiện Tab 'Thống kê' cơ bản.\n- UI/UX: Thêm nút 'Tạo Báo cáo Thống kê' để tổng hợp toàn bộ phiên quét dưới dạng văn bản, hiển thị: Top 5 IP, Top 5 Cổng, Phân loại Cảnh báo.",
    "8.0": "AI Tùy chỉnh (Tab Cài đặt)\n- Hoàn thiện Tab 'Cài đặt'.\n- Lưu trữ: Thêm file config.json để lưu trữ các ngưỡng (thresholds) tùy chỉnh của AI.\n- Nâng cấp AI: Các bộ não AI (Thống kê & Hành vi) giờ đây đọc các giá trị từ file config thay vì viết cứng.",
    "7.0": "Tái cấu trúc (Tab & Lọc)\n- Giao diện Tab: Tái cấu trúc toàn bộ giao diện, chia thành 3 tab chính: 'Giám sát', 'Thống kê', và 'Cài đặt'.\n- Khung Lọc: Thêm một 'Khung Lọc' mới vào tab Giám sát, bao gồm: Khay tìm kiếm và Checkbox 'Hiện Bất thường' / 'Hiện Bình thường'.\n- Logic Lọc Kép: Bộ lọc hoạt động thông minh cả khi đang quét (lọc real-time) và sau khi đã dừng quét (lọc lại toàn bộ dữ liệu đã lưu).",
    "6.0": "Chuyên nghiệp (Real-time & Phân tích DoS)\n- Giám sát Real-time: Thay đổi logic cốt lõi. Gói tin giờ đây được hiển thị ngay lập tức lên danh sách (giống Wireshark) thay vì phải chờ quét xong.\n- Tự động cuộn: Danh sách tự động cuộn xuống gói tin mới nhất.\n- Nâng cấp AI (Tầng 3): Cập nhật behavioral_analyzer.py để thêm khả năng phát hiện Tấn công Lũ lụt (DoS/Flood) dựa trên khối lượng gói tin.",
    "5.1": "Hoàn thiện (Sửa lỗi Theme)\n- Sửa lỗi UI: Khắc phục lỗi giao diện Tối/Sáng (nút bị trắng chữ trắng).\n- Tinh chỉnh: Bắt buộc dùng theme 'clam' của ttk để đảm bảo các Nút và Dropdown hiển thị màu sắc chính xác.",
    "5.0": "Nâng tầm AI (Phát hiện Quét)\n- AI Hành vi (Tầng 3): Thêm file behavioral_analyzer.py.\n- Phát hiện Tấn công: Nâng cấp AI để có 'bộ nhớ', có thể phát hiện các hành vi tấn công theo thời gian, bao gồm: Phát hiện Quét Cổng (Port Scan), Phát hiện Quét Mạng (Host Scan).\n- UI/UX: Cập nhật khung chi tiết để hiển thị kết quả của cả 3 tầng phân tích.",
    "4.0": "Thân thiện (Dịch thuật & Giao diện Tối)\n- Dịch thuật (Tiếng Việt): Dịch toàn bộ thông tin chi tiết gói tin kỹ thuật sang Tiếng Việt.\n- Định dạng: Chuyển khung chi tiết sang dạng bảng 2 cột.\n- UI/UX: Thêm nút 'Đổi Giao diện' (Dark/Light Mode).",
    "3.1": "Tinh chỉnh (Phân tích Lỗi)\n- Nới lỏng AI: Đổi tham số contamination thành 'auto' để AI 'dễ tính' hơn.\n- Phân tích Quy tắc (Rule-based): Thêm tầng phân tích đầu tiên (Tầng 1) để phát hiện các lỗi mạng kỹ thuật rõ ràng như TCP Reset (RST) và ICMP Unreachable.",
    "3.0": "Thông minh hơn (AI bền vững & Báo cáo)\n- Nâng cấp AI: Tăng số gói tin huấn luyện lên 1000.\n- Lưu trữ AI (Persistence): Mô hình AI và các chỉ số thống kê được lưu vào file (model.joblib).\n- Thay đổi UI: Chuyển sang giao diện Báo cáo 2 cột. Chỉ hiển thị kết quả sau khi nhấn 'Dừng quét'.\n- Phân tích AI: Lần đầu tiên thêm logic 'Suy đoán'.",
    "2.0": "Lên đời (Giao diện GUI)\n- Chức năng: Chuyển từ Terminal sang giao diện cửa sổ (GUI) bằng thư viện Tkinter.\n- UI/UX: Thêm Nút Bắt đầu/Dừng, Dropdown chọn giao diện và một khu vực Log văn bản.\n- Nâng cấp: Sử dụng threading (luồng) để chạy tác vụ quét mạng trong nền.",
    "1.0": "Khởi đầu (Nền tảng Terminal)\n- Chức năng: Chương trình chạy hoàn toàn trên Terminal (dòng lệnh).\n- AI: Sử dụng thuật toán IsolationForest để học 100 gói tin đầu tiên và sau đó in kết quả ra màn hình.\n- Kiến trúc: Bắt đầu với việc chia code thành 4 lớp cơ bản."
}