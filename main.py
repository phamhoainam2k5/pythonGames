import pygame
import time
import random
import math
pygame.font.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")
BG =pygame.transform.scale(pygame.image.load("./imgs/bg.jpeg"), (HEIGHT, WIDTH))

# Size player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 60

# PNG SPACESHIP
SHIP_IMG = pygame.image.load("./imgs/spaceship.png")
SHIP_IMG = pygame.transform.scale(SHIP_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))

# PLAYER MOVEMENT SPEED PER FRAME
PLAYER_VEL = 5

# SIZE STAR
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

class Star:
    def __init__(self, x, y, width, height, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

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

    time_text = FONT.render(f"Time: {round(eLapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    if player_visible:
        WIN.blit(SHIP_IMG, (player.x, player.y))

    for star in stars:
        star.draw(WIN)
    
    pygame.display.update()

def main():
    run = True

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_visible = True

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    start_add_increment = 2000
    start_count = 0

    stars = []
    hit = False
    all_sprites = pygame.sprite.Group()

    explosion_img = pygame.transform.scale(
        pygame.image.load("./imgs/explosion.png").convert_alpha(),
        (120, 120)
    )

    while run:
        dt = clock.tick(60)
        start_count += dt
        elapsed_time = time.time() - start_time

        if start_count > start_add_increment:
            for _ in range(5):
                variant = random.choice(STAR_VARIANTS)
                star_x = random.randint(0, WIDTH - variant["width"])
                star = Star(star_x, -variant["height"], variant["width"], variant["height"], variant["image"])
                stars.append(star)
            
            start_add_increment = max(200, start_add_increment - 50)
            start_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        for star in stars[:]:
            star.move(STAR_VEL)
            if star.off_screen(HEIGHT):
                stars.remove(star)
            elif is_close(player, star.rect, threshold= 40):
                stars.remove(star)
                hit = True

                explosion = Explosion(star.rect.center, explosion_img)
                all_sprites.add(explosion)
                break

        if hit:
            player_visible = False
            draw(player, elapsed_time, stars, player_visible)
            all_sprites.update()
            all_sprites.draw(WIN)
            lost_text = FONT.render("YOU LOST", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))    
            pygame.display.update()
            pygame.time.delay(4000)
            break

        draw(player, elapsed_time, stars, player_visible)

    pygame.quit()

if __name__ == "__main__":
    main()