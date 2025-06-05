import pygame
import sys

# Pygame initialisieren
pygame.init()

# Fenstergröße und -titel
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bewegung mit Pfeiltasten")

# Farben
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Figur-Eigenschaften
player_size = 50
player_x = width // 2
player_y = height // 2
player_speed = 5

# Haupt-Game-Loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.fill(WHITE)

    # Eingaben verarbeiten
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tastenabfrage
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Figur zeichnen
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # Anzeige aktualisieren
    pygame.display.flip()

# Spiel beenden
pygame.quit()
sys.exit()

