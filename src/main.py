#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import neat
from pong import Pong
from pong_train import PongTrain
import pickle
import PySimpleGUI as sg


def run():
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    if new_train:
        p = neat.Population(config)
    else:
        p = neat.Checkpointer.restore_checkpoint(load_path)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(int(check_intervals)))

    winner = p.run(PongTrain().run, int(generations))
    with open(best_genome_name, 'wb') as f:
        pickle.dump(winner, f)
        f.close()

    print(f'\nBest genome:\n{winner}')


if __name__ == '__main__':
    local_dir = os.getcwd()
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    new_train = True
    load_path = os.path.join(local_dir, 'neat-checkpoint-?')
    continue_train = False
    generations = 300
    check_intervals = 5
    best_genome_name = os.path.join(local_dir, 'winner.pkl')

    running = True
    sg.theme('Dark')

    main_layout = [
        [sg.Text('Welcome to Pong Project', )],
        [sg.Text('Click "Train" if you want to train a AI or "Play" if you just want to play.')],
        [sg.Button('Train'), sg.Button('Play')]
    ]

    main_window = sg.Window('Pong Project', main_layout, size=(480, 270))
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
                [sg.Text('Config path:'), sg.InputText(config_path, key='config_path')],
                [sg.Radio('New?', default=new_train, key='new_train', group_id='train')],
                [sg.Radio('Continue?', default=continue_train, group_id='train'), sg.Text('Load path:'), sg.InputText(load_path, key='load_path')],
                [sg.Text('Generations:'), sg.InputText(str(generations), key='generations')],
                [sg.Text('Checkpoint intervals:'), sg.InputText(str(check_intervals), key='check_intervals')],
                [sg.Text('Best genome save path:'), sg.InputText(best_genome_name, key='best_genome_name')],
                [sg.Button('Cancel'), sg.Button('Run')]
            ]

            train_window = sg.Window('Train Settings', train_layout, size=(480, 270))

            while True:
                event_train_window, values_train_window = train_window.read()
                if event_train_window == sg.WIN_CLOSED or event_train_window == 'Cancel':
                    train_window.close()
                    train_window_active = False
                    main_window.UnHide()
                    break
                elif event_train_window == 'Run':
                    config_path = values_train_window['config_path']
                    new_train = values_train_window['new_train']
                    load_path = values_train_window['load_path']
                    generations = values_train_window['generations']
                    check_intervals = values_train_window['check_intervals']
                    best_genome_name = values_train_window['best_genome_name']
                    main_window.close()
                    train_window.close()
                    running = False
                    run()
                    break

        elif event_main_window == 'Play':
            main_window.close()
            Pong().run()

    main_window.close()
