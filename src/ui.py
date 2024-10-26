import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import Qt

class BMDMachineControl(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMD machine control V3.5")
        self.setGeometry(100, 100, 800, 600)
        
        # Trạng thái cho các nút
        self.medicine_on = False
        self.herb_on = False

        # Tạo tab widget cho các chức năng
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.createFootMassageTab(), "Massage bàn chân")
        self.tab_widget.addTab(self.createCreateRoutineTab(), "Tạo bài bấm huyệt")
        self.tab_widget.addTab(self.createSettingsTab(), "Cài đặt")

        # Thiết lập widget trung tâm
        self.setCentralWidget(self.tab_widget)

    def createFootMassageTab(self):
        # Tab cho chức năng Massage bàn chân
        tab = QWidget()

        # Màn hình bên trái và bên phải
        left_display = QLabel("the screen display of the left foot")
        left_display.setAlignment(Qt.AlignCenter)
        left_display.setStyleSheet("background-color: #f0f0f0;")
        
        right_display = QLabel("the screen display of the right foot")
        right_display.setAlignment(Qt.AlignCenter)
        right_display.setStyleSheet("background-color: #a0a0a0;")

        # Lựa chọn bài bấm huyệt và các nút điều khiển
        routine_selection = QComboBox()
        routine_selection.addItems(["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", "Bổ thận tráng dương", "Nâng cao sức khỏe"])

        start_button = QPushButton("Bắt đầu bấm huyệt")
        start_button.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        
        stop_button = QPushButton("Dừng máy")
        stop_button.setStyleSheet("background-color: #ff0000; color: black; font-weight: bold;")

        # Các nút dẫn dược và đốt dược liệu
        self.btn_on_medicine = QPushButton("Bật dẫn dược")
        self.btn_on_medicine.clicked.connect(self.toggle_medicine)
        
        self.btn_off_medicine = QPushButton("Tắt dẫn dược")
        self.btn_off_medicine.clicked.connect(self.toggle_medicine)
        
        self.btn_on_herb = QPushButton("Đốt dược liệu")
        self.btn_on_herb.clicked.connect(self.toggle_herb)
        
        self.btn_off_herb = QPushButton("Tắt đốt dược liệu")
        self.btn_off_herb.clicked.connect(self.toggle_herb)

        # Khu vực hiển thị thông báo và mô tả hoạt động
        status_display = QLabel("Khu vực hiển thị thông báo trạng thái/lỗi (Text)")
        status_display.setAlignment(Qt.AlignCenter)
        
        description_display = QLabel("Khu vực hiển thị mô tả hoạt động của bài bấm (Text)")
        description_display.setAlignment(Qt.AlignCenter)

        # Layout cho màn hình hiển thị chân trái và phải
        display_layout = QHBoxLayout()
        display_layout.addWidget(left_display)
        display_layout.addWidget(right_display)

        # Layout cho lựa chọn bài bấm huyệt và các nút điều khiển
        control_layout = QVBoxLayout()
        control_layout.addWidget(routine_selection)
        
        control_buttons_layout = QHBoxLayout()
        control_buttons_layout.addWidget(self.btn_on_medicine)
        control_buttons_layout.addWidget(self.btn_off_medicine)
        control_buttons_layout.addWidget(self.btn_on_herb)
        control_buttons_layout.addWidget(self.btn_off_herb)
        
        control_layout.addLayout(control_buttons_layout)
        control_layout.addWidget(stop_button)
        control_layout.addWidget(start_button)

        # Layout chính của tab
        main_layout = QVBoxLayout()
        main_layout.addLayout(display_layout)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(status_display)
        main_layout.addWidget(description_display)

        tab.setLayout(main_layout)
        return tab

    def toggle_medicine(self):
        # Toggle trạng thái bật/tắt dẫn dược
        self.medicine_on = not self.medicine_on
        if self.medicine_on:
            self.btn_on_medicine.setStyleSheet("background-color: #00ff00; color: black;")
            self.btn_off_medicine.setStyleSheet("")
        else:
            self.btn_on_medicine.setStyleSheet("")
            self.btn_off_medicine.setStyleSheet("background-color: #00ff00; color: black;")

    def toggle_herb(self):
        # Toggle trạng thái bật/tắt đốt dược liệu
        self.herb_on = not self.herb_on
        if self.herb_on:
            self.btn_on_herb.setStyleSheet("background-color: #00ff00; color: black;")
            self.btn_off_herb.setStyleSheet("")
        else:
            self.btn_on_herb.setStyleSheet("")
            self.btn_off_herb.setStyleSheet("background-color: #00ff00; color: black;")

    def createCreateRoutineTab(self):
        # Tab cho chức năng Tạo bài bấm huyệt
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Tạo bài bấm huyệt - Giao diện chưa được thiết lập")
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab

    def createSettingsTab(self):
        # Tab cho chức năng Cài đặt
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Cài đặt - Giao diện chưa được thiết lập")
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab

def main():
    app = QApplication(sys.argv)
    window = BMDMachineControl()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
