"""
use this script to play any two agents against each other, or play manually with
any agent.
"""
import sys

import numpy as np

from Arena import Arena
from MCTS import MCTS
from ninemensmorris.NineMensMorrisGame import NineMensMorrisGame
from ninemensmorris.NineMensMorrisPlayers import RandomPlayer, HumanNineMensMorrisPlayer, GreedyNineMensMorrisPlayer
from ninemensmorris.pytorch.NNet import NNetWrapper
from utils import dotdict

human_vs_cpu = True
random_play = False
greedy_play = False

g = NineMensMorrisGame()

# all players
rp = RandomPlayer(g).play
gp = GreedyNineMensMorrisPlayer(g).play
hp = HumanNineMensMorrisPlayer(g, True).play

if human_vs_cpu:
    arena = Arena(rp, hp, g, display=NineMensMorrisGame.display)

    print(arena.playGames(4, verbose=True))

else:
    # nnet players
    n1 = NNetWrapper(g)
    n1.load_checkpoint('./pretrained_models/ninemensmorris/pytorch/',
                       'x_best.pth.tar')
    args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
    mcts1 = MCTS(g, n1, args1)
    n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

    if human_vs_cpu:
        player2 = hp
        file_name = "outputHuman.txt"
    elif random_play:
        player2 = rp
        file_name = "outputRandom.txt"
    elif greedy_play:
        player2 = gp
        file_name = "outputGreedy.txt"
    else:
        n2 = NNetWrapper(g)
        n2.load_checkpoint('./pretrained_models/ninemensmorris/pytorch/',
                           'x_best.pth.tar')
        args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
        mcts2 = MCTS(g, n2, args2)
        n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

        player2 = n2p
        file_name = "outputModel.txt"

    print("Arena play is starting.")
    with open(file_name, "w") as file:
        # Redirect sys.stdout to the file
        sys.stdout = file

        arena = Arena(n1p, player2, g, display=NineMensMorrisGame.display)

        print(arena.playGames(4, verbose=True))

        sys.stdout = sys.__stdout__
    print("Arena play is over.")
