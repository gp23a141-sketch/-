import pygame
import sys
import copy
import json

from settings import *
from assets import *

BOSS_SIZE = 150
boss_base = pygame.transform.scale(enemy_base, (BOSS_SIZE, BOSS_SIZE))

# =========================================================
# レイアウト（ゲーム画面を中央に縮小配置）
# =========================================================

GAME_SCALE = 0.6
game_box_w = int(width * GAME_SCALE)
game_box_h = int(height * GAME_SCALE)
game_box_x = (width - game_box_w) // 2
game_box_y = 20

from map_data import (
    DEMO_MAP,
    BLOCK_MAP_DEMO,
    MAP,
    MAP_HARD,
    BLOCK_MAP,
    BLOCK_MAP_HARD,
    BLOCK_OFFSET_X,
    MAP2,
    MAP2_HARD,
    BLOCK_MAP2,
    BLOCK_MAP2_HARD,
    MAP3,
    MAP3_HARD,
    BLOCK_MAP3,
    BLOCK_MAP3_HARD,
    ROCK_MAP_DEMO,
    ROCK_MAP,
    ROCK_MAP_2,
    ROCK_MAP_2_HARD,
    FIRE_MAP_DEMO,
    FIRE_MAP,
    FIRE_MAP_HARD,
    FIRE_MAP_2,
    FIRE_MAP_2_HARD,
    FIRE_MAP_3_HARD,
    BOSS_MAP,       
    BLOCK_MAP_BOSS,
    MAP4_HARD,
    BLOCK_MAP4_HARD,
    ROCK_MAP_3_HARD,
    FIRE_MAP_4_HARD,
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
        "offset": BLOCK_OFFSET_X,
        "fire": FIRE_MAP_2,
        "rock": ROCK_MAP_2,

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
        ],

        "fuses": [
            {
                "x": 1400,
                "y": floor_y - 100,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            },
            {
                "x": 1650,
                "y": floor_y - 160,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            }
            # 増やしたい場合はここに追加
        ]

    },

    {
        "map": MAP3,
        "block": BLOCK_MAP3,
        "offset": BLOCK_OFFSET_X,

        "warps": [
            {
                "x": 2400,      
                "y": floor_y - 64,
                "next_map": 4
            }
        ],

        "checkpoints": [
            {
                "x": 700,
                "y": floor_y - 64,
                "active": False
            }
        ],

        "plants": [
            {
                "x": 800, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 1250, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 1600, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 2000, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            # 増やしたい場合はここに追加MAP2は下に
        ]
    },

    {
        "map": BOSS_MAP,
        "block": BLOCK_MAP_BOSS,
        "offset": BLOCK_OFFSET_X,
        "warps": [],
        "checkpoints": [
            {
                "x": 600,
                "y": floor_y - 64,
                "active": False
            }
        ], 
    },

    {
        "map": MAP_HARD,
        "block": BLOCK_MAP_HARD,
        "rock": ROCK_MAP,
        "fire": FIRE_MAP_HARD,
        "offset": BLOCK_OFFSET_X,

        "warps": [
            {
                "x": 3000,
                "y": floor_y - 64,
                "next_map": 6
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
        "map": MAP2_HARD,
        "block": BLOCK_MAP2_HARD,
        "offset": BLOCK_OFFSET_X,
        "fire": FIRE_MAP_2_HARD,
        "rock": ROCK_MAP_2_HARD,

        "warps": [
            {
                "x": 2500,
                "y": floor_y - 64,
                "next_map": 7
            }
        ],

        "checkpoints": [
            {
                "x": 1000,
                "y": floor_y - 64,
                "active": False
            }
        ],

        "fuses": [
            {
                "x": 1400,
                "y": floor_y - 100,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            },
            {
                "x": 1650,
                "y": floor_y - 160,
                "lit": False,
                "timer": 0,
                "exploded": False,
                "explode_timer": 0
            }
            # 増やしたい場合はここに追加
        ]

    },

    {
        "map": MAP3_HARD,
        "block": BLOCK_MAP3_HARD,
        "offset": BLOCK_OFFSET_X,
        "fire": FIRE_MAP_3_HARD,

        "warps": [
            {
                "x": 2400,      
                "y": floor_y - 64,
                "next_map": 8
            }
        ],

        "checkpoints": [
            {
                "x": 700,
                "y": floor_y - 64,
                "active": False
            }
        ],

        "plants": [
            {
                "x": 800, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 1250, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 1600, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 2000, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            # 増やしたい場合はここに追加MAP2は下に
        ]
    },
    {
        "map": MAP4_HARD,
        "block": BLOCK_MAP4_HARD,
        "offset": BLOCK_OFFSET_X,
        "rock": ROCK_MAP_3_HARD,
         "fire": FIRE_MAP_4_HARD,
    
         "warps": [
            {
                "x": 2400,      
                "y": floor_y - 64,
                "next_map": 4
            }
        ],
    
        "checkpoints": [
            {
                "x": 700,
                "y": floor_y - 64,
                "active": False
            }
        ],
    
        "plants": [
            {
                "x": 200, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 400, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 600, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
            {
                "x": 800, 
                "y": floor_y - 64, 
                "state": 
                "small"
            },
                # 増やしたい場合はここに追加MAP2は下に
        ],

        "fuses": [
                    {
                        "x": 1000,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    {
                        "x": 1200,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    {
                        "x": 1400,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    {
                        "x": 1600,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    {
                        "x": 1800,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    {
                        "x": 2000,
                        "y": floor_y - 50,
                        "lit": False,
                        "timer": 0,
                        "exploded": False,
                        "explode_timer": 0
                    },
                    # 増やしたい場合はここに追加
        ]
    }
]

demo = 0 #デモモード切替
if demo == 0 :
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

    fuses = copy.deepcopy(data.get("fuses", []))

    goal_map_x = len(floor) - 5

    plants = data.get("plants", [])

destroyed_rocks = {}

load_map(map_number)

# =========================================================
# ランキング
# =========================================================

RANKING_FILE = "ranking.json"
RANKING_MAX = 10

def load_ranking():
    try:
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_ranking(ranking_list):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(ranking_list, f, ensure_ascii=False, indent=2)

def add_ranking(name, score_value):
    ranking_list = load_ranking()
    ranking_list.append({"name": name, "score": score_value})
    ranking_list.sort(key=lambda r: r["score"], reverse=True)
    ranking_list = ranking_list[:RANKING_MAX]
    save_ranking(ranking_list)
    return ranking_list

# =========================================================
# チュートリアル看板
# =========================================================

tutorial_signs = [
    {
        "x": 300,
        "y": floor_y - 64,
        "lines": ["紫色のペンライトを左右に動かして移動、振ると早くなる!","", "下に持ってくるとジャンプ!"]
    },
    {
        "x": 600,
        "y": floor_y - 64,
        "lines": ["ペンライトの1火、2水、3草ボタンで属性切替","", "振ると攻撃！","", "爆弾は火、火には水、枯れ木には草を使い分けよう!"]
    },
    {
        "x": 900,
        "y": floor_y - 64,
        "lines": ["火は草に強く水に弱い","",  "三すくみを使い分けよう!"]
    },
]

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

player_knockback = 0

player_attr = "fire"

# 向き (True=右向き, False=左向き)
facing_right = True

# 復活地点
respawn_map = map_number
respawn_x = -300

#bossステータス
BOSS_MAX_HP =60
boss = None

# =========================================================
# 敵
# =========================================================

defeated_enemies = {} 
enemies = []

def reset_enemies():

    enemies.clear()

    if map_number == 0 or map_number == 4:
        return

    attrs = ["fire", "water", "grass"]

    defeated = defeated_enemies.get(map_number, set())

    for i in range(6):

        if i in defeated:
            continue

        attr = attrs[i % 3]

        enemies.append({
            "x": 800 + i * 1600,
            "hp": ENEMY_MAX_HP,
            "max_hp": ENEMY_MAX_HP,
            "attr": attr,
            "dir": -1,      
            "speed": 2, 
            "knockback": 0,
            "invincible": 0,
            "move_timer": 0,
            "index": i,
        })

reset_enemies()

# =========================================================
# 攻撃
# =========================================================

attack = False
attack_timer = 0

ATTACK_TIME = 12

hit_enemies = set()

damage_numbers = []

score = 0

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
# 剣の回転描画
# =========================================================

def rotate_around_pivot(image, angle, pivot, pos):

    image_rect = image.get_rect(
        topleft=(pos[0] - pivot[0], pos[1] - pivot[1])
    )

    offset = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset.rotate(-angle)

    rotated_center = (
        pos[0] - rotated_offset.x,
        pos[1] - rotated_offset.y
    )

    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=rotated_center)

    return rotated_image, rotated_rect

# =========================================================
# ボス初期化
# =========================================================

def init_boss():
    global boss
    boss = {
        "x": width + 300,
        "hp": BOSS_MAX_HP,
        "max_hp": BOSS_MAX_HP,
        "attr": "fire",
        "attr_timer": 0,
        "state": "patrol",
        "dir": -1,
        "move_timer": 0,
        "knockback": 0,
        "invincible": 0,
        "charge_cooldown": 0,
        "phase": 1,
        "phase_changed": False,
        "crit_count": 0,
        "stun_timer": 0,
    }

# =========================================================
# 初期化
# =========================================================
life = 10
MAX_LIVES = 10
time_left = TIME_LIMIT

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
    global facing_right
    global player_knockback
    global boss
    global score

    global damage_numbers
    global score
    global princess_touched
    global life

    player_attr = "fire"
    facing_right = True

    camera_x = respawn_x
    player_x = respawn_x + width // 2

    pl_y = floor_y
    pl_yp = 0
    pl_jump = False

    player_hp = PLAYER_MAX_HP
    player_attr = "fire"

    invincible_timer = 0

    player_knockback = 0
    damage_numbers = []
    princess_touched = False

    if map_number == 4:
        init_boss()

    reset_enemies()

# =========================================================
# シーン
# =========================================================

scene = "title"

input_name = ""
INPUT_MAX_LEN = 8

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

    global facing_right
    global destroyed_rocks
    global damage_numbers
    global player_knockback
    global boss
    global score
    global defeated_enemies
    global input_name
    global screen
    global princess_touched
    global life

    hard_mode = 0 #ハードモード切替
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
    attr_prev_pos = (0, 0)
    princess_touched = False

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

                if event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()

                if scene == "clear":
                    if event.key == pygame.K_BACKSPACE:
                        input_name = input_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if input_name.strip() != "":
                            add_ranking(input_name.strip(), total_score)
                            scene = "ranking"
                    elif len(input_name) < INPUT_MAX_LEN:
                        if event.unicode.isprintable():
                            input_name += event.unicode

            if event.type == pygame.QUIT:

                running = False
            
            if (
                scene == "title" 
                and event.type == pygame.KEYDOWN
            ):
                if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                    hard_mode = 1 - hard_mode
                
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
                "Princess Quest",
                True,
                (255, 255, 255)
            )

            screen.blit(
                title,
                (width // 2 - 250, height // 2 - 120)
            )


            txt_Select = font_mid.render(
                "Select difficulty",
                True,
                (200, 200, 200)
            )

            screen.blit(
                txt_Select,
                (width // 2 - 150, height // 2 + 20)
            )

            diff_text = "Hard" if hard_mode == 1 else "Normal"
            txt_Difficulty = font_mid.render(
                diff_text, 
                True, 
                (200, 200, 200)
            )

            screen.blit(
                txt_Difficulty,
                (width // 2 - 70, height // 2 + 60)
            )
            
            if (timer // 30) % 2 == 0:

                txt = font_mid.render(
                    "Click to Start!!",
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
                life -= 1
                if life > 0:
                    scene = "gameover"
                else:
                    scene = "titleover"

            if USE_CAMERA:

                frame_count += 1

                if frame_count % 6 == 0:
                    last_camera_result = pen_con.update()

                move_detected, move_pos, action, speed_state, attr_detected, attr_element, attr_pos, debug_frame = last_camera_result

                if attr_element in attr_colors:
                    last_element = attr_element

                if attr_detected:
                    dx = attr_pos[0] - attr_prev_pos[0]
                    dy = attr_pos[1] - attr_prev_pos[1]
                    movement = (dx**2 + dy**2) ** 0.5
                    detected = movement > 80 and not attack
                    attr_prev_pos = attr_pos
                else:
                    detected = False
                    attr_prev_pos = (0, 0)

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
            block_hit = False

            # ========================================
            # 紫ペンライト移動
            # ========================================

            if move_detected:

                if action == "right":
                    player_x += move_speed
                    facing_right = True

                elif action == "left":
                    player_x = max(0, player_x - move_speed)
                    facing_right = False

                elif action == "jump":
                    if not pl_jump:
                        pl_jump = True
                        pl_yp = jump_power

                elif action == "jump_right":
                    player_x += move_speed
                    facing_right = True
                    if not pl_jump:
                        pl_jump = True
                        pl_yp = jump_power

                elif action == "jump_left":
                    player_x = max(0, player_x - move_speed)
                    facing_right = False
                    if not pl_jump:
                        pl_jump = True
                        pl_yp = jump_power

            # ========================================
            # キーボード移動
            # ========================================   

            if keys[pygame.K_RIGHT]:
                player_x += RUN_SPEED
                facing_right = True

            if keys[pygame.K_LEFT]:
                player_x -= RUN_SPEED
                facing_right = False

            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = jump_power

            # ノックバック更新
            if player_knockback != 0:
                player_x += player_knockback
                if player_knockback > 0:
                    player_knockback = max(0, player_knockback - 1)
                else:
                    player_knockback = min(0, player_knockback + 1)


            # 重力
            pl_y += pl_yp
            pl_yp += gravity

            # 穴落下判定
            if pl_y > FALL_DEATH_Y:
                life -= 1
                if life > 0:
                    scene = "gameover"
                else:
                    scene = "titleover"

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
                                #上から乗る
                                pl_y = block_rect.top
                                pl_yp = 0
                                pl_jump = False
                                on_block = True
                                player_rect.bottom = pl_y

                            elif(
                                pl_yp < 0
                                and player_rect.top >= block_rect.bottom - abs(pl_yp)-4
                            ):
                                #下から頭をぶつける
                                pl_yp = 0
                                pl_y = block_rect.bottom + 48

                            else:
                                block_hit = True
                        

                        # ブロック描画
                        screen.blit(
                            block,
                            (screen_x, by)
                        )

            if not on_block and pl_y < floor_y:

                pl_jump = True

            # 壁に当たったら移動を取り消す
            if block_hit:
                player_x = old_player_x
                player_rect.x = player_x - camera_x - 16

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
                                player_hp -= 25
                                invincible_timer = INVINCIBLE_TIME
                                hit_stop = 8
                                flash_timer = FLASH_TIME
                                flash_type = "black"

                                # ノックバック
                                fire_world_x = bx + 32
                                kb_dir = 1 if player_x > fire_world_x else -1
                                player_knockback = kb_dir * 10

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

            GROW_TIME = 10000  # 成長後に枯れるまでの時間（フレーム）

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

                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    rock_rect,
                    2
                )

                pygame.draw.rect(
                    screen,
                    (255, 0, 0),
                    block_rect,
                    2
                )
                    
                pygame.draw.rect(
                    screen,
                    (255, 200, 0),
                    point_rect,
                    2
                )

            # =================================================
            # 攻撃
            # =================================================

            if facing_right:
                atk_rect = pygame.Rect(
                    player_x - camera_x,
                    pl_y - 80,
                    160,
                    100
                )
            else:
                atk_rect = pygame.Rect(
                    player_x - camera_x - 160,
                    pl_y - 80,
                    160,
                    100
                )

            new_enemies = []

            for enemy in enemies:

                # 無敵タイマー更新
                if enemy["invincible"] > 0:
                    enemy["invincible"] -= 1

                # 移動・ノックバック処理
                if enemy["knockback"] != 0:
                    enemy["x"] += enemy["knockback"]
                    if enemy["knockback"] > 0:
                        enemy["knockback"] = max(0, enemy["knockback"] - 1)
                    else:
                        enemy["knockback"] = min(0, enemy["knockback"] + 1)
                else:
                    enemy["move_timer"] += 1
                    if enemy["move_timer"] >= 120:
                        enemy["dir"] *= -1
                        enemy["move_timer"] = 0
                    enemy["x"] += enemy["speed"] * enemy["dir"]

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
                                
                        if ex not in hit_enemies and enemy["invincible"] == 0:

                            hit_enemies.add(ex)

                            damage = get_damage(
                                player_attr,
                                enemy["attr"]
                            )

                            enemy["hp"] -= damage
                            enemy["invincible"] = 60

                            # ノックバック方向(プレイヤーと反対側)
                            kb_dir = 1 if enemy["x"] > player_x else -1

                            if damage == 3:
                                enemy["knockback"] = kb_dir * 20
                                feedback_text = "CRITICAL!"
                                feedback_color = (255, 255, 0)
                                hit_stop = 10
                                flash_timer = FLASH_TIME
                                flash_type = "white"

                            elif damage == 1:
                                enemy["knockback"] = kb_dir * 8
                                feedback_text = "GOOD"
                                feedback_color = (255, 255, 255)
                                hit_stop = 5

                            else:
                                feedback_text = "BAD..."
                                feedback_color = (255, 100, 180)

                            feedback_timer = 20

                            damage_numbers.append({
                                "x": screen_x,
                                "y": floor_y - 120,
                                "value": damage,
                                "timer": 40,
                                "color": (255, 255, 0) if damage == 3 else (255, 255, 255) if damage == 1 else (180, 180, 255)
                            })

                if player_rect.colliderect(enemy_rect):

                    if invincible_timer == 0:

                        player_hp -= 5

                        invincible_timer = INVINCIBLE_TIME

                        hit_stop = 8

                        flash_timer = FLASH_TIME
                        flash_type = "black"

                        # ノックバック
                        kb_dir = -1 if enemy["x"] > player_x else 1
                        player_knockback = kb_dir * 12

                if enemy["hp"] > 0:
                    new_enemies.append(enemy)
                else:
                    score += 100

                    if map_number not in defeated_enemies:  # ← 追加
                        defeated_enemies[map_number] = set()  # ← 追加
                    defeated_enemies[map_number].add(enemy["index"])

            enemies[:] = new_enemies

            # 攻撃時間
            if attack:

                attack_timer -= 1

                if attack_timer <= 0:
                    attack = False

            # =================================================
            # チュートリアル看板
            # =================================================

            if map_number == 0:

                for sign in tutorial_signs:

                    sign_screen_x = sign["x"] - camera_x

                    sign_rect = pygame.Rect(
                        sign_screen_x,
                        sign["y"],
                        64,
                        64
                    )

                    pygame.draw.rect(
                        screen,
                        (200, 170, 100),
                        sign_rect
                    )
                    pygame.draw.rect(
                        screen,
                        (100, 70, 30),
                        sign_rect,
                        3
                    )

                    near_rect = sign_rect.inflate(150, 150)

                    if player_rect.colliderect(near_rect):

                        for i, line in enumerate(sign["lines"]):

                            line_surf = font_small.render(
                                line,
                                True,
                                (255, 255, 255)
                            )

                            bg_surf = pygame.Surface(
                                (line_surf.get_width() + 16, line_surf.get_height() + 6)
                            )
                            bg_surf.fill((0, 0, 0))
                            bg_surf.set_alpha(180)

                            pos_x = sign_screen_x - 40
                            pos_y = sign["y"] - 70 - i * 30

                            screen.blit(bg_surf, (pos_x, pos_y))
                            screen.blit(line_surf, (pos_x + 8, pos_y + 3))

            # =================================================
            # プレイヤー
            # =================================================

            ani = (timer // 4) % 4

            if (
                invincible_timer == 0
                or invincible_timer % 10 < 5
            ):
                
                player_img = player_imgs[ani]

                if not facing_right:
                    player_img = pygame.transform.flip(player_img, True, False)

                screen.blit(
                    player_img,
                    player_img.get_rect(
                        center=(player_x - camera_x, pl_y - 20)
                    )
                )

            # プレイヤーHPバー（頭上）
            player_bar_x = player_x - camera_x - 30
            player_bar_y = pl_y - 90

            pygame.draw.rect(
                screen,
                (80, 80, 80),
                (player_bar_x, player_bar_y, 60, 8)
            )

            player_hp_ratio = max(0, player_hp / PLAYER_MAX_HP)

            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (player_bar_x, player_bar_y, int(60 * player_hp_ratio), 8)
            )

            # =================================================
            # 攻撃エフェクト（剣を振るモーション）
            # =================================================

            if attack:

                progress = 1 - (attack_timer / ATTACK_TIME)

                # 振る方向：上から下に振りたいなら True、下から上ならFalse
                SWING_TOP_TO_BOTTOM = True

                if SWING_TOP_TO_BOTTOM:
                    START_ANGLE = 70
                    END_ANGLE = -70
                else:
                    START_ANGLE = -70
                    END_ANGLE = 70

                angle = START_ANGLE + (END_ANGLE - START_ANGLE) * progress

                base_img = sword_imgs[player_attr]

                # 左向きの時だけ振る向きを反転させたい場合は True
                MIRROR_LEFT_ANGLE = True

                if facing_right:
                    sword_img = base_img
                    pivot = (0, base_img.get_height() // 2)
                    draw_angle = angle
                else:
                    sword_img = pygame.transform.flip(base_img, True, False)
                    pivot = (base_img.get_width(), base_img.get_height() // 2)
                    draw_angle = -angle if MIRROR_LEFT_ANGLE else angle

                hand_x = player_x - camera_x
                hand_y = pl_y - 40

                rotated_sword, sword_rect = rotate_around_pivot(
                    sword_img,
                    draw_angle,
                    pivot,
                    (hand_x, hand_y)
                )

                screen.blit(rotated_sword, sword_rect)

           # =================================================
            # 敵
            # =================================================

            for enemy in enemies:

                screen_x = enemy["x"] - camera_x

                if -120 < screen_x < width:
                        
                    if enemy["invincible"] == 0 or enemy["invincible"] % 6 < 3:

                        # 敵本体
                        tinted = enemy_base.copy()

                        tinted.fill(
                            attr_colors[enemy["attr"]],
                            special_flags=pygame.BLEND_RGBA_MULT
                        )

                        screen.blit(
                            tinted,
                            (screen_x, floor_y - 100)
                        )

                    # HPバー背景
                    pygame.draw.rect(
                        screen,
                        (80, 80, 80),
                        (screen_x, floor_y - 115, 100, 8)
                    )

                    # HPバー本体
                    hp_ratio = max(0, enemy["hp"] / enemy["max_hp"])

                    pygame.draw.rect(
                        screen,
                        (220, 50, 50),
                        (screen_x, floor_y - 115, int(100 * hp_ratio), 8)
                    )

            # ダメージ数値の更新と描画
            for dn in damage_numbers:

                dn["timer"] -= 1
                dn["y"] -= 1  # 上に流れる

                alpha = max(0, int(255 * (dn["timer"] / 40)))

                txt_surf = font_mid.render(
                    str(dn["value"]),
                    True,
                    dn["color"]
                )

                txt_surf.set_alpha(alpha)

                screen.blit(txt_surf, (dn["x"], dn["y"]))

            damage_numbers[:] = [
                dn for dn in damage_numbers
                if dn["timer"] > 0
            ]

            # =================================================
            # ボス
            # =================================================

            if map_number == 4 and boss is not None:

                # 第2形態移行チェック
                if boss["hp"] <= boss["max_hp"] // 2 and boss["phase"] == 1:
                    boss["phase"] = 2
                    boss["phase_changed"] = True
                    boss["attr"] = "fire"
                    boss["attr_timer"] = 0
                    flash_timer = FLASH_TIME * 5
                    flash_type = "white"
                    feedback_text = "PHASE 2!"
                    feedback_color = (255, 50, 50)
                    feedback_timer = 60

                # 属性サイクル(第2形態のみ、120フレームごと)
                if boss["phase"] == 2:
                    boss["attr_timer"] += 1
                    if boss["attr_timer"] >= 360:
                        boss["attr_timer"] = 0
                        attrs_cycle = ["fire", "water", "grass"]
                        idx = attrs_cycle.index(boss["attr"])
                        boss["attr"] = attrs_cycle[(idx + 1) % 3]

                # 無敵タイマー
                if boss["invincible"] > 0:
                    boss["invincible"] -= 1

                # 気絶タイマー
                if boss["stun_timer"] > 0:            
                    boss["stun_timer"] -= 1          

                # ノックバック
                if boss["stun_timer"] > 0:          
                    pass                            
                elif boss["knockback"] != 0:
                    boss["x"] += boss["knockback"]
                    if boss["knockback"] > 0:
                        boss["knockback"] = max(0, boss["knockback"] - 1)
                    else:
                        boss["knockback"] = min(0, boss["knockback"] + 1)

                elif boss["state"] == "patrol":

                    if boss["phase"] == 1:
                        patrol_speed = 3
                        charge_distance = 800
                    else:
                        patrol_speed = 6
                        charge_distance = 1200

                    boss["move_timer"] += 1
                    if boss["move_timer"] >= 120:
                        boss["dir"] *= -1
                        boss["move_timer"] = 0
                    boss["x"] += patrol_speed * boss["dir"]

                    if abs(boss["x"] - player_x) < charge_distance and boss["charge_cooldown"] == 0:
                        boss["state"] = "charge"
                        boss["dir"] = 1 if player_x > boss["x"] else -1

                elif boss["state"] == "charge":
                    charge_speed = 15 if boss["phase"] == 1 else 22
                    boss["x"] += charge_speed * boss["dir"]
                    if (
                        (boss["dir"] == 1 and boss["x"] > player_x + 200)
                        or (boss["dir"] == -1 and boss["x"] < player_x - 200)
                    ):
                        boss["state"] = "cooldown"
                        boss["charge_cooldown"] = 120 if boss["phase"] == 1 else 50

                if boss["charge_cooldown"] > 0:
                    boss["charge_cooldown"] -= 1
                    if boss["charge_cooldown"] == 0 and boss["state"] == "cooldown":
                        boss["state"] = "patrol"

                boss_screen_x = boss["x"] - camera_x

                boss_rect = pygame.Rect(
                    boss_screen_x,
                    floor_y - BOSS_SIZE,
                    BOSS_SIZE,
                    BOSS_SIZE
                )

                # 攻撃ヒット判定
                if attack and attack_timer > 7:
                    if atk_rect.colliderect(boss_rect) and boss["invincible"] == 0:

                        damage = get_damage(player_attr, boss["attr"])
                        boss["hp"] -= damage
                        boss["invincible"] = 30

                        kb_dir = 1 if boss["x"] > player_x else -1

                        if damage == 3:
                            boss["knockback"] = kb_dir * 20
                            feedback_text = "CRITICAL!"
                            feedback_color = (255, 255, 0)
                            hit_stop = 10
                            flash_timer = FLASH_TIME
                            flash_type = "white"

                            if boss["stun_timer"] == 0:
                                boss["crit_count"] += 1 

                            if boss["crit_count"] >= 5: 
                                boss["stun_timer"] = 300
                                boss["crit_count"] = 0
                                boss["state"] = "patrol"
                                feedback_text = "STUN!"
                                feedback_color = (255, 100, 255)

                        elif damage == 1:
                            boss["knockback"] = kb_dir * 8
                            feedback_text = "GOOD"
                            feedback_color = (255, 255, 255)
                            hit_stop = 5
                        else:
                            feedback_text = "BAD..."
                            feedback_color = (255, 100, 180)

                        feedback_timer = 20

                        damage_numbers.append({
                            "x": boss_screen_x,
                            "y": floor_y - BOSS_SIZE - 20,
                            "value": damage,
                            "timer": 40,
                            "color": (255, 255, 0) if damage == 3 else (255, 255, 255) if damage == 1 else (180, 180, 255)
                        })

                # プレイヤーへのダメージ
                if player_rect.colliderect(boss_rect):
                    if invincible_timer == 0:
                        player_hp -= 3
                        invincible_timer = INVINCIBLE_TIME
                        hit_stop = 15
                        flash_timer = FLASH_TIME
                        flash_type = "black"
                        kb_dir = -1 if boss["x"] > player_x else 1
                        player_knockback = kb_dir * 15

                # ボス描画
                if -BOSS_SIZE < boss_screen_x < width:
                    if boss["invincible"] == 0 or boss["invincible"] % 6 < 3:
                        boss_surf = boss_base.copy()
                        boss_surf.fill(
                            attr_colors[boss["attr"]],
                            special_flags=pygame.BLEND_RGBA_MULT
                        )

                        if boss["stun_timer"] > 0:  
                            boss_surf = pygame.transform.rotate(boss_surf, 90)  

                        screen.blit(boss_surf, (boss_screen_x, floor_y - BOSS_SIZE))

                    # ボスHPバー（頭上）
                    boss_bar_x = boss_screen_x + BOSS_SIZE // 2 - 50
                    boss_bar_y = floor_y - BOSS_SIZE - 20

                    pygame.draw.rect(
                        screen,
                        (80, 80, 80),
                        (boss_bar_x, boss_bar_y, 100, 10)
                    )

                    boss_hp_ratio = max(0, boss["hp"] / boss["max_hp"])

                    pygame.draw.rect(
                        screen,
                        (0, 255, 0),
                        (boss_bar_x, boss_bar_y, int(100 * boss_hp_ratio), 10)
                    )

                # ボスHPバー(画面上部中央)
                bar_w = 300
                bar_x = width // 2 - bar_w // 2 - 200
                bar_y = 20
                pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, 20))
                hp_ratio = max(0, boss["hp"] / boss["max_hp"])

                # 第1形態は赤、第2形態はオレンジ
                bar_color = (220, 50, 50) if boss["phase"] == 1 else (255, 140, 0)
                pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * hp_ratio), 20))

                phase_label = font_mid.render(
                    f"BOSS  PHASE {boss['phase']}",
                    True,
                    (255, 255, 255)
                )
                screen.blit(phase_label, (bar_x - 10, bar_y - 30))

                # 気絶ゲージ
                if boss["stun_timer"] > 0:
                    stun_ratio = boss["stun_timer"] / 300
                    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y + 25, bar_w, 10))
                    pygame.draw.rect(screen, (255, 100, 255), (bar_x, bar_y + 25, int(bar_w * stun_ratio), 10))
                    
                # ボス撃破
                if boss["hp"] <= 0:
                    score += 1000
                    scene = "clear"

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

                # 接触
                if player_rect.colliderect(point_rect):

                    # まだ未点火なら
                    if not point["active"]:

                        # 全焚火OFF
                        for p in checkpoints:
                            p["active"] = False

                        # 今の焚火ON
                        point["active"] = True
                        player_hp = min(PLAYER_MAX_HP, player_hp + 100)

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

                    if map_number == 4:
                        init_boss()

                    break

            # =================================================
            # Princess
            # =================================================
            if map_number == 0:
                princess_x = goal_map_x * size - camera_x + 200
            princess_y = floor_y - 40

            if map_number == 0:
                princess_rect = princess.get_rect(
                    center=(princess_x + size // 2, princess_y)
                )

            
                screen.blit(
                    princess,
                    princess_rect
                )

                if player_rect.colliderect(princess_rect) and not princess_touched:

                    princess_touched = True
                    feedback_text = "チュートリアルクリア!"
                    feedback_color = (100, 255, 150)
                    feedback_timer = 180  # 3秒(60fps換算)

                if princess_touched and feedback_timer <= 0:

                    princess_touched = False

                    if hard_mode == 0 :
                        map_number = 1
                    else :
                        map_number = 5

                    load_map(map_number)

                    player_x = width // 2
                    camera_x = 0

                    reset_enemies()

                    feedback_text = "マップ移動中..."
                    feedback_color = (200, 220, 255)
                    feedback_timer = 40

                # DEBUG Princess
                if DEBUG:

                    pygame.draw.rect(
                        screen,
                        (0, 255, 255),
                        princess_rect,
                        2
                    )

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
            # プリンセス演出中のカウントダウン表示
            # =================================================

            if princess_touched:

                seconds_left = feedback_timer // 60 + 1

                count_txt = font_mid.render(
                    f"次のマップへ… {seconds_left}",
                    True,
                    (255, 255, 255)
                )

                screen.blit(
                    count_txt,
                    (width // 2 - 120, height // 3 + 70)
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
                life -= 1
                if life > 0:
                    scene = "gameover"
                else:
                    scene = "titleover"

        # =================================================
        # GAME OVER
        # =================================================

        elif scene == "gameover":

            screen.fill((0, 0, 0))

            screen.blit(
                font_big.render(
                    "continue…",
                    True,
                    (255, 255, 0)
                ),
                (width // 2 - 220, height // 2 - 100)
            )

            screen.blit(
                font_mid.render(
                    f"SCORE: {score}",
                    True,
                    (255, 255, 255)
                ),
                (width // 2 - 100, height // 2 - 20)
            )

            screen.blit(
                font_mid.render(
                    f"残り残機: {life}",
                    True,
                    (255,255,255)
                ),
                (width//2-100, height//2+60)
            )

            if keys[pygame.K_r]:

                map_number = respawn_map

                load_map(map_number)

                camera_x = respawn_x

                init_game()

                scene = "game"

        # =================================================
        # TITLE OVER (残機切れ)
        # =================================================

        elif scene == "titleover":

            screen.fill((0, 0, 0))

            screen.blit(
                font_big.render(
                    "GAME OVER",
                    True,
                    (255, 0, 0)
                ),
                (width // 2 - 220, height // 2 - 140)
            )

            screen.blit(
                font_mid.render(
                    "残機がなくなりました",
                    True,
                    (255, 200, 200)
                ),
                (width // 2 - 150, height // 2 - 60)
            )

            screen.blit(
                font_mid.render(
                    f"FINAL SCORE: {score}",
                    True,
                    (255, 255, 255)
                ),
                (width // 2 - 150, height // 2)
            )

            screen.blit(
                font_mid.render(
                    "Rキーでタイトルへ",
                    True,
                    (200, 200, 200)
                ),
                (width // 2 - 130, height // 2 + 60)
            )

            if keys[pygame.K_r]:

                life = MAX_LIVES

                destroyed_rocks = {}
                defeated_enemies = {}
                score = 0
                input_name = ""

                if demo == 1:
                    map_number = 0
                else:
                    map_number = 1

                respawn_map = map_number
                respawn_x = -300

                load_map(map_number)

                scene = "title"

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

            time_bonus = time_left // 60 * 10
            total_score = score + time_bonus

            screen.blit(
                font_mid.render(
                    f"SCORE: {score}",
                    True,
                    (255, 255, 255)
                ),
                (width // 2 - 100, height // 2 - 20)
            )

            screen.blit(
                font_mid.render(
                    f"TIME BONUS: +{time_bonus}",
                    True,
                    (255, 255, 100)
                ),
                (width // 2 - 100, height // 2 + 20)
            )

            screen.blit(
                font_big.render(
                    f"TOTAL: {total_score}",
                    True,
                    (255, 200, 0)
                ),
                (width // 2 - 150, height // 2 + 60)
            )

            # 名前入力欄
            name_label = font_mid.render(
                "Name: " + input_name + "_",
                True,
                (255, 255, 255)
            )
            screen.blit(name_label, (width // 2 - 150, height // 2 + 120))

            enter_label = font_small.render(
                "Enterでランキング登録",
                True,
                (200, 200, 200)
            )
            screen.blit(enter_label, (width // 2 - 150, height // 2 + 160))

        # =================================================
        # RANKING
        # =================================================

        elif scene == "ranking":

            screen.fill((0, 0, 0))

            title_label = font_big.render(
                "RANKING", 
                True,
                (255, 215, 0)
            )
            screen.blit(title_label, (width // 2 - 150, 60))

            ranking_list = load_ranking()

            for i, entry in enumerate(ranking_list):

                color = (255, 255, 255)
                if i == 0:
                    color = (255, 215, 0)
                elif i == 1:
                    color = (200, 200, 200)
                elif i == 2:
                    color = (205, 127, 50)

                row_y = 160 + i * 45

                # 順位
                rank_label = font_mid.render(f"{i + 1}.", True, color)
                screen.blit(rank_label, (width // 2 - 200, row_y))

                # 名前
                name_label = font_mid.render(entry["name"], True, color)
                screen.blit(name_label, (width // 2 - 140, row_y))

                # スコア（右揃え）
                score_label = font_mid.render(str(entry["score"]), True, color)
                score_rect = score_label.get_rect(
                    topright=(width // 2 + 200, row_y)
                )
                screen.blit(score_label, score_rect)

            hint_label = font_mid.render(
                "Press R to Retry",
                True,
                (255, 255, 255)
            )
            screen.blit(hint_label, (width // 2 - 150, height - 80))

            if keys[pygame.K_r]:

                destroyed_rocks = {}
                defeated_enemies = {}
                respawn_map = map_number
                respawn_x = 0
                score = 0
                input_name = ""

                init_game()
                if demo == 1:
                    map_number = 0
                else:
                    map_number = 1
                load_map(map_number)
                scene = "game"

        # =================================================
        # 画面合成（ゲーム画面を中央に縮小配置）
        # =================================================

        real_screen.fill((15, 15, 15))

        scaled_game = pygame.transform.scale(screen, (game_box_w, game_box_h))
        real_screen.blit(scaled_game, (game_box_x, game_box_y))

        pygame.draw.rect(
            real_screen,
            (255, 255, 255),
            (game_box_x, game_box_y, game_box_w, game_box_h),
            2
        )

        # =================================================
        # カメラワイプ（ゲーム画面の下）
        # =================================================

        if USE_CAMERA and show_camera and cam_surface is not None:

            CAM_SCALE = 0.3

            cam_w = int(cam_surface.get_width() * CAM_SCALE)
            cam_h = int(cam_surface.get_height() * CAM_SCALE)

            scaled_cam = pygame.transform.scale(
                cam_surface,
                (cam_w, cam_h)
            )

            cam_x = width // 2 - cam_w // 2
            cam_y = game_box_y + game_box_h + 20

            real_screen.blit(
                scaled_cam,
                (cam_x, cam_y)
            )

            pygame.draw.rect(
                real_screen,
                (255, 255, 255),
                (cam_x, cam_y, cam_w, cam_h),
                2
            )

        # =================================================
        # HUD（左右の余白）
        # =================================================

        if scene == "game":

            hud_y = game_box_y + 20

            # 左側：HPバー・TIME
            hud_left_x = 30

            pygame.draw.rect(real_screen, (40, 40, 40), (hud_left_x, hud_y, 160, 16))
            pygame.draw.rect(
                real_screen,
                (0, 255, 0),
                (hud_left_x, hud_y, int(160 * max(0, player_hp / PLAYER_MAX_HP)), 16)
            )

            draw_outlined_text(
                real_screen, font_mid,
                f"TIME: {time_left // 60}",
                (255, 255, 255),
                (hud_left_x, hud_y + 30)
            )

            # 右側：SCORE・LIFE
            hud_right_x = game_box_x + game_box_w + 30

            draw_outlined_text(
                real_screen, font_mid,
                f"SCORE: {score}",
                (255, 255, 255),
                (hud_right_x, hud_y)
            )

            draw_outlined_text(
                real_screen, font_mid,
                f"LIFE: {life}",
                (255, 255, 255),
                (hud_right_x, hud_y + 40)
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