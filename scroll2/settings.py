# settings.py

import os

# =========================================================
# 設定
# =========================================================

USE_CAMERA = True
DEBUG = False

# =========================================================
# パス
# =========================================================

BASE_DIR = os.path.dirname(__file__)

SOUND_DIR = os.path.join(BASE_DIR, "sounds")
IMAGE_DIR = os.path.join(BASE_DIR, "image")

# =========================================================
# 基本設定
# =========================================================

width, height = 1200, 700

floor_y = 600
size = 24
fps = 60

PLAYER_W = 32
PLAYER_H = 48

WALK_SPEED = 2
RUN_SPEED = 10

jump_power = -28
gravity = 2

PLAYER_MAX_HP = 100
ENEMY_MAX_HP = 3

INVINCIBLE_TIME = 120
ATTACK_TIME = 12
FLASH_TIME = 6

FALL_DEATH_Y = floor_y + 300

TIME_LIMIT = 500 * 60
time_left = TIME_LIMIT