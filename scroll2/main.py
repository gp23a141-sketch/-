import pygame
import sys

from settings import *
from assets import *
from map_data import (
    MAP,
    BLOCK_MAP,
    BLOCK_OFFSET_X,
    MAP2,
    BLOCK_MAP2
)

# =========================================================
# マップ
# =========================================================

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

    global floor
    global BLOCK_MAP
    global BLOCK_OFFSET_X
    global goal_map_x

    data = maps[index]

    floor = [
        int(c)
        for line in data["map"].split()
        for c in line
    ]

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
# 攻撃
# =========================================================

attack = False
attack_timer = 0

ATTACK_TIME = 12

hit_enemies = set()

# =========================================================
# 演出
# =========================================================

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

# =========================================================
# 初期化
# =========================================================

def init_game():

    global camera_x
    global pl_y
    global pl_yp
    global pl_jump

    global player_hp
    global player_attr
    global invincible_timer
    global time_left

    time_left = TIME_LIMIT

    camera_x = 0

    pl_y = floor_y
    pl_yp = 0
    pl_jump = False

    player_hp = PLAYER_MAX_HP
    player_attr = "fire"

    invincible_timer = 0

    reset_enemies()

# =========================================================
# シーン
# =========================================================

scene = "title"

# =========================================================
# メイン
# =========================================================

