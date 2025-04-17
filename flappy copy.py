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

def generate_pipe():
    height = random.randint(150, 450)
    top_rect = pipe_img.get_rect(midbottom=(SCREEN_WIDTH + 50, height - PIPE_GAP // 2))
    bottom_rect = pipe_img.get_rect(midtop=(SCREEN_WIDTH + 50, height + PIPE_GAP // 2))
    return top_rect, bottom_rect

def draw_parallax(cloud_x, mountain_x, ground_x):
    screen.blit(clouds_img, (cloud_x, 0))
    screen.blit(clouds_img, (cloud_x + SCREEN_WIDTH, 0))
    screen.blit(mountains_img, (mountain_x, 100))
    screen.blit(mountains_img, (mountain_x + SCREEN_WIDTH, 100))
    screen.blit(ground_img, (ground_x, SCREEN_HEIGHT - 100))
    screen.blit(ground_img, (ground_x + SCREEN_WIDTH, SCREEN_HEIGHT - 100))

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

def draw_game_over(score):
    screen.fill(LIGHT_BLUE)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    replay_text = font.render("Replay", True, (0, 0, 0))
    quit_text = font.render("Quit", True, (0, 0, 0))

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 160))

    pygame.draw.rect(screen, LIGHT_GREEN, (SCREEN_WIDTH // 2 - 100, 250, 200, 60), border_radius=10)
    pygame.draw.rect(screen, LIGHT_RED, (SCREEN_WIDTH // 2 - 100, 330, 200, 60), border_radius=10)

    screen.blit(replay_text, (SCREEN_WIDTH // 2 - replay_text.get_width() // 2, 260))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 340))

    pygame.display.flip()

def check_collision(bird_rect, pipes, bird_mask, mask_cache):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            key = (pipe.x, pipe.y)
            if key not in mask_cache:
                pipe_img_flipped = pygame.transform.flip(pipe_img, False, True) if pipe.bottom < SCREEN_HEIGHT // 2 else pipe_img
                mask_cache[key] = pygame.mask.from_surface(pipe_img_flipped)
            offset = (pipe.x - bird_rect.x, pipe.y - bird_rect.y)
            if bird_mask.overlap(mask_cache[key], offset):
                return True
    return bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT

def main_game():
    bird_x, bird_y = 150, SCREEN_HEIGHT // 2
    bird_velocity = 0
    frame = 0
    score = 0
    pipes = []
    pipe_timer = 0
    running = True
    paused = False
    mask_cache = {}

    bird_rect = bird_frames[0].get_rect(center=(bird_x, bird_y))
    bird_mask = pygame.mask.from_surface(bird_frames[0])

    cloud_x = 0
    mountain_x = 0
    ground_x = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not paused:
                    bird_velocity = JUMP_STRENGTH
                    fly_sound.play()
                if event.key == pygame.K_p:
                    paused = not paused

        if paused:
            pause_text = font.render("Paused - Press 'P' to Resume", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            clock.tick(10)
            continue

        bird_velocity += GRAVITY
        bird_y += bird_velocity
        bird_rect.centery = bird_y
        bird_mask = pygame.mask.from_surface(bird_frames[frame // 5])

        frame = (frame + 1) % (FRAME_COUNT * 5)
        current_frame = bird_frames[frame // 5]

        # Scroll parallax layers
        cloud_x -= 1
        mountain_x -= 2
        ground_x -= PIPE_SPEED
        if cloud_x <= -SCREEN_WIDTH: cloud_x = 0
        if mountain_x <= -SCREEN_WIDTH: mountain_x = 0
        if ground_x <= -SCREEN_WIDTH: ground_x = 0

        # Draw background
        screen.blit(background, (0, 0))
        draw_parallax(cloud_x, mountain_x, ground_x)
        screen.blit(current_frame, bird_rect)

        # Pipes
        pipe_timer += 1
        if pipe_timer > 200:
            pipes.extend(generate_pipe())
            pipe_timer = 0

        for pipe in pipes:
            pipe.centerx -= PIPE_SPEED

        pipes = [p for p in pipes if p.right > 0]

        # Clean up old mask cache
        mask_cache = {(x, y): mask for (x, y), mask in mask_cache.items() if x > 0}

        for i, pipe in enumerate(pipes):
            flipped = pipe.bottom < SCREEN_HEIGHT // 2
            img = pygame.transform.flip(pipe_img, False, True) if flipped else pipe_img
            screen.blit(img, pipe)

        if check_collision(bird_rect, pipes, bird_mask, mask_cache):
            hit_sound.play()
            return score

        for i in range(0, len(pipes), 2):  # only bottom pipes
            bottom_pipe = pipes[i + 1]
            pipe_id = id(bottom_pipe)  # unique identifier

            if bottom_pipe.centerx < bird_x and pipe_id not in scored_pipes:
                score += 1
                score_sound.play()
                scored_pipes.add(pipe_id)

                score_text = font.render(str(int(score)), True, WHITE)
                screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 30))

        pygame.display.update()
        clock.tick(60)

def main_loop():
    while True:
        draw_main_menu()
        in_menu = True
        while in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if SCREEN_WIDTH // 2 - 100 <= mx <= SCREEN_WIDTH // 2 + 100:
                        if 250 <= my <= 310:
                            score = main_game()
                            draw_game_over(score)
                            in_game_over = True
                            while in_game_over:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        mx, my = pygame.mouse.get_pos()
                                        if SCREEN_WIDTH // 2 - 100 <= mx <= SCREEN_WIDTH // 2 + 100:
                                            if 250 <= my <= 310:
                                                in_game_over = False
                                                in_menu = False
                                            elif 330 <= my <= 390:
                                                pygame.quit()
                                                sys.exit()
                        elif 330 <= my <= 390:
                            pygame.quit()
                            sys.exit()

main_loop()
