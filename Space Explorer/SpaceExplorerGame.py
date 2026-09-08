import math
import random
from pathlib import Path
import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_START_X = 370
PLAYER_START_Y = 380
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150
ENEMY_SPEED_X = 4
ENEMY_SPEED_Y = 40
BULLET_SPEED_Y = 10
COLLISION_DISTANCE = 27

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

asset_dir = Path(__file__).resolve().parent
background = pygame.image.load(str(asset_dir / "Starz.webp"))
icon = pygame.image.load(str(asset_dir / "UFO.png"))
pygame.display.set_icon(icon)

# Thanks to dklon for the free sounds!
laser_sound = pygame.mixer.Sound(str(asset_dir / "laser1.wav"))

playerImg = pygame.image.load(str(asset_dir / "Spaceship.png"))
playerX = PLAYER_START_X
playerY = PLAYER_START_Y
playerX_change = 0

enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load(str(asset_dir / "UFO.png")))
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX))
    enemyX_change.append(ENEMY_SPEED_X)
    enemyY_change.append(ENEMY_SPEED_Y)

bulletImg = pygame.image.load(str(asset_dir / "Bullet.png"))
bulletX = 0
bulletY = playerY
bulletY_change = BULLET_SPEED_Y
bullet_state = "ready"

score_value = 0
font = pygame.font.Font(None, 32)
textX = 10
textY = 10

over_font = pygame.font.Font(None, 64)

def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def player(x, y):
    screen.blit(playerImg, (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    return distance < COLLISION_DISTANCE

running = True
game_over = False
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            elif event.key == pygame.K_RIGHT:
                playerX_change = 5
            elif event.key == pygame.K_SPACE and bullet_state == "ready":
                laser_sound.play()
                bulletX = playerX
                bulletY = playerY
                bullet_state = "fire"
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                playerX_change = 0

    if not game_over:
        playerX += playerX_change
        playerX = max(0, min(playerX, SCREEN_WIDTH - 64))

        for i in range(num_of_enemies):
            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0 or enemyX[i] >= SCREEN_WIDTH - 64:
                enemyX_change[i] *= -1
                enemyY[i] += enemyY_change[i]

            if isCollision(enemyX[i], enemyY[i], bulletX, bulletY):
                bulletY = playerY
                bullet_state = "ready"
                score_value += 5
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
                enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)

            if enemyY[i] > SCREEN_HEIGHT - 64:
                game_over = True

        if bullet_state == "fire":
            bulletY -= bulletY_change
            if bulletY <= 0:
                bulletY = playerY
                bullet_state = "ready"

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    for i in range(num_of_enemies):
        enemy(enemyX[i], enemyY[i], i)
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
    player(playerX, playerY)
    show_score(textX, textY)
    if game_over:
        game_over_text()
    pygame.display.update()
    clock.tick(60)

pygame.quit()