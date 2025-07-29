import pygame
import time
import random
import math

pygame.font.init()

pygame.mixer.init()
pygame.mixer.music.load("./sounds/bg_sound.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")
BG =pygame.transform.scale(pygame.image.load("./imgs/bg.jpeg"), (HEIGHT, WIDTH))


PLAYER_WIDTH = 50
PLAYER_HEIGHT = 60


SHIP_IMG = pygame.image.load("./imgs/spaceship.png")
SHIP_IMG = pygame.transform.scale(SHIP_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))


PLAYER_VEL = 4


STAR_WIDTH = 10
STAR_HEIGHT = 20
STAR_VEL = 3

STAR_VARIANTS = [
    {"image": "./imgs/star_small.png", "width": 30, "height": 40},
    {"image": "./imgs/star_large.png", "width": 40, "height": 50},
    {"image": "./imgs/star_squareSmall.png", "width": 30, "height": 40},
    {"image": "./imgs/star_squareLarge.png", "width": 40, "height": 50},
]

FONT = pygame.font.SysFont("comicsans", 30)

def is_close(player_rect, star_rect, threshold):
    player_center = player_rect.center
    star_center = star_rect.center

    distance = math.hypot(player_center[0] - star_center[0], player_center[1] - star_center[1])
    return distance < threshold

def is_far_enough(new_x, new_y, new_width, new_height, stars, min_distance=40):
    new_center = (new_x + new_width // 2, new_y + new_height // 2)
    for star in stars:
        existing_center = star.rect.center
        dist = math.hypot(new_center[0] - existing_center[0], new_center[1] - existing_center[1])
        if dist < min_distance:
            return False
    return True

class Star:
    def __init__(self, x, y, width, height, image_path):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (width, height))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.angle = random.randint(0, 360)  # Góc xoay ban đầu
        self.rotation_speed = random.choice([-5, -3, -2, 2, 3, 5])

    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        window.blit(rotated_image, new_rect.topleft)

    def move(self, speed):
        self.rect.y += speed
        

    def off_screen(self, screen_height):
        return self.rect.y > screen_height

    def collide(self, obj):
        return self.rect.colliderect(obj)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, position, image, duration=30):  # duration = số frame tồn tại
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)
        self.timer = duration

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

def draw(player, eLapsed_time, stars, player_visible):
    WIN.blit(BG, (0, 0))

    if eLapsed_time is not None:
        time_text = FONT.render(f"Time: {round(eLapsed_time)}s", 1, "white")
        WIN.blit(time_text, (10, 10))

    if player_visible:
        WIN.blit(SHIP_IMG, (player.x, player.y))

    for star in stars:
        star.draw(WIN)
    
    pygame.display.update()

def run_game():
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_visible = True

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    final_time = None
    start_count = 0

    stars = []
    hit = False
    all_sprites = pygame.sprite.Group()

    explosion_img = pygame.transform.scale(
        pygame.image.load("./imgs/explosion.png").convert_alpha(),
        (120, 120)
    )

    difficulty_timer = time.time()
    star_speed = STAR_VEL
    player_speed = PLAYER_VEL
    spawn_interval = 4000

    while True:
        dt = clock.tick(60)
        start_count += dt

        if not hit:
            elapsed_time = time.time() - start_time
        else:
            if final_time is None:
                final_time = elapsed_time  

        # Tăng độ khó mỗi 30 giây
        if time.time() - difficulty_timer >= 30:
            difficulty_timer = time.time()

            # Tăng tốc độ rơi
            star_speed += 1

            # Giảm thời gian spawn (tối thiểu 700ms)
            spawn_interval = max(1000, spawn_interval - 150)

            # Tăng tốc độ player (tối đa 10)
            player_speed = min(10, player_speed + 1)

            print(f"[+] Tăng độ khó! Star speed: {star_speed}, Spawn interval: {spawn_interval}ms, Player speed: {player_speed}")

        if start_count > spawn_interval and not hit:
            added = 0
            max_stars_to_add = random.randint(3, 8)
            max_attempts = 100
            attempts = 0

            while added < max_stars_to_add and attempts < max_attempts:
                variant = random.choice(STAR_VARIANTS)
                star_x = random.randint(0, WIDTH - variant["width"])
                star_y = -variant["height"]

                if is_far_enough(star_x, star_y, variant["width"], variant["height"], stars, min_distance=50):
                    star = Star(star_x, star_y, variant["width"], variant["height"], variant["image"])
                    stars.append(star)
                    added += 1

                attempts += 1

            spawn_interval = max(200, spawn_interval - 50)
            start_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if hit and event.type == pygame.MOUSEBUTTONDOWN:
                return True

        keys = pygame.key.get_pressed()
        if not hit:
            if keys[pygame.K_LEFT] and player.x - player_speed >= 0:
                player.x -= PLAYER_VEL
            if keys[pygame.K_RIGHT] and player.x + player_speed + player.width <= WIDTH:
                player.x += PLAYER_VEL

        for star in stars[:]:
            star.move(star_speed)
            if star.off_screen(HEIGHT):
                stars.remove(star)
            elif not hit and is_close(player, star.rect, threshold=40):
                stars.remove(star)
                hit = True
                explosion_sound = pygame.mixer.Sound("./sounds/explosion_sound.mp3")
                explosion_sound.set_volume(0.7)
                explosion_sound.play()
                explosion = Explosion(star.rect.center, explosion_img)
                all_sprites.add(explosion)
                break

        draw(player, final_time if hit else elapsed_time, stars, player_visible)

        if hit:
            current_volume = pygame.mixer.music.get_volume()
            player_visible = False
            all_sprites.update()
            all_sprites.draw(WIN)
            lost_text = FONT.render("YOU LOST - Click to Retry", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            if current_volume > 0:
                new_volume = max(0, current_volume - 0.005)
                pygame.mixer.music.set_volume(new_volume)
            pygame.display.update()

def main():
    pygame.init()
    while True:
        play_again = run_game()
        if not play_again:
            break
        else:
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()