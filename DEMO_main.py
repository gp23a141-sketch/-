import pygame
import sys
import cv2
import controller  # controller.py を読み込む

# 画面サイズ (テスト用)
width, height = 800, 600

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sword Reflection Test")
clock = pygame.time.Clock()

# コントローラーの初期化
pen_con = controller.PenlightController(camera_id=0)

# 画像の読み込み
try:
    # 剣のデータ
    swords = {
        "default": pygame.image.load("image/sword.png").convert_alpha(),
        "fire":    pygame.image.load("image/fire.png").convert_alpha(),
        "water":   pygame.image.load("image/water.png").convert_alpha(),
        "grass":   pygame.image.load("image/wood.png").convert_alpha(), # grass検出時はwood
    }
    
    # 画像を少し大きく表示して見やすくする（2倍）
    for key in swords:
        w, h = swords[key].get_size()
        swords[key] = pygame.transform.scale(swords[key], (w * 2, h * 2))

except pygame.error as e:
    print(f"画像読み込みエラー: {e}")
    pygame.quit()
    sys.exit()

font = pygame.font.Font(None, 50)

def game_loop():
    running = True
    current_element = "none"

    while running:
        # 1. カメラ認識更新
        is_detected, pos, element, debug_frame = pen_con.update()
        current_element = element
        

        # 2. イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # ESCキーでも終了できるようにする
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 3. 描画処理
        screen.fill((30, 30, 30))  # 背景をダークグレーに

        # 剣の選択
        if current_element in swords:
            display_sword = swords[current_element]
        else:
            display_sword = swords["default"]

        # 画面中央に配置
        rect = display_sword.get_rect(center=(width // 2, height // 2))
        screen.blit(display_sword, rect)

        # テキスト情報表示
        status_text = f"Status: {current_element.upper()}"
        
        # 文字色を属性に合わせる
        text_color = (255, 255, 255)
        if current_element == "fire": text_color = (255, 50, 50)
        elif current_element == "water": text_color = (50, 100, 255)
        elif current_element == "grass": text_color = (50, 255, 50)

        text_surf = font.render(status_text, True, text_color)
        text_rect = text_surf.get_rect(center=(width // 2, height // 2 + 100))
        screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    try:
        game_loop()
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        pen_con.release()
        pygame.quit()
        sys.exit()