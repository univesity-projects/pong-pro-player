#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pickle

import neat
import pygame
import math
import random
import time
import operator


class Entity:

    # set and get functions are simulating an centered object
    # to get or set the real x and y you've to set or get directly from respective var

    def __init__(self, x, y, width, height, speed, sprite, parent):
        self.x = x - width / 2
        self.y = y - height / 2
        self.width = width
        self.height = height
        self.speed = speed
        self.sprite = sprite
        self.parent = parent

    def update(self, delta):
        pass

    def render(self):
        self.parent.screen.blit(self.sprite, (self.x, self.y))

    def set_x(self, x):
        self.x = x - self.width / 2

    def set_y(self, y):
        self.y = y - self.height / 2

    def get_x(self):
        return self.x + self.width / 2

    def get_y(self):
        return self.y + self.height / 2

    def up_collision(self):
        if self.y <= 0:
            self.y = 0
            return True
        return False

    def down_collision(self):
        if self.y + self.height >= self.parent.DISPLAY_HEIGHT:
            self.y = self.parent.DISPLAY_HEIGHT - self.height
            return True
        return False


class Racket(Entity):

    up = False
    down = False

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)

    def update(self, delta):
        if self.up and not self.up_collision():
            self.y -= self.speed * delta
        elif self.down and not self.down_collision():
            self.y += self.speed * delta

    def update_machine(self, delta, player):
        ball = self.parent.ball

        # if the ball is coming to racket's' direction, it follow the ball
        if (ball.x_speed < 0 and player == self.parent.PLAYER_LEFT) or (ball.x_speed > 0 and player == self.parent.PLAYER_RIGHT):
            if ball.get_y() < self.get_y() - ball.height and not self.up_collision():
                self.y -= self.speed * delta
            elif ball.get_y() > self.get_y() + ball.height and not self.down_collision():
                self.y += self.speed * delta
        # else the racket just go to the middle of screen
        else:
            if self.get_y() > self.parent.DISPLAY_HEIGHT / 2 + ball.height:
                self.y -= self.speed * delta
            elif self.get_y() < self.parent.DISPLAY_HEIGHT / 2 - ball.height:
                self.y += self.speed * delta


