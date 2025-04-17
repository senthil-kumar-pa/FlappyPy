import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BIRD_SIZE = 64
FRAME_COUNT = 4

# Initialize
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 48)

# Load assets
background = pygame.image.load("background.jpg")
pipe_img = pygame.image.load("pipe.png").convert_alpha()
bird_sprite_sheet = pygame.image.load("bird_sprite.png").convert_alpha()
pygame.mixer.music.load("background_music.mp3")
# pygame.mixer.music.play(-1)

# Bird animation setup
bird_frames = [
    bird_sprite_sheet.subsurface(pygame.Rect(i * BIRD_SIZE, 0, BIRD_SIZE, BIRD_SIZE))
    for i in range(FRAME_COUNT)
]

# Game variables
gravity = 0.05
jump_strength = -2
pipe_gap = 300
pipe_speed = 1
pipe_mask_cache = {}

def generate_pipe():
    height = random.randint(150, 450)
    top_rect = pipe_img.get_rect(midbottom=(SCREEN_WIDTH + 50, height - pipe_gap // 2))
    bottom_rect = pipe_img.get_rect(midtop=(SCREEN_WIDTH + 50, height + pipe_gap // 2))
    return top_rect, bottom_rect

def get_mask(image):
    return pygame.mask.from_surface(image)

def check_collision(bird_image, bird_rect, pipes):
    bird_mask = get_mask(bird_image)

    for i, pipe in enumerate(pipes):
        if bird_rect.colliderect(pipe):
            # Create flipped pipe image if needed
            flipped = (i % 2 == 0)
            pipe_image = pygame.transform.flip(pipe_img, False, True) if flipped else pipe_img

            # Use cache
            key = id(pipe)
            if key not in pipe_mask_cache:
                pipe_mask_cache[key] = get_mask(pipe_image)

            pipe_mask = pipe_mask_cache[key]

            offset = (pipe.left - bird_rect.left, pipe.top - bird_rect.top)
            if bird_mask.overlap(pipe_mask, offset):
                return True

    return bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT

def draw_main_menu():
    screen.blit(background, (0, 0))
    title = font.render("Flappy Bird", True, (255, 255, 255))
    play_text = font.render("Play", True, (0, 0, 0))
    quit_text = font.render("Quit", True, (0, 0, 0))

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 100, 250, 200, 60))
    pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH // 2 - 100, 330, 200, 60))

    screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 260))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 340))

    pygame.display.flip()

def game_over_screen(score):
    while True:
        screen.blit(background, (0, 0))
        over_text = font.render("Game Over", True, (255, 0, 0))
        score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
        retry_text = font.render("Retry", True, (0, 0, 0))
        quit_text = font.render("Quit", True, (0, 0, 0))

        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))

        pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 100, 260, 200, 60))
        pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH // 2 - 100, 340, 200, 60))

        screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 270))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - 100 <= mx <= SCREEN_WIDTH // 2 + 100:
                    if 260 <= my <= 320:
                        return True  # Retry
                    elif 340 <= my <= 400:
                        pygame.quit()
                        sys.exit()

def main_game():
    bird_x = 100
    bird_y = 300
    bird_velocity = 0
    bird_rect = bird_frames[0].get_rect(center=(bird_x, bird_y))
    pipes = []
    frame = 0
    score = 0
    pipe_timer = 0

    global pipe_mask_cache
    pipe_mask_cache = {}

    running = True
    while running:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_velocity = jump_strength

        bird_velocity += gravity
        bird_y += bird_velocity
        bird_rect.centery = bird_y

        # Animate bird
        frame = (frame + 1) % (FRAME_COUNT * 5)
        current_frame = bird_frames[frame // 5]
        screen.blit(current_frame, bird_rect)

        # Pipe logic
        pipe_timer += 1
        if pipe_timer > 190:
            pipes.extend(generate_pipe())
            pipe_timer = 0

        for pipe in pipes:
            pipe.centerx -= pipe_speed

        # Remove off-screen pipes and clear their masks
        pipes = [p for p in pipes if p.right > 0]
        for key in list(pipe_mask_cache.keys()):
            if all(id(p) != key for p in pipes):
                pipe_mask_cache.pop(key, None)

        # Draw pipes
        for i, pipe in enumerate(pipes):
            flipped_pipe = pygame.transform.flip(pipe_img, False, True) if i % 2 == 0 else pipe_img
            screen.blit(flipped_pipe, pipe)

        # Collision
        if check_collision(current_frame, bird_rect, pipes):
            if game_over_screen(score):
                return

        # Score
        for pipe in pipes:
            if pipe.centerx == bird_x:
                score += 0.5
        score_text = font.render(str(int(score)), True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 50))

        pygame.display.update()
        clock.tick(60)

# Main loop
while True:
    draw_main_menu()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - 100 <= mx <= SCREEN_WIDTH // 2 + 100:
                    if 250 <= my <= 310:
                        main_game()
                    elif 330 <= my <= 390:
                        pygame.quit()
                        sys.exit()
