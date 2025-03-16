import pygame
import math

pygame.init()

# Game Constants
WIDTH, HEIGHT = 1920, 1020
BG_COLOR = (30, 30, 30)
RAT_COLOR = (200, 200, 200)
VISION_RADIUS = 150
FOG_ALPHA = 200
SPEED = 6
MAZE_SCALE = 3  # Increased scale for bigger maze

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Giant Mouse Maze")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.rect = pygame.Rect(x-25, y-15, 50, 30)
        self.image = self.create_mouse_image()
    
    def create_mouse_image(self):
        mouse_surface = pygame.Surface((50, 30), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(mouse_surface, RAT_COLOR, (5, 5, 40, 20))
        # Ears
        pygame.draw.circle(mouse_surface, RAT_COLOR, (15, 8), 6)
        pygame.draw.circle(mouse_surface, RAT_COLOR, (35, 8), 6)
        # Tail
        pygame.draw.polygon(mouse_surface, RAT_COLOR, [
            (45, 15), (50, 13), (55, 15), (50, 17)
        ])
        # Feet
        pygame.draw.circle(mouse_surface, RAT_COLOR, (15, 25), 4)
        pygame.draw.circle(mouse_surface, RAT_COLOR, (35, 25), 4)
        return mouse_surface

    def update(self, walls):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        
        keys = pygame.key.get_pressed()
        move_vec = [0, 0]
        rad_angle = math.radians(self.angle)

        if keys[pygame.K_w]:
            move_vec[0] += math.cos(rad_angle) * SPEED
            move_vec[1] += math.sin(rad_angle) * SPEED
        if keys[pygame.K_s]:
            move_vec[0] -= math.cos(rad_angle) * SPEED
            move_vec[1] -= math.sin(rad_angle) * SPEED
        if keys[pygame.K_a]:
            move_vec[0] += math.cos(rad_angle - math.pi/2) * SPEED
            move_vec[1] += math.sin(rad_angle - math.pi/2) * SPEED
        if keys[pygame.K_d]:
            move_vec[0] += math.cos(rad_angle + math.pi/2) * SPEED
            move_vec[1] += math.sin(rad_angle + math.pi/2) * SPEED

        new_x = self.x + move_vec[0]
        new_y = self.y + move_vec[1]
        self.rect.center = (new_x, new_y)
        
        if not any(self.rect.colliderect(w.rect) for w in walls):
            self.x, self.y = new_x, new_y

    def draw(self, screen):
        rotated_img = pygame.transform.rotate(self.image, -self.angle)
        screen.blit(rotated_img, rotated_img.get_rect(center=(self.x, self.y)))

class Wall:
    def __init__(self, x, y, w, h, color=(100, 100, 100)):
        self.rect = pygame.Rect(x*MAZE_SCALE, y*MAZE_SCALE, w*MAZE_SCALE, h*MAZE_SCALE)
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Expanded Maze Levels
levels = [
    {  # Level 1 - Giant Spiral
        'walls': [
            Wall(0, 0, 80, 5), Wall(0, 75, 80, 5),
            Wall(0, 0, 5, 75), Wall(75, 0, 5, 75),
            *[Wall(5 + i, 5 + i, 70 - 2*i, 5) for i in range(0, 35, 5)],
            *[Wall(5 + i, 70 - i, 5, 65 - 2*i) for i in range(0, 35, 5)],
            Wall(40, 40, 5, 30, (120, 80, 80))
        ],
        'start_pos': (100, 500),
        'exit': Wall(70, 70, 5, 5),
        'time': 15,
        'wall_color': (100, 100, 150)
    },
    {  # Level 2 - Grid Labyrinth
        'walls': [
            Wall(0, 0, 80, 5), Wall(0, 75, 80, 5),
            Wall(0, 0, 5, 75), Wall(75, 0, 5, 75),
            *[Wall(x, y, 5, 20) for x in range(10, 70, 15) for y in range(5, 65, 25)],
            *[Wall(x, y, 15, 5) for x in range(5, 65, 20) for y in range(20, 60, 20)],
            Wall(35, 30, 5, 40, (80, 100, 80))
        ],
        'start_pos': (100, 100),
        'exit': Wall(5, 70, 5, 5),
        'time': 15,
        'wall_color': (150, 100, 100)
    },
    {  # Level 3 - Forest Maze
        'walls': [
            Wall(0, 0, 80, 5), Wall(0, 75, 80, 5),
            Wall(0, 0, 5, 75), Wall(75, 0, 5, 75),
            *[Wall(random.randint(5, 70), random.randint(5, 70), 3, 15) for _ in range(40)],
            *[Wall(random.randint(5, 70), random.randint(5, 70), 15, 3) for _ in range(40)],
            Wall(40, 35, 5, 40, (80, 80, 100))
        ],
        'start_pos': (400, 800),
        'exit': Wall(70, 5, 5, 5),
        'time': 15,
        'wall_color': (100, 150, 100)
    }
]

def create_fog(player):
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog.fill((0, 0, 0, FOG_ALPHA))
    pygame.draw.circle(fog, (0, 0, 0, 0), (int(player.x), int(player.y)), VISION_RADIUS)
    return fog

def main():
    current_level = 0
    level = levels[current_level]
    player = Player(*level['start_pos'])
    start_time = pygame.time.get_ticks()
    
    running = True
    while running:
        time_left = level['time'] - (pygame.time.get_ticks() - start_time) // 1000
        
        if time_left <= 0:
            print("Time's up!")
            running = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        player.update(level['walls'])
        
        if player.rect.colliderect(level['exit'].rect):
            current_level += 1
            if current_level >= len(levels):
                print("Congratulations! You escaped all levels!")
                running = False
            else:
                level = levels[current_level]
                player = Player(*level['start_pos'])
                start_time = pygame.time.get_ticks()
        
        screen.fill(BG_COLOR)
        for wall in level['walls']:
            wall.draw(screen)
        pygame.draw.rect(screen, (0, 255, 0), level['exit'].rect)
        player.draw(screen)
        
        fog = create_fog(player)
        screen.blit(fog, (0, 0))
        
        timer_text = font.render(
            f"Level: {current_level+1} | Time: {time_left}",
            True, 
            (255, 0, 0) if time_left < 5 else (255, 255, 255)
        )
        screen.blit(timer_text, (20, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()