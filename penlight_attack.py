import pygame
import sys
import cv2
import controller_speed  # 必ず最新の controller_speed.py と同じフォルダに置くこと
from map_data import MAP, BLOCK_MAP, BLOCK_OFFSET_X

# 基本設定 
width, height = 1200, 720
floor_y = 600
size = 24
fps = 30
PLAYER_W = 32
PLAYER_H = 48

# === 戦闘システムの設定 ===
PLAYER_BASE_ATTACK = 50  # プレイヤーの基本攻撃力
ENEMY_MAX_HP = 200       # 敵の最大HP

# 移動速度の設定 
WALK_SPEED = 12
RUN_SPEED = 24  # 走っているときの速度（歩きの2倍）
jump_power = -35
gravity = 4

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Jump Action Game - Camera Sword")
clock = pygame.time.Clock()

# ペンライトコントローラー初期化
pen_con = controller_speed.PenlightController(camera_id=0)

# 画像読み込み 
bg = pygame.image.load("image/bg.png").convert()
block = pygame.image.load("image/block.png").convert_alpha()
princess = pygame.image.load("image/princess.png").convert_alpha()

player_imgs = [
    pygame.image.load("image/player0.png").convert_alpha(),
    pygame.image.load("image/player1.png").convert_alpha(),
    pygame.image.load("image/player0.png").convert_alpha(),
    pygame.image.load("image/player2.png").convert_alpha(),
]

font_large = pygame.font.Font(None, 60)
font_medium = pygame.font.Font(None, 40)

# マップ初期化
floor = [int(c) for line in MAP.split() for c in line]
goal_map_x = len(floor) - 3

BLOCK_H = len(BLOCK_MAP)
BLOCK_W = len(BLOCK_MAP[0])

# プレイヤー状態
camera_x = 0
pl_x = width // 2
pl_y = floor_y
pl_yp = 0
pl_jump = False
current_speed = WALK_SPEED

# 攻撃関連
attack = False
attack_timer = 0
ATTACK_TIME = 10
sword_color = "RED"

scene = "タイトル"
timer = 0
prev_detected = False

# テキスト描画関数
def render_text(surface, x, y, txt, font, color):
    surf = font.render(txt, True, color)
    rect = surf.get_rect(center=(x, y))
    surface.blit(surf, rect.topleft)

def get_sword_rgb(color_name):
    if color_name == "RED":
        return (255, 0, 0)
    elif color_name == "GREEN":
        return (0, 255, 0)
    elif color_name == "BLUE":
        return (0, 0, 255)
    return (255, 255, 255)

# 三すくみのダメージ倍率計算
def get_damage_multiplier(player_color, enemy_color):
    """
    属性の相性に応じてダメージ倍率を返す
    火(RED) > 木(GREEN) > 水(BLUE) > 火(RED)
    """
    if player_color == enemy_color:
        return 1.0  # 同じ属性なら等倍

    if player_color == "RED":
        return 2.0 if enemy_color == "GREEN" else 0.5
    elif player_color == "BLUE":
        return 2.0 if enemy_color == "RED" else 0.5
    elif player_color == "GREEN":
        return 2.0 if enemy_color == "BLUE" else 0.5

    return 1.0

# ブロック衝突判定
def check_block_collision():
    global pl_y, pl_yp, pl_jump, camera_x, current_speed

    player_rect = pygame.Rect(
        pl_x - PLAYER_W//2,
        pl_y - PLAYER_H,
        PLAYER_W,
        PLAYER_H
    )

    for by in range(BLOCK_H):
        for bx in range(BLOCK_W):
            if BLOCK_MAP[by][bx] != "1":
                continue

            world_x = (bx + BLOCK_OFFSET_X) * size
            world_y = floor_y - (BLOCK_H - by) * size

            block_rect = pygame.Rect(world_x, world_y, size, size)

            if player_rect.colliderect(block_rect):
                if pl_yp >= 0 and player_rect.bottom <= block_rect.top + 10:
                    pl_y = block_rect.top
                    pl_yp = 0
                    pl_jump = False
                elif pl_yp < 0 and player_rect.top >= block_rect.bottom - 10:
                    pl_yp = 0
                else:
                    if player_rect.centerx < block_rect.centerx:
                        camera_x -= current_speed
                    else:
                        camera_x += current_speed

