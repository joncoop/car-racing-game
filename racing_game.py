# Imports
import pygame
import random

# Initialize game engine
pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 700
TITLE = "Racing Game!"
FPS = 60

# Define colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 150, 0)
WHITE = (255, 255, 255)
GRAY = (175, 175, 175)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
FONT_SM = pygame.font.Font(None, 48)
FONT_MD = pygame.font.Font(None, 64)
FONT_LG = pygame.font.Font("fonts/RacingSansOne-Regular.ttf", 96)

# Sounds
pygame.mixer.music.load("sounds/engine.ogg")
CRASH = pygame.mixer.Sound("sounds/crash.ogg")

# Stages
START = 0
PLAYING = 1
END = 2

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Game settings
num_enemy_cars = 5

# Game classes
class PlayerCar(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        
        self.rect = pygame.Rect(x, y, 80, 125)
        self.image = pygame.surface.Surface([80, 125])
        self.image.fill(BLUE)
        self.hit = False

    def update(self, controls, road, enemies):
        if controls[pygame.K_LEFT]:
            self.rect.x -= 4
        elif controls[pygame.K_RIGHT]:
            self.rect.x += 4

        if controls[pygame.K_UP]:
            self.rect.y -= 4
            pygame.mixer.music.set_volume(0.8)
        elif controls[pygame.K_DOWN]:
            self.rect.y += 4
            pygame.mixer.music.set_volume(0.4)
        else:
            pygame.mixer.music.set_volume(0.5)

        self.rect.left = max(self.rect.left, road.left)
        self.rect.right = min(self.rect.right, road.right)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)

        hit_list = pygame.sprite.spritecollide(self, enemies, False)
        
        if len(hit_list) > 0 and self.hit == False:
            CRASH.play()
            self.hit = True
                
class EnemyCar(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        x = random.choice([120, 240, 360, 480, 600])
        y = random.randrange(-3000, -100)
        
        self.rect = pygame.Rect(x, y, 80, 125)
        self.image = pygame.surface.Surface([80, 125])
        self.image.fill(RED)
        
        self.speed = random.choice([3, 4, 5, 5, 5, 5, 10])
        self.drift = random.choice([0, 0, 0, 0, 0, 0, -1, 1])

    def update(self, road, enemies):
        self.rect.x += self.drift
        self.rect.y += self.speed

        if self.rect.left < road.left:
            self.rect.left = road.left
            self.drift *= -1 
        elif self.rect.right > road.right:
            self.rect.right = road.right
            self.drift *= -1
            
        if self.rect.top > HEIGHT:
            self.kill()

        hit_list = pygame.sprite.spritecollide(self, enemies, False)
        
        for h in hit_list:
            if self is not h and self.speed > h.speed and self.rect.centery < h.rect.centery:
                self.rect.bottom = h.rect.top - 10
                self.speed = h.speed

            elif self.rect.centerx < h.rect.centerx:
                self.rect.right = h.rect.left
            elif self.rect.centerx > h.rect.centerx:
                self.rect.left = h.rect.right

            self.drift, h.drift = h.drift, self.drift
        
class Road():

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.scroll = -100

    def draw(self):
        pygame.draw.rect(window, GRAY, [self.left, 0, self.right - self.left, HEIGHT])
        pygame.draw.rect(window, YELLOW, [self.left - 20, 0, 20, HEIGHT])
        pygame.draw.rect(window, YELLOW, [self.right, 0, 20, HEIGHT])

        for x in range(self.left + 120, self.right, 120):
            for y in range(self.scroll, HEIGHT, 100):
                pygame.draw.rect(window, WHITE, [x - 5, y, 10, 30])

    def update(self):
        self.scroll += 7

        if self.scroll >= 0:
            self.scroll = -100
      
# Helper functions
def setup():
    global road, car, player, enemies, stage
    
    road = Road(100, 700)
    car = PlayerCar(360, 500)
    player = pygame.sprite.GroupSingle()
    player.add(car)

    enemies = pygame.sprite.Group()
    for i in range(num_enemy_cars):
        e = EnemyCar()
        enemies.add(e)

    stage = START
    
def start():
    global stage
    
    stage = PLAYING
    pygame.mixer.music.play(-1)

def end():
    global stage
    
    stage = END
    pygame.mixer.music.stop()

def show_title_screen():
    title = FONT_LG.render(TITLE, 1, BLACK)
    title_rect = title.get_rect()
    title_rect.centerx = WIDTH / 2
    title_rect.centery = 250

    sub_title = FONT_SM.render("Press space to start", 1, BLACK)
    sub_title_rect = sub_title.get_rect()
    sub_title_rect.centerx = WIDTH / 2
    sub_title_rect.centery = 325

    window.blit(title, title_rect)
    window.blit(sub_title, sub_title_rect)

def show_end_screen():
    title = FONT_MD.render("Game Over", 1, BLACK)
    title_rect = title.get_rect()
    title_rect.centerx = WIDTH / 2
    title_rect.centery = 275

    sub_title = FONT_SM.render("Press space to restart", 1, BLACK)
    sub_title_rect = sub_title.get_rect()
    sub_title_rect.centerx = WIDTH / 2
    sub_title_rect.centery = 325

    window.blit(title, title_rect)
    window.blit(sub_title, sub_title_rect)

# Game loop
setup()
running = True

while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if stage == START:
                    start()
                elif stage == END:
                    setup()

    controls = pygame.key.get_pressed()
    
    # Game logic
    if stage == PLAYING:
        road.update()
        for e in enemies:
            e.update(road, enemies)

        player.update(controls, road, enemies)

        if car.hit == True:
            end()
            
        if len(enemies) < num_enemy_cars:
            e = EnemyCar()
            enemies.add(e)
            
    # Drawing
    window.fill(GREEN)
    road.draw()
    player.draw(window)
    enemies.draw(window)

    if stage == START:
        show_title_screen()
    elif stage == END:
        show_end_screen()

    # Update screen
    pygame.display.update()
    clock.tick(FPS)


# Close window on quit
pygame.quit()
