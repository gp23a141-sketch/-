import cv2
import numpy as np
from collections import deque

class PenlightController:
    def __init__(self, camera_id=0, width=1200, height=800):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        # 開けない場合はフォールバック
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            print(f"警告: camera_id={camera_id} が開けませんでした。camera_id=0 で再試行します。")
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -4)
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        self.proc_w = 320
        self.proc_h = 240
        
        self.area_threshold = 30

        # 動作判定用の設定 
        self.deadzone_x = 100  # 左右の反応エリアまでの距離
        self.deadzone_y = 100  # デッドゾーン設定値
        
        self.pos_history = deque(maxlen=8) # 過去8フレーム分の位置を記憶
        
        self.shake_threshold = 200 

        self.masks_config = {
            "fire": [
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
        dy = y - center_y  # dy < 0 は画面上半部、dy >= 0 は画面下半部

        # --- 領域判定ロジック（画面中央の横線を基準） ---
        if dy < 0:
            # 画面の中央横線より上：ジャンプ系アクション
            if dx > self.deadzone_x:
                action = "jump_right"   # 右上ジャンプ
            elif dx < -self.deadzone_x:
                action = "jump_left"    # 左上ジャンプ
            else:
                action = "jump"         # 垂直ジャンプ
        else:
            # 画面の中央横線より下：通常移動・静止系アクション
            if dx > self.deadzone_x:
                action = "right"        # 右移動
            elif dx < -self.deadzone_x:
                action = "left"         # 左移動
            else:
                action = "center"       # 静止

        return action, speed_state

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
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
        
        # 描画用のリスト
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

        # アクション判定（紫の位置を使用）
        action, speed = self.get_action(move_pos, move_detected, center_x, center_y)

        # --- ガイド線の描画 ---
        # 左右のデッドゾーン境界線
        cv2.line(frame, (center_x - self.deadzone_x, 0), (center_x - self.deadzone_x, h), (150, 150, 150), 2)
        cv2.line(frame, (center_x + self.deadzone_x, 0), (center_x + self.deadzone_x, h), (150, 150, 150), 2)
        # 画面真ん中の横線 (center_y)
        cv2.line(frame, (0, center_y), (w, center_y), (150, 150, 150), 2)

        def draw_ui_text(img, text, y_pos, color):
            cv2.putText(img, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 検出されたペンライトを描画
        for (x, y, r, elem) in draw_data:
            color = self.draw_colors[elem]
            cv2.circle(frame, (x, y), r, color, 2)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), -1)
            if elem == "purple":
                cv2.line(frame, (center_x, center_y), (x, y), color, 2)

        # UIテキスト表示
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

        return move_detected, move_pos, action, speed, attr_detected, attr_element, attr_pos, frame

    def release(self):
        """カメラ等のリソースを開放"""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("カメラ起動中... 'q' で終了")
    controller = PenlightController(camera_id=0)

    try:
        while True:
            move_detected, move_pos, action, speed, attr_detected, attr_element, attr_pos, debug_frame = controller.update()
            
            if debug_frame is not None:
                cv2.imshow('Penlight Debug Monitor', debug_frame)
            else:
                print("カメラからフレームを取得できませんでした。")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        controller.release()
        print("終了しました")