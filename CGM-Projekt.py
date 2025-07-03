import sqlite3
connection = sqlite3.connect('scores_CGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXITS highscores (
        name TEXT,
        score INTEGER,
        FOREIGN KEY(spieler_id) REFERENCES spieler(id)
)''')

cursor.execute("INSERT INTO Spielstand (spieler_id, name, score) VALUES (1, Spieler1, 0)")
cursor.execute("INSERT INTO Spielstand (spieler_id, name, score) VALUES (2, Spieler2, 0)")
connection.commit()

import pygame
import random
import sys

# Grundeinstellungen
pygame.init()
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 150, 255)
GROUND_Y = HEIGHT - 50
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump & Run mit Boden-Ducken und Luft-Hindernissen")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Spielerklasse
class Player:
    def __init__(self):
        self.width = 50
        self.normal_height = 50
        self.duck_height = 30
        self.height = self.normal_height
        self.x = 100
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.jump_strength = -12
        self.gravity = 0.6
        self.on_ground = True
        self.is_ducking = False

    def jump(self):
        if self.on_ground and not self.is_ducking:
            self.vel_y = self.jump_strength
            self.on_ground = False

    def duck(self, is_pressed):
        if self.on_ground:
            self.is_ducking = is_pressed
            if self.is_ducking:
                self.height = self.duck_height
                self.y = GROUND_Y - self.height
            else:
                self.height = self.normal_height
                self.y = GROUND_Y - self.height

    def update(self):
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
            self.is_ducking = False
            self.height = self.normal_height

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Hindernisklasse mit Stacheln
class Obstacle:
    def __init__(self, speed, kind):
        self.kind = kind  # 'ground' oder 'air'
        self.speed = speed
        self.width = 30
        self.height = 40
        self.x = WIDTH
        if kind == "ground":
            self.y = GROUND_Y - self.height
        else:  # Luft-Hindernis (z.B. fliegende Stacheln)
            self.y = GROUND_Y - 80

    def update(self):
        self.x -= self.speed

    def draw(self):
        color = (200, 0, 0) if self.kind == "ground" else (255, 120, 0)
        point1 = (self.x, self.y + self.height)
        point2 = (self.x + self.width // 2, self.y)
        point3 = (self.x + self.width, self.y + self.height)
        pygame.draw.polygon(screen, color, [point1, point2, point3])

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Initialisierung
player = Player()
obstacles = []
spawn_timer = 0
distance = 0
game_over = False
speed = 6
speed_increase_rate = 0.002

# Spielschleife
while True:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Steuerung
    keys = pygame.key.get_pressed()
    if not game_over:
        player.duck(keys[pygame.K_LCTRL])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player = Player()
                obstacles = []
                spawn_timer = 0
                distance = 0
                speed = 6
                game_over = False

    if not game_over:
        # Geschwindigkeit erhöhen
        speed += speed_increase_rate

        # Update
        player.update()

        # Hindernisse erzeugen
        spawn_timer += 1
        if spawn_timer > 90:
            spawn_timer = 0
            kind = "ground" if distance < 200 else random.choice(["ground", "air"])
            obstacles.append(Obstacle(speed, kind))

        for obs in obstacles:
            obs.speed = speed
            obs.update()

        obstacles = [obs for obs in obstacles if not obs.is_off_screen()]

        # Kollision prüfen
        for obs in obstacles:
            if player.get_rect().colliderect(obs.get_rect()):
                if obs.kind == "ground" and player.y + player.height >= obs.y:
                    game_over = True
                elif obs.kind == "air":
                    if not player.is_ducking:
                        game_over = True

        # Meter zählen
        distance += 1

    # Zeichnen
    player.draw()
    for obs in obstacles:
        obs.draw()
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    # Meteranzeige
    meter_text = font.render(f"Meter: {distance}", True, BLACK)
    screen.blit(meter_text, (10, 10))

    if game_over:
        over_text = font.render("Game Over! Drücke R zum Neustart", True, (200, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()