# メインループ
def game_loop():
    global scene, pl_x, pl_y, pl_yp, pl_jump
    global camera_x, timer, current_speed
    global attack, attack_timer
    global sword_color, prev_detected

    bg_w = bg.get_width()
    running = True

    # 敵の配置（テスト用）
    enemies = [
        {"x": 600, "y": floor_y, "hp": ENEMY_MAX_HP, "element": "GREEN", "alive": True},
        {"x": 1200, "y": floor_y, "hp": ENEMY_MAX_HP, "element": "RED", "alive": True},
        {"x": 1800, "y": floor_y, "hp": ENEMY_MAX_HP, "element": "BLUE", "alive": True}
    ]

    # UIフィードバック用の変数
    feedback_text = ""
    feedback_color = (255, 255, 255)
    feedback_timer = 0
    FEEDBACK_DURATION = 20  # 画面に文字を表示するフレーム数（約0.6秒）

    while running:
        
        is_detected, pos, element, action, speed_state, debug_frame = pen_con.update()

        if debug_frame is not None:
            attack_frame = debug_frame.copy()
            speed_frame = debug_frame.copy()

            cv2.rectangle(attack_frame, (0, 0), (280, 40), (0, 0, 0), -1)
            cv2.putText(attack_frame, "--- ATTACK & ELEMENT ---", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            if attack:
                cv2.putText(attack_frame, "ATTACKING!!!", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

            cv2.rectangle(speed_frame, (0, 0), (280, 40), (0, 0, 0), -1)
            cv2.putText(speed_frame, "--- MOVEMENT SPEED ---", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(speed_frame, f"CURRENT SPEED: {speed_state.upper()}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0) if speed_state == "run" else (255, 255, 255), 3)

            cv2.imshow("Camera Debug: ATTACK", attack_frame)
            cv2.imshow("Camera Debug: SPEED", speed_frame)
            cv2.waitKey(1)

        # 属性変換
        if element == "fire":
            sword_color = "RED"
        elif element == "water":
            sword_color = "BLUE"
        elif element == "grass":
            sword_color = "GREEN"

        # 立ち上がり検出で攻撃
        just_attacked = False
        if is_detected and not prev_detected and not attack and element != "purple":
            attack = True
            attack_timer = ATTACK_TIME
            just_attacked = True

        prev_detected = is_detected

        current_speed = RUN_SPEED if speed_state == "run" else WALK_SPEED

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scene == "タイトル":
                    camera_x = 0
                    pl_y = floor_y
                    pl_yp = 0
                    pl_jump = False
                    attack = False
                    scene = "ゲーム"
                    timer = 0
                    feedback_timer = 0
                    # ゲーム開始時に敵を復活させる
                    for e in enemies:
                        e["hp"] = ENEMY_MAX_HP
                        e["alive"] = True

        timer += 1

        # フィードバック表示のタイマーを減らす
        if feedback_timer > 0:
            feedback_timer -= 1

        # ゲーム処理
        if scene == "ゲーム":

            if is_detected and element == "purple":
                if action == "right":
                    camera_x += current_speed
                elif action == "left":
                    camera_x = max(0, camera_x - current_speed)
                elif action == "jump" and not pl_jump:
                    pl_jump = True
                    pl_yp = jump_power

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                camera_x += current_speed
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                camera_x = max(0, camera_x - current_speed)
            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            max_camera = goal_map_x * size - width // 2
            camera_x = min(camera_x, max_camera)

            pl_x = camera_x + width // 2

            pl_y += pl_yp
            pl_yp += gravity

            check_block_collision()
            if pl_y >= floor_y:
                pl_y = floor_y
                pl_yp = 0
                pl_jump = False

            # 攻撃の当たり判定とダメージ処理
            if just_attacked:
                attack_world_rect = pygame.Rect(pl_x, pl_y - PLAYER_H, 80, PLAYER_H)

                for enemy in enemies:
                    if not enemy["alive"]:
                        continue

                    enemy_world_rect = pygame.Rect(enemy["x"] - 20, enemy["y"] - 40, 40, 40)

                    if attack_world_rect.colliderect(enemy_world_rect):
                        multiplier = get_damage_multiplier(sword_color, enemy["element"])
                        damage = int(PLAYER_BASE_ATTACK * multiplier)
                        enemy["hp"] -= damage

                        # 倍率に応じたフィードバックの設定
                        if multiplier == 2.0:
                            feedback_text = "CRITICAL!"
                            feedback_color = (255, 255, 0)    # 黄色
                        elif multiplier == 1.0:
                            feedback_text = "GOOD"
                            feedback_color = (255, 255, 255)  # 白
                        elif multiplier == 0.5:
                            feedback_text = "BAD..."
                            feedback_color = (255, 105, 180)  # ピンク

                        feedback_timer = FEEDBACK_DURATION

                        if enemy["hp"] <= 0:
                            enemy["alive"] = False

            # 攻撃タイマー
            if attack:
                attack_timer -= 1
                if attack_timer <= 0:
                    attack = False

            if pl_y > floor_y + 200:
                scene = "ゲームオーバー"
                timer = 0

            if abs(pl_x - goal_map_x * size) < size:
                scene = "クリア"
                timer = 0

        elif scene in ["ゲームオーバー", "クリア"]:
            if timer > 150:
                scene = "タイトル"

        # 描画処理
        start_x = -(camera_x % bg_w)
        x = start_x
        while x < width:
            screen.blit(bg, (x, 0))
            x += bg_w

        first_map = int(camera_x // size)
        for i in range(width // size + 2):
            map_i = first_map + i
            if map_i < len(floor) and floor[map_i] == 1:
                screen.blit(block, (map_i * size - camera_x, floor_y + 40))

        for y in range(BLOCK_H):
            for x in range(BLOCK_W):
                if BLOCK_MAP[y][x] == "1":
                    world_x = (x + BLOCK_OFFSET_X) * size
                    world_y = floor_y - (BLOCK_H - y) * size
                    screen.blit(block, (world_x - camera_x, world_y))

        # ゴール
        princess_x = goal_map_x * size - camera_x
        screen.blit(
            princess,
            princess.get_rect(center=(princess_x + size // 2, floor_y - 40))
        )

        # 敵とHPバーの描画
        for enemy in enemies:
            if enemy["alive"]:
                ex = enemy["x"] - camera_x
                ey = enemy["y"] - 40
                
                enemy_rect = pygame.Rect(ex - 20, ey, 40, 40)
                pygame.draw.rect(screen, get_sword_rgb(enemy["element"]), enemy_rect)
                
                hp_ratio = max(0, enemy["hp"] / ENEMY_MAX_HP)
                pygame.draw.rect(screen, (255, 0, 0), (ex - 20, ey - 15, 40, 5))
                pygame.draw.rect(screen, (0, 255, 0), (ex - 20, ey - 15, int(40 * hp_ratio), 5))

        # プレイヤー
        ani = int(timer / 3) % 4
        screen.blit(
            player_imgs[ani],
            player_imgs[ani].get_rect(center=(width // 2, pl_y))
        )

        # 攻撃エフェクト
        if attack:
            sword_rgb = get_sword_rgb(sword_color)
            attack_rect = pygame.Rect(width // 2 + 20, pl_y - 20, 60, 60)
            pygame.draw.rect(screen, sword_rgb, attack_rect, 4)

        # フィードバックテキストの描画
        if scene == "ゲーム" and feedback_timer > 0:
            # 画面中央より少し上（高さの約1/3の位置）に描画して視認性を確保
            render_text(screen, width // 2, height // 3, feedback_text, font_large, feedback_color)

        # タイトルUI
        if scene == "タイトル":
            render_text(screen, width // 2, height * 0.4,
                        "Jump Action Game", font_large, (255, 215, 0))
            render_text(screen, width // 2, height * 0.6,
                        "Click to Start", font_medium, (200, 200, 255))

        pygame.display.flip()
        clock.tick(fps)

    pen_con.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()