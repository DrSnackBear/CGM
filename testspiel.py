import pygame
import sys

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bewegung & Schießen")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

player_size = 50
player_x = width // 2
player_y = height // 2
player_speed = 5

# Liste für Kugeln
bullets = []
bullet_speed = 10
bullet_width = 5
bullet_height = 10

clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Kugel abschießen bei Leertaste (keydown)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Kugel oben am Spieler starten
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Kugeln bewegen und zeichnen
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed  # nach oben bewegen
        if bullet[1] < 0:
            bullets.remove(bullet)  # entfernen, wenn oben raus
        else:
            pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

    # Spieler zeichnen
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    pygame.display.flip()

pygame.quit()
sys.exit()
