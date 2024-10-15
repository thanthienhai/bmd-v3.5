# Unit tests for camera functionality
import unittest
from src.camera import get_camera, release_camera

class TestCamera(unittest.TestCase):
    
    def test_camera_open(self):
        cap = get_camera()
        self.assertTrue(cap.isOpened())
        release_camera(cap)

if __name__ == "__main__":
    unittest.main()
