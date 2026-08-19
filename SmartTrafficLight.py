import random
import pygame

# Configuration
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

ROAD_COLOR = pygame.Color("darkgray")
WHITE = pygame.Color("white")
YELLOW = pygame.Color("yellow")
BLUE = pygame.Color("blue")
ORANGE = pygame.Color("orange")
RED = pygame.Color("red")
GREEN = pygame.Color("green")

SENSOR_TRIGGERED_EVENT = pygame.USEREVENT + 1


class Car(pygame.sprite.Sprite):

    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.velocity = [3, 0]

    def update(self):
        self.rect.move_ip(self.velocity)

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.velocity[0] = -self.velocity[0]
            pygame.event.post(pygame.event.Event(SENSOR_TRIGGERED_EVENT))

    def change_color(self):
        self.image.fill(random.choice([WHITE, YELLOW, BLUE, ORANGE]))


class TrafficSignal:

    def __init__(self):
        self.color = RED

    def toggle(self):
        self.color = GREEN if self.color == RED else RED

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color("black"), (275, 40, 50, 90))
        pygame.draw.circle(surface, self.color, (300, 85), 20)


def draw_road(screen):
    screen.fill(ROAD_COLOR)
    for x in range(0, SCREEN_WIDTH, 80):
        pygame.draw.rect(screen, WHITE, (x, 345, 45, 5))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Smart Traffic Signal Simulator")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    car = Car(WHITE, 70, 35)
    car.rect.x = 50
    car.rect.y = 300
    all_sprites.add(car)

    signal = TrafficSignal()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SENSOR_TRIGGERED_EVENT:
                car.change_color()
                signal.toggle()

        all_sprites.update()

        draw_road(screen)
        signal.draw(screen)
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()