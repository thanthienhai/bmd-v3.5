# processing.py
from ultralytics import YOLO
import cv2

class FootAcupointDetector:
    def __init__(self, model_path):
        # Load the YOLO-Pose model
        self.model = YOLO(model_path)
        # Định nghĩa tên các huyệt đạo
        self.acupoint_names = {
            0: "Ly Noi Dinh",
            1: "Doc Am",
            2: "Ly Hoanh Van", 
            3: "Dung Tuyen",
            4: "Tuc Tam",
            5: "That Mien"
        }

    def detect_acupoints(self, image):
        # Perform inference
        results = self.model(image)
        # Extract bounding boxes and keypoints
        keypoints = []
        for result in results:
            if result.keypoints is not None:  # Kiểm tra nếu có keypoints
                for detection in result.keypoints.xy:  # Lấy tọa độ x, y của các keypoints
                    points = detection.cpu().numpy()  # Chuyển thành numpy array để xử lý
                    keypoints.append(points)
        return keypoints

    def visualize_keypoints(self, image, keypoints):
        # Vẽ các điểm huyệt lên ảnh và hiển thị tên
        for points in keypoints:
            for idx, (x, y) in enumerate(points):
                if idx >= len(self.acupoint_names):  # Kiểm tra nếu vượt quá số lượng tên đã định nghĩa
                    break
                x, y = int(x), int(y)
                
                # Vẽ điểm keypoint với kích thước lớn hơn (radius = 6 thay vì 3)
                cv2.circle(image, (x, y), 6, (0, 0, 255), -1)  # Vẽ mỗi keypoint như một vòng tròn đỏ lớn hơn
                
                # Lấy tên huyệt đạo
                acupoint_name = self.acupoint_names[idx]
                
                # Tính toán vị trí để đặt text
                text_x = x + 10  # Tăng khoảng cách với điểm để dễ đọc hơn
                text_y = y + 10
                
                # Vẽ tên huyệt đạo trực tiếp không có nền
                cv2.putText(
                    image,
                    acupoint_name,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,  # Tăng kích thước font để dễ đọc hơn
                    (255, 0, 0),  # Màu trắng
                    2,  # Tăng độ dày để text nổi bật hơn
                    cv2.LINE_AA
                )
        # height, width, _ = image.shape
        # new_height, new_width = int(height * 0.25), int(width * 0.25)
        # image = cv2.resize(image, (new_width, new_height))
        return image

# import cv2
# import numpy as np
# import onnxruntime
# import time

# class FootAcupointDetector:
#     def __init__(self, model_path, input_size=640, scale_factor=0.5, enable_cuda=True):
#         self.input_size = input_size
#         self.scale_factor = scale_factor  # Hệ số scale cho ảnh đầu vào
        
#         # Cấu hình ONNX Runtime
#         sess_options = onnxruntime.SessionOptions()
#         sess_options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
#         sess_options.intra_op_num_threads = 4  # Số thread cho xử lý song song
        
#         # Chọn provider phù hợp
#         providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if enable_cuda else ['CPUExecutionProvider']
        
#         # Load model với các tùy chọn tối ưu
#         self.session = onnxruntime.InferenceSession(
#             model_path,
#             providers=providers,
#             sess_options=sess_options
#         )
        
#         self.input_name = self.session.get_inputs()[0].name
#         self.output_names = [output.name for output in self.session.get_outputs()]
        
#         self.acupoint_names = {
#             0: "Ly Noi Dinh",
#             1: "Doc Am",
#             2: "Ly Hoanh Van",
#             3: "Dung Tuyen",
#             4: "Tuc Tam",
#             5: "That Mien"
#         }
        
#         # Cache cho ảnh đã được tiền xử lý
#         self.preprocess_cache = {}

#     def letterbox(self, image):
#         """Resize và pad ảnh với tối ưu performance"""
#         # Scale down ảnh đầu vào theo scale_factor
#         if self.scale_factor != 1.0:
#             orig_h, orig_w = image.shape[:2]
#             scaled_h, scaled_w = int(orig_h * self.scale_factor), int(orig_w * self.scale_factor)
#             image = cv2.resize(image, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
        
#         orig_h, orig_w = image.shape[:2]
#         r = self.input_size / max(orig_h, orig_w)
#         new_h, new_w = int(orig_h * r), int(orig_w * r)
        
#         # Sử dụng INTER_LINEAR cho upscale, INTER_AREA cho downscale
#         interp = cv2.INTER_LINEAR if r > 1 else cv2.INTER_AREA
#         resized = cv2.resize(image, (new_w, new_h), interpolation=interp)
        
#         # Sử dụng np.zeros thay vì np.full cho tốc độ tốt hơn
#         padded = np.zeros((self.input_size, self.input_size, 3), dtype=np.uint8)
        
#         # Tính padding
#         dw, dh = (self.input_size - new_w) // 2, (self.input_size - new_h) // 2
        
#         # Sử dụng array slicing để copy nhanh hơn
#         padded[dh:dh+new_h, dw:dw+new_w] = resized
        
#         self.scale_factors = {
#             'orig_size': (orig_h, orig_w),
#             'resized_size': (new_h, new_w),
#             'pad': (dh, dw),
#             'scale': r,
#             'input_scale': self.scale_factor
#         }
        
