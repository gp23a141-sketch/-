import pygame
import sys

from settings import *
from assets import *
from map_data import (
    DEMO_MAP,
    BLOCK_MAP_DEMO,
    MAP,
    BLOCK_MAP,
    BLOCK_OFFSET_X,
    MAP2,
    BLOCK_MAP2,
    MAP3,
    BLOCK_MAP3,
    ROCK_MAP_DEMO,
    ROCK_MAP,
    FIRE_MAP_DEMO,
    FIRE_MAP,
    FIRE_MAP_2
)

# =========================================================
# マップ
# =========================================================

maps = [
    {
        "map": DEMO_MAP,
        "block": BLOCK_MAP_DEMO,
        "rock": ROCK_MAP_DEMO,
        "fire": FIRE_MAP_DEMO,
        "offset": BLOCK_OFFSET_X,

        "warps": [],

        "checkpoints": [],

        "fuses": [
            {
                "x": 700,
                "y": floor_y - 64,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            }
        ],

        "plants": [
            {
                "x": 1000, 
                "y": floor_y - 64, 
                "state": 
                "small"
            }
        ]
    },

    {
        "map": MAP,
        "block": BLOCK_MAP,
        "rock": ROCK_MAP,
        "fire": FIRE_MAP,
        "offset": BLOCK_OFFSET_X,

        "warps": [
            {
                "x": 3000,
                "y": floor_y - 64,
                "next_map": 2
            }
        ],

        "checkpoints": [
            {
                "x": 1500,
                "y": floor_y - 64,
                "active": False
           }
        ],

        "fuses": [
            {
                "x": 1650,
                "y": floor_y - 64,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            }
            # 増やしたい場合はここに追加
        ],

        "plants": [
            {
                "x": 2000, 
                "y": floor_y - 64, 
                "state": 
                "small"
            }
            # 増やしたい場合はここに追加MAP2は下に
        ]
    },

    {
        "map": MAP2,
        "block": BLOCK_MAP2,
        "fire": FIRE_MAP_2,
        "offset": BLOCK_OFFSET_X,

        "warps": [
            {
                "x": 2500,
                "y": floor_y - 64,
                "next_map": 3
            }
        ],

        "checkpoints": [
            {
                "x": 1000,
                "y": floor_y - 64,
                "active": False
            }
        ]
    },

    {
        "map": MAP3,
        "block": BLOCK_MAP3,
        "offset": BLOCK_OFFSET_X,

        "warps": [],

        "checkpoints": [
            {
                "x": 700,
                "y": floor_y - 64,
                "active": False
            }
        ]
    }
]

demo = 1 #デモモード切替
if demo == 1 :
    map_number = 0
else :
    map_number = 1

def load_map(index):

    global floor
    global BLOCK_MAP
    global ROCK_MAP
    global FIRE_MAP
    global BLOCK_OFFSET_X
    global goal_map_x
    global warps
    global checkpoints
    global fuses
    global plants

    data = maps[index]

    floor = [
        int(c)
        for line in data["map"].split()
        for c in line
    ]

    BLOCK_MAP = data["block"]
    ROCK_MAP = data.get("rock", [])
    ROCK_MAP = [list(row) for row in ROCK_MAP]
    FIRE_MAP = data.get("fire", [])
    FIRE_MAP = [list(row) for row in FIRE_MAP]

    if index in destroyed_rocks:
        for (ry, rx) in destroyed_rocks[index]:
            if ry < len(ROCK_MAP) and rx < len(ROCK_MAP[ry]):
                ROCK_MAP[ry][rx] = "0"


    BLOCK_OFFSET_X = data["offset"]

    warps = data["warps"]

    checkpoints = data["checkpoints"]

    fuses = data.get("fuses", [])

    goal_map_x = len(floor) - 5

    plants = data.get("plants", [])

destroyed_rocks = {}

load_map(map_number)

# =========================================================
# プレイヤー
# =========================================================

camera_x = 0
player_x = width // 2

pl_y = floor_y
pl_yp = 0
pl_jump = False

player_hp = PLAYER_MAX_HP

invincible_timer = 0
INVINCIBLE_TIME = 120

player_attr = "fire"

# 復活地点
respawn_map = 0
respawn_x = 0

