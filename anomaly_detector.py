# file: anomaly_detector.py
# -*- coding: utf-8 -*-

from sklearn.ensemble import IsolationForest
import numpy as np
from scapy.all import IP, TCP, UDP
import joblib
import json
import os

class AnomalyDetector:
    def __init__(self, n_packets_to_train=1000):
        """
        Khởi tạo mô hình AI.
        contamination='auto' để AI tự quyết định ngưỡng.
        n_packets_to_train: (MỚI) Nhận từ file config.
        """
        self.model = IsolationForest(contamination='auto', random_state=42)
        
        self.n_packets_to_train = n_packets_to_train
        self.packet_buffer = []
        self.is_trained = False
        self.just_trained = False # Báo hiệu cho UI biết vừa huấn luyện xong
        
        # Lưu trữ các chỉ số thống kê để giải thích
        self.training_stats = {}

    def _extract_features(self, packet):
        """Trích xuất đặc trưng từ một gói tin để làm đầu vào cho AI."""
        # Đặc trưng: [Độ dài gói tin, Giao thức, Cổng nguồn, Cổng đích]
        length = len(packet)
        proto = 0
        sport = 0
        dport = 0

        if packet.haslayer(IP):
            proto = packet[IP].proto
            if packet.haslayer(TCP):
                sport = packet[TCP].sport
                dport = packet[TCP].dport
            elif packet.haslayer(UDP):
                sport = packet[UDP].sport
                dport = packet[UDP].dport
        
        return [length, proto, sport, dport]

    def process_packet(self, packet):
        """
        Xử lý từng gói tin. Thu thập, huấn luyện, và sau đó dự đoán.
        Trả về:
            None: Nếu đang trong giai đoạn huấn luyện.
            1: Gói tin bình thường.
            -1: Gói tin bất thường (anomaly).
        """
        features = self._extract_features(packet)

        if not self.is_trained:
            self.packet_buffer.append(features)
            # Nếu đã đủ gói tin để huấn luyện
            if len(self.packet_buffer) >= self.n_packets_to_train:
                self.fit_model()
            return None # Chưa dự đoán
        else:
            # Nếu đã huấn luyện, bắt đầu dự đoán
            prediction = self.model.predict(np.array(features).reshape(1, -1))
            return prediction[0]

    def fit_model(self):
        """Huấn luyện mô hình và tính toán các chỉ số thống kê."""
        try:
            print("[AI] Bắt đầu huấn luyện...")
            self.model.fit(self.packet_buffer)
            self.is_trained = True
            self.just_trained = True # Báo hiệu cho UI
            
            # Tính toán chỉ số thống kê
            data = np.array(self.packet_buffer)
            self.training_stats['mean'] = np.mean(data, axis=0).tolist()
            self.training_stats['std'] = np.std(data, axis=0).tolist()
            # Lấy các cổng phổ biến
            ports = data[:, 2:4]
            common_ports = set(ports[ports > 0].flatten())
            # Giữ top 50 cổng phổ biến nhất (ví dụ)
            self.training_stats['common_ports'] = list(common_ports)[:50] 
            
            print("[AI] Huấn luyện hoàn tất và đã tính toán chỉ số.")
            self.packet_buffer = [] # Xóa bộ đệm
        except Exception as e:
            print(f"[AI LỖI] {e}")
            self.packet_buffer = []

    def explain_anomaly(self, features):
        """Cố gắng giải thích tại sao một gói tin là bất thường."""
        if not self.training_stats:
            return "Không có dữ liệu thống kê để giải thích."
        
        explanations = []
        try:
            mean = self.training_stats['mean']
            std = self.training_stats['std']
            common_ports = set(self.training_stats['common_ports'])
            
            # 1. Kích thước gói tin (features[0])
            if features[0] > mean[0] + 3 * std[0]:
                explanations.append(f"Kích thước lớn bất thường (Gói: {features[0]}, TB: {mean[0]:.0f}).")
            if features[0] < mean[0] - 3 * std[0] and features[0] > 0:
                explanations.append(f"Kích thước nhỏ bất thường (Gói: {features[0]}, TB: {mean[0]:.0f}).")

            # 2. Giao thức (features[1])
            if features[1] not in [6, 17, 1]: # 6=TCP, 17=UDP, 1=ICMP
                 if features[1] != 0:
                    explanations.append(f"Sử dụng giao thức không phổ biến (Proto: {features[1]}).")

            # 3. Cổng (features[2] = sport, features[3] = dport)
            if features[2] > 0 and features[2] not in common_ports:
                explanations.append(f"Sử dụng cổng nguồn hiếm (Port: {features[2]}).")
            if features[3] > 0 and features[3] not in common_ports:
                explanations.append(f"Sử dụng cổng đích hiếm (Port: {features[3]}).")

            if not explanations:
                return "Bất thường do sự kết hợp tinh vi của các yếu tố (khó giải thích)."
            
            return " | ".join(explanations)
        except Exception as e:
            return f"Lỗi khi giải thích: {e}"

    def save_model(self, model_path="model.joblib", stats_path="model_stats.json"):
        """Lưu mô hình và chỉ số thống kê."""
        if self.is_trained:
            try:
                joblib.dump(self.model, model_path)
                with open(stats_path, 'w') as f:
                    json.dump(self.training_stats, f)
                print(f"[AI] Đã lưu mô hình vào {model_path} và {stats_path}")
            except Exception as e:
                print(f"[AI Lỗi] Không thể lưu mô hình: {e}")

    def load_model(self, model_path="model.joblib", stats_path="model_stats.json"):
        """Tải mô hình và chỉ số. Trả về True nếu thành công."""
        if os.path.exists(model_path) and os.path.exists(stats_path):
            try:
                self.model = joblib.load(model_path)
                with open(stats_path, 'r') as f:
                    self.training_stats = json.load(f)
                self.is_trained = True
                print(f"[AI] Đã tải mô hình đã huấn luyện từ {model_path}")
                return True
            except Exception as e:
                print(f"[AI Lỗi] Không thể tải mô hình: {e}. Sẽ huấn luyện lại.")
                return False
        return False