class Ball(Entity):

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)
        self.racket_left = self.parent.racket_left
        self.racket_right = self.parent.racket_right
        self.x_speed = 0
        self.y_speed = 0
        self.slaps = 0

    def update(self, delta):
        self.x += self.x_speed * delta
        self.y += self.y_speed * delta

        self.collision()

        # check is some player did a score
        if self.get_x() > self.parent.DISPLAY_WIDTH:
            self.parent.score_up(self.parent.PLAYER_LEFT)
            self.slaps = 0
        elif self.get_x() < 0:
            self.slaps = 0
            self.parent.score_up(self.parent.PLAYER_RIGHT)

    def collision(self):
        ball_rect = pygame.rect.Rect((self.x, self.y, self.width, self.height))
        racket_left_rect = pygame.rect.Rect((self.racket_left.x, self.racket_left.y, self.racket_left.width, self.racket_left.height))
        racket_right_rect = pygame.rect.Rect((self.racket_right.x, self.racket_right.y, self.racket_right.width, self.racket_right.height))

        # check if the ball collided with left or right racket and set the new angle
        if ball_rect.colliderect(racket_left_rect):
            racket_y = self.racket_left.get_y()
            racket_height = self.racket_left.height
            self.find_angle(0, racket_y, racket_height)
        elif ball_rect.colliderect(racket_right_rect):
            racket_y = self.racket_right.get_y()
            racket_height = self.racket_right.height
            self.find_angle(1, racket_y, racket_height)

        if self.up_collision() or self.down_collision():
            self.y_speed *= -1

    def find_angle(self, index, racket_y, racket_height):
        # 0 left / 1 right
        degrees = [[-15, -30, -45, -60, 0, 15, 30, 45, 60], [-165, -150, -135, -120, 180, 165, 150, 135, 120]]
        ball_y = self.get_y()
        angle_in_degrees = 0

        # as in the original Pong, I divided the racket in 8 sections, returning a 90 degrees angle in the middle and
        # an more and more closed angle following to the end
        if racket_y > ball_y > racket_y - racket_height * 0.125:
            angle_in_degrees = degrees[index][0]
        elif racket_y > ball_y > racket_y - racket_height * 0.250:
            angle_in_degrees = degrees[index][1]
        elif racket_y > ball_y > racket_y - racket_height * 0.375:
            angle_in_degrees = degrees[index][2]
        elif racket_y > ball_y > racket_y - racket_height * 0.500 - self.height:
            angle_in_degrees = degrees[index][3]
        elif ball_y == racket_y:
            angle_in_degrees = degrees[index][4]
        elif racket_y < ball_y < racket_y + racket_height * 0.125:
            angle_in_degrees = degrees[index][5]
        elif racket_y < ball_y < racket_y + racket_height * 0.250:
            angle_in_degrees = degrees[index][6]
        elif racket_y < ball_y < racket_y + racket_height * 0.375:
            angle_in_degrees = degrees[index][7]
        elif racket_y < ball_y < racket_y + racket_height * 0.500 + self.height:
            angle_in_degrees = degrees[index][8]

        self.set_angle(math.radians(angle_in_degrees))
        self.slaps += 1

    def generate(self):
        player = self.parent.player_ball

        self.set_x(self.parent.DISPLAY_WIDTH / 2)
        self.set_y(random.randint(self.height, self.parent.DISPLAY_HEIGHT - self.height))

        if player != self.parent.NO_PLAYER:
            if player == self.parent.PLAYER_LEFT:
                angle = random.randint(120, 180)
                angle = angle * -1 if random.randint(0, 1) == 0 else angle
                self.set_angle(math.radians(angle))
            else:
                self.set_angle(math.radians(random.randint(-60, 60)))
        else:
            num = random.randint(0, 3)
            if num == 0 or num == 2:
                self.set_angle(math.radians(random.randint(-60, 60)))
            elif num == 1:
                self.set_angle(math.radians(random.randint(120, 180)))
            elif num == 3:
                self.set_angle(math.radians(random.randint(-180, -120)))

    def set_angle(self, angle_in_radians):
        speed = self.speed + (50 * self.slaps)
        self.x_speed = speed * math.cos(angle_in_radians)
        self.y_speed = speed * math.sin(angle_in_radians)


