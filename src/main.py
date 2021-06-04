#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import neat
from pong import Pong
from pong_train import PongTrain
import pickle


def replay_genome(config_path, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    # game(genomes, config)


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint('jl2_neat-checkpoint-194')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(PongTrain().run, 1)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    print(f'\nBest genome:\n{winner}')


if __name__ == "__main__":
    Pong().run()

    # local_dir = os.path.dirname(__file__)
    # config_path = os.path.join(local_dir, 'config-feedforward.txt')
    # run(config_path)
