import pygame #pygame wird für das Spiel zugänglich gemacht
import random # Zufallszahlen/Zufallsfunktionen werden im Programm verfügbar gemacht
import sys #Systemfunktionen werden freigeschaltet/zugänglich gemacht
import sqlite3 # Datenbanksystem wird in den Quellcode miteingebracht

# Datenbank Setup
connection = sqlite3.connect('scores_CGM.db') # Datenbank wird mit Spiel verbunden
cursor = connection.cursor()
# als Nächstes wird in der Datenbank die tabelle highscores erstellt und ihre Spalten zugeteilt
cursor.execute('''
    CREATE TABLE IF NOT EXISTS highscores (
        name TEXT PRIMARY KEY,
        score INTEGER,
        coins INTEGER
    )
''')
connection.commit()
# hier wird der beste highscore von einem Spieler genommen & angezeigt
def get_highscore(name):
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result else 0
# der Highscore derjenigen Person wird in der Datenbank gepsiechert und für später vermerkt
def save_score(name, score, coins):
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result is None: # Daten, wie score, wird auf Null gesetzt, da der Spieler noch neu ist
        cursor.execute("INSERT INTO highscores (name, score, coins) VALUES (?, ?, ?)", (name, score, coins))
    else:
        if score > result[0]: # Daten werden geupdatet, wenn es den Spieler schon gab und seinen Highscore geknackt hat
            cursor.execute("UPDATE highscores SET score = ?, coins = ? WHERE name = ?", (score, coins, name))
    connection.commit()

def get_all_highscores(limit=5): # 5 besten Highscores werden für die Anzeigetafel im Menu ausgewählt und gezeigt
    cursor.execute("SELECT name, score, coins FROM highscores ORDER BY score DESC LIMIT ?", (limit,))
    return cursor.fetchall()

# Spielername per input abfragen, passiert vor den Start des eigentlichen Spiels
player_name = input("Bitte gib deinen Namen ein: ")
if not player_name.strip(): #wenn Spieler nicht seinen Namen eingibt, dann wird es als Spieler1 vermerkt
    player_name = "Spieler1"
 
highscore = get_highscore(player_name) #highscore des Spielers wird gespeichert
restart_count = 0 #Neustart des Spieler wird am Anfang auf 0 gesetzt

# Pygame Setup, Spiel wird also vorbereitet
pygame.init()
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 150, 255)
GROUND_Y = HEIGHT - 50
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Spielfeldgröße wird mithilfe der oberen Variablen erstellt
pygame.display.set_caption("Jump & Run CGM") # Name des Spiels, in der Leiste des Fensters angezeigt
clock = pygame.time.Clock() # Zeit im Spiel, ist für die Distanzen wichtig
font = pygame.font.SysFont(None, 36) #Schriftgröße wird hier festgelegt

coin_image = pygame.image.load("coin.png").convert_alpha() # Münzenbild wird eingebaut mit Verweis auf die png
coin_image = pygame.transform.scale(coin_image, (30, 30)) # hier wird die Pixelgröße des Bildes festgelegt

