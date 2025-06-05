import pygame
import sys
import random
import math

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ausweichen - Startmenü & Retry")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

player_size = 50
player_speed = 5
enemy_radius = 20
enemy_speed = 3

font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()

def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, width)
        y = -enemy_radius
        angle = math.pi / 4  # nach unten
    elif side == 'bottom':
        x = random.randint(0, width)
        y = height + enemy_radius
        angle = -math.pi / 4  # nach oben
    elif side == 'left':
        x = -enemy_radius
        y = random.randint(0, height)
        angle = 0  # nach rechts
    else:  # right
        x = width + enemy_radius
        y = random.randint(0, height)
        angle = math.pi  # nach links
    return [x, y, angle]

def move_enemy(enemy, speed):
    x, y, angle = enemy
    x += speed * math.cos(angle)
    y += speed * math.sin(angle)
    return [x, y, angle]

def check_collision(player_rect, enemy_pos, enemy_radius):
    ex, ey = enemy_pos
    circle_distance_x = abs(ex - player_rect.centerx)
    circle_distance_y = abs(ey - player_rect.centery)

    if circle_distance_x > (player_rect.width / 2 + enemy_radius):
        return False
    if circle_distance_y > (player_rect.height / 2 + enemy_radius):
        return False

    if circle_distance_x <= (player_rect.width / 2):
        return True
    if circle_distance_y <= (player_rect.height / 2):
        return True

    corner_distance_sq = (circle_distance_x - player_rect.width / 2) ** 2 + \
                         (circle_distance_y - player_rect.height / 2) ** 2

    return corner_distance_sq <= (enemy_radius ** 2)

def draw_button(rect, text, font, base_color, hover_color, mouse_pos):
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                            rect.centery - text_surf.get_height() // 2))

def game_loop():
    player_x = width // 2
    player_y = height // 2
    enemies = []
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1000)

    running = True
    while running:
        clock.tick(60)
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == SPAWN_EVENT:
                enemies.append(spawn_enemy())

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_DOWN]:
            player_y += player_speed

        # Spieler Rechteck
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        new_enemies = []
        for enemy in enemies:
            enemy = move_enemy(enemy, enemy_speed)
            ex, ey, _ = enemy

            pygame.draw.circle(screen, RED, (int(ex), int(ey)), enemy_radius)

            if check_collision(player_rect, (ex, ey), enemy_radius):
                return False  # Game Over -> zurück zum Hauptprogramm

            if -enemy_radius <= ex <= width + enemy_radius and -enemy_radius <= ey <= height + enemy_radius:
                new_enemies.append(enemy)
        enemies = new_enemies

        pygame.draw.rect(screen, BLUE, player_rect)
        pygame.display.flip()

def start_menu():
    running = True
    while running:
        clock.tick(60)
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        title_surf = font_large.render("Ausweichen!", True, BLACK)
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 150))

        start_rect = pygame.Rect(width // 2 - 100, 300, 200, 60)
        draw_button(start_rect, "Start", font_medium, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    running = False

        pygame.display.flip()

def game_over_menu():
    running = True
    while running:
        clock.tick(60)
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        over_surf = font_large.render("Game Over!", True, BLACK)
        screen.blit(over_surf, (width // 2 - over_surf.get_width() // 2, 120))

        retry_rect = pygame.Rect(width // 2 - 150, 300, 140, 60)
        quit_rect = pygame.Rect(width // 2 + 10, 300, 140, 60)

        draw_button(retry_rect, "Nochmal", font_medium, GRAY, DARK_GRAY, mouse_pos)
        draw_button(quit_rect, "Beenden", font_medium, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    return True  # nochmal spielen
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

def main():
    while True:
        start_menu()
        result = game_loop()
        if result is False:  # Game Over
            play_again = game_over_menu()
            if not play_again:
                break

if __name__ == "__main__":
    main()