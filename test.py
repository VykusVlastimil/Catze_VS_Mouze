import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1920, 1020
BG_COLOR = (30, 30, 30)
RAT_COLOR = (200, 200, 200)
ENEMY_COLOR = (255, 0, 0)
VISION_COLOR = (255, 255, 100, 120)  # Průhledný kužel
WALL_COLOR = (100, 100, 100)
WALL_OUTLINE_COLOR = (150, 150, 150)
DOOR_COLOR = (139, 69, 19)  # Hnědá barva dveří
SPEED = 3
ENEMY_SPEED = 2.5
VISION_ANGLE = 120
VISION_LENGTH = 400
PERIPHERAL_RADIUS = 50
PLAYER_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse-Cat Game")
clock = pygame.time.Clock()

class Rat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RAT_COLOR, (0, 0, 20, 10))
        self.rect = pygame.Rect(x - 10, y - 5, 20, 10)  # Hitbox

    def update(self, walls):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        # Pohyb relativní k rotaci
        move_vec = [0, 0]
        keys = pygame.key.get_pressed()
        rad_angle = math.radians(self.angle)

        if keys[pygame.K_w]:
            move_vec[0] += math.cos(rad_angle) * SPEED
            move_vec[1] += math.sin(rad_angle) * SPEED
        if keys[pygame.K_s]:
            move_vec[0] -= math.cos(rad_angle) * SPEED
            move_vec[1] -= math.sin(rad_angle) * SPEED
        if keys[pygame.K_a]:  # Strafe vlevo
            move_vec[0] += math.cos(rad_angle - math.pi / 2) * SPEED
            move_vec[1] += math.sin(rad_angle - math.pi / 2) * SPEED
        if keys[pygame.K_d]:  # Strafe vpravo
            move_vec[0] += math.cos(rad_angle + math.pi / 2) * SPEED
            move_vec[1] += math.sin(rad_angle + math.pi / 2) * SPEED

        # Kolize se zdmi
        new_x = self.x + move_vec[0]
        new_y = self.y + move_vec[1]
        self.rect.center = (new_x, new_y)

        collision = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            self.x = new_x
            self.y = new_y
        else:
            self.rect.center = (self.x, self.y)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)
        self.draw_vision(screen)

    def draw_vision(self, screen):
        left_angle = self.angle - VISION_ANGLE / 2
        right_angle = self.angle + VISION_ANGLE / 2
        left_x = self.x + math.cos(math.radians(left_angle)) * VISION_LENGTH
        left_y = self.y + math.sin(math.radians(left_angle)) * VISION_LENGTH
        right_x = self.x + math.cos(math.radians(right_angle)) * VISION_LENGTH
        right_y = self.y + math.sin(math.radians(right_angle)) * VISION_LENGTH
        left_x, left_y = self.clip_vision(self.x, self.y, left_x, left_y)
        right_x, right_y = self.clip_vision(self.x, self.y, right_x, right_y)
        pygame.draw.polygon(screen, VISION_COLOR, [(self.x, self.y), (left_x, left_y), (right_x, right_y)])
        pygame.draw.circle(screen, VISION_COLOR, (int(self.x), int(self.y)), PERIPHERAL_RADIUS, width=1)

    def clip_vision(self, start_x, start_y, end_x, end_y):
        for wall in walls:
            intersection = self.line_rect_intersection(start_x, start_y, end_x, end_y, wall.rect)
            if intersection:
                end_x, end_y = intersection
        return end_x, end_y

    def line_rect_intersection(self, x1, y1, x2, y2, rect):
        edges = [
            ((rect.left, rect.top), (rect.right, rect.top)),
            ((rect.right, rect.top), (rect.right, rect.bottom)),
            ((rect.right, rect.bottom), (rect.left, rect.bottom)),
            ((rect.left, rect.bottom), (rect.left, rect.top))
        ]
        for edge in edges:
            intersect = self.line_line_intersection(x1, y1, x2, y2, edge[0][0], edge[0][1], edge[1][0], edge[1][1])
            if intersect:
                return intersect
        return None

    def line_line_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1))
        return None

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
        if distance > VISION_LENGTH:
            return False
        angle = math.degrees(math.atan2(dy, dx))
        angle_diff = abs((angle - self.angle) % 360)
        if angle_diff > VISION_ANGLE / 2 and angle_diff < 360 - VISION_ANGLE / 2:
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
                self.x = new_x
                self.y = new_y

    def wander(self):
        self.angle += random.uniform(-10, 10)
        new_x = self.x + math.cos(math.radians(self.angle)) * self.speed
        new_y = self.y + math.sin(math.radians(self.angle)) * self.speed
        if not self.check_collision(new_x, new_y, walls):
            self.x = new_x
            self.y = new_y

    def check_collision(self, x, y, walls):
        enemy_rect = pygame.Rect(x - 10, y - 5, 20, 10)
        for wall in walls:
            if enemy_rect.colliderect(wall.rect):
                return True
        return False

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, rat):
        if self.is_visible(rat):
            pygame.draw.rect(screen, WALL_OUTLINE_COLOR, self.rect, 2)

    def is_visible(self, rat):
        dx, dy = self.rect.centerx - rat.x, self.rect.centery - rat.y
        distance = math.hypot(dx, dy)
        if distance > VISION_LENGTH:
            return False
        angle = math.degrees(math.atan2(dy, dx))
        angle_diff = abs((angle - rat.angle) % 360)
        if angle_diff > VISION_ANGLE / 2 and angle_diff < 360 - VISION_ANGLE / 2:
            return False
        return True

class Door:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False

    def draw(self, screen):
        color = DOOR_COLOR if not self.is_open else (0, 0, 0, 0)  # Otevřené dveře jsou průhledné
        pygame.draw.rect(screen, color, self.rect)

    def toggle(self):
        self.is_open = not self.is_open

# Místnost s dveřmi v levém dolním rohu
walls = [
    Wall(200, 100, 20, 800),
    Wall(200, 100, 1600, 20),
    Wall(1800, 100, 20, 800),
    Wall(200, 900, 1600, 20),
    Wall(500, 300, 20, 400),
    Wall(800, 100, 20, 400),
    Wall(1100, 300, 20, 400),
    Wall(1400, 100, 20, 400),
    Wall(300, 500, 400, 20),
    Wall(900, 500, 400, 20),
    Wall(1300, 500, 400, 20),
]

door = Door(100, 900, 100, 20)  # Dveře v levém dolním rohu

rat = Rat(100, 100)
enemy = Enemy(random.randint(100, 300), random.randint(100, 300))

running = True
while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if door.rect.collidepoint(event.pos):  # Kliknutí na dveře
                door.toggle()

    rat.update(walls)
    rat.draw(screen)

    enemy.update(rat, walls)
    enemy.draw(screen)

    for wall in walls:
        wall.draw(screen, rat)
    door.draw(screen)  # Vykreslení dveří

    pygame.display.flip()
    clock.tick(60)

pygame.quit()