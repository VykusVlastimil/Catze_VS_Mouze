import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1600, 900
BG_COLOR = (25, 25, 30)
MOUSE_COLOR = (210, 210, 220)
BASE_VISION = 250
SPEED = 7 
MAZE_SCALE = 3.5
LEVEL_TIME = 15
LEVELS = 15  

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 60)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x-25, y-20, 50, 40)
        self.image = self.create_mouse_image()
    
    def create_mouse_image(self):
        surface = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, MOUSE_COLOR, (10, 10, 35, 25))
        pygame.draw.circle(surface, MOUSE_COLOR, (40, 15), 10)
        pygame.draw.polygon(surface, (230, 230, 230), [(35, 8), (40, 0), (45, 8)])
        pygame.draw.line(surface, MOUSE_COLOR, (8, 20), (-8, 20), 6)
        pygame.draw.circle(surface, (40, 40, 50), (42, 12), 3)
        return surface

    def update(self, walls):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.x, mouse_y - self.y
        angle = math.radians(math.degrees(math.atan2(dy, dx)))
        
        keys = pygame.key.get_pressed()
        move_vec = [0, 0]
        if keys[pygame.K_w]:
            move_vec[0] += math.cos(angle) * SPEED
            move_vec[1] += math.sin(angle) * SPEED
        if keys[pygame.K_s]:
            move_vec[0] -= math.cos(angle) * SPEED
            move_vec[1] -= math.sin(angle) * SPEED
        if keys[pygame.K_a]:
            move_vec[0] += math.cos(angle - math.pi/2) * SPEED
            move_vec[1] += math.sin(angle - math.pi/2) * SPEED
        if keys[pygame.K_d]:
            move_vec[0] += math.cos(angle + math.pi/2) * SPEED
            move_vec[1] += math.sin(angle + math.pi/2) * SPEED

        new_x = self.x + move_vec[0]
        new_y = self.y + move_vec[1]
        self.rect.center = (new_x, new_y)
        if not any(self.rect.colliderect(w.rect) for w in walls):
            self.x, self.y = new_x, new_y

    def draw(self, screen):
        screen.blit(pygame.transform.rotate(self.image, -math.degrees(math.atan2(pygame.mouse.get_pos()[1]-self.y, pygame.mouse.get_pos()[0]-self.x))), self.rect)

class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x*MAZE_SCALE, y*MAZE_SCALE, random.randint(20,40), random.randint(20,40))
    
    def draw(self, screen):
        pygame.draw.rect(screen, (110, 120, 130), self.rect)

class ExitBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (50, 200, 50), self.rect)

def generate_maze(level_num):
    return [Wall(random.randint(50, int(WIDTH/MAZE_SCALE)-50), random.randint(50, int(HEIGHT/MAZE_SCALE)-50)) for _ in range(18 + level_num)]  # More walls

def find_valid_position(walls, size):
    for _ in range(2000):
        x = random.randint(100, WIDTH-100)
        y = random.randint(100, HEIGHT-100)
        test_rect = pygame.Rect(x-size[0]//2, y-size[1]//2, size[0], size[1])
        if not any(test_rect.colliderect(w.rect) for w in walls):
            return (x, y)
    return (WIDTH//2, HEIGHT//2)

levels = []
for i in range(LEVELS):
    walls = generate_maze(i)
    start_pos = find_valid_position(walls, (50, 40))
    exit_pos = find_valid_position(walls, (40, 40))
    levels.append({
        'walls': walls,
        'start_pos': start_pos,
        'exit': ExitBlock(*exit_pos)
    })

def create_fog(player, vision):
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog.fill((0, 0, 0, 255))
    pygame.draw.circle(fog, (0, 0, 0, 0), (int(player.x), int(player.y)), vision)
    return fog

def main():
    current_level = 0
    player = Player(*levels[current_level]['start_pos'])
    start_time = pygame.time.get_ticks()
    
    while current_level < LEVELS:
        vision = max(90, BASE_VISION - 12 * current_level)  
        time_left = LEVEL_TIME - (pygame.time.get_ticks() - start_time) // 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        player.update(levels[current_level]['walls'])
        
        if player.rect.colliderect(levels[current_level]['exit'].rect):
            current_level += 1
            if current_level < LEVELS:
                player = Player(*levels[current_level]['start_pos'])
                start_time = pygame.time.get_ticks()
        
        if time_left <= 0:
            current_level = LEVELS
        
        screen.fill(BG_COLOR)
        
        for wall in levels[current_level]['walls']:
            if math.hypot(player.x - wall.rect.centerx, player.y - wall.rect.centery) <= vision:
                wall.draw(screen)
        
        if math.hypot(player.x - levels[current_level]['exit'].rect.centerx, player.y - levels[current_level]['exit'].rect.centery) <= vision:
            levels[current_level]['exit'].draw(screen)
        
        player.draw(screen)
        screen.blit(create_fog(player, vision), (0, 0))
        screen.blit(font.render(f"Level {current_level+1}/{LEVELS} | Time: {time_left}s", True, (220, 220, 240) if time_left >5 else (240,90,90)), (20, 20))
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()