#         return padded

#     def preprocess_image(self, image):
#         # Tạo key cho cache dựa trên shape và content của ảnh
#         cache_key = hash(image.tobytes())
        
#         # Kiểm tra cache
#         if cache_key in self.preprocess_cache:
#             return self.preprocess_cache[cache_key]
        
#         padded_img = self.letterbox(image)
        
#         # Chuyển đổi màu và normalize trong một bước
#         img = cv2.cvtColor(padded_img, cv2.COLOR_BGR2RGB)
#         img = img.astype(np.float32) * (1.0/255.0)
        
#         # Sử dụng ascontiguousarray để tối ưu memory layout
#         img = np.ascontiguousarray(np.transpose(img, (2, 0, 1)))
#         img = np.expand_dims(img, axis=0)
        
#         # Lưu vào cache
#         self.preprocess_cache[cache_key] = img
        
#         return img

#     def scale_coordinates(self, x, y):
#         """Scale coordinates về kích thước ảnh gốc"""
#         sf = self.scale_factors
        
#         # Loại bỏ padding
#         x = (x - sf['pad'][1])
#         y = (y - sf['pad'][0])
        
#         # Scale về kích thước ảnh đã scale
#         x = x / sf['scale']
#         y = y / sf['scale']
        
#         # Scale về kích thước ảnh gốc
#         x = x / sf['input_scale']
#         y = y / sf['input_scale']
        
#         return x, y

#     def detect_acupoints(self, image):
#         preprocessed_img = self.preprocess_image(image)
        
#         try:
#             # Thực hiện inference
#             start_time = time.time()
#             outputs = self.session.run(self.output_names, {self.input_name: preprocessed_img})
#             inference_time = time.time() - start_time
#             print(f"Inference time: {inference_time:.3f} seconds")
            
#             keypoints = []
#             if outputs[0].size > 0:
#                 detection = outputs[0]
#                 if len(detection.shape) == 3:
#                     kps = detection[0]
#                 elif len(detection.shape) == 2:
#                     kps = detection
#                 else:
#                     return []
                
#                 scaled_kps = []
#                 for kp in kps:
#                     if len(kp) == 2:
#                         x, y = self.scale_coordinates(kp[0], kp[1])
#                         scaled_kps.append([x, y])
                
#                 keypoints.append(scaled_kps)
            
#             return keypoints
            
#         except Exception as e:
#             print(f"Error during inference: {str(e)}")
#             return []
        
#     def visualize_keypoints(self, image, keypoints):
#         output_img = image.copy()
        
#         # Tạo font và các tham số text một lần
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 0.7
#         font_thickness = 2
        
#         for points in keypoints:
#             for idx, (x, y) in enumerate(points):
#                 if idx >= len(self.acupoint_names):
#                     break
                    
#                 x, y = int(x), int(y)
                
#                 if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
#                     # Vẽ điểm
#                     cv2.circle(output_img, (x, y), 8, (255, 255, 255), -1)
#                     cv2.circle(output_img, (x, y), 6, (0, 0, 255), -1)
                    
#                     # Vẽ text
#                     acupoint_name = self.acupoint_names[idx]
#                     (text_w, text_h), _ = cv2.getTextSize(
#                         acupoint_name, font, font_scale, font_thickness
#                     )
                    
#                     text_x = min(x + 10, image.shape[1] - text_w - 5)
#                     text_y = min(y + 10, image.shape[0] - 5)
                    
#                     cv2.rectangle(
#                         output_img,
#                         (text_x - 2, text_y - text_h - 2),
#                         (text_x + text_w + 2, text_y + 2),
#                         (0, 0, 0),
#                         -1
#                     )
                    
#                     cv2.putText(
#                         output_img,
#                         acupoint_name,
#                         (text_x, text_y),
#                         font,
#                         font_scale,
#                         (255, 255, 255),
#                         font_thickness,
#                         cv2.LINE_AA
#                     )
        
#         return output_img

#     def process_image(self, image_path, benchmark=False):
#         """Process ảnh với tùy chọn benchmark"""
#         total_start = time.time()
        
#         # Đọc ảnh
#         read_start = time.time()
#         image = cv2.imread(image_path)
#         read_time = time.time() - read_start
        
#         if image is None:
#             raise ValueError(f"Không thể đọc ảnh từ {image_path}")
        
#         # Detect keypoints
#         detect_start = time.time()
#         keypoints = self.detect_acupoints(image)
#         detect_time = time.time() - detect_start
        
#         # Visualize kết quả
#         vis_start = time.time()
#         output_img = self.visualize_keypoints(image, keypoints)
#         vis_time = time.time() - vis_start
        
#         total_time = time.time() - total_start
        
#         if benchmark:
#             print(f"Performance metrics:")
#             print(f"- Image reading: {read_time:.3f}s")
#             print(f"- Detection: {detect_time:.3f}s")
#             print(f"- Visualization: {vis_time:.3f}s")
#             print(f"- Total time: {total_time:.3f}s")
#             print(f"- FPS: {1/total_time:.1f}")
        
#         return output_img, keypoints