def game_loop():

    global scene

    global camera_x

    global pl_y
    global pl_yp
    global pl_jump

    global attack
    global attack_timer

    global player_hp
    global player_attr

    global invincible_timer

    global feedback_text
    global feedback_color
    global feedback_timer

    global hit_stop

    global flash_timer
    global flash_type

    global last_element
    global detected
    global map_number

    global time_left

    running = True
    timer = 0

    while running:

        timer += 1

        screen.fill((0, 0, 0))

        # =================================================
        # ヒットストップ
        # =================================================

        if hit_stop > 0:

            hit_stop -= 1

            pygame.display.flip()
            clock.tick(fps)

            continue

        # =================================================
        # イベント
        # =================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if (
                scene == "title"
                and event.type == pygame.MOUSEBUTTONDOWN
            ):

                if event.button == 1:

                    scene = "game"
                    init_game()

        keys = pygame.key.get_pressed()

        # =================================================
        # タイトル
        # =================================================

        if scene == "title":

            screen.blit(bg, (0, 0))

            # =================================================
            # タイトル床
            # =================================================

            for i in range(300):

                screen.blit(
                    block,
                    (i * size, floor_y + 20)
                )

            ani = (timer // 4) % 4

            screen.blit(
                player_imgs[ani],
                player_imgs[ani].get_rect(
                    center=(width // 2, floor_y)
                )
            )

            overlay = pygame.Surface((width, height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(120)

            screen.blit(overlay, (0, 0))

            title = font_big.render(
                "My Action Game",
                True,
                (255, 255, 255)
            )

            screen.blit(
                title,
                (width // 2 - 250, height // 2 - 120)
            )

            if (timer // 30) % 2 == 0:

                txt = font_mid.render(
                    "Click to Start",
                    True,
                    (200, 200, 200)
                )

                screen.blit(
                    txt,
                    (width // 2 - 150, height // 2 - 40)
                )

        # =================================================
        # GAME
        # =================================================

        elif scene == "game":

            screen.blit(bg, (0, 0))

            time_left -= 1

            if time_left <= 0:
                scene = "gameover"

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
                attack_timer = ATTACK_TIME

                hit_enemies.clear()

                sounds[player_attr].play()

            # 移動
            move_speed = (
                speed * 2
                if keys[pygame.K_LSHIFT]
                else speed
            )

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

            # 穴落下判定
            if pl_y > FALL_DEATH_Y:
                scene = "gameover"

            if invincible_timer > 0:
                invincible_timer -= 1

            # =================================================
            # プレイヤーRect
            # =================================================

            player_rect = pygame.Rect(
                width // 2 - 16,
                pl_y - 48,
                32,
                48
            )

            prev_bottom = player_rect.bottom - pl_yp

            on_block = False

            # =================================================
            # ブロック
            # =================================================

            for y, row in enumerate(BLOCK_MAP):

                for x, cell in enumerate(row):

                    if cell == "1":

                        bx = (
                            x + BLOCK_OFFSET_X
                        ) * size

                        by = floor_y - (
                            len(BLOCK_MAP) - y
                        ) * size + 22

                        screen_x = bx - camera_x

                        block_rect = pygame.Rect(
                            screen_x,
                            by,
                            size,
                            size
                        )

                        # 当たり判定
                        if player_rect.colliderect(block_rect):

                            if (
                                pl_yp >= 0
                                and prev_bottom <= block_rect.top
                            ):

                                pl_y = block_rect.top

                                pl_yp = 0
                                pl_jump = False

                                on_block = True

                                player_rect.bottom = pl_y
                        

                        # ブロック描画
                        screen.blit(
                            block,
                            (screen_x, by)
                        )

                        # DEBUG
                        if DEBUG:

                            pygame.draw.rect(
                                screen,
                                (255, 0, 0),
                                block_rect,
                                2
                            )

            if not on_block and pl_y < floor_y:

                pl_jump = True

            # =================================================
            # DEBUG PLAYER
            # =================================================

            if DEBUG:

                pygame.draw.rect(
                    screen,
                    (0, 0, 255),
                    player_rect,
                    2
                )

                foot_rect = pygame.Rect(
                    player_rect.x,
                    player_rect.bottom,
                    player_rect.width,
                    4
                )

                pygame.draw.rect(
                    screen,
                    (255, 255, 0),
                    foot_rect,
                    2
                )

            # =================================================
            # 攻撃
            # =================================================

            atk_rect = pygame.Rect(
                width // 2 - 80,
                pl_y - 80,
                160,
                100
            )

            new_enemies = []

            for enemy in enemies:

                ex = enemy["x"]

                screen_x = ex - camera_x

                enemy_rect = pygame.Rect(
                    screen_x,
                    floor_y - 100,
                    100,
                    100
                )

                if attack and attack_timer > 7:

                    if atk_rect.colliderect(enemy_rect):

                        if ex not in hit_enemies:

                            hit_enemies.add(ex)

                            damage = get_damage(
                                player_attr,
                                enemy["attr"]
                            )

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

            # 攻撃時間
            if attack:

                attack_timer -= 1

                if attack_timer <= 0:
                    attack = False

            # =================================================
            # プレイヤー
            # =================================================

            ani = (timer // 4) % 4

            if (
                invincible_timer == 0
                or invincible_timer % 10 < 5
            ):

                screen.blit(
                    player_imgs[ani],
                    player_imgs[ani].get_rect(
                        center=(width // 2, pl_y -20)
                    )
                )

            # =================================================
            # 攻撃エフェクト
            # =================================================

            if attack and attack_timer > 7:

                color = attr_colors[player_attr]

                surf = pygame.Surface(
                    (atk_rect.width, atk_rect.height),
                    pygame.SRCALPHA
                )

                surf.fill((*color, 120))

                screen.blit(
                    surf,
                    atk_rect.topleft
                )

            # =================================================
            # 敵
            # =================================================

            for enemy in enemies:

                screen_x = enemy["x"] - camera_x

                if -120 < screen_x < width:

                    tinted = enemy_base.copy()

                    tinted.fill(
                        attr_colors[enemy["attr"]],
                        special_flags=pygame.BLEND_RGBA_MULT
                    )

                    screen.blit(
                        tinted,
                        (screen_x, floor_y - 100)
                    )

            # =================================================
            # Princess
            # =================================================

            princess_x = goal_map_x * size - camera_x -400
            princess_y = floor_y - 40

            if map_number == 1:
                princess_rect = princess.get_rect(
                    center=(princess_x + size // 2, princess_y)
                )

            
                screen.blit(
                    princess,
                    princess_rect
                )

                if player_rect.colliderect(princess_rect):

                    scene = "clear"

                # DEBUG Princess
                if DEBUG:

                    pygame.draw.rect(
                        screen,
                        (0, 255, 255),
                        princess_rect,
                        2
                    )
            
            # =================================================
            # HP
            # =================================================

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (50, 50, 200, 20)
            )

            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (
                    50,
                    50,
                    200 * (
                        player_hp / PLAYER_MAX_HP
                    ),
                    20
                )
            )

            txt = font_mid.render(
                f"TIME: {time_left // 60}",
                True,
                (255, 255, 255)
            )

            screen.blit(txt, (50, 80))

            # =================================================
            # フィードバック
            # =================================================

            if feedback_timer > 0:

                feedback_timer -= 1

                txt = font_big.render(
                    feedback_text,
                    True,
                    feedback_color
                )

                screen.blit(
                    txt,
                    (width // 2 - 180, height // 3)
                )

            # =================================================
            # フラッシュ
            # =================================================

            if flash_timer > 0:

                flash_timer -= 1

                overlay = pygame.Surface(
                    (width, height)
                )

                if flash_type == "white":
                    overlay.fill((255, 255, 255))

                elif flash_type == "black":
                    overlay.fill((0, 0, 0))

                overlay.set_alpha(120)

                screen.blit(overlay, (0, 0))

            # =================================================
            # マップ切替
            # =================================================

            if camera_x > 2000:

                map_number += 1

                if map_number >= len(maps):
                    map_number = 0

                load_map(map_number)

                camera_x = 0

                reset_enemies()

            # =================================================
            # GAME OVER
            # =================================================

            if player_hp <= 0:
                scene = "gameover"

        # =================================================
        # GAME OVER
        # =================================================

        elif scene == "gameover":

            screen.fill((0, 0, 0))

            screen.blit(
                font_big.render(
                    "GAME OVER",
                    True,
                    (255, 0, 0)
                ),
                (width // 2 - 220, height // 2 - 100)
            )

            screen.blit(
                font_mid.render(
                    "Press R to Retry",
                    True,
                    (255, 255, 255)
                ),
                (width // 2 - 150, height // 2)
            )

            if keys[pygame.K_r]:

                init_game()
                scene = "game"

        # =================================================
        # CLEAR
        # =================================================

        elif scene == "clear":

            screen.fill((0, 0, 0))

            screen.blit(
                font_big.render(
                    "GAME CLEAR!",
                    True,
                    (255, 255, 0)
                ),
                (width // 2 - 250, height // 2 - 100)
            )

            screen.blit(
                font_mid.render(
                    "Press R to Retry",
                    True,
                    (255, 255, 255)
                ),
                (width // 2 - 150, height // 2)
            )

            if keys[pygame.K_r]:

                init_game()
                map_number = 0
                load_map(map_number)
                scene = "game"

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