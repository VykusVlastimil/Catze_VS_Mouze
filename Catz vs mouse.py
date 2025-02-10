import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1020
BG_COLOR = (30, 30, 30)
RAT_COLOR = (200, 200, 200)
VISION_COLOR = (255, 255, 100, 80)
SPEED = 3
SPRINT_SPEED = 6
SPRINT_TIME = 5000
SPRINT_COOLDOWN = 5000
VISION_ANGLE = 80
VISION_LENGTH = 250
PERIPHERAL_RADIUS = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse-Cat Game")
clock = pygame.time.Clock()

class Rat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = SPEED
        self.sprinting = False
        self.sprint_start = 0
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RAT_COLOR, (0, 0, 20, 10))

    def move_forward(self, walls):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Move only when "W" is pressed
            new_x = self.x + math.cos(math.radians(self.angle)) * self.speed
            new_y = self.y + math.sin(math.radians(self.angle)) * self.speed
            if not self.check_collision(new_x, new_y, walls):
                self.x = new_x
                self.y = new_y

    def rotate_towards_cursor(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

    def check_collision(self, x, y, walls):
        rat_rect = pygame.Rect(x - 10, y - 5, 20, 10)
        for wall in walls:
            if rat_rect.colliderect(wall.rect):
                return True
        return False

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)
        self.draw_vision(screen)

    def draw_vision(self, screen):
        left_angle = self.angle - VISION_ANGLE // 2
        right_angle = self.angle + VISION_ANGLE // 2
        left_x = self.x + math.cos(math.radians(left_angle)) * VISION_LENGTH
        left_y = self.y + math.sin(math.radians(left_angle)) * VISION_LENGTH
        right_x = self.x + math.cos(math.radians(right_angle)) * VISION_LENGTH
        right_y = self.y + math.sin(math.radians(right_angle)) * VISION_LENGTH
        pygame.draw.polygon(screen, VISION_COLOR, [(self.x, self.y), (left_x, left_y), (right_x, right_y)])
        pygame.draw.circle(screen, VISION_COLOR, (int(self.x), int(self.y)), PERIPHERAL_RADIUS, width=1)

    def can_see(self, wall):
        return self.line_rect_intersection(self.x, self.y, self.x + math.cos(math.radians(self.angle)) * VISION_LENGTH, 
                                           self.y + math.sin(math.radians(self.angle)) * VISION_LENGTH, wall.rect)

    def line_rect_intersection(self, x1, y1, x2, y2, rect):
        edges = [
            ((rect.left, rect.top), (rect.right, rect.top)),
            ((rect.right, rect.top), (rect.right, rect.bottom)),
            ((rect.right, rect.bottom), (rect.left, rect.bottom)),
            ((rect.left, rect.bottom), (rect.left, rect.top))
        ]
        for edge in edges:
            if self.line_line_intersection(x1, y1, x2, y2, edge[0][0], edge[0][1], edge[1][0], edge[1][1]):
                return True
        return False

    def line_line_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        return 0 <= t <= 1 and 0 <= u <= 1

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)

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

rat = Rat(100, 100)

running = True
while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    rat.rotate_towards_cursor()
    rat.move_forward(walls)
    rat.draw(screen)

    for wall in walls:
        if rat.can_see(wall):
            wall.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
