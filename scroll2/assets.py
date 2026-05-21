# assets.py

import pygame
import os
import controller

from settings import *

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

pygame.mixer.music.load(
    os.path.join(SOUND_DIR, "bgm.wav")
)

pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# =========================================================
# SE
# =========================================================

sounds = {
    "fire": pygame.mixer.Sound(
        os.path.join(SOUND_DIR, "slash_fire.wav")
    ),

    "water": pygame.mixer.Sound(
        os.path.join(SOUND_DIR, "slash_water.wav")
    ),

    "grass": pygame.mixer.Sound(
        os.path.join(SOUND_DIR, "slash_grass.wav")
    ),
}

# =========================================================
# カメラ
# =========================================================

pen_con = controller.PenlightController(camera_id=0)

last_element = "none"
detected = False

# =========================================================
# 画像
# =========================================================

bg = pygame.image.load(
    os.path.join(IMAGE_DIR, "bg.png")
).convert()

block = pygame.image.load(
    os.path.join(IMAGE_DIR, "block.png")
).convert_alpha()

princess = pygame.image.load(
    os.path.join(IMAGE_DIR, "princess.png")
).convert_alpha()

player_imgs = [
    pygame.image.load(
        os.path.join(IMAGE_DIR, "player0.png")
    ).convert_alpha(),

    pygame.image.load(
        os.path.join(IMAGE_DIR, "player1.png")
    ).convert_alpha(),

    pygame.image.load(
        os.path.join(IMAGE_DIR, "player0.png")
    ).convert_alpha(),

    pygame.image.load(
        os.path.join(IMAGE_DIR, "player2.png")
    ).convert_alpha(),
]

enemy_base = pygame.image.load(
    os.path.join(IMAGE_DIR, "devil.png")
).convert_alpha()

enemy_base = pygame.transform.scale(
    enemy_base,
    (100, 100)
)

warp_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "warp.png")
).convert_alpha()

warp_img = pygame.transform.scale(
    warp_img,
    (64, 64)
)

takibi_off_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "takibi_off.png")
).convert_alpha()

takibi_off_img = pygame.transform.scale(
    takibi_off_img,
    (64, 64)
)

takibi_on_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "takibi_on.png")
).convert_alpha()

takibi_on_img = pygame.transform.scale(
    takibi_on_img,
    (64, 64)
)

# =========================================================
# 色
# =========================================================

attr_colors = {
    "fire": (255, 80, 80),
    "water": (80, 120, 255),
    "grass": (80, 255, 120)
}