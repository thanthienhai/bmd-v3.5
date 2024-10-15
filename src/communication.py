# Code for Raspberry Pi to communicate with microcontroller (I2C)
import smbus
import time

class RaspberryPiI2C:
    def __init__(self, bus=1, address=0x08):
        # Initialize the I2C bus
        self.bus = smbus.SMBus(bus)
        self.address = address

    def write_data(self, data):
        """Send data to the microcontroller via I2C."""
        try:
            # Send data as a single byte
            self.bus.write_byte(self.address, data)
            print(f"Data {data} sent successfully!")
        except Exception as e:
            print(f"Failed to send data: {e}")

    def read_data(self):
        """Read a byte of data from the microcontroller."""
        try:
            data = self.bus.read_byte(self.address)
            print(f"Data {data} received from microcontroller.")
            return data
        except Exception as e:
            print(f"Failed to read data: {e}")
            return None

    def close(self):
        """Close the I2C bus."""
        self.bus.close()

if __name__ == "__main__":
    # Example usage
    i2c = RaspberryPiI2C(address=0x08)  # Replace with your microcontroller I2C address
    while True:
        # Write and read data to/from microcontroller
        i2c.write_data(1)  # Example: sending a byte
        time.sleep(1)
        data = i2c.read_data()  # Example: reading a byte
        time.sleep(1)
