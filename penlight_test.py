import pygame
import sys
import os
import cv2
import controller_test

from map_data import (
    MAP,
    BLOCK_MAP,
    BLOCK_OFFSET_X,
    MAP2,
    BLOCK_MAP2
)

# =========================================================
# 設定
# =========================================================

USE_CAMERA = True
DEBUG = True

# =========================================================
# パス
# =========================================================

BASE_DIR = os.path.dirname(__file__)

SOUND_DIR = os.path.join(BASE_DIR, "sounds")
IMAGE_DIR = os.path.join(BASE_DIR, "image")

# =========================================================
# 基本設定
# =========================================================

width, height = 1500, 900

floor_y = 600
size = 24
fps = 60

PLAYER_W = 32
PLAYER_H = 48

# 速度の設定を2段階に変更
WALK_SPEED = 10
RUN_SPEED = 20

jump_power = -28
gravity = 2

PLAYER_MAX_HP = 5
ENEMY_MAX_HP = 3

# =========================================================
# 初期化
# =========================================================

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My Action Game")

clock = pygame.time.Clock()

# =========================================================
# フォント
# =========================================================

font_big = pygame.font.SysFont(None, 80)
font_mid = pygame.font.SysFont(None, 40)

# =========================================================
# BGM
# =========================================================

