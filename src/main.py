#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import neat
from pong import Pong
from pong_train import PongTrain
import pickle
import PySimpleGUI as sg


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-19')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(PongTrain().run, 300)
    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)
        f.close()

    print(f'\nBest genome:\n{winner}')


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    file_name = 'config-feedforward.txt'
    config_path = os.path.join(local_dir, file_name)
    new_train = True
    generations = 300
    check_intervals = 5
    best_genome_name = os.path.join(local_dir, 'winner.pkl')

    running = True
    sg.theme('Dark')

    main_layout = [
        [sg.Text('Welcome to Pong Project.')],
        [sg.Text('Click "Train" if you want to train a AI or "Play" if you just want to play.')],
        [sg.Button('Train'), sg.Button('Play')]
    ]

    main_window = sg.Window('Pong Project', main_layout)
    train_window_active = False

    while running:
        event_main_window, values_main_window = main_window.read()

        if event_main_window == sg.WIN_CLOSED:
            running = False
        elif event_main_window == 'Train' and not train_window_active:
            train_window_active = True
            main_window.Hide()

            train_layout = [
                [sg.Text('Parameters:')],
                [sg.Text('Config path:'), sg.InputText(config_path)],
                [sg.Text('New network:'), sg.Checkbox(default=new_train)],
                [sg.Text('Generations:'), sg.InputText(str(generations))],
                [sg.Text('Checkpoint intervals:'), sg.InputText(str(check_intervals))],
                [sg.Text('Best genome save path:'), sg.InputText(best_genome_name)],
                [sg.Button('Cancel'), sg.Button('Run')]
            ]

            train_window = sg.Window('Window 2', train_layout)

            while True:
                event_train_window, values_train_window = train_window.read()
                if event_train_window == sg.WIN_CLOSED:
                    train_window.close()
                    train_window_active = False
                    main_window.UnHide()
                    break
                elif event_main_window == 'Run':
                    run(config_path)

        elif event_main_window == 'Play':
            main_window.close()
            Pong().run()

    main_window.close()
