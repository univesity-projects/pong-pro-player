#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame as pg
import operator
import os


def sprite_load_scaled(path, scale):
    sprite = pg.image.load(path)
    sprite = pg.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
    return sprite


class Entity:

    def __init__(self, x, y, width, height, speed, sprite, parent):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.sprite = sprite
        self.parent = parent

    def update(self):
        pass

    def render(self):
        self.parent.screen.blit(self.sprite, (self.x - self.width / 2, self.y - self.height / 2))


class Ball(Entity):

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)

    def update(self):
        pass


class Racket(Entity):

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)

    def update(self):
        pass


class Pong:

    # constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    SCALE = 8
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600

    STATE_PLAYING = 0
    STATE_MAIN_MENU = 1
    STATE_PAUSE_MENU = 2

    def __init__(self):
        # print(os.getcwd())
        pg.init()
        icon = pg.image.load('src/res/icon.png')
        pg.display.set_icon(icon)
        pg.display.set_caption("Pong")
        self.screen = pg.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

        # keys
        self.k_up = False
        self.k_down = False
        self.k_w = False
        self.k_s = False
        self.k_enter = False
        self.k_esc = False

        # sprites
        self.sprite_scanline = pg.image.load('src/res/sprite/scanline_overlay.png')
        self.sprite_tv_vignette = pg.image.load('src/res/sprite/tv_vignette_overlay.png')
        self. sprite_num = []
        for i in range(10):
            self.sprite_num.append(sprite_load_scaled('src/res/sprite/sprite_num_' + str(i) + '.png', int(self.SCALE / 2)))
        self.sprite_net = sprite_load_scaled('src/res/sprite/net.png', self.SCALE)
        sprite_ball = sprite_load_scaled('src/res/sprite/ball.png', self.SCALE)
        sprite_racket = sprite_load_scaled('src/res/sprite/racket.png', self.SCALE)
        self.font_title = pg.font.Font('src/res/font/bit5x3.ttf', 128)
        self.font = pg.font.Font('src/res/font/bit5x3.ttf', 32)

        # objects
        self.ball = Ball(400, 300, 16, 16, 5, sprite_ball, self)
        self.racket_left = Racket(50, 300, 16, 64, 5, sprite_racket, self)
        self.racket_right = Racket(750, 300, 16, 64, 5, sprite_racket, self)

        # control
        self.running = False
        self.effects = True
        self.player = False
        self.state = self.STATE_MAIN_MENU
        self.menu_op = 0
        self.score_left = 0
        self.score_right = 0

    def run(self):
        self.running = True

        # main loop
        while self.running:
            self.update()
            self.render()

        pg.quit()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.k_up = True
                elif event.key == pg.K_DOWN:
                    self.k_down = True
                elif event.key == pg.K_w:
                    self.k_w = True
                elif event.key == pg.K_s:
                    self.k_s = True
                elif event.key == pg.K_KP_ENTER:
                    self.k_enter = True
                elif event.key == pg.K_ESCAPE:
                    self.k_esc = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.k_up = False
                elif event.key == pg.K_DOWN:
                    self.k_down = False
                elif event.key == pg.K_w:
                    self.k_w = False
                elif event.key == pg.K_s:
                    self.k_s = False
                elif event.key == pg.K_KP_ENTER:
                    self.k_enter = False
                elif event.key == pg.K_ESCAPE:
                    self.k_esc = False

        if self.state == self.STATE_PLAYING:
            pass
        elif self.state == self.STATE_MAIN_MENU:
            pass
        elif self.state == self.STATE_PAUSE_MENU:
            pass

    def render(self):
        self.screen.fill((50, 50, 50))

        if self.state == self.STATE_PLAYING:
            self.draw_score()
            self.draw_net()
            self.draw_racket()
            self.draw_ball()
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU:
            self.draw_menu()

        if self.effects:
            self.draw_overlay_effects()

        pg.display.flip()

    def draw_score(self):
        x_left = 200
        x_right = 600
        top = 50
        half_width = 32
        self.screen.blit(self.sprite_num[self.score_left], (x_left - half_width, top))
        self.screen.blit(self.sprite_num[self.score_left], (x_right - half_width, top))
        pass

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
            pg.draw.rect(self.screen, self.WHITE, pos1)
        else:
            str1_r = self.font.render(str1, False, self.WHITE)
            str2_r = self.font.render(str2, False, self.BLACK)
            pg.draw.rect(self.screen, self.WHITE, pos2)
        pos1 = tuple(map(operator.add, pos1, adjust))
        pos2 = tuple(map(operator.add, pos2, adjust))
        title = self.font_title.render(str3, False, self.WHITE)
        title_w = title.get_width()
        self.screen.blit(title, (int(self.DISPLAY_WIDTH / 2 - title_w / 2), 96))
        self.screen.blit(str1_r, pos1)
        self.screen.blit(str2_r, pos2)

    def draw_overlay_effects(self):
        self.screen.blit(self.sprite_scanline, (0, 0))
        self.screen.blit(self.sprite_tv_vignette, (0, 0))