try:
    pygame.mixer.music.load(os.path.join(SOUND_DIR, "bgm.wav"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except pygame.error:
    print("BGMファイルが見つかりません。スキップします。")

# =========================================================
# SE
# =========================================================

sounds = {}
try:
    sounds = {
        "fire": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_fire.wav")),
        "water": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_water.wav")),
        "grass": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_grass.wav")),
    }
except pygame.error:
    print("SEファイルが見つかりません。スキップします。")

# =========================================================
# カメラ
# =========================================================

pen_con = controller_test.PenlightController(camera_id=1)

# =========================================================
# 画像
# =========================================================

# ※画像ファイルが存在しない場合はダミーを描画するようにしていますが、
# 実際にはご自身の環境に合わせて画像を読み込んでください。
try:
    bg = pygame.image.load(os.path.join(IMAGE_DIR, "bg.png")).convert()
    block = pygame.image.load(os.path.join(IMAGE_DIR, "block.png")).convert_alpha()
    princess = pygame.image.load(os.path.join(IMAGE_DIR, "princess.png")).convert_alpha()

    player_imgs = [
        pygame.image.load(os.path.join(IMAGE_DIR, "player0.png")).convert_alpha(),
        pygame.image.load(os.path.join(IMAGE_DIR, "player1.png")).convert_alpha(),
        pygame.image.load(os.path.join(IMAGE_DIR, "player0.png")).convert_alpha(),
        pygame.image.load(os.path.join(IMAGE_DIR, "player2.png")).convert_alpha(),
    ]

    enemy_base = pygame.image.load(os.path.join(IMAGE_DIR, "devil.png")).convert_alpha()
    enemy_base = pygame.transform.scale(enemy_base, (100, 100))
except pygame.error:
    print("画像ファイルが見つかりません。エラー終了を防ぐため、仮のSurfaceを使用します。")
    bg = pygame.Surface((width, height)); bg.fill((50, 50, 50))
    block = pygame.Surface((size, size)); block.fill((100, 100, 100))
    princess = pygame.Surface((40, 60)); princess.fill((255, 100, 255))
    player_imgs = [pygame.Surface((PLAYER_W, PLAYER_H)) for _ in range(4)]
    for p in player_imgs: p.fill((255, 255, 255))
    enemy_base = pygame.Surface((100, 100)); enemy_base.fill((200, 50, 50))

# =========================================================
# 色
# =========================================================

attr_colors = {
    "fire": (255, 80, 80),
    "water": (80, 120, 255),
    "grass": (80, 255, 120)
}

# =========================================================
# マップ
# =========================================================

maps = [
    {"map": MAP, "block": BLOCK_MAP, "offset": BLOCK_OFFSET_X},
    {"map": MAP2, "block": BLOCK_MAP2, "offset": BLOCK_OFFSET_X}
]

map_number = 0

def load_map(index):
    global floor, BLOCK_MAP, BLOCK_OFFSET_X, goal_map_x

    data = maps[index]
    floor = [int(c) for line in data["map"].split() for c in line]
    BLOCK_MAP = data["block"]
    BLOCK_OFFSET_X = data["offset"]
    goal_map_x = len(floor) - 5

load_map(map_number)

# =========================================================
# プレイヤー
# =========================================================

camera_x = 0
pl_y = floor_y
pl_yp = 0
pl_jump = False
player_hp = PLAYER_MAX_HP
invincible_timer = 0
INVINCIBLE_TIME = 120
player_attr = "fire"

# =========================================================
# 敵
# =========================================================

enemies = []

def reset_enemies():
    enemies.clear()
    attrs = ["fire", "water", "grass"]
    for i in range(6):
        attr = attrs[i % 3]
        enemies.append({
            "x": 800 + i * 400,
            "hp": ENEMY_MAX_HP,
            "max_hp": ENEMY_MAX_HP,
            "attr": attr
        })

reset_enemies()

# =========================================================
# 攻撃と演出
# =========================================================

attack = False
attack_timer = 0
ATTACK_TIME = 12
hit_enemies = set()

feedback_text = ""
feedback_color = (255, 255, 255)
feedback_timer = 0
hit_stop = 0
flash_timer = 0
flash_type = None
FLASH_TIME = 6

# =========================================================
# 属性相性
# =========================================================

def get_damage(player_attr, enemy_attr):
    if player_attr == enemy_attr:
        return 1
    if player_attr == "fire":
        if enemy_attr == "grass": return 3
        elif enemy_attr == "water": return 0
    elif player_attr == "water":
        if enemy_attr == "fire": return 3
        elif enemy_attr == "grass": return 0
    elif player_attr == "grass":
        if enemy_attr == "water": return 3
        elif enemy_attr == "fire": return 0
    return 1

# =========================================================
# 初期化処理
# =========================================================

def init_game():
    global camera_x, pl_y, pl_yp, pl_jump, player_hp, player_attr, invincible_timer
    camera_x = 0
    pl_y = floor_y
    pl_yp = 0
    pl_jump = False
    player_hp = PLAYER_MAX_HP
    player_attr = "fire"
    invincible_timer = 0
    reset_enemies()

scene = "title"

# =========================================================
# メインループ
# =========================================================

def game_loop():
    global scene, camera_x, pl_y, pl_yp, pl_jump
    global attack, attack_timer, player_hp, player_attr, invincible_timer
    global feedback_text, feedback_color, feedback_timer
    global hit_stop, flash_timer, flash_type, map_number

    running = True
    timer = 0
    prev_attr_detected = False  # 【修正】属性用ペンライトの立ち上がり判定用

    while running:
        timer += 1
        screen.fill((0, 0, 0))

        # ヒットストップ
        if hit_stop > 0:
            hit_stop -= 1
            pygame.display.flip()
            clock.tick(fps)
            continue

        # =================================================
        # カメラコントローラーの更新と画像変換
        # =================================================
        # 【修正】8つの変数を受け取るように初期化
        move_detected, move_pos, action, speed_state = False, (0, 0), "none", "walk"
        attr_detected, attr_element, attr_pos = False, "none", (0, 0)
        debug_frame, cam_surface = None, None
        
        if USE_CAMERA:
            # 【修正】8つの変数を受け取る
            move_detected, move_pos, action, speed_state, attr_detected, attr_element, attr_pos, debug_frame = pen_con.update()

            if debug_frame is not None:
                combined_frame = debug_frame.copy()

                # 背景用の黒い四角形を描画
                cv2.rectangle(combined_frame, (0, 0), (320, 130), (0, 0, 0), -1)

                # --- 攻撃情報 ---
                cv2.putText(combined_frame, "[ATTACK & ELEMENT]", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                if attack:
                    cv2.putText(combined_frame, "ATTACKING!!!", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                # --- 速度情報 ---
                cv2.putText(combined_frame, "[MOVEMENT SPEED]", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                speed_color = (255, 255, 0) if speed_state == "run" else (255, 255, 255)
                cv2.putText(combined_frame, f"SPEED: {speed_state.upper()}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, speed_color, 2)

                # BGR(OpenCV)からRGB(Pygame)に色を変換
                rgb_frame = cv2.cvtColor(combined_frame, cv2.COLOR_BGR2RGB)
                
                # PygameのSurface（画像オブジェクト）に変換
                h, w = rgb_frame.shape[:2]
                cam_surface = pygame.image.frombuffer(rgb_frame.tobytes(), (w, h), 'RGB')

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if scene == "title" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scene = "game"
                init_game()

        keys = pygame.key.get_pressed()

        # =================================================
        # タイトル
        # =================================================
        if scene == "title":
            screen.blit(bg, (0, 0))
            for i in range(300):
                screen.blit(block, (i * size, floor_y + 40))

            ani = (timer // 4) % 4
            screen.blit(player_imgs[ani], player_imgs[ani].get_rect(center=(width // 2, floor_y)))

            overlay = pygame.Surface((width, height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(120)
            screen.blit(overlay, (0, 0))

            title = font_big.render("My Action Game", True, (255, 255, 255))
            screen.blit(title, (width // 2 - 250, height // 2 - 120))

            if (timer // 30) % 2 == 0:
                txt = font_mid.render("Click to Start", True, (200, 200, 200))
                screen.blit(txt, (width // 2 - 150, height // 2 - 40))

        # =================================================
        # ゲーム中
        # =================================================
        elif scene == "game":
            screen.blit(bg, (0, 0))

            # 【修正】属性用変数を参照して属性を更新
            if attr_detected and attr_element in attr_colors:
                player_attr = attr_element

            # 【修正】攻撃判定（属性用ペンライトの立ち上がり検出）
            # 紫の除外ロジックは attr_element には元々含まれないため不要になりました
            if attr_detected and not prev_attr_detected and not attack:
                attack = True
                attack_timer = ATTACK_TIME
                hit_enemies.clear()
                
                if player_attr in sounds:
                    sounds[player_attr].play()

            # 現在の状態を保存
            prev_attr_detected = attr_detected

            # 移動速度の決定
            move_speed = RUN_SPEED if speed_state == "run" else WALK_SPEED
            
            # 【修正】カメラ（移動用ペンライト）での移動操作
            if move_detected:
                if action == "right":
                    camera_x += move_speed
                elif action == "left":
                    camera_x = max(0, camera_x - move_speed)
                elif action == "jump" and not pl_jump:
                    pl_jump = True
                    pl_yp = jump_power

            # キーボード操作
            if keys[pygame.K_RIGHT]:
                camera_x += move_speed
            if keys[pygame.K_LEFT]:
                camera_x = max(0, camera_x - move_speed)
            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            # 重力
            pl_y += pl_yp
            pl_yp += gravity

            if invincible_timer > 0:
                invincible_timer -= 1

            # プレイヤーRect
            player_rect = pygame.Rect(width // 2 - 16, pl_y - 32, 32, 48)
            prev_bottom = player_rect.bottom - pl_yp
            on_block = False

            # 床描画
            for i in range(300):
                screen.blit(block, (i * size - camera_x, floor_y + 40))

            # ブロック処理と描画
            for y, row in enumerate(BLOCK_MAP):
                for x, cell in enumerate(row):
                    if cell == "1":
                        bx = (x + BLOCK_OFFSET_X) * size
                        by = floor_y - (len(BLOCK_MAP) - y) * size
                        screen_x = bx - camera_x

                        block_rect = pygame.Rect(screen_x, by, size, size)

                        if player_rect.colliderect(block_rect):
                            if pl_yp >= 0 and prev_bottom <= block_rect.top:
                                pl_y = block_rect.top
                                pl_yp = 0
                                pl_jump = False
                                on_block = True
                                player_rect.bottom = pl_y

                        screen.blit(block, (screen_x, by))

                        if DEBUG:
                            pygame.draw.rect(screen, (255, 0, 0), block_rect, 2)

            if not on_block and pl_y < floor_y:
                pl_jump = True

            if pl_y >= floor_y:
                pl_y = floor_y
                pl_yp = 0
                pl_jump = False

            if DEBUG:
                pygame.draw.rect(screen, (0, 0, 255), player_rect, 2)
                foot_rect = pygame.Rect(player_rect.x, player_rect.bottom, player_rect.width, 4)
                pygame.draw.rect(screen, (255, 255, 0), foot_rect, 2)

            # 攻撃と敵への当たり判定
            atk_rect = pygame.Rect(width // 2 - 80, pl_y - 80, 160, 100)
            new_enemies = []

            for enemy in enemies:
                ex = enemy["x"]
                screen_x = ex - camera_x
                enemy_rect = pygame.Rect(screen_x, floor_y - 100, 100, 100)

                if attack and attack_timer > 7:
                    if atk_rect.colliderect(enemy_rect):
                        if ex not in hit_enemies:
                            hit_enemies.add(ex)
                            damage = get_damage(player_attr, enemy["attr"])
                            enemy["hp"] -= damage

                            if damage == 3:
                                feedback_text = "CRITICAL!"
                                feedback_color = (255, 255, 0)
                                hit_stop = 10
                                flash_timer = FLASH_TIME
                                flash_type = "white"
                            elif damage == 1:
                                feedback_text = "GOOD"
                                feedback_color = (255, 255, 255)
                                hit_stop = 5
                            else:
                                feedback_text = "BAD..."
                                feedback_color = (255, 100, 180)

                            feedback_timer = 20

                if player_rect.colliderect(enemy_rect):
                    if invincible_timer == 0:
                        player_hp -= 1
                        invincible_timer = INVINCIBLE_TIME
                        hit_stop = 8
                        flash_timer = FLASH_TIME
                        flash_type = "black"

                if enemy["hp"] > 0:
                    new_enemies.append(enemy)

            enemies[:] = new_enemies

            if attack:
                attack_timer -= 1
                if attack_timer <= 0:
                    attack = False

            # プレイヤー描画
            ani = (timer // 4) % 4
            if invincible_timer == 0 or invincible_timer % 10 < 5:
                screen.blit(player_imgs[ani], player_imgs[ani].get_rect(center=(width // 2, pl_y)))

            # 攻撃エフェクト
            if attack and attack_timer > 7:
                color = attr_colors[player_attr]
                surf = pygame.Surface((atk_rect.width, atk_rect.height), pygame.SRCALPHA)
                surf.fill((*color, 120))
                screen.blit(surf, atk_rect.topleft)

            # 敵の描画
            for enemy in enemies:
                screen_x = enemy["x"] - camera_x
                if -120 < screen_x < width:
                    tinted = enemy_base.copy()
                    tinted.fill(attr_colors[enemy["attr"]], special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(tinted, (screen_x, floor_y - 100))

            # プリンセス（ゴール）描画
            princess_x = goal_map_x * size - camera_x - 400
            princess_y = floor_y - 40
            princess_rect = princess.get_rect(center=(princess_x + size // 2, princess_y))
            screen.blit(princess, princess_rect)

            if player_rect.colliderect(princess_rect):
                scene = "clear"

            if DEBUG:
                pygame.draw.rect(screen, (0, 255, 255), princess_rect, 2)

            # HPバー
            pygame.draw.rect(screen, (0, 0, 0), (50, 50, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (50, 50, 200 * (player_hp / PLAYER_MAX_HP), 20))

            # フィードバックテキスト描画
            if feedback_timer > 0:
                feedback_timer -= 1
                txt = font_big.render(feedback_text, True, feedback_color)
                screen.blit(txt, (width // 2 - 180, height // 3))

            # フラッシュ演出
            if flash_timer > 0:
                flash_timer -= 1
                overlay = pygame.Surface((width, height))
                if flash_type == "white":
                    overlay.fill((255, 255, 255))
                elif flash_type == "black":
                    overlay.fill((0, 0, 0))
                overlay.set_alpha(120)
                screen.blit(overlay, (0, 0))

            # マップ切替
            if camera_x > 2000:
                map_number += 1
                if map_number >= len(maps):
                    map_number = 0
                load_map(map_number)
                camera_x = 0
                reset_enemies()

            if player_hp <= 0:
                scene = "gameover"

        # =================================================
        # GAME OVER / CLEAR
        # =================================================
        elif scene == "gameover":
            screen.fill((0, 0, 0))
            screen.blit(font_big.render("GAME OVER", True, (255, 0, 0)), (width // 2 - 220, height // 2 - 100))
            screen.blit(font_mid.render("Press R to Retry", True, (255, 255, 255)), (width // 2 - 150, height // 2))
            if keys[pygame.K_r]:
                init_game()
                scene = "game"

        elif scene == "clear":
            screen.fill((0, 0, 0))
            screen.blit(font_big.render("GAME CLEAR!", True, (255, 255, 0)), (width // 2 - 250, height // 2 - 100))
            screen.blit(font_mid.render("Press R to Retry", True, (255, 255, 255)), (width // 2 - 150, height // 2))
            if keys[pygame.K_r]:
                init_game()
                scene = "game"

        # =================================================
        # カメラ映像の2画面表示（ワイプ統合）
        # =================================================
        if USE_CAMERA and cam_surface is not None:
            CAM_SCALE = 0.45 
            
            cam_w = int(cam_surface.get_width() * CAM_SCALE)
            cam_h = int(cam_surface.get_height() * CAM_SCALE)
            scaled_cam = pygame.transform.scale(cam_surface, (cam_w, cam_h))
            
            cam_x = width - cam_w - 0
            cam_y = 0
            
            screen.blit(scaled_cam, (cam_x, cam_y))
            pygame.draw.rect(screen, (255, 255, 255), (cam_x, cam_y, cam_w, cam_h), 2)

        pygame.display.flip()
        clock.tick(fps)

    pen_con.release()
    pygame.quit()
    sys.exit()

# =========================================================
# 実行
# =========================================================
if __name__ == "__main__":
    game_loop()