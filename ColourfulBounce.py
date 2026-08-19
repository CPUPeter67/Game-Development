import pygame 
import random

pygame.init()

SPRITE_COLOUR_CHANGE_EVENT = pygame.USEREVENT + 1
BACKGROUND_COLOUR_CHANGE_EVENT = pygame.USEREVENT + 2

BLUE = pygame.Color('blue')
LIGHTBLUE = pygame.Color('lightblue')
DARKBLUE = pygame.Color('darkblue')

YELLOW = pygame.Color('yellow')
MAGENTA = pygame.Color('magenta')
ORANGE = pygame.Color('orange')
WHITE = pygame.Color('white')

class Sprite(pygame.sprite.Sprite):
    def __init__(self, colour, height, width):

        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.velocity = [random.choice([-1, 1]), random.choice([-1, 1])]

    def update(self):
        self.rect.move_ip(self.velocity)
        boundary_hit = False
        if self.rect.left <= 0 or self.rect.right >= 500:
            self.velocity[0] = -self.velocity[0]
            boundary_hit = True

        if self.rect.top <= 0 or self.rect.bottom >= 400:
            self.velocity[1] = -self.velocity[1]
            boundary_hit = True 

        if boundary_hit:
            pygame.event.post(pygame.event.Event(SPRITE_COLOUR_CHANGE_EVENT))
            pygame.event.post(pygame.event.Event(BACKGROUND_COLOUR_CHANGE_EVENT))

    def change_colour(self, colour):
        self.image.fill(random.choice([YELLOW, MAGENTA, ORANGE, WHITE]))

    def change_background_color(self):
        global bg_color
        bg_color = random.choice([BLUE, LIGHTBLUE, DARKBLUE])

all_sprites_list = pygame.sprite.Group()
sp1 = Sprite(WHITE, 20, 30)
sp1.rect.x = random.randint(0, 480)
sp1.rect.y = random.randint(0, 370)
all_sprites_list.add(sp1)

screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Boundary Sprite")  

bg_color = BLUE
screen.fill(bg_color)

exit = False
clock = pygame.time.Clock()

while not exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

        elif event.type == SPRITE_COLOUR_CHANGE_EVENT:
            sp1.change_colour(random.choice([YELLOW, MAGENTA, ORANGE, WHITE]))
        elif event.type == BACKGROUND_COLOUR_CHANGE_EVENT:
            sp1.change_background_color()

all_sprites_list.update()
screen.fill(bg_color)  
all_sprites_list.draw(screen)

pygame.display.flip()
clock.tick(60)

pygame.quit()
