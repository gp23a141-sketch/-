import pygame
import sys
import controller
from map_data import MAP,BLOCK_MAP,BLOCK_OFFSET_X

# ===== 基本設定 =====
width, height = 1200, 720
floor_y = 600
size = 24
fps = 60

speed = 10
jump_power = -30
gravity = 3

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# ===== カメラ =====
pen_con = controller.PenlightController(camera_id=0)

# ===== 画像 =====
bg = pygame.image.load("image/bg.png").convert()
block = pygame.image.load("image/block.png").convert_alpha()

player_imgs = [
    pygame.image.load("image/player0.png").convert_alpha(),
    pygame.image.load("image/player1.png").convert_alpha(),
    pygame.image.load("image/player0.png").convert_alpha(),
    pygame.image.load("image/player2.png").convert_alpha(),
]

enemy_base = pygame.image.load("image/devil.png").convert_alpha()
enemy_base = pygame.transform.scale(enemy_base, (100, 100))

# ===== マップ =====
floor = [int(c) for line in MAP.split() for c in line]

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
        enemies.append([800 + i * 400, 3, attr])

reset_enemies()

# ===== 攻撃 =====
attack = False
attack_timer = 0
ATTACK_TIME = 12
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

# ===== メイン =====
def game_loop():
    global pl_y, pl_yp, pl_jump, camera_x
    global attack, attack_timer, prev_detected
    global player_hp, invincible_timer
    global player_attr
    global critical_timer, hit_stop
    global flash_timer, flash_type

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

        # ===== カメラ =====
        if timer % 2 == 0:
            is_detected, _, element, _ = pen_con.update()
        else:
            is_detected = False
            element = "none"

        if element in ["fire", "water", "grass"]:
            player_attr = element

        if is_detected and not prev_detected:
            attack = True
            attack_timer = ATTACK_TIME

        prev_detected = is_detected

        # ===== イベント =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ===== 入力 =====
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            camera_x += speed
        if keys[pygame.K_LEFT]:
            camera_x = max(0, camera_x - speed)

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
        atk_rect = pygame.Rect(width//2 + 40, pl_y - 40, 80, 80)
        player_rect = pygame.Rect(width//2-16, pl_y-48, 32, 48)

        new_enemies = []

        for ex, hp, attr in enemies:
            screen_x = ex - camera_x
            enemy_rect = pygame.Rect(screen_x, floor_y-100, 100, 100)

            # 攻撃ヒット
            if attack and attack_timer == ATTACK_TIME - 2:
                if atk_rect.colliderect(enemy_rect):
                    damage = get_damage(player_attr, attr)
                    hp -= damage

                    if damage == 3:
                        critical_timer = CRITICAL_TIME
                        hit_stop = 10

                        flash_timer = FLASH_TIME
                        flash_type = "white"
                    else:
                        hit_stop = 5

            # 被ダメ
            if player_rect.colliderect(enemy_rect):
                if invincible_timer == 0:
                    player_hp -= 1
                    invincible_timer = INVINCIBLE_TIME
                    hit_stop = 8

                    flash_timer = FLASH_TIME
                    flash_type = "black"

            if hp > 0:
                new_enemies.append([ex, hp, attr])

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
        ani = int(timer / 3) % 4
        screen.blit(
            player_imgs[ani],
            player_imgs[ani].get_rect(center=(width // 2, pl_y))
        )
        pygame.draw.rect(screen, (0, 0, 255), player_rect, 2)
        foot_rect = pygame.Rect(player_rect.x, player_rect.bottom, player_rect.width, 2)
        pygame.draw.rect(screen, (255, 255, 0), foot_rect, 2)

        # 攻撃エフェクト
        if attack:
            pygame.draw.rect(screen, attr_colors[player_attr], atk_rect, 3)

        # 敵
        for ex, hp, attr in enemies:
            screen_x = ex - camera_x

            if -120 < screen_x < width:
                tinted = enemy_base.copy()
                tinted.fill(attr_colors[attr], special_flags=pygame.BLEND_RGBA_MULT)

                screen.blit(tinted, (screen_x, floor_y-100))

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

        # GAME OVER
        if player_hp <= 0:
            font = pygame.font.Font(None, 100)
            text = font.render("GAME OVER", True, (255,0,0))
            screen.blit(text, (width//2 - 250, height//2 - 50))

        pygame.display.flip()
        clock.tick(fps)

    pen_con.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()