import pygame
import sys

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
GRAVITY = 0.5
JUMP_STRENGTH = -10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Einfaches Jump and Run")
clock = pygame.time.Clock()

# Spielerklasse
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 150
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        # Schwerkraft
        self.vel_y += GRAVITY
        dy = self.vel_y

        # Bewegung und Kollision mit Plattformen
        self.on_ground = False
        self.rect.x += dx
        self.rect.y += dy
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH

# Plattformklasse
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Gruppen
player = Player()
platforms = [
    Platform(0, HEIGHT - 40, WIDTH, 40),
    Platform(200, 450, 150, 20),
    Platform(400, 350, 150, 20),
    Platform(600, 250, 150, 20)
]

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
for plat in platforms:
    all_sprites.add(plat)

# Spiel-Loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    player.update(platforms)

    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
