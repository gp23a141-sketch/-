import pygame
import sys
import cv2
import controller
from map_data import MAP, BLOCK_MAP, BLOCK_OFFSET_X

# ===== 基本設定 =====
width, height = 1200, 720
floor_y = 600
size = 24
fps = 30

speed = 12
jump_power = -60
gravity = 6

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Jump Action Game - Camera Sword")
clock = pygame.time.Clock()

# ===== ペンライトコントローラー初期化 =====
pen_con = controller.PenlightController(camera_id=0)

# ===== 画像読み込み =====
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

# ===== マップ初期化 =====
floor = [int(c) for line in MAP.split() for c in line]
goal_map_x = len(floor) - 3

BLOCK_H = len(BLOCK_MAP)
BLOCK_W = len(BLOCK_MAP[0])

# ===== プレイヤー状態 =====
camera_x = 0
pl_x = width // 2
pl_y = floor_y
pl_yp = 0
pl_jump = False

# ===== 攻撃関連 =====
attack = False
attack_timer = 0
ATTACK_TIME = 10

# 剣属性（カメラで変更）
sword_color = "RED"

scene = "タイトル"
timer = 0

prev_detected = False  # 立ち上がり検出用


# ===== テキスト描画 =====
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


def on_block_top(px, py, vy):
    tx = int(px // size) - BLOCK_OFFSET_X
    if 0 <= tx < BLOCK_W:
        for by in range(BLOCK_H):
            if BLOCK_MAP[by][tx] == "1":
                block_y = floor_y - (BLOCK_H - by) * size
                if py <= block_y and py >= block_y - abs(vy) - 2:
                    return block_y
    return None


# ===== メインループ =====
def game_loop():
    global scene, pl_x, pl_y, pl_yp, pl_jump
    global camera_x, timer
    global attack, attack_timer
    global sword_color, prev_detected

    bg_w = bg.get_width()
    running = True

    while running:
        # ==========================
        # カメラ認識
        # ==========================
        is_detected, pos, element, debug_frame = pen_con.update()

        # カメラデバッグ画面表示
        if debug_frame is not None:
            cv2.imshow("Camera Debug", debug_frame)
            cv2.waitKey(1)

        # 属性変換
        if element == "fire":
            sword_color = "RED"
        elif element == "water":
            sword_color = "BLUE"
        elif element == "grass":
            sword_color = "GREEN"

        # 立ち上がり検出で攻撃
        if is_detected and not prev_detected and not attack:
            attack = True
            attack_timer = ATTACK_TIME

        prev_detected = is_detected

        # -------- イベント --------
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

        timer += 1

        # -------- ゲーム処理 --------
        if scene == "ゲーム":

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                camera_x += speed
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                camera_x = max(0, camera_x - speed)

            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            pl_x = camera_x + width // 2

            # 重力
            pl_y += pl_yp
            pl_yp += gravity

            # 足場判定
            by = on_block_top(pl_x, pl_y, pl_yp)
            if by is not None:
                pl_y = by
                pl_yp = 0
                pl_jump = False
            elif pl_y >= floor_y:
                pl_y = floor_y
                pl_yp = 0
                pl_jump = False

            # 攻撃中
            if attack:
                attack_timer -= 1
                if attack_timer <= 0:
                    attack = False

            # 落下
            if pl_y > floor_y + 200:
                scene = "ゲームオーバー"
                timer = 0

            # ゴール
            if abs(pl_x - goal_map_x * size) < size:
                scene = "クリア"
                timer = 0

        elif scene in ["ゲームオーバー", "クリア"]:
            if timer > 150:
                scene = "タイトル"

        # ==========================
        # 描画
        # ==========================
        start_x = -(camera_x % bg_w)
        x = start_x
        while x < width:
            screen.blit(bg, (x, 0))
            x += bg_w

        # 地面
        first_map = int(camera_x // size)
        for i in range(width // size + 2):
            map_i = first_map + i
            if map_i < len(floor) and floor[map_i] == 1:
                screen.blit(block, (map_i * size - camera_x, floor_y + 40))

        # 空中ブロック
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