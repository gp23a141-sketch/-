import pygame
import sys
import os
import controller
from map_data import MAP,BLOCK_MAP,BLOCK_OFFSET_X,MAP2,BLOCK_MAP2

# ===== 設定 =====
USE_CAMERA = True
DEBUG = False

# ===== パス =====
BASE_DIR = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
IMAGE_DIR = os.path.join(BASE_DIR, "image")

# ===== 基本設定 =====
width, height = 1200, 720
floor_y = 600
size = 24
fps = 60

speed = 10
jump_power = -28
gravity = 2

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# ===== フォント =====
font_big = pygame.font.SysFont(None, 80)
font_mid = pygame.font.SysFont(None, 40)
font_fps = pygame.font.SysFont(None, 30)

# ===== BGM =====
pygame.mixer.music.load(os.path.join(SOUND_DIR, "bgm.wav"))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# ===== SE =====
sounds = {
    "fire": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_fire.wav")),
    "water": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_water.wav")),
    "grass": pygame.mixer.Sound(os.path.join(SOUND_DIR, "slash_grass.wav")),
}

# ===== カメラ =====
pen_con = controller.PenlightController(camera_id=0)
last_element = "none"
detected = False

# ===== 画像 =====
bg = pygame.image.load(os.path.join(IMAGE_DIR, "bg.png")).convert()
block = pygame.image.load(os.path.join(IMAGE_DIR, "block.png")).convert_alpha()

