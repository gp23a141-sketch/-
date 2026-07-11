import cv2
import numpy as np
from collections import deque

class PenlightController:
    def __init__(self, camera_id=1, width=1200, height=800):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_id)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -10)
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        self.proc_w = 320
        self.proc_h = 240
        
        self.area_threshold = 30

        # 動作判定用の設定 
        self.deadzone_x = 100  # 左右の反応エリアまでの距離
        self.deadzone_y = 100  # 下の反応エリア（ジャンプ）までの距離
        
        self.pos_history = deque(maxlen=8) # 過去8フレーム分の位置を記憶
        
        self.shake_threshold = 200 

        self.masks_config = {
            "fire":  [
                ([0, 160, 160], [10, 255, 255]), 
                ([170, 160, 160], [180, 255, 255])
            ],
            "purple": [
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
        """位置と軌跡から現在のアクションを判定する（移動用ペンライト専用）"""
        if not is_detected:
            self.pos_history.clear()
            return "none", "idle"

        self.pos_history.append(pos)

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

        if dy > self.deadzone_y:
            action = "jump"
        elif dx > self.deadzone_x:
            action = "right"
        elif dx < -self.deadzone_x:
            action = "left"
        else:
            action = "center"

        return action, speed_state

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            # 戻り値の形式を変更（移動用と属性用を別々に返す）
            return False, (0, 0), "none", "idle", False, "none", (0, 0), None

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2

        frame_resized = cv2.resize(frame, (self.proc_w, self.proc_h))
        blurred = cv2.GaussianBlur(frame_resized, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # 移動用（紫）の変数
        move_detected = False
        move_pos = (0, 0)
        
        # 属性用（赤・緑・青）の変数
        attr_detected = False
        attr_element = "none"
        attr_pos = (0, 0)
        
        # 描画用のリスト（複数色描画するため）
        draw_data = []

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
                    
                    cx_small, cy_small = int(cx_float), int(cy_float)
                    scale_x, scale_y = w / self.proc_w, h / self.proc_h
                    final_x, final_y = int(cx_small * scale_x), int(cy_small * scale_y)
                    scale_radius = max(scale_x, scale_y)
                    detected_radius = int(radius_float * scale_radius)
                    
                    # 紫なら移動用、それ以外なら属性用として記録
                    if element == "purple":
                        move_detected = True
                        move_pos = (final_x, final_y)
                    else:
                        attr_detected = True
                        attr_element = element
                        attr_pos = (final_x, final_y)
                    
                    draw_data.append((final_x, final_y, detected_radius, element))
                    
                    # 【修正ポイント】ここで break していたのを削除し、他の色も探し続けるようにしました

        # アクション判定は「移動用のペンライト（紫）」の位置を使用
        action, speed = self.get_action(move_pos, move_detected, center_x, center_y)

        # --- 描画処理 ---
        cv2.line(frame, (center_x - self.deadzone_x, 0), (center_x - self.deadzone_x, h), (150, 150, 150), 10)
        cv2.line(frame, (center_x + self.deadzone_x, 0), (center_x + self.deadzone_x, h), (150, 150, 150), 10)
        cv2.line(frame, (0, center_y + self.deadzone_y), (w, center_y + self.deadzone_y), (150, 150, 150), 10)

        def draw_ui_text(img, text, y_pos, color):
            cv2.putText(img, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 検出されたすべてのペンライトを描画
        for (x, y, r, elem) in draw_data:
            color = self.draw_colors[elem]
            cv2.circle(frame, (x, y), r, color, 2)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), -1)
            # 紫（移動用）の場合のみ、中心からの線を描画
            if elem == "purple":
                cv2.line(frame, (center_x, center_y), (x, y), color, 2)

        # UIテキストの更新
        if move_detected:
            draw_ui_text(frame, f"MOVE: PURPLE", 30, self.draw_colors["purple"])
            draw_ui_text(frame, f"ACTION: {action.upper()}", 60, (255, 255, 255))
            draw_ui_text(frame, f"SPEED: {speed.upper()}", 90, (255, 255, 0) if speed == "run" else (255, 255, 255))
        else:
            draw_ui_text(frame, "No move penlight", 30, (200, 200, 200))

        if attr_detected:
            draw_ui_text(frame, f"ATTR: {attr_element.upper()}", 120, self.draw_colors[attr_element])
        else:
            draw_ui_text(frame, "No attr penlight", 120, (200, 200, 200))

        # 戻り値を移動用と属性用に分けて返す
        return move_detected, move_pos, action, speed, attr_detected, attr_element, attr_pos, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("カメラ起動中... 'q' で終了")
    controller = PenlightController(camera_id=1)

    try:
        while True:
            # 戻り値の受け取り方も合わせて変更
            move_detected, move_pos, action, speed, attr_detected, attr_element, attr_pos, debug_frame = controller.update()
            
            if debug_frame is not None:
                cv2.imshow('Penlight Debug Monitor', debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        controller.release()
        print("終了しました")