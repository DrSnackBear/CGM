import pygame
import random
import sys

# Grundeinstellungen
pygame.init()
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 150, 255)
OBSTACLE_COLOR = (255, 50, 50)
GROUND_Y = HEIGHT - 50
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endloses Jump and Run (mit Meter und steigender Geschwindigkeit)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Spielerklasse
class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.jump_strength = -12
        self.gravity = 0.6
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False

    def update(self):
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Hindernisklasse
class Obstacle:
    def __init__(self, speed):
        self.width = 40
        self.height = 60
        self.x = WIDTH
        self.y = GROUND_Y - self.height
        self.speed = speed

    def update(self):
        self.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_COLOR, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Initialisierung
player = Player()
obstacles = []
spawn_timer = 0
distance = 0  # gemessene Meter
game_over = False
speed = 6
speed_increase_rate = 0.002  # Geschwindigkeit steigt langsam pro Tick

# Spielschleife
while True:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Eventhandling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset
                player = Player()
                obstacles = []
                spawn_timer = 0
                distance = 0
                speed = 6
                game_over = False

    if not game_over:
        # Geschwindigkeit erhöhen
        speed += speed_increase_rate

        # Spielerupdate
        player.update()

        # Hindernisse erzeugen
        spawn_timer += 1
        if spawn_timer > 90:
            spawn_timer = 0
            if random.random() < 0.8:
                obstacles.append(Obstacle(speed))

        # Hindernisse aktualisieren
        for obs in obstacles:
            obs.speed = speed
            obs.update()

        # Hindernisse entfernen
        obstacles = [obs for obs in obstacles if not obs.is_off_screen()]

        # Kollision prüfen
        for obs in obstacles:
            if player.get_rect().colliderect(obs.get_rect()):
                game_over = True

        # Meter zählen (1 Tick = 1 Meter für Einfachheit)
        distance += 1

    # Zeichnen
    player.draw()
    for obs in obstacles:
        obs.draw()
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    # Meter-Anzeige
    meter_text = font.render(f"Meter: {distance}", True, BLACK)
    screen.blit(meter_text, (10, 10))

    # Game Over-Anzeige
    if game_over:
        over_text = font.render("Game Over! Drücke R zum Neustart", True, (200, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()