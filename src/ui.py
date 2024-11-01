import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO

# Thread riêng cho camera capture
class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Chuyển BGR sang RGB vì Qt sử dụng RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(frame)
            self.msleep(30)  # Delay 30ms
            
        cap.release()

    def stop(self):
        self.running = False
        self.wait()

class BMDMachineControl(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMD machine control V3.5")
        self.setGeometry(100, 100, 800, 600)
        
        # Khởi tạo detector
        try:
            self.detector = FootAcupointDetector("path/to/your/model.pt")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.detector = None
        
        # Khởi tạo camera thread
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.process_frame)
        
        # Trạng thái cho các nút
        self.medicine_on = False
        self.herb_on = False
        self.is_processing = False

        # Tạo tab widget cho các chức năng
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.createFootMassageTab(), "Massage bàn chân")
        self.tab_widget.addTab(self.createCreateRoutineTab(), "Tạo bài bấm huyệt")
        self.tab_widget.addTab(self.createSettingsTab(), "Cài đặt")

        # Thiết lập widget trung tâm
        self.setCentralWidget(self.tab_widget)

    def createFootMassageTab(self):
        tab = QWidget()

        # Màn hình bên trái và phải
        self.left_display = QLabel()
        self.left_display.setAlignment(Qt.AlignCenter)
        self.left_display.setStyleSheet("background-color: #f0f0f0;")
        self.left_display.setMinimumSize(320, 240)
        
        self.right_display = QLabel()
        self.right_display.setAlignment(Qt.AlignCenter)
        self.right_display.setStyleSheet("background-color: #a0a0a0;")
        self.right_display.setMinimumSize(320, 240)

        # Các control khác
        routine_selection = QComboBox()
        routine_selection.addItems(["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", "Bổ thận tráng dương", "Nâng cao sức khỏe"])

        self.start_button = QPushButton("Bắt đầu bấm huyệt")
        self.start_button.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        self.start_button.setFixedHeight(100)
        self.start_button.clicked.connect(self.start_massage)
        
        self.stop_button = QPushButton("Dừng máy")
        self.stop_button.setStyleSheet("background-color: #ff0000; color: black; font-weight: bold;")
        self.stop_button.clicked.connect(self.stop_massage)

        self.btn_on_medicine = QPushButton("Bật dẫn dược")
        self.btn_off_medicine = QPushButton("Tắt dẫn dược")
        self.btn_on_herb = QPushButton("Đốt dược liệu")
        self.btn_off_herb = QPushButton("Tắt đốt dược liệu")

        self.btn_on_medicine.clicked.connect(self.toggle_medicine)
        self.btn_off_medicine.clicked.connect(self.toggle_medicine)
        self.btn_on_herb.clicked.connect(self.toggle_herb)
        self.btn_off_herb.clicked.connect(self.toggle_herb)

        self.status_display = QLabel("Đang chờ...")
        self.status_display.setAlignment(Qt.AlignCenter)
        
        self.description_display = QLabel("Chọn bài bấm huyệt và nhấn Bắt đầu")
        self.description_display.setAlignment(Qt.AlignCenter)

        # Layouts
        display_layout = QHBoxLayout()
        display_layout.addWidget(self.left_display)
        display_layout.addWidget(self.right_display)

        control_layout = QVBoxLayout()
        control_layout.addWidget(routine_selection)
        
        control_buttons_layout = QHBoxLayout()
        control_buttons_layout.addWidget(self.btn_on_medicine)
        control_buttons_layout.addWidget(self.btn_off_medicine)
        control_buttons_layout.addWidget(self.btn_on_herb)
        control_buttons_layout.addWidget(self.btn_off_herb)
        
        control_layout.addLayout(control_buttons_layout)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.start_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(display_layout)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.status_display)
        main_layout.addWidget(self.description_display)

        tab.setLayout(main_layout)
        return tab

    @pyqtSlot(np.ndarray)
    def process_frame(self, frame):
        if self.is_processing and self.detector is not None:
            try:
                # Phát hiện các điểm huyệt
                keypoints = self.detector.detect_acupoints(frame)
                
                # Vẽ các điểm huyệt lên frame
                processed_frame = self.detector.visualize_keypoints(frame.copy(), keypoints)
                
                # Chuyển đổi frame thành QImage
                height, width, channel = processed_frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Hiển thị lên left_display
                self.left_display.setPixmap(QPixmap.fromImage(q_img).scaled(
                    self.left_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
            except Exception as e:
                print(f"Error processing frame: {e}")
        else:
            # Hiển thị frame gốc nếu không trong trạng thái xử lý
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.left_display.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.left_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def start_massage(self):
        self.is_processing = True
        self.camera_thread.start()
        self.status_display.setText("Đang thực hiện bấm huyệt...")
        
    def stop_massage(self):
        self.is_processing = False
        self.camera_thread.stop()
        self.status_display.setText("Đã dừng")

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

    def toggle_medicine(self):
        self.medicine_on = not self.medicine_on
        if self.medicine_on:
            self.btn_on_medicine.setStyleSheet("background-color: #00ff00; color: black;")
            self.btn_off_medicine.setStyleSheet("")
        else:
            self.btn_on_medicine.setStyleSheet("")
            self.btn_off_medicine.setStyleSheet("background-color: #00ff00; color: black;")

    def toggle_herb(self):
        self.herb_on = not self.herb_on
        if self.herb_on:
            self.btn_on_herb.setStyleSheet("background-color: #00ff00; color: black;")
            self.btn_off_herb.setStyleSheet("")
        else:
            self.btn_on_herb.setStyleSheet("")
            self.btn_off_herb.setStyleSheet("background-color: #00ff00; color: black;")

    def createCreateRoutineTab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Tạo bài bấm huyệt - Giao diện chưa được thiết lập")
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab

    def createSettingsTab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Cài đặt - Giao diện chưa được thiết lập")
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab

def main():
    # Đảm bảo Qt platform plugin được tìm thấy
    try:
        # Thử set environment variable cho Qt plugins
        import os
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
        
        app = QApplication(sys.argv)
        window = BMDMachineControl()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()