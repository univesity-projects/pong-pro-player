#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import sys

import neat
import pygame
import math
import random
import time


class Entity:

    def __init__(self, x, y, width, height, speed, parent, color):
        self.x = x - width / 2
        self.y = y - height / 2
        self.width = width
        self.height = height
        self.speed = speed
        self.sprite = pygame.Rect((x, y, width, height))
        self.parent = parent
        self.color = color
        self.dead = False

    def update(self, delta):
        pass

    def render(self):
        pygame.draw.rect(self.parent.screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

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

    def __init__(self, x, y, width, height, speed, parent, ball, color, gen_id):
        Entity.__init__(self, x, y, width, height, speed, parent, color)
        self.ball = ball
        self.gen_id = gen_id
        self.negative = (255 - color[0], 255 - color[1], 255 - color[2])

        # pad
        self.super_pad = 0

        # checks
        self.moved = False
        self.moved_last_col = False

    def update(self, delta):
        self.moved = False

        if self.up and not self.up_collision() and not self.out_limit():
            self.moved = True
            self.moved_last_col = True
            self.y -= self.speed * delta
        elif self.down and not self.down_collision() and not self.out_limit():
            self.moved = True
            self.moved_last_col = True
            self.y += self.speed * delta

    def render(self):
        pygame.draw.rect(self.parent.screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
        r_id = self.parent.font_sm.render(str(self.gen_id), False, self.negative)
        self.parent.screen.blit(r_id, (self.get_x() - r_id.get_width() / 2, self.get_y() - r_id.get_height() / 2))

    def out_limit(self):
        return self.ball.get_y() < 50


class Ball(Entity):

    def __init__(self, x, y, width, height, speed, parent, racket_left, color):
        Entity.__init__(self, x, y, width, height, speed, parent, color)
        self.racket_left = racket_left
        self.x_speed = 0
        self.y_speed = 0
        self.slaps = 0

        # checks
        self.col = False
        self.col_y = 0
        self.calculated = False
        self.right_pos = False

    def update(self, delta):
        self.col = False

        self.x += self.x_speed * delta
        self.y += self.y_speed * delta

        self.collision()

        if self.get_x() < 0:
            self.dead = True
            self.racket_left.dead = True

        if self.x_speed < 0 and not self.calculated:
            x = copy.copy(self.x)
            y = copy.copy(self.y)
            x_speed = copy.copy(self.x_speed)
            y_speed = copy.copy(self.y_speed)
            while True:
                if x <= 50:
                    self.col_y = y + self.height / 2
                    self.calculated = True
                    break
                if y + self.height >= self.parent.DISPLAY_HEIGHT or y <= 0:
                    y_speed *= -1
                x += x_speed * delta
                y += y_speed * delta

        self.right_pos = self.racket_left.y < self.col_y < self.racket_left.y + self.racket_left.height

        # if self.calculated:
        #     print('rack y: ', self.racket_left.y)
        #     print('rack y + height: ', self.racket_left.y + self.racket_left.height)
        #     print('ball cent y: ', self.get_y())
        #     print('ball predict y: ', self.col_y)
        #     print('right pos: ', self.right_pos)
        #
        #     # time.sleep(10)
        #     while not self.parent.k_esc:
        #         pass

    def collision(self):
        ball_rect = pygame.rect.Rect((self.x, self.y, self.width, self.height))
        racket_left_rect = pygame.rect.Rect((self.racket_left.x, self.racket_left.y, self.racket_left.width, self.racket_left.height))

        # check if the ball collided with left or right racket and set the new angle
        if ball_rect.colliderect(racket_left_rect):
            self.racket_left.moved_last_col = False
            self.col = True
            self.calculated = False
            racket_y = self.racket_left.get_y()
            racket_height = self.racket_left.height
            self.find_angle(0, racket_y, racket_height)

            # print('rack y: ', self.racket_left.y)
            # print('rack y + height: ', self.racket_left.y + self.racket_left.height)
            # print('ball cent y: ', self.get_y())
            # print('ball predict y: ', self.col_y)
            # print('right pos: ', self.right_pos)

            # while not self.parent.k_esc:
            #     pass

        elif self.get_x() >= self.parent.DISPLAY_WIDTH - 50:
            num = self.racket_left.height / 2 - 1
            racket_y = self.get_y() + random.randint(int(-num), num)
            racket_height = self.racket_left.height
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
        self.set_x(self.parent.DISPLAY_WIDTH / 2)
        self.set_y(random.randint(self.height, self.parent.DISPLAY_HEIGHT - self.height))

        num = random.randint(0, 3)
        if num == 0 or num == 2:
            self.set_angle(math.radians(random.randint(-60, 60)))
        elif num == 1:
            self.set_angle(math.radians(random.randint(120, 180)))
        elif num == 3:
            self.set_angle(math.radians(random.randint(-180, -120)))

    def set_angle(self, angle_in_radians):
        speed = self.speed + (50 * self.slaps)
        if speed > 1500:
            speed = 1500
        self.x_speed = speed * math.cos(angle_in_radians)
        self.y_speed = speed * math.sin(angle_in_radians)


class PongTrain:
    # constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    SCALE = 8
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600

    def __init__(self):
        pygame.init()
        icon = pygame.image.load('src/res/icon.png')
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Pong Train')
        self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        random.seed(time.time())

        self.gen = -1

        # keys
        self.k_up = False
        self.k_down = False
        self.k_w = False
        self.k_s = False
        self.k_enter = False
        self.k_esc = False

        # sprites
        self.clean_color = self.BLACK
        self.font_sm = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.font_md = pygame.font.Font(pygame.font.get_default_font(), 24)

        # objects
        self.left_rackets = []
        self.balls = []

        # control
        self.running = True
        self.mode = False
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.elapsed = 0

    def run(self, genomes, config):
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.elapsed = 0
        self.gen += 1

        nets = []
        genes = []

        speed = 800
        mid = self.DISPLAY_HEIGHT / 2
        i = 0
        for genome_id, genome in genomes:
            genome.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genes.append(genome)
            color = (random.randint(55, 255), random.randint(55, 255), random.randint(55, 255))
            racket_left = Racket(50, mid, 16, 64, speed, self, None, color, i)
            i += 1
            ball = Ball(400, mid, 16, 16, 600, self, racket_left, color)
            racket_left.ball = ball
            ball.generate()
            self.left_rackets.append(racket_left)
            self.balls.append(ball)

        # main loop
        while len(self.balls) > 0:
            self.elapsed = self.clock.tick(60)
            self.delta = self.elapsed / 1000.0

            for i in range(len(self.balls)):
                cur_left = self.left_rackets[i]
                cur_ball = self.balls[i]

                output = nets[i].activate((cur_left.get_y(), cur_ball.get_x(), cur_ball.get_y(), cur_ball.x_speed, cur_ball.y_speed))

                if output[0] >= 0.66:
                    cur_left.up = True
                    cur_left.down = False
                if 0.66 > output[0] > 0.33:
                    cur_left.up = False
                    cur_left.down = False
                if output[0] <= 0.33:
                    cur_left.up = False
                    cur_left.down = True

                cur_left.update(self.delta)
                cur_ball.update(self.delta)

                if cur_ball.col:
                    genes[i].fitness += 10.0
                    # genes[i].fitness += 10.0
                if cur_ball.right_pos:
                    genes[i].fitness += 0.5
                # else:
                #     max_weight = 1.0
                #     dist = abs(cur_left.get_y() - cur_ball.get_y())
                #     fit = (max_weight * (dist / self.DISPLAY_HEIGHT)) / 100.0
                #     # print('distance: ',dist)
                #     # print('fit before: ',genes[i].fitness)
                #     genes[i].fitness += 1.0 * fit
                #     # print('fit after: ',genes[i].fitness)
                #     # print('---')

            # remove ended games
            for i, ball in enumerate(self.balls):
                if ball.dead:
                    self.balls.pop(i)
                    self.left_rackets.pop(i)
                    nets.pop(i)
                    genes.pop(i)

            self.update()
            self.render()

    def update(self):
        self.update_events()

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
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

    def render(self):
        self.screen.fill(self.clean_color)

        self.draw_net()

        for i in range(len(self.left_rackets)):
            self.left_rackets[i].render()
            self.balls[i].render()

        self.draw_data()

        pygame.display.flip()

    def draw_data(self):
        str1 = 'POP: ' + str(len(self.balls)) + ' / GEN: ' + str(self.gen)
        text1 = self.font_md.render(str1, False, self.WHITE)
        pygame.draw.rect(self.screen, self.BLACK, (100, 0, text1.get_width() + 20, text1.get_height() + 10))
        self.screen.blit(text1, (120, 10))

    def draw_net(self):
        pygame.draw.rect(self.screen, self.WHITE, pygame.Rect(self.DISPLAY_WIDTH / 2 - 4, 0, 8, self.DISPLAY_HEIGHT))
        pygame.draw.rect(self.screen, self.WHITE, pygame.Rect(self.DISPLAY_WIDTH - 42, 0, 42, self.DISPLAY_HEIGHT))
