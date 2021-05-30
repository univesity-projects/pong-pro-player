#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame as pg


class Pong:

    def __init__(self):
        self.DISPLAY_WIDTH = 800
        self.DISPLAY_HEIGHT = 450
        self.running = False

        pg.init()
        icon = pg.image.load('/res/icon.png')
        pg.display.set_icon(icon)
        pg.display.set_caption("Pong")
        self.screen = pg.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def render(self):
        pass

    def run(self):
        self.running = True

        # main loop
        while self.running:
            self.update()
            self.render()

        pg.quit()
