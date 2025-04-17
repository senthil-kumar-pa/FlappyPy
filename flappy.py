import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BIRD_SIZE = 64
FRAME_COUNT = 4
PIPE_GAP = 250
PIPE_SPEED = 1
GRAVITY = 0.24
JUMP_STRENGTH = -5
scored_pipes = set()

# Colors
WHITE = (255, 255, 255)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
LIGHT_BLUE = (173, 216, 230)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 36)

# Load assets
background = pygame.image.load("background.jpg")
pipe_img = pygame.image.load("pipe.png").convert_alpha()
bird_sprite_sheet = pygame.image.load("bird_sprite.png").convert_alpha()
clouds_img = pygame.image.load("clouds.png").convert_alpha()
mountains_img = pygame.image.load("mountains.png").convert_alpha()
ground_img = pygame.image.load("ground.png").convert_alpha()

bird_frames = [
    bird_sprite_sheet.subsurface(pygame.Rect(i * BIRD_SIZE, 0, BIRD_SIZE, BIRD_SIZE))
    for i in range(FRAME_COUNT)
]

# Load sounds
pygame.mixer.init()
pygame.mixer.music.load("background_music.mp3")
fly_sound = pygame.mixer.Sound("fly.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
score_sound = pygame.mixer.Sound("score.wav")

pygame.mixer.music.play(-1)  # loop forever


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.frame = 0
        self.rect = bird_frames[0].get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(bird_frames[0])

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.centery = self.y
        self.mask = pygame.mask.from_surface(bird_frames[self.frame // 5])
        self.frame = (self.frame + 1) % (FRAME_COUNT * 5)

    def jump(self):
        self.velocity = JUMP_STRENGTH
        fly_sound.play()

    def get_frame(self):
        return bird_frames[self.frame // 5]


class Pipe:
    def __init__(self):
        height = random.randint(150, 450)
        self.top_rect = pipe_img.get_rect(midbottom=(SCREEN_WIDTH + 50, height - PIPE_GAP // 2))
        self.bottom_rect = pipe_img.get_rect(midtop=(SCREEN_WIDTH + 50, height + PIPE_GAP // 2))

    def move(self):
        self.top_rect.centerx -= PIPE_SPEED
        self.bottom_rect.centerx -= PIPE_SPEED

    def draw(self):
        screen.blit(pipe_img, self.top_rect)
        screen.blit(pipe_img, self.bottom_rect)


class Parallax:
    def __init__(self):
        self.cloud_x = 0
        self.mountain_x = 0
        self.ground_x = 0

    def move(self):
        self.cloud_x -= 1
        self.mountain_x -= 2
        self.ground_x -= PIPE_SPEED
        if self.cloud_x <= -SCREEN_WIDTH: self.cloud_x = 0
        if self.mountain_x <= -SCREEN_WIDTH: self.mountain_x = 0
        if self.ground_x <= -SCREEN_WIDTH: self.ground_x = 0

    def draw(self):
        screen.blit(clouds_img, (self.cloud_x, 0))
        screen.blit(clouds_img, (self.cloud_x + SCREEN_WIDTH, 0))
        screen.blit(mountains_img, (self.mountain_x, 100))
        screen.blit(mountains_img, (self.mountain_x + SCREEN_WIDTH, 100))
        screen.blit(ground_img, (self.ground_x, SCREEN_HEIGHT - 100))
        screen.blit(ground_img, (self.ground_x + SCREEN_WIDTH, SCREEN_HEIGHT - 100))


class Game:
    def __init__(self):
        self.bird = Bird(150, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.pipe_timer = 0
        self.score = 0
        self.paused = False
        self.mask_cache = {}
        self.parallax = Parallax()

    def generate_pipe(self):
        pipe = Pipe()
        self.pipes.append(pipe)

    def check_collision(self):
        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                return True
        return self.bird.rect.top <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT

    def update(self):
        if not self.paused:
            self.bird.update()
            self.parallax.move()
            self.pipe_timer += 1

            if self.pipe_timer > 200:
                self.generate_pipe()
                self.pipe_timer = 0

            for pipe in self.pipes:
                pipe.move()

            self.pipes = [pipe for pipe in self.pipes if pipe.top_rect.right > 0]

            if self.check_collision():
                hit_sound.play()
                return False
            return True

    def draw(self):
        screen.fill(WHITE)
        self.parallax.draw()
        screen.blit(self.bird.get_frame(), self.bird.rect)

        for pipe in self.pipes:
            pipe.draw()

        score_text = font.render(str(self.score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 30))

        pygame.display.update()

    def toggle_pause(self):
        self.paused = not self.paused


def draw_main_menu():
    screen.fill(LIGHT_BLUE)
    title = font.render("Flappy Bird", True, WHITE)
    play_text = font.render("Play", True, (0, 0, 0))
    quit_text = font.render("Quit", True, (0, 0, 0))

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    pygame.draw.rect(screen, LIGHT_GREEN, (SCREEN_WIDTH // 2 - 100, 250, 200, 60), border_radius=10)
    pygame.draw.rect(screen, LIGHT_RED, (SCREEN_WIDTH // 2 - 100, 330, 200, 60), border_radius=10)

    screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 260))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 340))

    pygame.display.flip()


def main_loop():
    game = Game()
    running = True

    while running:
        draw_main_menu()
        in_menu = True
        while in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game = Game()  # Reset game
                        in_menu = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        while running and game.update():
            game.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.bird.jump()
                    if event.key == pygame.K_p:
                        game.toggle_pause()

            clock.tick(60)

        pygame.display.flip()


main_loop()
