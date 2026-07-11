# assets.py

import pygame
import os
import cv2
import controller_test

from settings import *

# =========================================================
# 初期化
# =========================================================

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("My Action Game")

clock = pygame.time.Clock()

# =========================================================
# フォント
# =========================================================

font_big = pygame.font.SysFont(None, 80)
font_mid = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 28)

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

pen_con = controller_test.PenlightController(camera_id=1)

last_element = "none"
detected = False

# =========================================================
# 画像
# =========================================================

bg = pygame.image.load(
    os.path.join(IMAGE_DIR, "bg.png")
).convert()

bg = pygame.transform.scale(bg, (width, height))

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

bakudan_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "bakudan.png")
).convert_alpha()

bakudan_img = pygame.transform.scale(
    bakudan_img,
    (64, 64)
)

bakudan_chakka_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "bakudan_chakka.png")
).convert_alpha()

bakudan_chakka_img = pygame.transform.scale(
    bakudan_chakka_img,
    (64, 64)
)

bakuhatu_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "bakuhatsu_01.png")
).convert_alpha()

bakuhatu_img = pygame.transform.scale(
    bakuhatu_img,
    (128, 128)
)

iwa_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "iwa.png")
).convert_alpha()

iwa_img = pygame.transform.scale(
    iwa_img,
    (64, 64)
)

hi_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "hi.png")
).convert_alpha()

hi_img = pygame.transform.scale(
    hi_img,
    (64, 64)
)

kareki_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "kareki.png")
).convert_alpha()

kareki_img = pygame.transform.scale(
    kareki_img,
    (64, 64)
)

ki_img = pygame.image.load(
    os.path.join(IMAGE_DIR, "ki.png")
).convert_alpha()

ki_img = pygame.transform.scale(
    ki_img,
    (128, 128)
)

sword_imgs = {
    "fire": pygame.image.load(
        os.path.join(IMAGE_DIR, "sword_fire.png")
    ).convert_alpha(),

    "water": pygame.image.load(
        os.path.join(IMAGE_DIR, "sword_water.png")
    ).convert_alpha(),

    "grass": pygame.image.load(
        os.path.join(IMAGE_DIR, "sword_grass.png")
    ).convert_alpha(),
}

SWORD_SIZE = (90, 90)  # (幅, 高さ) お好みで調整してください

sword_imgs = {
    key: pygame.transform.scale(img, SWORD_SIZE)
    for key, img in sword_imgs.items()
}

sword_imgs_flipped = {
    key: pygame.transform.flip(img, True, False)
    for key, img in sword_imgs.items()
}

# =========================================================
# 色
# =========================================================

attr_colors = {
    "fire": (255, 80, 80),
    "water": (80, 120, 255),
    "grass": (80, 255, 120),
    "purple": (180, 80, 255),
}