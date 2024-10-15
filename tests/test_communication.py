# Unit tests for communication functions
import unittest
from src.communication import RaspberryPiI2C

class TestCommunication(unittest.TestCase):

    def setUp(self):
        # Set up the I2C communication
        self.i2c = RaspberryPiI2C(address=0x08)

    def test_write_data(self):
        try:
            self.i2c.write_data(1)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Write data failed: {e}")

    def test_read_data(self):
        try:
            data = self.i2c.read_data()
            self.assertIsNotNone(data)
        except Exception as e:
            self.fail(f"Read data failed: {e}")

    def tearDown(self):
        self.i2c.close()

if __name__ == "__main__":
    unittest.main()
