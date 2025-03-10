import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1920, 1020
BG_COLOR = (30, 30, 30)
RAT_COLOR = (200, 200, 200)
ENEMY_COLOR = (255, 0, 0)
VISION_COLOR = (255, 255, 100, 120)  # Semi-transparent yellow
WALL_COLOR = (100, 100, 100)
WALL_OUTLINE_COLOR = (150, 150, 150)
DOOR_COLOR = (139, 69, 19)
SPEED = 3
ENEMY_SPEED = 2.5
VISION_RADIUS = 300
PLAYER_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse-Cat Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Rat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RAT_COLOR, (0, 0, 20, 10))
        self.rect = pygame.Rect(x - 10, y - 5, 20, 10)

    def update(self, walls):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        move_vec = [0, 0]
        keys = pygame.key.get_pressed()
        rad_angle = math.radians(self.angle)

        if keys[pygame.K_w]:
            move_vec[0] += math.cos(rad_angle) * SPEED
            move_vec[1] += math.sin(rad_angle) * SPEED
        if keys[pygame.K_s]:
            move_vec[0] -= math.cos(rad_angle) * SPEED
            move_vec[1] -= math.sin(rad_angle) * SPEED
        if keys[pygame.K_a]:
            move_vec[0] += math.cos(rad_angle - math.pi / 2) * SPEED
            move_vec[1] += math.sin(rad_angle - math.pi / 2) * SPEED
        if keys[pygame.K_d]:
            move_vec[0] += math.cos(rad_angle + math.pi / 2) * SPEED
            move_vec[1] += math.sin(rad_angle + math.pi / 2) * SPEED

        new_x = self.x + move_vec[0]
        new_y = self.y + move_vec[1]
        self.rect.center = (new_x, new_y)

        collision = any(self.rect.colliderect(wall.rect) for wall in walls)
        if not collision:
            self.x, self.y = new_x, new_y
        else:
            self.rect.center = (self.x, self.y)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = ENEMY_SPEED
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, ENEMY_COLOR, (0, 0, 20, 10))
        self.target = None

    def update(self, rat, walls):
        if self.can_see_rat(rat, walls):
            self.target = (rat.x, rat.y)
        else:
            self.target = None
            self.wander()

        if self.target:
            self.move_towards_target(walls)

    def can_see_rat(self, rat, walls):
        dx, dy = rat.x - self.x, rat.y - self.y
        distance = math.hypot(dx, dy)
        if distance > VISION_RADIUS:
            return False
        for wall in walls:
            if self.line_rect_intersection(self.x, self.y, rat.x, rat.y, wall.rect):
                return False
        return True

    def move_towards_target(self, walls):
        dx, dy = self.target[0] - self.x, self.target[1] - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.angle = math.degrees(math.atan2(dy, dx))
            new_x = self.x + math.cos(math.radians(self.angle)) * self.speed
            new_y = self.y + math.sin(math.radians(self.angle)) * self.speed
            if not self.check_collision(new_x, new_y, walls):
                self.x, self.y = new_x, new_y

    def wander(self):
        self.angle += random.uniform(-10, 10)
        new_x = self.x + math.cos(math.radians(self.angle)) * self.speed
        new_y = self.y + math.sin(math.radians(self.angle)) * self.speed
        if not self.check_collision(new_x, new_y, walls):
            self.x, self.y = new_x, new_y

    def check_collision(self, x, y, walls):
        temp_rect = pygame.Rect(x - 10, y - 5, 20, 10)
        return any(temp_rect.colliderect(wall.rect) for wall in walls)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, mouse_pos):
        if self.is_visible(mouse_pos):
            pygame.draw.rect(screen, WALL_OUTLINE_COLOR, self.rect, 2)

    def is_visible(self, mouse_pos):
        closest_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
        closest_y = max(self.rect.top, min(mouse_pos[1], self.rect.bottom))
        distance = math.hypot(mouse_pos[0]-closest_x, mouse_pos[1]-closest_y)
        return distance <= VISION_RADIUS

class Door:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False

    def draw(self, screen, mouse_pos):
        if self.is_visible(mouse_pos):
            color = DOOR_COLOR if not self.is_open else (0, 0, 0, 0)
            pygame.draw.rect(screen, color, self.rect)

    def is_visible(self, mouse_pos):
        closest_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
        closest_y = max(self.rect.top, min(mouse_pos[1], self.rect.bottom))
        distance = math.hypot(mouse_pos[0]-closest_x, mouse_pos[1]-closest_y)
        return distance <= VISION_RADIUS

# Level configurations
levels = [
    {  # Level 1
        'walls': [
            Wall(200, 100, 20, 800),
            Wall(200, 100, 1600, 20),
            Wall(1800, 100, 20, 800),
            Wall(200, 20, 400),
            Wall(300, 500, 400, 20),
            Wall(900, 500, 400, 20),
            Wall(1300, 5,180,150)
            ],
        'door': Door(100, 900, 100, 20),
        'enemies': [Enemy(700, 200)],
        'rat_start': (200, 200)
    },
    {  # Level 2
        'walls': [
            Wall(200, 
        20, 800),
            Wall(200, 900, 1600, 2),
            Wall(600, 300,00, 20400), 
            Wall(1200,300, 20, 00),
            Wall(1500,100, 20, 400),
            Wall(1400, 500, 400, 20),
        ],
        'door': Door(1800, 100, 100, 20),
        'enemies': [Enemy(1600, 500), Enemy(1000, 300)],
        'rat_start': (200, 200)
    }
]

current_level = 0
start_ticks = pygame.time.get_ticks()

def load_level(level_index):
    level = levels[level_index]
    return (level['walls'],
            level['door'],
            level['enemies'],
            level['rat_start'])

walls, door, enemies, rat_start = load_level(current_level)
rat = Rat(*rat_start)

running = True
while running:
    screen.fill(BG_COLOR)
    mouse_pos = pygame.mouse.get_pos()
    
    # Draw vision circle
    vision_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(vision_surface, VISION_COLOR, mouse_pos, VISION_RADIUS)
    screen.blit(vision_surface, (0, 0))
    
    # Timer logic
    current_ticks = pygame.time.get_ticks()
    elapsed = (current_ticks - start_ticks) / 1000
    remaining = max(60 - elapsed, 0)
    timer_text = font.render(f"Time: {int(remaining)}", True, (255, 255, 255))
    
    if remaining <= 0:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if door.rect.collidepoint(event.pos):
                door.toggle()

    rat.update(walls)
    rat.draw(screen)

    for enemy in enemies:
        enemy.update(rat, walls)
        enemy.draw(screen)

    for wall in walls:
        wall.draw(screen, mouse_pos)

    door.draw(screen, mouse_pos)
    screen.blit(timer_text, (10, 10))

    if door.is_open and rat.rect.colliderect(door.rect):
        current_level += 1
        if current_level < len(levels):
            walls, door, enemies, rat_start = load_level(current_level)
            rat = Rat(*rat_start)
            start_ticks = pygame.time.get_ticks()
        else:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()