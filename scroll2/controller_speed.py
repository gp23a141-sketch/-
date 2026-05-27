import cv2
import numpy as np
from collections import deque

class PenlightController:
    def __init__(self, camera_id=0, width=1200, height=800):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_id)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -6) # 露出設定（背景を暗くして光を際立たせる）
        self.cap.set(cv2.CAP_PROP_SATURATION, 200) # 彩度の設定 値の範囲はカメラによる（0〜255など）
        
        self.proc_w = 320
        self.proc_h = 240
        
        self.area_threshold = 30

        # 動作判定用の設定 
        self.deadzone_x = 100  # 左右の反応エリアまでの距離
        self.deadzone_y = 100  # 下の反応エリア（ジャンプ）までの距離
        
        self.pos_history = deque(maxlen=8) # 過去8フレーム分の位置を記憶
        
        # 走りと判定する閾値　数値を200以上に変更すると判定が鈍くなる
        # 逆に200以下にすると判定がピーキーになっていく
        self.shake_threshold = 200 

        self.masks_config = {
            "fire":  [
                ([0, 160, 160], [10, 255, 255]), 
                ([170, 160, 160], [180, 255, 255])
            ],
            "purple": [
                # 紫に変更
                ([140, 160, 160], [165, 255, 255])
            ],
            "grass": [
                ([45, 160, 160], [75, 255, 255])
            ],
            "water": [
                ([100, 160, 160], [130, 255, 255])
            ]
        }
        
        self.draw_colors = {
            "fire": (0, 0, 255),
            "purple": (128, 0, 128),
            "grass": (0, 255, 0),
            "water": (255, 0, 0),
            "none": (200, 200, 200)
        }

        self.morph_kernel = np.ones((5, 5), np.uint8)

    def get_action(self, pos, is_detected, center_x, center_y):
        """位置と軌跡から現在のアクションを判定する"""
        if not is_detected:
            self.pos_history.clear()
            return "none", "idle"

        self.pos_history.append(pos)

        # 軌跡の合計移動距離を計算して「振り」を判定
        total_movement = 0
        if len(self.pos_history) > 1:
            for i in range(1, len(self.pos_history)):
                p1 = self.pos_history[i-1]
                p2 = self.pos_history[i]
                dist = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                total_movement += dist

        is_shaking = total_movement > self.shake_threshold
        speed_state = "run" if is_shaking else "walk"

        x, y = pos
        dx = x - center_x
        dy = y - center_y

        action = "none"

        # 下にあるかどうかの判定（ジャンプ優先）
        if dy > self.deadzone_y:
            action = "jump"
        # 左右の判定
        elif dx > self.deadzone_x:
            action = "right"
        elif dx < -self.deadzone_x:
            action = "left"
        else:
            action = "center" # 中央にいるときは停止

        return action, speed_state

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, (0, 0), "none", "none", "idle", None

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2

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
                    
                    detected_pos = (final_x, final_y)
                    detected_element = element
                    is_detected = True
                    scale_radius = max(scale_x, scale_y)
                    detected_radius = int(radius_float * scale_radius)
                    break

        # 動作判定 
        action, speed = self.get_action(detected_pos, is_detected, center_x, center_y)

        # 描画処理 
        cv2.line(frame, (center_x - self.deadzone_x, 0), (center_x - self.deadzone_x, h), (150, 150, 150), 1)
        cv2.line(frame, (center_x + self.deadzone_x, 0), (center_x + self.deadzone_x, h), (150, 150, 150), 1)
        cv2.line(frame, (0, center_y + self.deadzone_y), (w, center_y + self.deadzone_y), (150, 150, 150), 1)

        def draw_ui_text(img, text, y_pos, color):
            cv2.putText(img, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if is_detected:
            color = self.draw_colors[detected_element]
            cv2.circle(frame, detected_pos, detected_radius, color, 2)
            cv2.circle(frame, detected_pos, 6, (255, 255, 255), -1)
            cv2.line(frame, (center_x, center_y), detected_pos, color, 2)
            
            draw_ui_text(frame, f"ELEM: {detected_element.upper()}", 30, color)
            draw_ui_text(frame, f"ACTION: {action.upper()}", 60, (255, 255, 255))
            draw_ui_text(frame, f"SPEED: {speed.upper()}", 90, (255, 255, 0) if speed == "run" else (255, 255, 255))
        else:
            draw_ui_text(frame, "No penlight detected", 30, (255, 255, 255))

        return is_detected, detected_pos, detected_element, action, speed, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("カメラ起動中... 'q' で終了")
    controller = PenlightController(camera_id=0)

    try:
        while True:
            detected, pos, element, action, speed, debug_frame = controller.update()
            
            if debug_frame is not None:
                cv2.imshow('Penlight Debug Monitor', debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        controller.release()
        print("終了しました")