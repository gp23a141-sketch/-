import pygame
import sys
import cv2
import controller_speed  # 作成した controller_speed.py を読み込む

# 画面・ゲーム設定
WIDTH, HEIGHT = 800, 600
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Penlight Action Demo")
clock = pygame.time.Clock()

# コントローラーの初期化
pen_con = controller_speed.PenlightController(camera_id=0)

# プレイヤー設定
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - 100 - player_size
vel_y = 0               # 縦方向の速度
is_jumping = False      # ジャンプ中かどうか

# 物理演算のパラメータ
GRAVITY = 1.5           # 重力
JUMP_POWER = -20        # ジャンプ力
WALK_SPEED = 5          # 歩き速度
RUN_SPEED = 12          # 走り速度
GROUND_Y = HEIGHT - 100 # 地面の高さ

# 剣（属性）のステータス
current_sword = "none"

font = pygame.font.Font(None, 40)

def game_loop():
    global player_x, player_y, vel_y, is_jumping, current_sword
    running = True

    while running:
        # カメラ認識の更新
        # 返り値が6つになると、すべて受け取る
        is_detected, pos, element, action, speed, debug_frame = pen_con.update()

        # 確認用の画面表示
        if debug_frame is not None:
            cv2.imshow('Camera Debug', debug_frame)
            cv2.waitKey(1)

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # アクション・移動処理
        # スピードの設定（走っているか歩いているか）
        move_speed = RUN_SPEED if speed == "run" else WALK_SPEED

        if is_detected:
            if element == "yellow":
                # 黄色の時：移動とジャンプ
                if action == "right":
                    player_x += move_speed
                elif action == "left":
                    player_x -= move_speed
                elif action == "jump" and not is_jumping:
                    vel_y = JUMP_POWER
                    is_jumping = True

            elif element in ["fire", "water", "grass"]:
                # それ以外の色の時：属性（剣）の切り替え
                current_sword = element

        # 物理演算（重力と床の判定） 
        vel_y += GRAVITY
        player_y += vel_y

        # 床との衝突判定
        if player_y >= GROUND_Y - player_size:
            player_y = GROUND_Y - player_size
            vel_y = 0
            is_jumping = False

        # 画面端からはみ出さないように制限
        if player_x < 0: player_x = 0
        if player_x > WIDTH - player_size: player_x = WIDTH - player_size

        # 描画処理 
        screen.fill((30, 30, 40))  # 背景

        # 地面の描画
        pygame.draw.rect(screen, (80, 80, 80), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        # プレイヤー（四角形）の色を現在の属性に合わせる
        # 黄色（移動モード）の時は黄色く光らせる
        player_color = (200, 200, 200)
        if element == "yellow":
            player_color = (255, 255, 0)
        elif current_sword == "fire":
            player_color = (255, 50, 50)
        elif current_sword == "water":
            player_color = (50, 100, 255)
        elif current_sword == "grass":
            player_color = (50, 255, 50)

        # プレイヤーの描画
        pygame.draw.rect(screen, player_color, (player_x, int(player_y), player_size, player_size))

        # （テキスト）の描画 
        # 剣の属性
        sword_text = font.render(f"Sword: {current_sword.upper()}", True, (255, 255, 255))
        screen.blit(sword_text, (20, 20))

        # 現在のアクション
        action_text = font.render(f"Action: {action.upper()}", True, (255, 255, 255))
        screen.blit(action_text, (20, 60))
        
        # 現在のスピード（走っているときは黄色にする）
        speed_color = (255, 255, 0) if speed == "run" else (255, 255, 255)
        speed_text = font.render(f"Speed: {speed.upper()}", True, speed_color)
        screen.blit(speed_text, (20, 100))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    try:
        game_loop()
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        pen_con.release()
        pygame.quit()
        sys.exit()