player_imgs = [
    pygame.image.load(os.path.join(IMAGE_DIR, "player0.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMAGE_DIR, "player1.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMAGE_DIR, "player0.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMAGE_DIR, "player2.png")).convert_alpha(),
]

enemy_base = pygame.image.load(os.path.join(IMAGE_DIR, "devil.png")).convert_alpha()
enemy_base = pygame.transform.scale(enemy_base, (100, 100))

# ===== 色 =====
attr_colors = {
    "fire": (255, 80, 80),
    "water": (80, 120, 255),
    "grass": (80, 255, 120)
}

# ===== マップ =====
maps = [
    {
        "map": MAP,
        "block": BLOCK_MAP,
        "offset": BLOCK_OFFSET_X
    },
    {
        "map": MAP2,
        "block": BLOCK_MAP2,
        "offset": BLOCK_OFFSET_X
    }
]
map_number = 0
def load_map(index):
    global floor, BLOCK_MAP, BLOCK_OFFSET_X

    data = maps[index]
    floor = [int(c) for line in data["map"].split() for c in line]
    BLOCK_MAP = data["block"]
    BLOCK_OFFSET_X = data["offset"]
load_map(map_number)

# ===== プレイヤー =====
camera_x = 0
pl_y = floor_y
pl_yp = 0
pl_jump = False

PLAYER_MAX_HP = 5
player_hp = PLAYER_MAX_HP

invincible_timer = 0
INVINCIBLE_TIME = 180

player_attr = "fire"

# ===== 敵 =====
enemies = []

def reset_enemies():
    enemies.clear()
    attrs = ["fire", "water", "grass"]
    for i in range(6):
        attr = attrs[i % 3]
        enemies.append([800 + i * 400, 3, 3, attr])

reset_enemies()

# ===== 攻撃 =====
attack = False
attack_timer = 0
ATTACK_TIME = 12
hit_enemies = set()
prev_detected = False

# ===== 演出 =====
critical_timer = 0
CRITICAL_TIME = 30

hit_stop = 0

# フラッシュ
flash_timer = 0
flash_type = None  # "white" or "black"
FLASH_TIME = 6

# ===== 色 =====
attr_colors = {
    "fire": (255, 80, 80),
    "water": (80, 120, 255),
    "grass": (80, 255, 120)
}

# ===== 属性相性 =====
def get_damage(player_attr, enemy_attr):
    if player_attr == "fire":
        if enemy_attr == "grass":
            return 3
        elif enemy_attr == "water":
            return 0
    elif player_attr == "water":
        if enemy_attr == "fire":
            return 3
        elif enemy_attr == "grass":
            return 0
    elif player_attr == "grass":
        if enemy_attr == "water":
            return 3
        elif enemy_attr == "fire":
            return 0
    return 1

# ===== 初期化 =====
def init_game():
    global camera_x, pl_y, pl_yp, pl_jump
    global player_hp, invincible, player_attr, enemies

    camera_x = 0
    pl_y = floor_y
    pl_yp = 0
    pl_jump = False

    player_hp = 5
    invincible = 0
    player_attr = "fire"

    reset_enemies()

scene = "title"

# ===== メイン =====
def game_loop():
    global scene, pl_y, pl_yp, pl_jump, camera_x
    global attack, attack_timer, prev_detected, last_element
    global player_hp, invincible_timer
    global player_attr
    global critical_timer, hit_stop
    global flash_timer, flash_type
    global map_number

    running = True
    timer = 0

    while running:
        timer += 1

        # ===== ヒットストップ =====
        if hit_stop > 0:
            hit_stop -= 1
            pygame.display.flip()
            clock.tick(fps)
            continue

        # ===== イベント =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if scene == "title" and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    scene = "game"
                    camera_x = 0  # ← スタート時リセット
        
        # ===== 入力 =====
        keys = pygame.key.get_pressed()
        
        # ===== タイトル =====
        if scene == "title":
            screen.blit(bg, (0, 0))

            camera_x += 1  # ← スクロール

            start = int(camera_x // size)
            end = start + width // size + 2

            # 地面
            for i in range(start, end):
                screen.blit(block, (i * size - camera_x, floor_y + 40))

            # プレイヤー
            ani = (timer // 4) % 4
            screen.blit(player_imgs[ani],
                        player_imgs[ani].get_rect(center=(width//2, floor_y)))

            # 暗幕
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # タイトル文字
            screen.blit(font_big.render("My Action Game", True, (255,255,255)),
                        (width//2-250, height//2-120))

            if (timer // 30) % 2 == 0:
                screen.blit(font_mid.render("Click to Start", True, (200,200,200)),
                            (width//2-150, height//2-40))
        
        # ===== ゲーム =====
        elif scene == "game":

            # カメラ入力
            if USE_CAMERA and timer % 8 == 0:
                d, _, element, _ = pen_con.update()
                if element != last_element:
                    last_element = element
                    detected = d
                else:
                    detected = False
            else:
                detected = False

            if last_element in attr_colors:
                player_attr = last_element
            
            # 攻撃
            if detected and not attack:
                attack = True
                attack_timer = 12
                hit_enemies.clear()
                sounds[player_attr].play()

            move_speed = speed * 2 if keys[pygame.K_LSHIFT] else speed
            
            if keys[pygame.K_RIGHT]:
                camera_x += move_speed
            if keys[pygame.K_LEFT]:
                camera_x = max(0, camera_x - move_speed)

            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            # ===== 重力 =====
            pl_y += pl_yp
            pl_yp += gravity

            if pl_y >= floor_y:
                pl_y = floor_y
                pl_yp = 0
                pl_jump = False

            # ===== 無敵 =====
            if invincible_timer > 0:
                invincible_timer -= 1

            # ===== 判定 =====
            atk_rect = pygame.Rect(width//2-80, pl_y-80, 160, 100)
            player_rect = pygame.Rect(width//2-16, pl_y-48, 32, 48)

            new_enemies = []

            for ex, hp, max_hp, attr in enemies:
                screen_x = ex - camera_x
                enemy_rect = pygame.Rect(screen_x, floor_y-100, 100, 100)

                # 攻撃ヒット
                if attack and attack_timer > 7:
                    if atk_rect.colliderect(enemy_rect):
                        if ex not in hit_enemies:
                            hit_enemies.add(ex)
                            damage = get_damage(player_attr, attr)
                            hp -= damage

                            if damage == 3:
                                critical_timer = CRITICAL_TIME
                                hit_stop = 10

                                flash_timer = FLASH_TIME
                                flash_type = "white"
                            else:
                                hit_stop = 5
                            sounds[player_attr].play()

                # 被ダメ
                if player_rect.colliderect(enemy_rect):
                    if invincible_timer == 0:
                        player_hp -= 1
                        invincible_timer = INVINCIBLE_TIME
                        hit_stop = 8

                        flash_timer = FLASH_TIME
                        flash_type = "black"

                if hp > 0:
                    new_enemies.append([ex, hp, max_hp, attr])

            enemies[:] = new_enemies

            # ===== 攻撃時間 =====
            if attack:
                attack_timer -= 1
                if attack_timer <= 0:
                    attack = False

            # ===== 描画 =====
            screen.fill((0, 0, 0))
            screen.blit(bg, (0, 0))

            # 床
            if enemies:
                max_enemy_x = max(e[0] for e in enemies)
            else:
                max_enemy_x = camera_x + width

            end_tile = int(max_enemy_x // size) + 20

            for i in range(end_tile):
                screen.blit(block, (i * size - camera_x, floor_y + 40))
            player_rect = pygame.Rect(width//2-16, pl_y-24, 32, 48)

            if camera_x > 2000:  # 適当な終点
                map_number += 1

                if map_number >= len(maps):
                    map_number = 0  # ループさせる場合

                load_map(map_number)

                camera_x = 0
                reset_enemies()
            for y, row in enumerate(BLOCK_MAP):
                for x, cell in enumerate(row):
                    if cell == "1":
                        bx = (x + BLOCK_OFFSET_X) * size
                        by = floor_y - (len(BLOCK_MAP) - y) * size

                        screen_x = bx - camera_x
                        block_rect = pygame.Rect(screen_x, by, size, size)

                        # 当たり判定
                        if player_rect.colliderect(block_rect):
                            if pl_yp > 0 and player_rect.bottom <= block_rect.top + 40:
                                pl_y = by
                                pl_yp = 0
                                pl_jump = False

                        # 描画
                        screen.blit(block, (screen_x, by))

                        # ★可視化（デバッグ）
                        pygame.draw.rect(screen, (255, 0, 0), block_rect, 2)
            # プレイヤー
                        ani = (timer // 4) % 4
            if invincible_timer == 0 or invincible_timer % 10 < 5:
                screen.blit(player_imgs[ani],
                            player_imgs[ani].get_rect(center=(width//2, pl_y)))
            pygame.draw.rect(screen, (0, 0, 255), player_rect, 2)
            foot_rect = pygame.Rect(player_rect.x, player_rect.bottom, player_rect.width, 2)
            pygame.draw.rect(screen, (255, 255, 0), foot_rect, 2)

            # 攻撃エフェクト
            if attack and attack_timer > 7:
                color = attr_colors[player_attr]

                surf = pygame.Surface((atk_rect.width, atk_rect.height), pygame.SRCALPHA)
                surf.fill((*color, 120))
                screen.blit(surf, atk_rect.topleft)

                pygame.draw.rect(screen, color, atk_rect, 2)

            # 敵
            for ex, hp, max_hp, attr in enemies:
                screen_x = ex - camera_x

                if -120 < screen_x < width:
                    tinted = enemy_base.copy()
                    tinted.fill(attr_colors[attr], special_flags=pygame.BLEND_RGBA_MULT)

                    screen.blit(tinted, (screen_x, floor_y-100))

                    bar_w = 100
                    hp_ratio = hp / max_hp
                    pygame.draw.rect(screen, (0,0,0),
                        (screen_x, floor_y-115, 100, 10))
                    pygame.draw.rect(screen, attr_colors[attr],
                        (screen_x, floor_y-115, 100*(hp/3), 10))

            # プレイヤーHP
            pygame.draw.rect(screen, (0,0,0), (50,50,200,20))
            pygame.draw.rect(screen, (0,255,0),
                (50,50,200*(player_hp/PLAYER_MAX_HP),20))

            # CRITICAL表示
            if critical_timer > 0:
                font = pygame.font.Font(None, 80)
                text = font.render("CRITICAL!", True, (255,255,0))
                y_offset = -120 + (CRITICAL_TIME - critical_timer) * 2
                screen.blit(text, (width//2 - 180, pl_y + y_offset))
                critical_timer -= 1

            # ===== フラッシュ演出 =====
            if flash_timer > 0:
                flash_timer -= 1
                overlay = pygame.Surface((width, height))

                if flash_type == "white":
                    overlay.fill((255, 255, 255))
                elif flash_type == "black":
                    overlay.fill((0, 0, 0))

                overlay.set_alpha(120)
                screen.blit(overlay, (0, 0))

            if player_hp <= 0:
                scene = "gameover"
            
        # ===== ゲームオーバー =====
        elif scene == "gameover":
            screen.fill((0,0,0))
            screen.blit(font_big.render("GAME OVER", True, (255,0,0)),
                        (width//2-200, height//2-100))
            screen.blit(font_mid.render("Press R to Retry", True, (200,200,200)),
                        (width//2-150, height//2))

            if keys[pygame.K_r]:
                init_game()
                scene = "game"

        pygame.display.flip()
        clock.tick(fps)

    pen_con.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()