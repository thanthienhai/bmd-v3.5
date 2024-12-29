import serial
import serial.tools.list_ports
import time

class UARTManager:
    def __init__(self, baudrate=115200, timeout=1):
        """
        Khởi tạo UARTManager với các thông số mặc định
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None
        self.is_connected = False
        self.setup_serial()

    def setup_serial(self):
        """
        Thiết lập kết nối UART
        """
        try:
            # Tìm cổng COM đang kết nối
            ports = serial.tools.list_ports.comports()
            for port in ports:
                # Trên Linux thường là /dev/ttyUSB0 hoặc /dev/ttyACM0
                # Trên Windows thường là COM3, COM4, ...
                if "USB" in port.description or "ACM" in port.description:
                    self.serial_port = serial.Serial(
                        port=port.device,
                        baudrate=self.baudrate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=self.timeout
                    )
                    self.is_connected = True
                    print(f"Đã kết nối UART với {port.device}")
                    return True
            raise Exception("Không tìm thấy cổng UART phù hợp")
        except Exception as e:
            print(f"Lỗi khi thiết lập UART: {str(e)}")
            self.is_connected = False
            return False

    def connect_to_port(self, port_name):
        """
        Kết nối với một cổng COM cụ thể
        """
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self.is_connected = True
            print(f"Đã kết nối UART với {port_name}")
            return True
        except Exception as e:
            print(f"Lỗi khi kết nối với {port_name}: {str(e)}")
            self.is_connected = False
            return False

    def list_available_ports(self):
        """
        Liệt kê tất cả các cổng COM đang có
        """
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port in ports:
            available_ports.append({
                'device': port.device,
                'description': port.description,
                'manufacturer': port.manufacturer
            })
        return available_ports

    def send_data(self, data):
        """
        Gửi dữ liệu qua UART
        """
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            print("Chưa kết nối UART")
            return False

        try:
            # Chuyển string thành bytes và gửi
            self.serial_port.write(data.encode('utf-8'))
            print(f"Đã gửi dữ liệu: {data}")
            return True
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu: {str(e)}")
            return False

    def read_data(self, size=1024):
        """
        Đọc dữ liệu từ UART
        """
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            print("Chưa kết nối UART")
            return None

        try:
            if self.serial_port.in_waiting:
                return self.serial_port.read(size).decode('utf-8')
        except Exception as e:
            print(f"Lỗi khi đọc d�� liệu: {str(e)}")
        return None

    def close(self):
        """
        Đóng kết nối UART
        """
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_connected = False
            print("Đã đóng kết nối UART")

    def __del__(self):
        """
        Destructor để đảm bảo đóng kết nối khi object bị hủy
        """
        self.close()


# Ví dụ sử dụng
if __name__ == "__main__":
    # Khởi tạo UART Manager
    uart = UARTManager(baudrate=115200)

    # In ra danh sách cổng có sẵn
    print("\nDanh sách cổng COM có sẵn:")
    ports = uart.list_available_ports()
    for port in ports:
        print(f"Device: {port['device']}")
        print(f"Description: {port['description']}")
        print(f"Manufacturer: {port['manufacturer']}\n")

    # Gửi dữ liệu test
    if uart.is_connected:
        test_data = "*\n {\"test\": \"Hello UART\"} #\n"
        uart.send_data(test_data)

        # Đọc phản hồi (nếu có)
        time.sleep(1)  # Đợi 1 giây để nhận phản hồi
        response = uart.read_data()
        if response:
            print(f"Nhận được phản hồi: {response}")

    # Đóng kết nối khi hoàn th��nh
    uart.close() 