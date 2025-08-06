import pygame
import time
import random
import math
import sys

pygame.font.init()

pygame.mixer.init()
pygame.mixer.music.load("./sounds/bg_start_sound.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, fade_ms=2000)

WIDTH, HEIGHT = 500,800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")

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

def main_menu(background_stars):
    font = pygame.font.SysFont("comicsans", 60)
    button_color = (0, 200, 0)
    text_color = (255, 255, 255)
    bg_color = (0, 0, 0)

    while True:
        WIN.fill(bg_color)

        for star in background_stars:
            star.move(speed_multiplier=0.3)
            star.draw(WIN)

        title_text = font.render("SPACE DODGE", True, text_color)
        WIN.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))

        start_text = font.render("START", True, text_color)
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        pygame.draw.rect(WIN, button_color, start_rect.inflate(40, 20))
        WIN.blit(start_text, start_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    return

        pygame.display.update()

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
        self.angle = (self.angle + self.rotation_speed) % 360

    def off_screen(self, screen_height):
        return self.rect.y > screen_height

    def collide(self, obj):
        return self.rect.colliderect(obj)

class StarBackground:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(1, 3)

    def move(self, speed_multiplier=1.0):
        self.y += self.speed * speed_multiplier
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.size)

def transition_scene(background_stars):
    clock = pygame.time.Clock()
    ship_y = HEIGHT + 100  # Bắt đầu dưới màn hình
    target_y = int(HEIGHT * 0.75)
    ship_x = WIDTH // 2 - PLAYER_WIDTH // 2
    speed = 5

    while ship_y > target_y:
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for star in background_stars:
            star.move(speed_multiplier=1.0)
            star.draw(WIN)

        ship_rect = pygame.Rect(ship_x, ship_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        WIN.blit(SHIP_IMG, ship_rect)

        ship_y -= speed
        pygame.display.update()

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

def draw(player, eLapsed_time, stars, player_visible, player_angle, background_stars):
    WIN.fill((0, 0, 0))  # Nền đen

    for bg_star in background_stars:
        bg_star.move()
        bg_star.draw(WIN)

    if eLapsed_time is not None:
        time_text = FONT.render(f"Time: {round(eLapsed_time)}s", 1, "white")
        WIN.blit(time_text, (10, 10))

    if player_visible:
        rotated_ship = pygame.transform.rotate(SHIP_IMG, player_angle)
        new_rect = rotated_ship.get_rect(center=player.center)
        WIN.blit(rotated_ship, new_rect.topleft)

    for star in stars:
        star.draw(WIN)
    
    pygame.display.update()

def run_game(background_stars):
    base_player_y = int(HEIGHT * 0.75)
    player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, base_player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_angle = 0
    player_visible = True

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    final_time = None

    stars = []
    hit = False
    next_spawn_time = time.time() + random.uniform(0.2, 1.5)
    all_sprites = pygame.sprite.Group()

    explosion_img = pygame.transform.scale(
        pygame.image.load("./imgs/explosion.png").convert_alpha(),
        (120, 120)
    )

    star_speed = STAR_VEL
    player_speed = PLAYER_VEL

    while True:
        dt = clock.tick(60)

        if not hit:
            float_offset = math.sin(pygame.time.get_ticks() * 0.0035) * 5
            player.y = base_player_y + float_offset
            elapsed_time = time.time() - start_time
        else:
            if final_time is None:
                final_time = elapsed_time

        if time.time() >= next_spawn_time and not hit:
            added = 0
            stars_to_add = random.randint(1, 4)
            max_attempts = 100
            attempts = 0

            while added < stars_to_add and attempts < max_attempts:
                variant = random.choice(STAR_VARIANTS)
                star_x = random.randint(0, WIDTH - variant["width"])
                star_y = -variant["height"]

                if is_far_enough(star_x, star_y, variant["width"], variant["height"], stars, min_distance=50):
                    star = Star(star_x, star_y, variant["width"], variant["height"], variant["image"])
                    stars.append(star)
                    added += 1

                attempts += 1

            next_spawn_time = time.time() + random.uniform(0.3, 1.5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if hit and event.type == pygame.MOUSEBUTTONDOWN:
                return True

        keys = pygame.key.get_pressed()
        if not hit:
            if keys[pygame.K_LEFT] and player.x - player_speed >= 0:
                player.x -= PLAYER_VEL
                player_angle = min(player_angle + 2, 20)  # Nghiêng trái (góc dương)
            elif keys[pygame.K_RIGHT] and player.x + player_speed + player.width <= WIDTH:
                player.x += PLAYER_VEL
                player_angle = max(player_angle - 2, -20)  # Nghiêng phải (góc âm)
            else:
                # Tự động trở về trạng thái thẳng
                if player_angle > 0:
                    player_angle -= 1
                elif player_angle < 0:
                    player_angle += 1

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

        draw(player, final_time if hit else elapsed_time, stars, player_visible, player_angle, background_stars)

        if hit:
            current_volume = pygame.mixer.music.get_volume()
            player_visible = False
            all_sprites.update()
            all_sprites.draw(WIN)
            lost_text = FONT.render("CLICK TO RETRY", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            if current_volume > 0:
                new_volume = max(0, current_volume - 0.005)
                pygame.mixer.music.set_volume(new_volume)
            pygame.display.update()

def main():
    pygame.init()
    background_stars = [StarBackground() for _ in range(100)]
    main_menu(background_stars)
    transition_scene(background_stars)
    while True:
        play_again = run_game(background_stars)
        if not play_again:
            break
        else:
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
