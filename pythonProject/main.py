# Flappy Birds Game

import random
import sys
import pygame
from pygame.locals import *
from itertools import cycle

FPS = 32
screen_width = 288
screen_height = 512

pygame.init()
window = pygame.display.set_mode((screen_width, screen_height))
time_clock = pygame.time.Clock()
play_area = screen_height * 0.8
game_image = {}
game_audio_sound = {}

player_imgs = [
    "assets/sprites/redbird-downflap.png",
    "assets/sprites/redbird-midflap.png",
    "assets/sprites/redbird-upflap.png",
]

background_img = "assets/sprites/background-day.png"
pipe_img = "assets/sprites/pipe-green.png"
gameover_img = "assets/sprites/gameover.png"


def welcome_main_screen():
    p_x = int(screen_width / 5)
    p_y = int(screen_height - game_image['player'][0].get_height() / 2)
    msgx = int((screen_width - game_image['message'].get_width()) / 2)
    msgy = int(screen_height * 0.13)
    b_x = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
        window.blit(game_image['background'], (0, 0))
        window.blit(game_image['player'][0], (p_x, p_y))
        window.blit(game_image['message'], (msgx, msgy))
        window.blit(game_image['base'], (b_x, play_area))
        pygame.display.update()
        time_clock.tick(FPS)


def main_gameplay():
    score = 0
    p_x = int(screen_width / 5)
    p_y = int(screen_width / 2)
    b_x = 0
    bird_index = 0
    bird_index_gen = cycle([0, 1, 2, 1])

    n_pip1 = get_random_pipes()
    n_pip2 = get_random_pipes()

    up_pipes = [
        {'x': screen_width + 200, 'y': n_pip1[0]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': n_pip2[0]['y']},
    ]

    low_pipes = [
        {'x': screen_width + 200, 'y': n_pip1[1]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': n_pip2[1]['y']},
    ]

    pipe_vx = -4

    p_vx = -9
    p_mvx = 10
    p_mvy = -8
    p_accuracy = 1

    p_flap_accuracy = -8
    p_flap = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if p_y > 0:
                    p_vx = p_flap_accuracy
                    p_flap = True
                    game_audio_sound['wing'].play()

        cr_test = is_colliding(p_x, p_y, up_pipes, low_pipes)
        if cr_test:
            display_gameover_screen()
            return

        p_middle_positions = p_x + game_image['player'][0].get_width() / 2
        for pipe in up_pipes:
            pip_middle_positions = pipe['x'] + game_image['pipe'][0].get_width() / 2
            if pip_middle_positions <= p_middle_positions < pip_middle_positions + 4:
                score += 1
                print(f"Your score is {score}")
                game_audio_sound['point'].play()

        if p_vx < p_mvx and not p_flap:
            p_vx += p_accuracy

        if p_flap:
            p_flap = False
        p_height = game_image['player'][0].get_height()
        p_y = p_y + min(p_vx, play_area - p_y - p_height)

        for pipe_upper, pipe_lower in zip(up_pipes, low_pipes):
            pipe_upper['x'] += pipe_vx
            pipe_lower['x'] += pipe_vx

        if 0 < up_pipes[0]['x'] < 5:
            new_pipe = get_random_pipes()
            up_pipes.append(new_pipe[0])
            low_pipes.append(new_pipe[1])

        if up_pipes[0]['x'] < -game_image['pipe'][0].get_width():
            up_pipes.pop(0)
            low_pipes.pop(0)

        bird_index = next(bird_index_gen)
        window.blit(game_image['background'], (0, 0))
        for pipe_upper, pipe_lower in zip(up_pipes, low_pipes):
            window.blit(game_image['pipe'][0], (pipe_upper['x'], pipe_upper['y']))
            window.blit(game_image['pipe'][1], (pipe_lower['x'], pipe_lower['y']))

        window.blit(game_image['base'], (b_x, play_area))
        window.blit(game_image['player'][bird_index], (p_x, p_y))
        d = [int(x) for x in list(str(score))]
        w = 0

        for digit in d:
            w += game_image['numbers'][digit].get_width()

        x_offset = (screen_width - w) / 2

        for digit in d:
            window.blit(game_image['numbers'][digit], (x_offset, screen_height * 0.12))
            x_offset += game_image['numbers'][digit].get_width()

        pygame.display.update()
        time_clock.tick(FPS)


def is_colliding(p_x, p_y, up_pipes, low_pipes):
    player_rect = pygame.Rect(p_x, p_y, game_image['player'][0].get_width(), game_image['player'][0].get_height())

    if p_y > play_area - 25 or p_y < 0:
        game_audio_sound['hit'].play()
        return True

    for pipe in up_pipes:
        pipe_rect = pygame.Rect(pipe['x'], pipe['y'], game_image['pipe'][0].get_width(),
                                game_image['pipe'][0].get_height())
        if player_rect.colliderect(pipe_rect):
            game_audio_sound['hit'].play()
            return True

    for pipe in low_pipes:
        pipe_rect = pygame.Rect(pipe['x'], pipe['y'], game_image['pipe'][1].get_width(),
                                game_image['pipe'][1].get_height())
        if player_rect.colliderect(pipe_rect):
            game_audio_sound['hit'].play()
            return True

    return False


def get_random_pipes():
    pipe_h = game_image['pipe'][0].get_height()
    off_s = screen_height / 3
    yes2 = off_s + random.randrange(0, int(screen_height - game_image['base'].get_height() - 1.2 * off_s))
    pipe_x = screen_width + 10
    y1 = pipe_h - yes2 + off_s
    pipe = [
        {'x': pipe_x, 'y': -y1},
        {'x': pipe_x, 'y': yes2},
    ]

    return pipe


def display_gameover_screen():
    window.blit(game_image['gameover'], (screen_width // 2 - game_image['gameover'].get_width() // 2,
                                         screen_height // 2 - game_image['gameover'].get_height() // 2))
    pygame.display.update()
    pygame.time.wait(2000)


if __name__ == "__main__":
    pygame.display.set_caption("Flappy Bird Game")
    game_image['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha(),
    )

    game_image['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    game_image['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    game_image['pipe'] = (
        pygame.transform.rotate(pygame.image.load(pipe_img).convert_alpha(), 180),
        pygame.image.load(pipe_img).convert_alpha(),
    )

    game_audio_sound['die'] = pygame.mixer.Sound('assets/audio/die.wav')
    game_audio_sound['hit'] = pygame.mixer.Sound('assets/audio/hit.wav')
    game_audio_sound['point'] = pygame.mixer.Sound('assets/audio/point.wav')
    game_audio_sound['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh.wav')
    game_audio_sound['wing'] = pygame.mixer.Sound('assets/audio/wing.wav')

    game_image['background'] = pygame.image.load(background_img).convert()
    game_image['player'] = [
        pygame.image.load(player_imgs[0]).convert_alpha(),
        pygame.image.load(player_imgs[1]).convert_alpha(),
        pygame.image.load(player_imgs[2]).convert_alpha(),
    ]

    game_image['gameover'] = pygame.image.load(gameover_img).convert_alpha()

    while True:
        welcome_main_screen()
        main_gameplay()
