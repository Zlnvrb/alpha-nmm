"""
use this script to play any two agents against each other, or play manually with
any agent.
"""
import numpy as np

from Arena import Arena
from MCTS import MCTS
from ninemensmorris.NineMensMorrisGame import NineMensMorrisGame
from ninemensmorris.NineMensMorrisPlayers import RandomPlayer, HumanNineMensMorrisPlayer
from ninemensmorris.pytorch.NNet import NNetWrapper
from utils import dotdict

human_vs_cpu = False

g = NineMensMorrisGame()

# all players
rp = RandomPlayer(g).play
hp = HumanNineMensMorrisPlayer(g, True).play

# nnet players
n1 = NNetWrapper(g)
n1.load_checkpoint('/Users/iva.stanojkovska/Documents/GitHub/alpha-nmm/ninemensmorris/pretrained_models',
                   'best.pth.tar')
args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

if human_vs_cpu:
    player2 = hp
else:
    n2 = NNetWrapper(g)
    n2.load_checkpoint('/Users/iva.stanojkovska/Documents/GitHub/alpha-nmm/ninemensmorris/pretrained_models',
                       'best.pth.tar')
    args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
    mcts2 = MCTS(g, n2, args2)
    n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

    player2 = n2p

arena = Arena(n1p, player2, g, display=NineMensMorrisGame.display)

print(arena.playGames(20, verbose=True))
