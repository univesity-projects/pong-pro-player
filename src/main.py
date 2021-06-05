#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import neat
from pong import Pong
from pong_train import PongTrain
import pickle


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-19')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(PongTrain().run, 300)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    print(f'\nBest genome:\n{winner}')


if __name__ == "__main__":
    print('Choose an option:')
    print('1 - Train')
    print('? - Play')
    # op = input('Choose: ')
    op = '1'

    if op == '1':
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        run(config_path)
    else:
        Pong().run()
