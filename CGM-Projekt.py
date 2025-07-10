import pygame
import random
import sys
import sqlite3

# --- Datenbank Setup ---
connection = sqlite3.connect('scores_CGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS highscores (
        name TEXT PRIMARY KEY,
        score INTEGER
    )
''')
connection.commit()

# Vorhandene Duplikate bereinigen, falls vorhanden (nur bester Score pro Spieler)
def clean_duplicates():
    # Hole alle Namen mit mehrfachen Einträgen
    cursor.execute('''
        SELECT name, MAX(score) as max_score
        FROM highscores
        GROUP BY name
        HAVING COUNT(*) > 1
    ''')
    duplicates = cursor.fetchall()
    for name, max_score in duplicates:
        # Lösche alle Einträge mit dem Namen
        cursor.execute('DELETE FROM highscores WHERE name = ?', (name,))
        # Schreibe den besten Score zurück
        cursor.execute('INSERT INTO highscores (name, score) VALUES (?, ?)', (name, max_score))
    connection.commit()

clean_duplicates()

def get_highscore(name):
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result else 0

def save_score(name, score):
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
    else:
        if score > result[0]:
            cursor.execute("UPDATE highscores SET score = ? WHERE name = ?", (score, name))
    connection.commit()

def get_all_highscores():
    cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC")
    return cursor.fetchall()

player_name = "Spieler1"
highscore = get_highscore(player_name)
restart_count = 0

# --- Pygame Setup ---
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

# --- Münzbild laden ---
coin_image = pygame.image.load("coin.png").convert_alpha()
coin_image = pygame.transform.scale(coin_image, (30, 30))

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
            if not self.on_ground:
                self.is_ducking = False
                self.height = self.normal_height

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, speed, kind):
        self.kind = kind
        self.speed = speed
        self.width = 30
        self.height = 40
        self.x = WIDTH
        if kind == "ground":
            self.y = GROUND_Y - self.height
        else:
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

class Coin:
    def __init__(self, speed):
        self.radius = 15
        self.speed = speed
        self.x = WIDTH
        self.y = GROUND_Y - 100

    def update(self):
        self.x -= self.speed

    def draw(self):
        screen.blit(coin_image, (int(self.x - self.radius), int(self.y - self.radius)))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def is_off_screen(self):
        return self.x + self.radius < 0

player = Player()
obstacles = []
coins = []
spawn_timer = 0
coin_spawn_timer = 0
distance = 0
coins_collected = 0
game_over = False
speed = 6
speed_increase_rate = 0.002

show_instructions = True
show_highscore_table = False

def draw_highscore_table():
    screen.fill(WHITE)
    title = font.render("Highscore Tabelle", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    headers = ["Name", "Score"]
    x_positions = [WIDTH // 4, WIDTH // 4 * 3]
    for i, header in enumerate(headers):
        header_text = font.render(header, True, BLACK)
        screen.blit(header_text, (x_positions[i] - header_text.get_width() // 2, 70))

    highscores = get_all_highscores()
    y_start = 110
    line_height = 36

    if not highscores:
        no_data = font.render("Keine Highscores vorhanden.", True, BLACK)
        screen.blit(no_data, (WIDTH // 2 - no_data.get_width() // 2, HEIGHT // 2))
    else:
        for i, (name, score) in enumerate(highscores):
            name_text = font.render(name, True, BLACK)
            score_text = font.render(str(score), True, BLACK)
            y = y_start + i * line_height
            screen.blit(name_text, (x_positions[0] - name_text.get_width() // 2, y))
            screen.blit(score_text, (x_positions[1] - score_text.get_width() // 2, y))

    instr = font.render("Drücke R zum Neustart oder Q zum Beenden", True, BLACK)
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 50))

while True:
    clock.tick(FPS)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            connection.close()
            sys.exit()

        if show_instructions:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                show_instructions = False

        elif show_highscore_table:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    show_highscore_table = False
                    show_instructions = True
                    player = Player()
                    obstacles = []
                    coins = []
                    spawn_timer = 0
                    coin_spawn_timer = 0
                    distance = 0
                    coins_collected = 0
                    speed = 6
                    game_over = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    connection.close()
                    sys.exit()

        else:
            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if distance > highscore:
                        highscore = distance
                        save_score(player_name, highscore)
                    restart_count += 1
                    show_highscore_table = True

    if show_instructions:
        instructions = [
            "Springe mit LEERTASTE",
            "Ducke mit STRG",
            "Sammle gelbe Münzen!",
            "Viel Spaß!",
            "Drücke R zum Starten"
        ]
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))

    elif show_highscore_table:
        draw_highscore_table()

    else:
        keys = pygame.key.get_pressed()
        if not game_over:
            player.duck(keys[pygame.K_LCTRL])

        if not game_over:
            speed += speed_increase_rate
            player.update()

            spawn_timer += 1
            coin_spawn_timer += 1

            if spawn_timer > 90:
                spawn_timer = 0
                kind = "ground" if distance < 200 else random.choice(["ground", "air"])
                obstacles.append(Obstacle(speed, kind))

            if coin_spawn_timer > 150:
                coin_spawn_timer = 0
                coins.append(Coin(speed))

            for obs in obstacles:
                obs.speed = speed
                obs.update()
            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]

            for coin in coins:
                coin.speed = speed
                coin.update()
            coins = [coin for coin in coins if not coin.is_off_screen()]

            for obs in obstacles:
                if player.get_rect().colliderect(obs.get_rect()):
                    if obs.kind == "ground" and player.y + player.height >= obs.y:
                        game_over = True
                    elif obs.kind == "air" and not player.is_ducking:
                        game_over = True

            for coin in coins[:]:
                if player.get_rect().colliderect(coin.get_rect()):
                    coins_collected += 1
                    coins.remove(coin)

            distance += 1

        player.draw()
        for obs in obstacles:
            obs.draw()
        for coin in coins:
            coin.draw()
        pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        meter_text = font.render(f"Meter: {distance}", True, BLACK)
        screen.blit(meter_text, (10, 10))

        coin_text = font.render(f"Münzen: {coins_collected}", True, BLACK)
        screen.blit(coin_text, (10, 50))

        highscore_text = font.render(f"Highscore: {highscore}", True, BLACK)
        screen.blit(highscore_text, (10, 90))

        restart_text = font.render(f"Neustarts: {restart_count}", True, BLACK)
        screen.blit(restart_text, (10, 130))

        if game_over:
            over_text = font.render("Game Over! Drücke R zum Neustart", True, (200, 0, 0))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()