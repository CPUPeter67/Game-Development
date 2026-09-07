import pygame
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 500, 400
MOVEMENT_SPEED = 5
FONT_SIZE = 60

pygame.init()

background_image = pygame.transform.scale(
    pygame.image.load("doggyz.webp"),
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

font = pygame.font.SysFont(
    "Arial",
    FONT_SIZE
)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, color, width, height):
        super().__init__()

        self.image = pygame.Surface(
            [width, height]
        )
        self.image.fill(color)

        self.rect = self.image.get_rect()

    def move(self, x_change, y_change):
        self.rect.x = max(
            min(
                self.rect.x + x_change,
                SCREEN_WIDTH - self.rect.width
            ),
            0
        )

        self.rect.y = max(
            min(
                self.rect.y + y_change,
                SCREEN_HEIGHT - self.rect.height
            ),
            0
        )


screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "Pet Food Collection Game"
)

all_sprites = pygame.sprite.Group()

pet = Sprite(
    pygame.Color("brown"),
    40,
    40
)

pet.rect.x = 30
pet.rect.y = 180

all_sprites.add(pet)

pet_food = Sprite(
    pygame.Color("orange"),
    30,
    30
)

pet_food.rect.x = random.randint(
    100,
    SCREEN_WIDTH - pet_food.rect.width
)

pet_food.rect.y = random.randint(
    0,
    SCREEN_HEIGHT - pet_food.rect.height
)

all_sprites.add(pet_food)

running = True
food_collected = False

clock = pygame.time.Clock()


while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    if not food_collected:

        keys = pygame.key.get_pressed()

        x_change = (
            keys[pygame.K_RIGHT] -
            keys[pygame.K_LEFT]
        ) * MOVEMENT_SPEED

        y_change = (
            keys[pygame.K_DOWN] -
            keys[pygame.K_UP]
        ) * MOVEMENT_SPEED

        pet.move(
            x_change,
            y_change
        )

        if pet.rect.colliderect(
            pet_food.rect
        ):
            all_sprites.remove(
                pet_food
            )

            food_collected = True

    screen.blit(
        background_image,
        (0, 0)
    )

    all_sprites.draw(screen)

    if food_collected:

        win_text = font.render(
            "Food Collected!",
            True,
            pygame.Color("black")
        )

        text_x = (
            SCREEN_WIDTH -
            win_text.get_width()
        ) // 2

        text_y = (
            SCREEN_HEIGHT -
            win_text.get_height()
        ) // 2

        screen.blit(
            win_text,
            (text_x, text_y)
        )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()