# =========================================================
# 敵
# =========================================================

enemies = []

def reset_enemies():
    if map_number != 0:
        enemies.clear()

        attrs = ["fire", "water", "grass"]

        for i in range(6):

            attr = attrs[i % 3]

            enemies.append({
                "x": 800 + i * 1600,
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
    global player_x
    global respawn_x
    global pl_y
    global pl_yp
    global pl_jump

    global player_hp
    global player_attr
    global invincible_timer
    global time_left
    global destroyed_rocks

    time_left = TIME_LIMIT

    camera_x = respawn_x
    player_x = respawn_x + width // 2

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

no_camera_mode = True #カメラ使わないモード
def game_loop():

    global scene

    global camera_x
    global player_x

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

    global respawn_map
    global respawn_x

    running = True
    timer = 0

    show_camera = True

    frame_count = 0

    last_camera_result = (
        False,
        (0, 0),
        "none",
        "walk",
        False,
        "none",
        (0, 0),
        None
    )

    speed_state = "walk"
    last_element = "none"
    detected = False
    prev_detected = False

    while running:

        cam_surface = None

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

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_TAB:

                    show_camera = not show_camera

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

            if USE_CAMERA:

                frame_count += 1

                if frame_count % 2 == 0:
                    last_camera_result = pen_con.update()

                move_detected, move_pos, action, speed_state, attr_detected, attr_element, attr_pos, debug_frame = last_camera_result

                if attr_element in attr_colors:
                    last_element = attr_element

                detected = attr_detected and not prev_detected
                prev_detected = attr_detected

                # ================================
                # ワイプ用カメラ映像
                # ================================

                if debug_frame is not None:

                    rgb_frame = cv2.cvtColor(
                        debug_frame,
                        cv2.COLOR_BGR2RGB
                    )

                    h, w = rgb_frame.shape[:2]

                    cam_surface = pygame.image.frombuffer(
                        rgb_frame.tobytes(),
                        (w, h),
                        "RGB"
                    )

            else:
                detected = False
                d = False
                element = "none"
                action = "none"
                speed_state = "walk"

            if last_element in attr_colors:
                player_attr = last_element

            # 攻撃
            if no_camera_mode == 1:
                if keys[pygame.K_r]:
                    player_attr = "fire"
                    detected = True
                if keys[pygame.K_g]:
                    player_attr = "grass"
                    detected = True
                if keys[pygame.K_b]:
                    player_attr = "water"
                    detected = True
            if detected and not attack:

                attack = True
                attack_timer = ATTACK_TIME

                hit_enemies.clear()

                if player_attr in sounds:
                    sounds[player_attr].play()

            # ========================================
            # 移動速度
            # ========================================

            move_speed = RUN_SPEED if speed_state == "run" else WALK_SPEED

            old_player_x = player_x
            rock_hit = False

            # ========================================
            # 紫ペンライト移動
            # ========================================

            if move_detected:

                if "right" in action:
                    player_x += move_speed

                if "left" in action:
                    player_x = max(0, player_x - move_speed)

                if "jump" in action and not pl_jump:
                    pl_jump = True
                    pl_yp = jump_power

            # ========================================
            # キーボード移動
            # ========================================   

            if keys[pygame.K_RIGHT]:
                player_x += move_speed

            if keys[pygame.K_LEFT]:
                player_x -= move_speed

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

            # カメラ追従
            camera_x = max(
                0,
                player_x - width // 2
            )

            # =================================================
            # プレイヤーRect
            # =================================================

            player_rect = pygame.Rect(
                player_x - camera_x - 16,
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
            # 岩描画
            # =================================================

            for y, row in enumerate(ROCK_MAP):

                for x, cell in enumerate(row):

                    if cell == "1":

                        bx = (
                            x + BLOCK_OFFSET_X
                        ) * size

                        by = floor_y - (
                            len(ROCK_MAP) - y
                        ) * size + 22

                        screen_x = bx - camera_x

                        rock_rect = pygame.Rect(
                            screen_x,
                            by,
                            64,
                            64
                        )

                        # 横方向の壁判定
                        if player_rect.colliderect(rock_rect):

                            if (
                                pl_yp >= 0
                                and prev_bottom <= rock_rect.top
                            ):
                                # 上から乗る
                                pl_y = rock_rect.top
                                pl_yp = 0
                                pl_jump = False
                                on_block = True
                                player_rect.bottom = pl_y

                            elif (
                                pl_yp < 0
                                and player_rect.top >= rock_rect.bottom - abs(pl_yp) - 4
                            ):
                                # 下から頭をぶつける
                                pl_yp = 0
                                pl_y = rock_rect.bottom + 48

                            else:
                                rock_hit = True

                        screen.blit(
                            iwa_img,
                            (screen_x, by)
                        )

                        pygame.draw.rect(
                            screen,
                            (0,255,0),
                            (
                                screen_x,
                                by,
                                64,
                                64
                            ),
                            2
                        )

                        if DEBUG:
                            pygame.draw.rect(
                                screen,
                                (0, 255, 0),
                                rock_rect,
                                2
                            )

            # 岩に当たったら移動を取り消す
            if rock_hit:
                player_x = old_player_x
                player_rect.x = player_x - camera_x - 16

            # =================================================
            # 炎
            # =================================================

            for y, row in enumerate(FIRE_MAP):
                for x, cell in enumerate(row):
                    if cell == "1":

                        bx = (x + BLOCK_OFFSET_X) * size
                        by = floor_y - (len(FIRE_MAP) - y) * size + 22
                        screen_x = bx - camera_x

                        fire_rect = pygame.Rect(screen_x, by, 64, 64)

                        # 描画
                        screen.blit(hi_img, (screen_x, by))

                        if DEBUG:
                            pygame.draw.rect(
                                screen,
                                (0, 255, 0),
                                (screen_x, by, 64, 64),
                                2
                            )

                        # 触れたらダメージ
                        if player_rect.colliderect(fire_rect):
                            if invincible_timer == 0:
                                player_hp -= 1
                                invincible_timer = INVINCIBLE_TIME
                                hit_stop = 8
                                flash_timer = FLASH_TIME
                                flash_type = "black"

                        # 水属性攻撃で消す
                        if (
                            attack
                            and player_attr == "water"
                            and atk_rect.colliderect(fire_rect)
                        ):
                            FIRE_MAP[y][x] = "0"

            # =================================================
            # 植物
            # =================================================

            GROW_TIME = 300  # 成長後に枯れるまでの時間（フレーム）

            for plant in plants:

                px = plant["x"] - camera_x
                py = plant["y"]

                if plant["state"] == "small":

                    plant_rect = pygame.Rect(px, py, 64, 64)

                    # 描画
                    screen.blit(kareki_img, (px, py))

                    # 草属性攻撃で成長
                    if (
                        attack
                        and player_attr == "grass"
                        and atk_rect.colliderect(plant_rect)
                    ):
                        plant["state"] = "grown"
                        plant["timer"] = GROW_TIME

                elif plant["state"] == "grown":

                    plant_rect = pygame.Rect(px - 32, py - 64, 128, 128)

                    # 描画
                    screen.blit(ki_img, (px - 32, py - 64))

                    # 足場判定
                    if player_rect.colliderect(plant_rect):
                        if (
                            pl_yp >= 0
                            and prev_bottom <= plant_rect.top
                        ):
                            pl_y = plant_rect.top
                            pl_yp = 0
                            pl_jump = False
                            on_block = True
                            player_rect.bottom = pl_y

                    # タイマー
                    plant["timer"] -= 1
                    if plant["timer"] <= 0:
                        plant["state"] = "small"

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
                player_x - camera_x - 80,
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
                        center=(player_x - camera_x, pl_y - 20)
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
            # Fuse
            # =================================================

            for fuse in fuses:

                screen_x = fuse["x"] - camera_x

                fuse_rect = pygame.Rect(
                    screen_x,
                    fuse["y"],
                    60,
                    20
                )

                if (
                    attack
                    and player_attr == "fire"
                    and atk_rect.colliderect(fuse_rect)
                ):
                    fuse["lit"] = True

                if fuse["lit"] and not fuse["exploded"]:

                    fuse["timer"] += 1

                    if fuse["timer"] > 180:
                        fuse["exploded"] = True
                        fuse["explode_timer"] = 30
                        fuse["lit"] = False

                        EXPLODE_RANGE = 200

                        for ry, row in enumerate(ROCK_MAP):
                            for rx, cell in enumerate(row):
                                if cell == "1":

                                    bx = (rx + BLOCK_OFFSET_X) * size
                                    by = floor_y - (len(ROCK_MAP) - ry) * size + 22

                                    rock_cx = bx + 32
                                    rock_cy = by + 32

                                    dist = (
                                        (fuse["x"] - rock_cx) ** 2
                                        + (fuse["y"] - rock_cy) ** 2
                                    ) ** 0.5

                                    if dist < EXPLODE_RANGE:
                                        ROCK_MAP[ry][rx] = "0"

                                        if map_number not in destroyed_rocks:
                                            destroyed_rocks[map_number] = set()
                                        destroyed_rocks[map_number].add((ry, rx))

                if fuse["exploded"]:
                    fuse["explode_timer"] -= 1


                # 描画
                if fuse["exploded"] and fuse["explode_timer"] > 0:

                    screen.blit(
                        bakuhatu_img,
                        (screen_x - 32, fuse["y"] - 32)
                    )

                elif fuse["lit"]:

                    screen.blit(
                        bakudan_chakka_img,
                        fuse_rect
                    )

                else:

                    screen.blit(
                        bakudan_img,
                        fuse_rect
                    )  
                    
            fuses[:] = [
                fuse for fuse in fuses
                if not (
                    fuse["exploded"]
                    and fuse["explode_timer"] <= 0
                )
            ]

            # =================================================
            # Check Point
            # =================================================

            for point in checkpoints:

                screen_x = point["x"] - camera_x

                point_rect = pygame.Rect(
                    screen_x,
                    point["y"],
                    64,
                    64
                )

                # ON/OFF画像切替
                if point["active"]:

                    screen.blit(
                        takibi_on_img,
                        point_rect
                    )

                else:

                    screen.blit(
                        takibi_off_img,
                        point_rect
                    )

                # DEBUG
                if DEBUG:

                    pygame.draw.rect(
                        screen,
                        (255, 200, 0),
                        point_rect,
                        2
                    )

                # 接触
                if player_rect.colliderect(point_rect):

                    # まだ未点火なら
                    if not point["active"]:

                        # 全焚火OFF
                        for p in checkpoints:
                            p["active"] = False

                        # 今の焚火ON
                        point["active"] = True

                        # 復活地点更新
                        respawn_map = map_number

                        respawn_x = max(0, point["x"] - width // 2)

            # =================================================
            # ワープ
            # =================================================

            for warp in warps:

                screen_x = warp["x"] - camera_x

                warp_rect = pygame.Rect(
                    screen_x,
                    warp["y"],
                    64,
                    64
                )

                screen.blit(
                    warp_img,
                    warp_rect
                )

                # DEBUG
                if DEBUG:

                    pygame.draw.rect(
                        screen,
                        (255, 0, 255),
                        warp_rect,
                        2
                    )

                # 当たり判定
                if player_rect.colliderect(warp_rect):

                    map_number = warp["next_map"]

                    load_map(map_number)

                    player_x = width // 2
                    camera_x = 0

                    reset_enemies()

                    break

            # =================================================
            # Princess
            # =================================================
            if map_number == 0:
                princess_x = goal_map_x * size - camera_x +200
            elif map_number == 3:
                princess_x = goal_map_x * size - camera_x -400
            princess_y = floor_y - 40

            if map_number == 0 or map_number == 3:
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

                map_number = respawn_map

                load_map(map_number)

                camera_x = respawn_x

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
                if demo == 1 :
                    map_number = 0
                else :
                    map_number = 1
                load_map(map_number)
                scene = "game"

        # =================================================
        # カメラワイプ
        # =================================================

        if USE_CAMERA and show_camera and cam_surface is not None:

            CAM_SCALE = 0.45

            cam_w = int(cam_surface.get_width() * CAM_SCALE)
            cam_h = int(cam_surface.get_height() * CAM_SCALE)

            scaled_cam = pygame.transform.scale(
                cam_surface,
                (cam_w, cam_h)
            )

            cam_x = width - cam_w
            cam_y = 0

            screen.blit(
                scaled_cam,
                (cam_x, cam_y)
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (cam_x, cam_y, cam_w, cam_h),
                2
            )

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