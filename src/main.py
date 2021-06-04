#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import neat
from pong import Pong
from pong_train import PongTrain


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-149')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(PongTrain().run, 999)

    print(f'\nBest genome:\n{winner}')


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
