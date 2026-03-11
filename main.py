import pygame
import sys
from map_data import MAP, BLOCK_MAP, BLOCK_OFFSET_X

# 基本設定
width, height = 1200, 720
floor_y = 600
size = 24
fps = 30
PLAYER_W = 32
PLAYER_H = 48

speed = 12
jump_power = -35
gravity = 4
PLAYER_W = 32
PLAYER_H = 48

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("jump action game")
clock = pygame.time.Clock()

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

# 攻撃関連
attack = False
attack_timer = 0
ATTACK_TIME = 10

attack_gauge = 0
ATTACK_THRESHOLD = 120

# 剣の色（将来：画像認識から上書き）
sword_color = "RED"   # "RED", "GREEN", "BLUE"

scene = "タイトル"
timer = 0

# 関数
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


def check_block_collision():

    global pl_y, pl_yp, pl_jump, camera_x

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

                # 上から着地
                if pl_yp >= 0 and player_rect.bottom <= block_rect.top + 10:

                    pl_y = block_rect.top
                    pl_yp = 0
                    pl_jump = False

                # 下から頭ぶつけ
                elif pl_yp < 0 and player_rect.top >= block_rect.bottom - 10:

                    pl_yp = 0

                # 横衝突
                else:

                    if player_rect.centerx < block_rect.centerx:
                        camera_x -= speed
                    else:
                        camera_x += speed

# メインループ
def game_loop():
    global scene, pl_x, pl_y, pl_yp, pl_jump
    global camera_x, timer
    global attack, attack_timer, attack_gauge
    global sword_color

    bg_w = bg.get_width()
    running = True

    while running:
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
                    attack_gauge = 0
                    scene = "ゲーム"
                    timer = 0

        timer += 1

        # -------- ゲーム処理 --------
        if scene == "ゲーム":
            keys = pygame.key.get_pressed()

            # 移動
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                camera_x += speed
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                camera_x = max(0, camera_x - speed)
                max_camera = goal_map_x * size - width // 2
                camera_x = min(camera_x, max_camera)

            # ジャンプ
            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            # デバッグ用：剣の色切り替え
            if keys[pygame.K_1]:
                sword_color = "RED"
            if keys[pygame.K_2]:
                sword_color = "GREEN"
            if keys[pygame.K_3]:
                sword_color = "BLUE"

            pl_x = camera_x + width // 2

            # 重力
            pl_y += pl_yp
            pl_yp += gravity

            # 足場判定
            check_block_collision()
            if pl_y >= floor_y:
                pl_y = floor_y
                pl_yp = 0
                pl_jump = False

            # 攻撃ゲージ増加
            if not attack:
                attack_gauge += 1

            # 閾値で自動攻撃
            if attack_gauge >= ATTACK_THRESHOLD and not attack:
                attack = True
                attack_timer = ATTACK_TIME
                attack_gauge = 0

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

    # 描画
        # 背景
        start_x = -(camera_x % bg.get_width())
        x = start_x
        while x < width:
            screen.blit(bg, (x, 0))
            x += bg.get_width()

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

        # 攻撃（剣の色反映）
        if attack:
            sword_rgb = get_sword_rgb(sword_color)
            attack_rect = pygame.Rect(width // 2 + 20, pl_y - 20, 40, 40)
            pygame.draw.rect(screen, sword_rgb, attack_rect, 3)

        # 攻撃ゲージUI
        pygame.draw.rect(screen, (255, 255, 255), (50, 50, 200, 20), 2)
        gauge_w = int(200 * min(attack_gauge / ATTACK_THRESHOLD, 1))
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, gauge_w, 20))

        # タイトルUI
        if scene == "タイトル":
            render_text(screen, width // 2, height * 0.4,
                        "jump action game", font_large, (255, 215, 0))
            render_text(screen, width // 2, height * 0.6,
                        "click to start", font_medium, (200, 200, 255))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
