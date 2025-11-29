# file: behavioral_analyzer.py
# -*- coding: utf-8 -*-

import time
from scapy.all import IP, TCP, UDP 

class BehavioralAnalyzer:
    def __init__(self, 
                 portscan_count=20, portscan_window=10,
                 hostscan_count=20, hostscan_window=10,
                 flood_count=500, flood_window=2):
        
        self.portscan_count = portscan_count
        self.portscan_window = portscan_window
        self.hostscan_count = hostscan_count
        self.hostscan_window = hostscan_window
        self.flood_count = flood_count
        self.flood_window = flood_window

        # Bộ theo dõi (Chỉ lưu timestamp, không lưu trạng thái "đã phát hiện" vĩnh viễn)
        self.scan_tracker = {}
        self.flood_tracker = {}
        print("[Hành vi] Khởi tạo với chế độ Báo động Định kỳ (Periodic Alert).")

    def reset(self):
        """Xóa bộ nhớ khi bắt đầu phiên quét mới."""
        self.scan_tracker = {}
        self.flood_tracker = {}
        print("[Hành vi] Đã xóa bộ nhớ theo dõi.")

    def _check_floods(self, packet, current_time):
        if not packet.haslayer(IP):
            return None
            
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        dst_port = 0
        
        if packet.haslayer(TCP):
            dst_port = packet[TCP].dport
        elif packet.haslayer(UDP):
            dst_port = packet[UDP].dport
            
        target_key = (dst_ip, proto, dst_port)

        # (THAY ĐỔI) Không kiểm tra 'if target_key in self.detected_floods' nữa
        # Để cho phép báo động lại
            
        if target_key not in self.flood_tracker:
            self.flood_tracker[target_key] = []
            
        timestamps = self.flood_tracker[target_key]
        timestamps.append(current_time)
        
        # Xóa các gói tin cũ quá cửa sổ thời gian
        window_start_time = current_time - self.flood_window
        while timestamps and timestamps[0] < window_start_time:
            timestamps.pop(0)
            
        # Nếu vượt ngưỡng -> Báo động & Reset bộ đếm ngay lập tức
        if len(timestamps) > self.flood_count:
            # Reset bộ đếm để bắt đầu chu kỳ mới (tránh spam từng gói một)
            self.flood_tracker[target_key] = [] 
            
            return (
                f"PHÁT HIỆN TẤN CÔNG LŨ LỤT (DoS/Flood Attack):\n"
                f"     Đích: {dst_ip}\n"
                f"     Dịch vụ: Giao thức {proto}, Cổng {dst_port}\n"
                f"     Đã nhận: >{self.flood_count} gói tin trong {self.flood_window} giây."
            )
            
        return None

    def _check_scans(self, packet, current_time):
        if not packet.haslayer(IP):
            return None
            
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        dst_port = 0
        
        if packet.haslayer(TCP): dst_port = packet[TCP].dport
        elif packet.haslayer(UDP): dst_port = packet[UDP].dport
        
        # (THAY ĐỔI) Tương tự, bỏ qua kiểm tra 'detected_scans'

        if src_ip not in self.scan_tracker:
            self.scan_tracker[src_ip] = {
                'first_seen': current_time,
                'ports_targeted': {}, 
                'hosts_targeted': {} 
            }
        
        tracker = self.scan_tracker[src_ip]
        
        # Reset nếu quá cửa sổ thời gian
        if current_time - tracker['first_seen'] > self.portscan_window:
            tracker['first_seen'] = current_time
            tracker['ports_targeted'] = {}
            tracker['hosts_targeted'] = {}

        if dst_port > 0:
            if dst_ip not in tracker['ports_targeted']:
                tracker['ports_targeted'][dst_ip] = set()
            tracker['ports_targeted'][dst_ip].add(dst_port)
            
            if dst_port not in tracker['hosts_targeted']:
                tracker['hosts_targeted'][dst_port] = set()
            tracker['hosts_targeted'][dst_port].add(dst_ip)

        # Phân tích Quét Cổng
        for target_ip, ports in tracker['ports_targeted'].items():
            if len(ports) >= self.portscan_count:
                # Reset để báo lại đợt sau
                tracker['ports_targeted'][target_ip] = set()
                
                return (
                    f"PHÁT HIỆN QUÉT CỔNG (Port Scan):\n"
                    f"     Nguồn: {src_ip}\n"
                    f"     Đích: {target_ip}\n"
                    f"     Đã quét: >{self.portscan_count} cổng trong {self.portscan_window} giây."
                )
        
        # Phân tích Quét Mạng
        for target_port, hosts in tracker['hosts_targeted'].items():
            if len(hosts) >= self.hostscan_count:
                # Reset
                tracker['hosts_targeted'][target_port] = set()
                
                return (
                    f"PHÁT HIỆN QUÉT MẠNG (Host Scan):\n"
                    f"     Nguồn: {src_ip}\n"
                    f"     Trên Cổng: {target_port}\n"
                    f"     Đã quét: >{self.hostscan_count} máy chủ trong {self.hostscan_window} giây."
                )

        return None

    def process_packet(self, packet):
        current_time = time.time()
        
        flood_analysis = self._check_floods(packet, current_time)
        if flood_analysis:
            return flood_analysis
        
        scan_analysis = self._check_scans(packet, current_time)
        if scan_analysis:
            return scan_analysis

        return None