class Player: #Klasse des Spielers wird eröffnet und der Spielblockeigenschaft(Größe,Breite,usw.) festgelegt
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
        self.on_ground = True # Dies ist für das Ducken und Springen, da diese Aktionen nicht gleichzeitig verfügbar sein sollen
        self.is_ducking = False

    def jump(self):
        if self.on_ground and not self.is_ducking: # Spieler darf also nicht gleichzeitig ducken und springen
            self.vel_y = self.jump_strength
            self.on_ground = False

    def duck(self, is_pressed):
        if self.on_ground: # also nur wenn der Spieler auf Boden ist
            self.is_ducking = is_pressed # Ducken-Aktion wird hier definiert
            if self.is_ducking:
                self.height = self.duck_height # Größe des Spielblocks wird verändert
                self.y = GROUND_Y - self.height
            else:
                self.height = self.normal_height
                self.y = GROUND_Y - self.height #Ansonsten soll der Spielblock normal aussehen (Quadrat)

    def update(self):
        self.vel_y += self.gravity # Schwerkraft wird im Spiel simuliert
        self.y += self.vel_y
        if self.y >= GROUND_Y - self.height: #Überprüfung des Position des Spielblocks
            self.y = GROUND_Y - self.height
            self.vel_y = 0 #Wenn also der Spielerblock den Boden berüht, wird Fallgeschwindigkeit auf 0 gesetzt
            self.on_ground = True
        else:
            self.on_ground = False
            if not self.on_ground: #Spielblock wird beim Spiringen auf normale Größe gesetzt
                self.is_ducking = False
                self.height = self.normal_height

    def draw(self): # Spielerblock wird ins Spielfeld gesetzt(wörtlich:hineingemalt)
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    def get_rect(self): # Prüfung von Kollisionen des Spielers mit Objekten
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle: # Klasse der Objekte/Hürden wird erstellt
    def __init__(self, speed, kind):
        self.kind = kind
        self.speed = speed #Bewegung des Objekt über das Spielfeld
        self.width = 30 # Größe des Hürden festgelegt
        self.height = 40
        self.x = WIDTH
        self.y = GROUND_Y - self.height if kind == "ground" else GROUND_Y - 80 #Höhenunterschiedsetzung des Hürden

    def update(self):
        self.x -= self.speed

    def draw(self):
        color = (200, 0, 0) if self.kind == "ground" else (255, 120, 0) # Zwei verschiedene Farben für Hürden in der Luft und auf dem Boden
        points = [(self.x, self.y + self.height), (self.x + self.width // 2, self.y), (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, color, points) # Hürdenkonstruktion, werden also geformt

    def is_off_screen(self): #Prüfung von Objekt aus dem Bildschirm ist
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
# Klasse der Münze wird erstellt
class Coin:
    def __init__(self, speed):
        self.radius = 15
        self.speed = speed # soll mit der gleichen Geschwindigkeit, wie die andern Objekte vorbeiziehen
        self.x = WIDTH
        self.y = GROUND_Y - 100 # Münze soll sich über dem Boden befinden

    def update(self): # geschwindigkeitbewegung(passby) wird immer erhöht
        self.x -= self.speed

    def draw(self):
        screen.blit(coin_image, (int(self.x - self.radius), int(self.y - self.radius)))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def is_off_screen(self): # oben ähnlich erklärt
        return self.x + self.radius < 0

player = Player()
obstacles = [] # Spiel wird hier startklar gemacht und vorbereitet
coins = []
spawn_timer = 0
coin_spawn_timer = 0
distance = 0
coins_collected = 0 # Alles wird auf 0 gesetzt
game_over = False
speed = 6
speed_increase_rate = 0.002 # Erhöhung der Geschwindigkeit
show_instructions = True # für ganz am Anfang, wenn das Spiel erst startet
show_highscore_table = False

def draw_highscore_table():
    screen.fill(WHITE) # Highscore-tabelle wird hier geformt
    title = font.render("Highscore Tabelle (Top 5)", True, BLACK) #Überschrift der Tabelle
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    headers = ["Name", "Score", "Münzen"] #Sind die Überschriften des einzelnen Zeilen, 
    x_positions = [WIDTH // 4 - 60, WIDTH // 2, WIDTH // 4 * 3 + 60]
    for i, header in enumerate(headers):
        header_text = font.render(header, True, BLACK)
        screen.blit(header_text, (x_positions[i] - header_text.get_width() // 2, 70))

    highscores = get_all_highscores(limit=5)
    y_start = 110
    line_height = 36

    if not highscores:
        no_data = font.render("Keine Highscores vorhanden.", True, BLACK) # wenn es keine Highscores gibt, dann werden auch keine angezeigt
        screen.blit(no_data, (WIDTH // 2 - no_data.get_width() // 2, HEIGHT // 2))
    else:
        for i, (name, score, coins) in enumerate(highscores): # gibt es highscores, dann werden sie im zwischen Menu angezeigt
            name_text = font.render(name, True, BLACK)
            score_text = font.render(str(score), True, BLACK) 
            coin_text = font.render(str(coins), True, BLACK)
            y = y_start + i * line_height
            screen.blit(name_text, (x_positions[0] - name_text.get_width() // 2, y)) # Zeilen werden hier ausgegeben und positioniert
            screen.blit(score_text, (x_positions[1] - score_text.get_width() // 2, y))
            screen.blit(coin_text, (x_positions[2] - coin_text.get_width() // 2, y))

    instr = font.render("Drücke R zum Neustart oder Q zum Beenden", True, BLACK) #nachdem man die besten scores gesehen hat, wird angeboten das Spiel zu beenden oder weiterzuspielen
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 50))

while True:
    clock.tick(FPS)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            connection.close()
            sys.exit()

        if show_instructions and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
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
            if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.jump()
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if distance > highscore:
                    highscore = distance
                save_score(player_name, int(highscore), coins_collected)
                restart_count += 1
                show_highscore_table = True

    if show_instructions:
        instructions = ["Springe mit LEERTASTE", "Ducke mit STRG", "Sammle Münzen!", "Drücke R zum Starten"]
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

        screen.blit(font.render(f"Meter: {distance}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Münzen: {coins_collected}", True, BLACK), (10, 50))
        screen.blit(font.render(f"Highscore: {highscore}", True, BLACK), (10, 90))
        screen.blit(font.render(f"Neustarts: {restart_count}", True, BLACK), (10, 130))

        if game_over:
            over_text = font.render("Game Over! Drücke R zum Neustart", True, (200, 0, 0))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

