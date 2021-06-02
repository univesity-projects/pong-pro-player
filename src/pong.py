#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
import random
import time
import operator
import os


def sprite_load_scaled(path, scale):
    sprite = pygame.image.load(path)
    sprite = pygame.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
    return sprite


class Entity:

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
        # print('---\nx: ', self.x, '\ny: ', self.y)
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

    def update_ia(self, delta):
        ball = self.parent.ball
        if ball.get_y() < self.get_y() and not self.up_collision():
            self.y -= self.speed * delta
        elif ball.get_y() > self.get_y() and not self.down_collision():
            self.y += self.speed * delta


class Ball(Entity):

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)
        self.racket_left = self.parent.racket_left
        self.racket_right = self.parent.racket_right
        self.x_speed = 0
        self.y_speed = 0

    def update(self, delta):
        self.x += self.x_speed * delta
        self.y += self.y_speed * delta
        self.collision()
        if self.get_x() > self.parent.DISPLAY_WIDTH:
            self.parent.score_up(False)
        elif self.get_x() < 0:
            self.parent.score_up(True)

    def collision(self):
        ball_rect = pygame.rect.Rect((self.x, self.y, self.width, self.height))
        racket_left_rect = pygame.rect.Rect((self.racket_left.x, self.racket_left.y, self.racket_left.width, self.racket_left.height))
        racket_right_rect = pygame.rect.Rect((self.racket_right.x, self.racket_right.y, self.racket_right.width, self.racket_right.height))
        angle_in_degrees = 0
        if ball_rect.colliderect(racket_left_rect):
            ball_y = self.get_y()
            racket_y = self.racket_left.get_y()
            racket_height = self.racket_left.height
            if ball_y < racket_y and ball_y > racket_y - racket_height * 0.125:
                angle_in_degrees = -15
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.250:
                angle_in_degrees = -30
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.375:
                angle_in_degrees = -45
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.500 - self.height:
                angle_in_degrees = -60
            elif ball_y == racket_y:
                angle_in_degrees = 0
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.125:
                angle_in_degrees = 15
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.250:
                angle_in_degrees = 30
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.375:
                angle_in_degrees = 45
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.500 + self.height:
                angle_in_degrees = 60
            self.set_angle(math.radians(angle_in_degrees))
        elif ball_rect.colliderect(racket_right_rect):
            ball_y = self.get_y()
            racket_y = self.racket_right.get_y()
            racket_height = self.racket_right.height
            if ball_y < racket_y and ball_y > racket_y - racket_height * 0.125:
                angle_in_degrees = -165
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.250:
                angle_in_degrees = -150
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.375:
                angle_in_degrees = -135
            elif ball_y < racket_y and ball_y > racket_y - racket_height * 0.500 - self.height:
                angle_in_degrees = -120
            elif ball_y == racket_y:
                angle_in_degrees = 180
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.125:
                angle_in_degrees = 165
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.250:
                angle_in_degrees = 150
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.375:
                angle_in_degrees = 135
            elif ball_y > racket_y and ball_y < racket_y + racket_height * 0.500 + self.height:
                angle_in_degrees = 120
            self.set_angle(math.radians(angle_in_degrees))

        if self.up_collision() or self.down_collision():
            self.y_speed *= -1

    def generate(self):
        # self.x_speed = 150
        # return
        self.set_x(self.parent.DISPLAY_WIDTH / 2)
        self.set_y(random.randint(self.height, self.parent.DISPLAY_HEIGHT - self.height))
        if random.randint(0, 1) == 0:
            self.set_angle(math.radians(random.randint(-60, 60)))
        else:
            self.set_angle(math.radians(random.randint(-120, 120)))

    def set_angle(self, angle_in_radians):
        self.x_speed = self.speed * math.cos(angle_in_radians)
        self.y_speed = self.speed * math.sin(angle_in_radians)


