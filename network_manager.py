# file: network_manager.py
# -*- coding: utf-8 -*-

import psutil
# (CẬP NHẬT) Import thêm srp (send/receive packet), Ether, ARP để quét mạng
from scapy.all import sniff, conf, srp, Ether, ARP
import sys

class NetworkManager:
    def __init__(self):
        # Cấu hình Scapy để bật chế độ 'Promiscuous' (Nghe lén toàn bộ)
        conf.sniff_promisc = True

    def list_interfaces(self):
        """
        Liệt kê các giao diện mạng.
        Trả về một dict {tên_hiển_thị: tên_hệ_thống}
        """
        interfaces = {}
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for name, addr_list in addrs.items():
                if name in stats and stats[name].isup:
                    ip = "Không có IP"
                    for addr in addr_list:
                        if addr.family == 2: # AF_INET (IPv4)
                            ip = f"IP: {addr.address}"
                            break
                    
                    display_name = f"{name} ({ip})"
                    interfaces[display_name] = name 
                    
        except Exception as e:
            print(f"[LỖI] Không thể liệt kê giao diện: {e}")
        return interfaces

    def start_sniffing(self, iface_name, packet_callback, stop_event):
        """
        Bắt đầu quét (sniff) trên một giao diện cụ thể.
        Dừng lại khi stop_event (một đối tượng threading.Event) được set.
        """
        print(f"\n[MẠNG] Gateway Monitor đang chạy trên: {iface_name}...")
        try:
            # store=False: Không lưu gói tin vào bộ nhớ (tiết kiệm RAM)
            # prn=packet_callback: Gọi hàm này cho mỗi gói tin
            # stop_filter: Kiểm tra sự kiện này sau mỗi gói tin
            sniff(
                iface=iface_name,
                prn=packet_callback,
                store=False,
                stop_filter=lambda x: stop_event.is_set()
            )
        except PermissionError:
            print("\n[LỖI] Không có quyền. Hãy chạy với Admin/Sudo!")
            raise PermissionError("Không có quyền quét. Vui lòng chạy với quyền Admin/sudo.")
        except Exception as e:
            print(f"\n[LỖI] Quá trình quét dừng lại: {e}")
        
        print("[MẠNG] Đã dừng lắng nghe.")

    def scan_network(self, ip_range, iface_name):
        """
        (MỚI) Quét mạng để tìm các thiết bị đang hoạt động bằng ARP Request.
        Trả về: List các dict [{'ip': '192.168.1.5', 'mac': 'AA:BB:CC...'}]
        """
        print(f"[MẠNG] Đang quét thiết bị trong dải {ip_range} trên giao diện {iface_name}...")
        try:
            # Tạo gói tin ARP Request gửi tới Broadcast (hỏi toàn mạng)
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            # Gửi và nhận phản hồi
            # srp trả về 2 list: (đã trả lời, chưa trả lời). Ta chỉ lấy [0]
            # timeout=2: Chờ 2 giây cho mỗi phản hồi
            result = srp(packet, timeout=2, verbose=False, iface=iface_name)[0]

            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
            
            print(f"[MẠNG] Quét hoàn tất. Tìm thấy {len(devices)} thiết bị.")
            return devices
            
        except Exception as e:
            print(f"[LỖI] Quét mạng thất bại: {e}")
            return []