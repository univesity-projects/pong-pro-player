#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame as pg
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

    def __init__(self):
        # sprites
        self.sprite_scanline = pg.image.load('src/res/sprite/scanline_overlay.png')
        self.sprite_tv_vignette = pg.image.load('src/res/sprite/tv_vignette_overlay.png')
        self. sprite_num = []
        for i in range(10):
            self.sprite_num.append(sprite_load_scaled('src/res/sprite/sprite_num_' + str(i) + '.png', int(self.SCALE / 2)))
        self.sprite_net = sprite_load_scaled('src/res/sprite/net.png', self.SCALE)
        sprite_ball = sprite_load_scaled('src/res/sprite/ball.png', self.SCALE)
        sprite_racket = sprite_load_scaled('src/res/sprite/racket.png', self.SCALE)

        # objects
        self.ball = Ball(400, 300, 16, 16, 5, sprite_ball, self)
        self.racket_left = Racket(50, 300, 16, 64, 5, sprite_racket, self)
        self.racket_right = Racket(750, 300, 16, 64, 5, sprite_racket, self)

        # control
        self.running = False
        self.effects = True
        self.score_left = 0
        self.score_right = 0

        pg.init()
        # print(os.getcwd())
        icon = pg.image.load('src/res/icon.png')
        pg.display.set_icon(icon)
        pg.display.set_caption("Pong")
        self.screen = pg.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

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

    def render(self):
        self.screen.fill((50, 50, 50))

        self.draw_score()
        self.draw_net()
        self.draw_racket()
        self.draw_ball()

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

    def draw_overlay_effects(self):
        self.screen.blit(self.sprite_scanline, (0, 0))
        self.screen.blit(self.sprite_tv_vignette, (0, 0))