class Pong:
    # constants
    BLACK = (0, 0, 0)
    DARK_GRAY = (25, 25, 25)
    WHITE = (255, 255, 255)

    SCALE = 8
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600

    PLAYER_LEFT = 0
    PLAYER_RIGHT = 1
    NO_PLAYER = 2

    PLAYER_VS_PLAYER = 0
    PLAYER_VS_MACHINE = 1
    PLAYER_VS_IA = 2
    IA_VS_MACHINE = 3

    STATE_PLAYING = 0
    STATE_MAIN_MENU = 1
    STATE_PAUSE_MENU = 2
    STATE_SEL_MODE_MENU = 3
    STATE_END_GAME = 5
    STATE_WAIT = 6

    def __init__(self):
        pygame.init()
        icon = pygame.image.load('src/res/icon.png')
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        random.seed(time.time())

        # keys
        self.k_up = False
        self.k_down = False
        self.k_w = False
        self.k_s = False
        self.k_enter = False
        self.k_esc = False

        # sprites
        self.clean_color = self.DARK_GRAY
        self.sprite_scanline = pygame.image.load('src/res/sprite/scanline_overlay.png')
        self.sprite_tv_vignette = pygame.image.load('src/res/sprite/tv_vignette_overlay.png')
        self.sprite_num = []
        for i in range(10):
            self.sprite_num.append(
                self.sprite_load_scaled('src/res/sprite/sprite_num_' + str(i) + '.png', int(self.SCALE / 2)))
        self.sprite_net = self.sprite_load_scaled('src/res/sprite/net.png', self.SCALE)
        sprite_ball = self.sprite_load_scaled('src/res/sprite/ball.png', self.SCALE)
        sprite_racket = self.sprite_load_scaled('src/res/sprite/racket.png', self.SCALE)
        self.font_title = pygame.font.Font('src/res/font/bit5x3.ttf', 128)
        self.font_mid = pygame.font.Font('src/res/font/bit5x3.ttf', 94)
        self.font = pygame.font.Font('src/res/font/bit5x3.ttf', 64)

        # objects
        speed = 800
        mid = 300
        self.racket_left = Racket(50, mid, 16, 64, speed, sprite_racket, self)
        self.racket_right = Racket(750, mid, 16, 64, speed, sprite_racket, self)
        self.ball = Ball(400, mid, 16, 16, 600, sprite_ball, self)

        # control
        self.running = False
        self.effects = True
        self.mode = 0
        self.state = self.STATE_MAIN_MENU
        self.player_ball = self.NO_PLAYER
        # self.state = self.STATE_END_GAME
        self.ia = self.load_ia()
        self.menu_op = 0
        self.sound = True
        self.score_left = 0
        self.score_right = 0
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.timer = 0
        self.elapsed = 0

    def run(self):
        self.running = True

        # main loop
        while self.running:
            self.delta = self.elapsed / 1000.0
            self.update()
            self.render()
            self.elapsed = self.clock.tick(60)

        pygame.quit()

    @staticmethod
    def load_ia():
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        with open('winner.pkl', "rb") as f:
            genome = pickle.load(f)
        return neat.nn.FeedForwardNetwork.create(genome, neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path))

    @staticmethod
    def sprite_load_scaled(path, scale):
        sprite = pygame.image.load(path)
        sprite = pygame.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
        return sprite

    def restart(self):
        self.score_left = 0
        self.score_right = 0
        self.start_match()

    def start_match(self):
        self.racket_left.set_y(self.DISPLAY_HEIGHT / 2)
        self.racket_right.set_y(self.DISPLAY_HEIGHT / 2)
        self.ball.generate()

    def score_up(self, player):
        if player == self.PLAYER_LEFT:
            self.score_left += 1
            self.player_ball = self.PLAYER_RIGHT
        else:
            self.score_right += 1
            self.player_ball = self.PLAYER_LEFT

        self.state = self.STATE_WAIT
        self.timer = 1

    def update(self):
        self.update_events()

        if self.state == self.STATE_PLAYING:
            self.update_playing()
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU or self.state == self.STATE_SEL_MODE_MENU:
            self.update_menus()
        elif self.state == self.STATE_END_GAME:
            self.update_end_game()
        elif self.state == self.STATE_WAIT:
            self.update_wait()

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.k_up = True
                elif event.key == pygame.K_DOWN:
                    self.k_down = True
                elif event.key == pygame.K_w:
                    self.k_w = True
                elif event.key == pygame.K_s:
                    self.k_s = True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.k_enter = True
                elif event.key == pygame.K_ESCAPE:
                    self.k_esc = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.k_up = False
                elif event.key == pygame.K_DOWN:
                    self.k_down = False
                elif event.key == pygame.K_w:
                    self.k_w = False
                elif event.key == pygame.K_s:
                    self.k_s = False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.k_enter = False
                elif event.key == pygame.K_ESCAPE:
                    self.k_esc = False

    def update_playing(self):
        if self.k_esc:
            self.state = self.STATE_PAUSE_MENU

        if self.mode == self.PLAYER_VS_PLAYER:
            # player left (HUMAN)
            self.racket_left.up = self.k_w
            self.racket_left.down = self.k_s
            self.racket_left.update(self.delta)
            # player right (HUMAN)
            self.racket_right.up = self.k_up
            self.racket_right.down = self.k_down
            self.racket_right.update(self.delta)
        elif self.mode == self.PLAYER_VS_MACHINE:
            # player left (MACHINE)
            self.racket_left.update_machine(self.delta, self.PLAYER_LEFT)
            # player right (HUMAN)
            self.racket_right.up = self.k_up
            self.racket_right.down = self.k_down
            self.racket_right.update(self.delta)
        elif self.mode == self.PLAYER_VS_IA:
            # player left (IA)
            self.update_ia()
            # player right (HUMAN)
            self.racket_right.up = self.k_up
            self.racket_right.down = self.k_down
            self.racket_right.update(self.delta)
        elif self.mode == self.IA_VS_MACHINE:
            # player left (IA)
            self.update_ia()
            # player right (MACHINE)
            self.racket_right.update_machine(self.delta, self.PLAYER_RIGHT)

        self.ball.update(self.delta)

        if self.score_right >= 11 or self.score_left >= 11:
            self.state = self.STATE_END_GAME

    def update_ia(self):
        output = self.ia.activate((self.racket_left.get_y(), self.ball.get_x(), self.ball.get_y(), self.ball.x_speed, self.ball.y_speed))

        if output[0] > 0.66:
            self.racket_left.up = True
            self.racket_left.down = False
        if 0.66 > output[0] > 0.33:
            self.racket_left.up = False
            self.racket_left.down = False
        if output[0] < 0.33:
            self.racket_left.up = False
            self.racket_left.down = True

        self.racket_left.update(self.delta)

    def update_menus(self):
        op_size = 3
        if self.state == self.STATE_SEL_MODE_MENU:
            op_size = 5

        if (self.k_up or self.k_w) and 0 <= self.menu_op - 1 < op_size:
            self.menu_op -= 1
            self.k_up = False
            self.k_w = False
        elif (self.k_down or self.k_s) and 0 <= self.menu_op + 1 < op_size:
            self.menu_op += 1
            self.k_down = False
            self.k_s = False

        if self.k_enter:
            self.k_enter = False
            option = self.menu_op
            self.menu_op = 0
            if self.state == self.STATE_MAIN_MENU:
                if option == 0:
                    self.state = self.STATE_SEL_MODE_MENU
                elif option == 1:
                    self.sound = not self.sound
                    self.menu_op = 1
                elif option == 2:
                    self.running = False
                    self.menu_op = 2
            elif self.state == self.STATE_PAUSE_MENU:
                if option == 0:
                    self.state = self.STATE_PLAYING
                elif option == 1:
                    self.sound = not self.sound
                    self.menu_op = 1
                elif option == 2:
                    self.state = self.STATE_MAIN_MENU
            elif self.state == self.STATE_SEL_MODE_MENU:
                self.state = self.STATE_PLAYING
                self.restart()
                if option == 0:
                    self.mode = self.PLAYER_VS_PLAYER
                elif option == 1:
                    self.mode = self.PLAYER_VS_MACHINE
                elif option == 2:
                    self.mode = self.PLAYER_VS_IA
                elif option == 3:
                    self.mode = self.IA_VS_MACHINE
                elif option == 4:
                    self.state = self.STATE_MAIN_MENU

    def update_end_game(self):
        if self.k_enter:
            self.state = self.STATE_MAIN_MENU
            self.k_enter = False

    def update_wait(self):
        self.timer -= self.delta
        if self.timer <= 0:
            self.state = self.STATE_PLAYING
            self.start_match()

    def render(self):
        self.screen.fill(self.clean_color)

        if self.state == self.STATE_PLAYING or self.state == self.STATE_WAIT:
            self.draw_score()
            self.draw_net()
            self.draw_racket()
            self.draw_ball()
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU or self.state == self.STATE_SEL_MODE_MENU:
            self.draw_menu()
        elif self.state == self.STATE_END_GAME:
            self.draw_end_game()

        if self.effects:
            self.draw_overlay_effects()
        else:
            self.clean_color = self.BLACK

        pygame.display.flip()

    def draw_score(self):
        x_left = self.DISPLAY_WIDTH * 0.25
        x_right = self.DISPLAY_WIDTH * 0.75
        top = self.DISPLAY_HEIGHT * 0.1
        half_width = self.sprite_num[0].get_width() / 2

        # handle two digits score
        if self.score_left > 9:
            self.screen.blit(self.sprite_num[1], ((x_left - half_width) - half_width * 2, top))
            self.screen.blit(self.sprite_num[self.score_left - 10], ((x_left - half_width) + half_width * 2, top))
        else:
            self.screen.blit(self.sprite_num[self.score_left], (x_left - half_width, top))

        if self.score_right > 9:
            self.screen.blit(self.sprite_num[1], ((x_right - half_width) - half_width * 2, top))
            self.screen.blit(self.sprite_num[self.score_right - 10], ((x_right - half_width) + half_width * 2, top))
        else:
            self.screen.blit(self.sprite_num[self.score_right], (x_right - half_width, top))

    def draw_net(self):
        y = 20
        for i in range(18):
            self.screen.blit(self.sprite_net, (self.DISPLAY_WIDTH / 2 - 4, y + i * 32))

    def draw_racket(self):
        self.racket_left.render()
        self.racket_right.render()

    def draw_ball(self):
        self.ball.render()

    def draw_menu(self):
        padding = (16, 8)
        adjust = (2, 1, 0, 0)

        str_title = ''
        options_str = []

        if self.state == self.STATE_PAUSE_MENU:
            str_title = 'PAUSED'
            options_str.append('CONTINUE')
            options_str.append('SOUND: ' + str(self.sound))
            options_str.append('BACK TO MAIN MENU')
        elif self.state == self.STATE_SEL_MODE_MENU:
            str_title = 'SEL. A MODE'
            options_str.append('PLAYER VS. PLAYER')
            options_str.append('PLAYER VS. MACHINE')
            options_str.append('PLAYER VS. IA')
            options_str.append('IA VS. MACHINE')
            options_str.append('BACK')
        elif self.state == self.STATE_MAIN_MENU:
            str_title = 'PONG'
            options_str.append('PLAY')
            options_str.append('SOUND: ' + str(self.sound))
            options_str.append('EXIT')

        str_size = []
        pos = []
        pos_f = []
        str_rend = []
        op_pad = 0

        for i, op_str in enumerate(options_str):
            str_s = self.font.size(op_str) + padding
            str_size.append(str_s)
            pos.append((int(self.DISPLAY_WIDTH / 2 - str_s[0] / 2),
                        int(((self.DISPLAY_HEIGHT / 4) * 1.5 - str_s[1] / 2) + str_s[1] * op_pad),
                        str_s[0],
                        str_s[1]))
            op_pad += 1.5
            if i == self.menu_op:
                str_rend.append(self.font.render(options_str[i], False, self.BLACK))
                pygame.draw.rect(self.screen, self.WHITE, pos[i])
            else:
                str_rend.append(self.font.render(options_str[i], False, self.WHITE))

            pos_f.append(tuple(map(operator.add, pos[i], adjust)))
            self.screen.blit(str_rend[i], pos_f[i])

        title = self.font_title.render(str_title, False, self.WHITE)
        title_w = title.get_width()
        self.screen.blit(title, (int(self.DISPLAY_WIDTH / 2 - title_w / 2), 60))

    def draw_end_game(self):
        str1 = 'END GAME'
        str2 = 'WINNER: ' + ('LEFT PLAYER' if self.score_left >= 11 else 'RIGHT PLAYER')
        str3 = 'ENTER TO CONTINUE'

        text1 = self.font_mid.render(str1, False, self.WHITE)
        text2 = self.font.render(str2, False, self.WHITE)
        text3 = self.font.render(str3, False, self.WHITE)

        pad_top = self.DISPLAY_HEIGHT * 0.16

        self.screen.blit(text1, (int(self.DISPLAY_WIDTH / 2 - text1.get_width() / 2), pad_top))
        self.screen.blit(text2, (int(self.DISPLAY_WIDTH / 2 - text2.get_width() / 2), pad_top + (text1.get_height() * 2)))
        self.screen.blit(text3, (int(self.DISPLAY_WIDTH / 2 - text3.get_width() / 2), pad_top + (text1.get_height() * 5)))

    def draw_overlay_effects(self):
        self.screen.blit(self.sprite_scanline, (0, 0))
        self.screen.blit(self.sprite_tv_vignette, (0, 0))
