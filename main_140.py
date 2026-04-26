import pygame
import sys
import os
import controller

# ===== 設定 =====
USE_CAMERA = True
DEBUG = False

# ===== パス =====
BASE_DIR = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
IMAGE_DIR = os.path.join(BASE_DIR, "image")

# ===== 基本設定 =====
WIDTH, HEIGHT = 1200, 720
FLOOR_Y = 600
SIZE = 24
FPS = 60

SPEED = 10
JUMP_POWER = -28
GRAVITY = 2

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

# ===== 初期化 =====
def init_game():
    global camera_x, pl_y, pl_yp, pl_jump
    global player_hp, invincible, player_attr, enemies

    camera_x = 0
    pl_y = FLOOR_Y
    pl_yp = 0
    pl_jump = False

    player_hp = 5
    invincible = 0
    player_attr = "fire"

    enemies = []
    attrs = ["fire", "water", "grass"]
    for i in range(6):
        img = enemy_base.copy()
        img.fill(attr_colors[attrs[i % 3]], special_flags=pygame.BLEND_RGBA_MULT)
        enemies.append([800 + i * 300, 3, 3, attrs[i % 3], img])

scene = "title"

def main():
    global scene, detected, last_element
    global camera_x, pl_y, pl_yp, pl_jump
    global player_hp, invincible, player_attr

    attack = False
    attack_timer = 0
    hit_enemies = set()
    timer = 0

    init_game()

    while True:
        timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if scene == "title" and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    scene = "game"
                    camera_x = 0  # ← スタート時リセット

        keys = pygame.key.get_pressed()

        # ===== タイトル =====
        if scene == "title":
            screen.blit(bg, (0, 0))

            camera_x += 1  # ← スクロール

            start = int(camera_x // SIZE)
            end = start + WIDTH // SIZE + 2

            # 地面
            for i in range(start, end):
                screen.blit(block, (i * SIZE - camera_x, FLOOR_Y + 40))

            # プレイヤー
            ani = (timer // 4) % 4
            screen.blit(player_imgs[ani],
                        player_imgs[ani].get_rect(center=(WIDTH//2, FLOOR_Y)))

            # 暗幕
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # タイトル文字
            screen.blit(font_big.render("My Action Game", True, (255,255,255)),
                        (WIDTH//2-250, HEIGHT//2-120))

            if (timer // 30) % 2 == 0:
                screen.blit(font_mid.render("Click to Start", True, (200,200,200)),
                            (WIDTH//2-150, HEIGHT//2-40))

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

            move_speed = SPEED * 2 if keys[pygame.K_LSHIFT] else SPEED

            if keys[pygame.K_RIGHT]:
                camera_x += move_speed
            if keys[pygame.K_LEFT]:
                camera_x = max(0, camera_x - move_speed)

            if keys[pygame.K_SPACE] and not pl_jump:
                pl_jump = True
                pl_yp = JUMP_POWER

            pl_y += pl_yp
            pl_yp += GRAVITY

            if pl_y >= FLOOR_Y:
                pl_y = FLOOR_Y
                pl_yp = 0
                pl_jump = False

            if invincible > 0:
                invincible -= 1

            # 当たり判定
            atk_rect = pygame.Rect(WIDTH//2-80, pl_y-80, 160, 100)
            player_rect = pygame.Rect(WIDTH//2-16, pl_y-48, 32, 48)

            new_enemies = []

            for ex, hp, max_hp, attr, img in enemies:
                screen_x = ex - camera_x
                enemy_rect = pygame.Rect(screen_x, FLOOR_Y-100, 100, 100)

                if attack and attack_timer > 7:
                    if atk_rect.colliderect(enemy_rect):
                        if ex not in hit_enemies:
                            hit_enemies.add(ex)
                            hp -= 1
                            sounds[player_attr].play()

                if player_rect.colliderect(enemy_rect):
                    if invincible == 0:
                        player_hp -= 1
                        invincible = 120

                if hp > 0:
                    new_enemies.append([ex, hp, max_hp, attr, img])

            enemies[:] = new_enemies

            if attack:
                attack_timer -= 1
                if attack_timer <= 0:
                    attack = False

            # ===== 描画 =====
            screen.blit(bg, (0, 0))

            start = int(camera_x // SIZE)
            end = start + WIDTH // SIZE + 2
            for i in range(start, end):
                screen.blit(block, (i * SIZE - camera_x, FLOOR_Y + 40))

            ani = (timer // 4) % 4
            if invincible == 0 or invincible % 10 < 5:
                screen.blit(player_imgs[ani],
                            player_imgs[ani].get_rect(center=(WIDTH//2, pl_y)))

            # 敵
            for ex, hp, max_hp, attr, img in enemies:
                screen_x = ex - camera_x
                if -120 < screen_x < WIDTH:
                    screen.blit(img, (screen_x, FLOOR_Y-100))

                    bar_w = 100
                    hp_ratio = hp / max_hp
                    pygame.draw.rect(screen, (100,100,100), (screen_x, FLOOR_Y-110, bar_w, 8))
                    pygame.draw.rect(screen, (0,255,0), (screen_x, FLOOR_Y-110, bar_w * hp_ratio, 8))

            # ★ 攻撃時のみ当たり判定表示 ★
            if attack and attack_timer > 7:
                color = attr_colors[player_attr]

                surf = pygame.Surface((atk_rect.width, atk_rect.height), pygame.SRCALPHA)
                surf.fill((*color, 120))
                screen.blit(surf, atk_rect.topleft)

                pygame.draw.rect(screen, color, atk_rect, 2)

            # UI
            screen.blit(font_mid.render(f"HP: {player_hp}", True, (255,255,255)), (20,20))
            screen.blit(font_mid.render(f"ATTR: {player_attr}", True, attr_colors[player_attr]), (20,60))
            screen.blit(font_fps.render(f"FPS: {int(clock.get_fps())}", True, (0,255,0)), (WIDTH-120, 10))

            if player_hp <= 0:
                scene = "gameover"

        # ===== ゲームオーバー =====
        elif scene == "gameover":
            screen.fill((0,0,0))
            screen.blit(font_big.render("GAME OVER", True, (255,0,0)),
                        (WIDTH//2-200, HEIGHT//2-100))
            screen.blit(font_mid.render("Press R to Retry", True, (200,200,200)),
                        (WIDTH//2-150, HEIGHT//2))

            if keys[pygame.K_r]:
                init_game()
                scene = "game"

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()