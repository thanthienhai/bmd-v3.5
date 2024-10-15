# Unit tests for image processing functions
import unittest
import cv2
from src.processing import convert_to_grayscale, apply_canny_edge_detection

class TestProcessing(unittest.TestCase):
    
    def setUp(self):
        self.test_image = cv2.imread("/home/thanthien/Coding/bmd-v3.5/tests/images/e2bbe41183cb3a9563da.jpg")
    
    def test_convert_to_grayscale(self):
        gray_image = convert_to_grayscale(self.test_image)
        self.assertEqual(len(gray_image.shape), 2)  # Grayscale should have 2 dimensions

    def test_apply_canny_edge_detection(self):
        edges = apply_canny_edge_detection(self.test_image)
        self.assertEqual(len(edges.shape), 2)

if __name__ == "__main__":
    unittest.main()
