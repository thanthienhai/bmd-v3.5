import cv2
import numpy as np
import ncnn

def preprocess_image(image):
    """Tiền xử lý ảnh đầu vào"""
    height, width = image.shape[:2]
    input_size = 192  # Kích thước đầu vào cho mô hình
    
    # Resize ảnh
    resized_image = cv2.resize(image, (input_size, input_size))
    
    # Chuẩn hóa ảnh
    normalized_image = resized_image.astype(np.float32) / 255.0
    
    # Chuyển định dạng cho ncnn
    blob = ncnn.Mat.from_pixels(normalized_image, ncnn.Mat.PixelType.PIXEL_RGB)
    return blob, width, height

def load_pose_model(model_path, param_path):
    """Tải mô hình pose estimation"""
    net = ncnn.Net()
    net.load_param(param_path)
    net.load_model(model_path)
    return net

def detect_keypoints(net, blob):
    """Phát hiện keypoint từ ảnh đầu vào"""
    extractor = net.create_extractor()
    extractor.input("input", blob)
    
    # Lấy kết quả keypoint
    ret, heatmaps = extractor.extract("output")
    
    return heatmaps

def postprocess_keypoints(heatmaps, orig_width, orig_height, num_keypoints=17):
    """Xử lý hậu kỳ để trích xuất vị trí keypoint"""
    keypoints = []
    
    for i in range(num_keypoints):
        heatmap = heatmaps[i]
        # Tìm điểm có giá trị cao nhất
        _, max_val, _, max_loc = cv2.minMaxLoc(heatmap)
        
        # Chuyển đổi tọa độ về kích thước gốc
        x = int(max_loc[0] * orig_width / heatmap.shape[1])
        y = int(max_loc[1] * orig_height / heatmap.shape[0])
        
        keypoints.append((x, y, max_val))
    
    return keypoints

def draw_keypoints(image, keypoints):
    """Vẽ keypoint lên ảnh"""
    for kp in keypoints:
        x, y, _ = kp
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
    return image

def main():
    # Đường dẫn mô hình (bạn cần tải mô hình tương ứng)
    MODEL_PATH = "models/yolo_pose_model_ncnn_model/model.ncnn.bin"
    PARAM_PATH = "models/yolo_pose_model_ncnn_model/model.ncnn.param"
    
    # Đọc ảnh
    image = cv2.imread("tests/images/e2bbe41183cb3a9563da.jpg")
    
    # Nạp mô hình
    net = load_pose_model(MODEL_PATH, PARAM_PATH)
    
    # Tiền xử lý ảnh
    blob, width, height = preprocess_image(image)
    
    # Nhận diện keypoint
    heatmaps = detect_keypoints(net, blob)
    
    # Xử lý hậu kỳ
    keypoints = postprocess_keypoints(heatmaps, width, height)
    
    # Vẽ keypoint
    result_image = draw_keypoints(image.copy(), keypoints)
    
    # Hiển thị kết quả
    cv2.imshow("Keypoint Detection", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()