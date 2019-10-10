# Imports
import pygame
import random

# Initialize game engine
pygame.init()

# Window settings
WIDTH = 960
HEIGHT = 660
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

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Images
''' Cars '''
BLACK_CAR = pygame.image.load("images/Cars/car_black_2.png").convert_alpha()
RED_CAR = pygame.image.load("images/Cars/car_red_2.png").convert_alpha()
GREEN_CAR = pygame.image.load("images/Cars/car_green_2.png").convert_alpha()
BLUE_CAR = pygame.image.load("images/Cars/car_blue_2.png").convert_alpha()
YELLOW_CAR = pygame.image.load("images/Cars/car_yellow_2.png").convert_alpha()
enemy_car_images = [RED_CAR, GREEN_CAR, BLUE_CAR, YELLOW_CAR]

''' Scenery '''
GRASS = pygame.image.load("images/Tiles/land_grass11.png").convert_alpha()

''' Items '''
OIL = pygame.image.load("images/Items/oil.png").convert_alpha()

# Fonts
FONT_SM = pygame.font.Font(None, 48)
FONT_MD = pygame.font.Font(None, 64)
FONT_LG = pygame.font.Font("fonts/RacingSansOne-Regular.ttf", 96)

# Sounds
pygame.mixer.music.load("sounds/engine.ogg")
CRASH = pygame.mixer.Sound("sounds/crash.ogg")
HONK = pygame.mixer.Sound("sounds/honk.ogg")
SQUEAL = pygame.mixer.Sound("sounds/tire_squeal.ogg")

# Stages
START = 0
PLAYING = 1
END = 2

# Game settings
num_enemy_cars = 7

# Game classes
class PlayerCar(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.image_original = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit = False
        self.spinning = False
        self.angle = 0

    def rotate(self):
        self.angle += 15
        center = self.rect.center
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect.center = center
        
    def update(self, events, pressed, road, enemies):
        if self.spinning and self.angle < 360:
            self.rotate()
        else:
            self.spinning = False
            self.angle = 0
        
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    HONK.play()

        if not self.spinning:
            if pressed[pygame.K_LEFT]:
                self.rect.x -= 4
            elif pressed[pygame.K_RIGHT]:
                self.rect.x += 4

            if pressed[pygame.K_UP]:
                self.rect.y -= 4
                pygame.mixer.music.set_volume(0.8)
            elif pressed[pygame.K_DOWN]:
                self.rect.y += 4
                pygame.mixer.music.set_volume(0.4)
            else:
                pygame.mixer.music.set_volume(0.5)

        self.rect.left = max(self.rect.left, road.left)
        self.rect.right = min(self.rect.right, road.right)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)

        hit_list = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        
        for car in hit_list:
            CRASH.play()
            self.hit = True
            car.hit = True
            
        hit_list = pygame.sprite.spritecollide(self, items, False, pygame.sprite.collide_mask)
        
        for item in hit_list:
            item.apply(self)
                
class EnemyCar(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = random.choice(enemy_car_images);
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        x = random.choice([203, 323, 443, 563, 683])
        y = random.randrange(-3000, -100)
        self.rect.x = x
        self.rect.y = y
        self.hit = False        

        self.speed = random.choice([3, 4, 5, 5, 5, 5, 10])
        self.drift = random.choice([0, 0, 0, 0, 0, 0, -1, 1])

    def update(self, road, enemies):
        if not self.hit:
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

        hit_list = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        
        for h in hit_list:
            if self is not h and self.speed > h.speed and self.rect.centery < h.rect.centery:
                self.rect.bottom = h.rect.top - 10
                self.speed = h.speed

            elif self.rect.centerx < h.rect.centerx:
                self.rect.right = h.rect.left
            elif self.rect.centerx > h.rect.centerx:
                self.rect.left = h.rect.right

            self.drift, h.drift = h.drift, self.drift
        
class Road(pygame.sprite.Sprite):

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
        self.scroll += speed

        if self.scroll >= 0:
            self.scroll = -100

class Grass(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
                
        self.image = pygame.surface.Surface([WIDTH, HEIGHT])
        self.rect = self.image.get_rect()

        tile_size = GRASS.get_width()

        for x in range(0, WIDTH, tile_size):
            for y in range(-1 * tile_size, HEIGHT, tile_size):
                self.image.blit(GRASS, [x, y])

        self.scroll = 0

    def update(self):
        self.scroll = (self.scroll + speed) % 128
        self.rect.y = self.scroll

class OilSlick(pygame.sprite.Sprite):

    def __init__(self, img, x, y):
        super().__init__()
        
        self.image = img
        self.rect = self.image.get_rect()
        self.set_random_loc()

        self.used = False

    def set_random_loc(self):
        self.rect.x = random.randrange(185, 665)
        self.rect.y = random.randrange(-2000, -100)
        self.used = False

    def apply(self, other):
        if not self.used:
            other.spinning = True
            SQUEAL.play()
    
    def update(self):
        self.rect.y += speed

        if self.rect.top > HEIGHT:
            self.set_random_loc() 
      
# Helper functions
def setup():
    global road, car, player, enemies, scenery, items, score, stage, speed, ticks
    
    road = Road(180, 780)
    grass = Grass()
    car = PlayerCar(445, 500, BLACK_CAR)
    player = pygame.sprite.GroupSingle()
    player.add(car)
    score = 0

    enemies = pygame.sprite.Group()
    for i in range(num_enemy_cars):
        e = EnemyCar()
        enemies.add(e)

    items = pygame.sprite.Group()
    oil = OilSlick(OIL, 500, 400)
    items.add(oil)
    
    scenery = pygame.sprite.Group()
    scenery.add(grass)

    speed = 16
    ticks = 0
    stage = START
    
def start():
    global stage
    
    stage = PLAYING
    pygame.mixer.music.play(-1)

def end():
    global stage

    for e in enemies:
        e.speed *= -1
        
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

def show_stats():
    score_txt = FONT_SM.render(str(score), 1, BLACK)
    score_rect = score_txt.get_rect()
    score_rect.centerx = WIDTH / 2
    score_rect.centery = 30

    window.blit(score_txt, score_rect)
 
# Game loop
setup()
running = True

while running:
    # Input handling
    key_events = []
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if stage == START:
                    start()
                elif stage == END:
                    setup()
                else:
                    key_events.append(event)

    keys_pressed = pygame.key.get_pressed()
    
    # Game logic
    if stage == PLAYING:
        road.update()
        scenery.update()

        items.update()

        player.update(key_events, keys_pressed, road, enemies)

        if car.hit == True:
            end()
            
        if len(enemies) < num_enemy_cars:
            e = EnemyCar()
            enemies.add(e)

        ticks = (ticks + 1) % (FPS // 4)

        if ticks == 0:
            score += 1

            if score % 100 == 0:
                num_enemy_cars += 1
                
    if stage != START:            
        for e in enemies:
            e.update(road, enemies)
            
    # Drawing
    scenery.draw(window)
    road.draw()
    items.draw(window)
    player.draw(window)
    enemies.draw(window)

    if stage != START:
        show_stats()
    
    if stage == START:
        show_title_screen()
    elif stage == END:
        show_end_screen()

    # Update screen
    pygame.display.update()
    clock.tick(FPS)


# Close window on quit
pygame.quit()