class Pong:

    # constants
    BLACK = (0, 0, 0)
    DARK_GRAY = (50, 50, 50)
    WHITE = (255, 255, 255)
    SCALE = 8
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600

    STATE_PLAYING = 0
    STATE_MAIN_MENU = 1
    STATE_PAUSE_MENU = 2
    STATE_SEL_MENU = 3
    STATE_END_GAME = 4
    STATE_WAIT = 5

    def __init__(self):
        # print(os.getcwd())
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
        self. sprite_num = []
        for i in range(10):
            self.sprite_num.append(sprite_load_scaled('src/res/sprite/sprite_num_' + str(i) + '.png', int(self.SCALE / 2)))
        self.sprite_net = sprite_load_scaled('src/res/sprite/net.png', self.SCALE)
        sprite_ball = sprite_load_scaled('src/res/sprite/ball.png', self.SCALE)
        sprite_racket = sprite_load_scaled('src/res/sprite/racket.png', self.SCALE)
        self.font_title = pygame.font.Font('src/res/font/bit5x3.ttf', 128)
        self.font = pygame.font.Font('src/res/font/bit5x3.ttf', 32)

        # objects
        self.racket_left = Racket(50, 300, 16, 64, 500, sprite_racket, self)
        self.racket_right = Racket(750, 300, 16, 64, 500, sprite_racket, self)
        self.ball = Ball(400, 300, 16, 16, 500, sprite_ball, self)

        # control
        self.running = False
        self.effects = False
        self.player = False
        self.state = self.STATE_MAIN_MENU
        self.menu_op = 0
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

    def start_match(self):
        self.racket_left.set_y(self.DISPLAY_HEIGHT / 2)
        self.racket_right.set_y(self.DISPLAY_HEIGHT / 2)
        self.ball.generate()

    def score_up(self, right):
        if right:
            self.score_right += 1
        else:
            self.score_left += 1
        self.state = self.STATE_WAIT
        self.timer = 1

    def update(self):
        self.update_events()

        if self.state == self.STATE_PLAYING:
            self.update_playing()
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU or self.state == self.STATE_SEL_MENU:
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
                elif event.key == pygame.K_RETURN:
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
                elif event.key == pygame.K_RETURN:
                    self.k_enter = False
                elif event.key == pygame.K_ESCAPE:
                    self.k_esc = False

    def update_playing(self):
        if self.k_esc:
            self.state = self.STATE_PAUSE_MENU
        if self.player:
            self.racket_left.up = self.k_w
            self.racket_left.down = self.k_s
            self.racket_left.update(self.delta)
        else:
            self.racket_left.update_ia(self.delta)
        self.racket_right.up = self.k_up
        self.racket_right.down = self.k_down
        self.racket_right.update(self.delta)
        self.ball.update(self.delta)
        if self.score_right >= 11 or self.score_left >= 11:
            self.state = self.STATE_END_GAME

    def update_menus(self):
        if self.k_up or self.k_w:
            self.menu_op = 0
        elif self.k_down or self.k_s:
            self.menu_op = 1
        if self.k_enter:
            if self.menu_op == 0:
                if self.state == self.STATE_MAIN_MENU:
                    self.state = self.STATE_SEL_MENU
                elif self.state == self.STATE_PAUSE_MENU:
                    self.state = self.STATE_PLAYING
                elif self.state == self.STATE_SEL_MENU:
                    self.state = self.STATE_PLAYING
                    self.start_match()
                    self.player = True
            else:
                if self.state == self.STATE_MAIN_MENU:
                    self.running = False
                elif self.state == self.STATE_SEL_MENU:
                    self.state = self.STATE_PLAYING
                    self.start_match()
                    self.player = False
                else:
                    self.state = self.STATE_MAIN_MENU
                self.menu_op = 0
            self.k_enter = False

    def update_end_game(self):
        if self.k_enter:
            self.state = self.STATE_MAIN_MENU

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
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU or self.state == self.STATE_SEL_MENU:
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
        half_width = self.sprite_num[self.score_left].get_width() / 2
        self.screen.blit(self.sprite_num[self.score_left], (x_left - half_width, top))
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
        if self.state == self.STATE_PAUSE_MENU:
            str1 = 'CONTINUE'
            str2 = 'BACK TO MAIN MENU'
            str3 = 'PAUSED'
        elif self.state == self.STATE_SEL_MENU:
            str1 = 'PLAYER VS. PLAYER'
            str2 = 'PLAYER VS. MACHINE'
            str3 = 'MODE'
        else:
            str1 = 'PLAY'
            str2 = 'EXIT'
            str3 = 'PONG'
        str1_size = self.font.size(str1) + padding
        str2_size = self.font.size(str2) + padding
        pos1 = (int(self.DISPLAY_WIDTH / 2 - str1_size[0] / 2),
                int(self.DISPLAY_HEIGHT / 2 - str1_size[1] / 2),
                str1_size[0],
                str1_size[1])
        pos2 = (int(self.DISPLAY_WIDTH / 2 - str2_size[0] / 2),
                int((self.DISPLAY_HEIGHT / 2 - str2_size[1] / 2) + str2_size[1] * 1.5),
                str2_size[0],
                str2_size[1])
        if self.menu_op == 0:
            str1_r = self.font.render(str1, False, self.BLACK)
            str2_r = self.font.render(str2, False, self.WHITE)
            pygame.draw.rect(self.screen, self.WHITE, pos1)
        else:
            str1_r = self.font.render(str1, False, self.WHITE)
            str2_r = self.font.render(str2, False, self.BLACK)
            pygame.draw.rect(self.screen, self.WHITE, pos2)
        pos1 = tuple(map(operator.add, pos1, adjust))
        pos2 = tuple(map(operator.add, pos2, adjust))
        title = self.font_title.render(str3, False, self.WHITE)
        title_w = title.get_width()
        self.screen.blit(title, (int(self.DISPLAY_WIDTH / 2 - title_w / 2), 96))
        self.screen.blit(str1_r, pos1)
        self.screen.blit(str2_r, pos2)

    def draw_end_game(self):
        str1 = 'END GAME'
        str2 = 'WINNER: ' + 'LEFT PLAYER' if self.score_left >= 11 else 'RIGHT PLAYER'
        str3 = 'ENTER TO CONTINUE'
        text1 = self.font_title.render(str1, False, self.WHITE)
        text2 = self.font_title.render(str2, False, self.WHITE)
        text3 = self.font_title.render(str3, False, self.WHITE)
        self.screen.blit(text1, (int(self.DISPLAY_WIDTH / 2 - text1.get_width() / 2), 96))
        self.screen.blit(text2, (int(self.DISPLAY_WIDTH / 2 - text2.get_width() / 2), 96))
        self.screen.blit(text3, (int(self.DISPLAY_WIDTH / 2 - text3.get_width() / 2), 96))

    def draw_overlay_effects(self):
        self.screen.blit(self.sprite_scanline, (0, 0))
        self.screen.blit(self.sprite_tv_vignette, (0, 0))
