import pygame # pygame nutzbar gemacht
import random # Freischaltung von Auswahl zufälliger Zahlen
import sys # Interaktion mit System freigeschaltet
import sqlite3 # Datenbank-System wird miteingebracht

# --- Datenbank Setup ---
connection = sqlite3.connect('scores_CGM.db')
cursor = connection.cursor()

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS highscores (
        name TEXT,
        score INTEGER
    )
''')
# Datenbank wird erstellt mit den Tabellen "Name" und "Score"
cursor.execute('''
    INSERT INTO highscores (name, scores)
    VALUES ( Spieler1, 0)
    ''')
connection.commit()
# "Name" und "Score" wird anfangs sofort festgelegt

def get_highscore(name):
    cursor.execute("SELECT MAX(score) FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else 0

def save_score(name, score):
    cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
    connection.commit()

player_name = "Spieler1"
highscore = get_highscore(player_name)
restart_count = 0

# --- Pygame Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 400 # Bildschirmgröße festgelegt
WHITE = (255, 255, 255) # Färbung des Hintergrundes
BLACK = (0, 0, 0) # 
PLAYER_COLOR = (50, 150, 255)
GROUND_Y = HEIGHT - 50
FPS = 60 # Anzahl der Frames, die pro Sekunde ablaufen sollen

screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Festerbildöffnung + als Variable "screen" festlegen
pygame.display.set_caption("Jump & Run CGM") #Benennung des Spiels
clock = pygame.time.Clock() # Steuerung Bildwiederholrate
font = pygame.font.SysFont(None, 36) #Schriftstyle festlegen

# --- Spielerklasse ---
class Player: #Klasse Spieler eingebaut
    def __init__(self):
        self.width = 50
        self.normal_height = 50 #Größeeigenschaften des Spielblocks
        self.duck_height = 30
        self.height = self.normal_height
        self.x = 100
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.jump_strength = -12 # Springkraft und Springhöhe (unten drunter) wird zugeordnet 
        self.gravity = 0.6
        self.on_ground = True 
        self.is_ducking = False

    def jump(self):
        if self.on_ground and not self.is_ducking: #Limiert Aktion, Spieler kann nicht springen und sich ducken
            self.vel_y = self.jump_strength
            self.on_ground = False

    def duck(self, is_pressed):
        if self.on_ground: # wenn sich Spielerblock auf Boden befindet, dann kann sich der Spieler ducken
            self.is_ducking = is_pressed # Blockzustand wird eine Variable zugeordnet
            if self.is_ducking:
                self.height = self.duck_height #Normale Höhe des Blocks wird auf die niederigere Höhe fürs Ducken übernommen
                self.y = GROUND_Y - self.height
            else:
                self.height = self.normal_height
                self.y = GROUND_Y - self.height

    def update(self):
        self.vel_y += self.gravity #Gravitation des Blocks wird in Variablen gepackt
        self.y += self.vel_y
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True # das Landen des Blocks wird hier überprüft & gecheckt, damit Spieler zunächst wieder springen kann
        else:
            self.on_ground = False
            # Beim Springen kann man nicht ducken
            if not self.on_ground:
                self.is_ducking = False
                self.height = self.normal_height

    def draw(self): # fügt den Block auf das Fesnter/Spielfeld
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    def get_rect(self): # prüft im Spiel die Kollision mit den Hindernissen
        return pygame.Rect(self.x, self.y, self.width, self.height)

# --- Hindernisklasse ---
class Obstacle:
    def __init__(self, speed, kind):
        self.kind = kind  # "ground" oder "air"
        self.speed = speed
        self.width = 30 # Hindernisgröße wird festgelegt
        self.height = 40
        self.x = WIDTH
        if kind == "ground":
            self.y = GROUND_Y - self.height
        else:
            self.y = GROUND_Y - 80 # Hindernisse in der Luft

    def update(self):
        self.x -= self.speed # Geschwindigkeitsbewegung des Spielers wird vergrößert

    def draw(self): # Design der Dreiecke wird hier festgelegt, also Farbe und das es gleichschenklig ist
        color = (200, 0, 0) if self.kind == "ground" else (255, 120, 0)
        point1 = (self.x, self.y + self.height)
        point2 = (self.x + self.width // 2, self.y)
        point3 = (self.x + self.width, self.y + self.height)
        pygame.draw.polygon(screen, color, [point1, point2, point3])

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_rect(self): #Erklärung oben
        return pygame.Rect(self.x, self.y, self.width, self.height)

# --- Initialisierung ---
player = Player()
obstacles = []
spawn_timer = 0
distance = 0
game_over = False
speed = 6
speed_increase_rate = 0.002

# --- Spielschleife ---
while True:
    clock.tick(FPS)
    screen.fill(WHITE)

    keys = pygame.key.get_pressed() #Aktionen für Spieler werden hier benutztbar gemacht
    if not game_over:
        player.duck(keys[pygame.K_LCTRL])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() #Spiel wird beim Verlieren beendet
            connection.close()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Highscore prüfen und speichern
                if distance > highscore:
                    highscore = distance
                    save_score(player_name, highscore)
                restart_count += 1

                # Neustart
                player = Player()
                obstacles = []
                spawn_timer = 0
                distance = 0
                speed = 6
                game_over = False

    if not game_over:
        speed += speed_increase_rate

        player.update()

        spawn_timer += 1
        if spawn_timer > 90:
            spawn_timer = 0
            kind = "ground" if distance < 200 else random.choice(["ground", "air"])
            obstacles.append(Obstacle(speed, kind))

        for obs in obstacles:
            obs.speed = speed
            obs.update()

        obstacles = [obs for obs in obstacles if not obs.is_off_screen()]

        for obs in obstacles:
            if player.get_rect().colliderect(obs.get_rect()):
                if obs.kind == "ground" and player.y + player.height >= obs.y:
                    game_over = True
                elif obs.kind == "air" and not player.is_ducking:
                    game_over = True

        distance += 1

    player.draw()
    for obs in obstacles:
        obs.draw()
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    meter_text = font.render(f"Meter: {distance}", True, BLACK)
    screen.blit(meter_text, (10, 10))

    highscore_text = font.render(f"Highscore: {highscore}", True, BLACK)
    screen.blit(highscore_text, (10, 50))

    restart_text = font.render(f"Neustarts: {restart_count}", True, BLACK)
    screen.blit(restart_text, (10, 90))

    if game_over:
        over_text = font.render("Game Over! Drücke R zum Neustart", True, (200, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()