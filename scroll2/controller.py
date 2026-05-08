#controller.py
import cv2
import numpy as np

class PenlightController:
    def __init__(self, camera_id=0, width=320, height=240):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_id)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.cap.set(cv2.CAP_PROP_EXPOSURE, -4)
        
        self.proc_w = 320
        self.proc_h = 240
        
        self.valid_radius_ratio = 0.5
        
        # 面積閾値: ここの数値変えれば感度が調節できる
        self.area_threshold = 30

        # 閾値を下げた
        # S(彩度)とV(明度)の下限を 100 まで下げてる
        self.masks_config = {
            "fire":  [
                ([0, 100, 100], [10, 255, 255]), 
                ([170, 100, 100], [180, 255, 255])
            ],
            "grass": [
                ([40, 100, 100], [80, 255, 255])
            ],
            "water": [
                ([100, 100, 100], [140, 255, 255])
            ]
        }

        self.draw_colors = {
            "fire": (0, 0, 255),
            "grass": (0, 255, 0),
            "water": (255, 0, 0),
            "none": (200, 200, 200)
        }

        self.morph_kernel = np.ones((5, 5), np.uint8)

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, (0, 0), "none", None

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        valid_radius = int(min(h, w) * self.valid_radius_ratio)

        frame_resized = cv2.resize(frame, (self.proc_w, self.proc_h))
        blurred = cv2.GaussianBlur(frame_resized, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        detected_pos = (0, 0)
        detected_element = "none"
        is_detected = False
        detected_radius = 0

        for element, ranges in self.masks_config.items():
            mask = np.zeros(hsv.shape[:2], dtype="uint8")
            for (lower, upper) in ranges:
                mask += cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.morph_kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.morph_kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > self.area_threshold]
                
                if valid_contours:
                    all_points = np.vstack(valid_contours)
                    (cx_float, cy_float), radius_float = cv2.minEnclosingCircle(all_points)
                    
                    cx_small = int(cx_float)
                    cy_small = int(cy_float)
                    
                    scale_x = w / self.proc_w
                    scale_y = h / self.proc_h
                    final_x = int(cx_small * scale_x)
                    final_y = int(cy_small * scale_y)
                    
                    dist = np.sqrt((final_x - center_x)**2 + (final_y - center_y)**2)
                    
                    if dist <= valid_radius:
                        detected_pos = (final_x, final_y)
                        detected_element = element
                        is_detected = True
                        scale_radius = max(scale_x, scale_y)
                        detected_radius = int(radius_float * scale_radius)
                        break

        # 描画処理
        cv2.circle(frame, (center_x, center_y), valid_radius, (0, 0, 0), 2)

        def draw_ui_text(img, text, y_pos, color):
            x_pos = 10
            # フォント縁取りなし
            cv2.putText(img, text, (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if is_detected:
            color = self.draw_colors[detected_element]
            cv2.circle(frame, detected_pos, detected_radius, color, 2)
            cv2.circle(frame, detected_pos, 6, (255, 255, 255), -1)
            cv2.circle(frame, detected_pos, 4, color, -1)
            cv2.line(frame, (center_x, center_y), detected_pos, color, 2)
            draw_ui_text(frame, f"DETECTED: {detected_element.upper()}", 30, color)
        else:
            draw_ui_text(frame, "Please move inside the circle", 30, (255, 255, 255))

        return is_detected, detected_pos, detected_element, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("カメラ起動中... 'q' で終了")
    controller = PenlightController(camera_id=0)

    try:
        while True:
            detected, pos, element, debug_frame = controller.update()
            if debug_frame is not None:
                cv2.imshow('Penlight Debug Monitor', debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        controller.release()
        print("終了しました")