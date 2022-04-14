import random

import pygame
import sys

pygame.init()

# system variables
clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936 

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# load images
bg = pygame.image.load("img/bg.png")
ground = pygame.image.load("img/ground.png")
button_img = pygame.image.load("img/restart.png")

# font and color variables
font = pygame.font.SysFont("Bauhaus 93", 60)
color_white = (255, 255, 255)
color_red = (255, 50, 50)
color_yellow = (230, 230, 70)

# define game variables
ground_scroll = 0
scroll_speed = 4
gravity = 0.5
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # in ms
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    size = font.size(text)
    drawX = x - (size[0] / 2.)
    drawY = y - (size[1] / 2.)
    screen.blit(img, (drawX, drawY))


def reset_game():
    pipe_group.empty()
    bird_group.empty()
    new_flappy = Bird(100, int(screen_width / 2))
    bird_group.add(new_flappy)

    return 0, new_flappy  # score, flappy replace


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.frame_count = 0
        for i in range(3):
            img = pygame.image.load(f"img/bird{i + 1}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if game_over:
            return

        if flying:
            self.vel += gravity
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        # jump
        if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
            self.vel = -10
            self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # handle animation
        self.frame_count += 1
        flap_cooldown = 5

        if self.frame_count > flap_cooldown:
            self.frame_count = 0
            self.index += 1
            self.index %= len(self.images)

        # handle bird rotation
        self.image = pygame.transform.rotate(self.images[self.index], self.vel * -3)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        # position 1 is form top, -1 is bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        else:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def clicked(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
            action = True

        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # draw ground
    screen.blit(ground, (ground_scroll, 768))

    # score
    if len(pipe_group) > 0:
        if pipe_group.sprites()[0].rect.left < bird_group.sprites()[0].rect.left < pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, color_yellow, int(screen_width / 2), 60)

    # look for collision and check if bird hit ground
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 or flappy.rect.bottom >= 768:
        game_over = True
        flying = False
        draw_text("GAME OVER", font, color_red, int(screen_width / 2), int(screen_height / 2 - 200))

    if not game_over and flying:
        # generate pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2 + pipe_height), -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2 + pipe_height), 1)
            pipe_group.add(top_pipe)
            pipe_group.add(btm_pipe)
            last_pipe = time_now

        # scroll the ground
        ground_scroll -= scroll_speed
        if ground_scroll < -35:
            ground_scroll = 0
        pipe_group.update()

    if game_over:
        button.draw()

        if button.clicked():
            game_over = False
            flying = True
            score, flappy = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()
