from __future__ import print_function
from Game import Game
from .NineMensMorrisLogic import Board
import sys
import numpy as np
import copy

sys.path.append('..')

"""
Helper methods
"""

"""
   Rotates a move by 90 degrees
"""


def rotate(move):
    """
    Input:
        move: Tuple (origin, destination, piece to take)
    Returns:
        rot_move: Tuple (new_origin, new_destination, new_piece to capture)
    """
    if move[0] == 'none':
        new_origin = 'none'

    elif move[0] in [6, 7, 14, 15, 22, 23]:
        new_origin = move[0] - 6

    else:
        new_origin = move[0] + 2

    if move[1] in [6, 7, 14, 15, 22, 23]:
        new_destination = move[1] - 6

    else:
        new_destination = move[1] + 2

    if move[2] == 'none':
        new_enemy = 'none'

    elif move[2] in [6, 7, 14, 15, 22, 23]:
        new_enemy = move[2] - 6

    else:
        new_enemy = move[2] + 2

    return new_origin, new_destination, new_enemy


"""
    Generates all possible moves for game phase zero
"""


def get_all_moves_phase_zero():
    """
    Returns:
        moves: list of all possible move Tuples
    """

    moves = []
    index = 0

    while index < 24:

        moves.append(("none", index, "none"))
        count = 0

        while count < 24:

            if count != index:
                moves.append(("none", index, count))

            count += 1

        index += 1

    return list(moves)


"""
    Generates all possible moves for game phase one and two
"""


def get_all_moves_phase_one_and_two():
    """
    Returns:
        moves: list of all possible move Tuples
    """

    moves = []
    index_origin = 0

    while index_origin < 24:

        index_move = 0

        while index_move < 24:

            if index_move != index_origin:

                moves.append((index_origin, index_move, "none"))

                count = 0

                while count < 24:

                    if (count != index_move) and (count != index_origin):
                        moves.append((index_origin, index_move, count))

                    count += 1

            index_move += 1

        index_origin += 1

    return list(moves)


"""
  Gets the list of all possible moves
"""


def get_all_moves():
    """
    Returns:
       moves: A list with all possible moves for the game
    """
    moves = get_all_moves_phase_zero() + get_all_moves_phase_one_and_two()
    return list(moves)


class NineMensMorrisGame(Game):
    """
    Initializes the list of all possible moves, the policy rotation vector and
    the number of moves without a mill to determine a draw
    """

    def __init__(self):
        super().__init__()
        self.n = 6
        self.all_moves = get_all_moves()
        self.policy_rotation_vector = self.get_policy_rotation_90()
        self.MAX_MOVES_WITHOUT_MILL = 50

    """
    Gets the lookup list for the rotation of the vector of legal moves
    """

    def get_policy_rotation_90(self):
        """
        Returns:
            rotation_90: lookup list for the rotation of the legal moves vector
        """

        rotation_90 = [-1] * len(self.all_moves)

        i = 0
        while i < len(self.all_moves):
            move = self.all_moves[i]
            rotated_move = rotate(move)
            new_index = self.all_moves.index(rotated_move)
            rotation_90[i] = new_index

            i += 1

        return rotation_90

    """
    based on Othellogame.py
    Gets the initial form of the board in game phase zero
    """

    def getInitBoard(self):
        """
        Returns:
            board: the initial board configuration
        """
        b = Board()

        return np.array(b.pieces)

    """
    based on Othellogame.py
    Gets the size of the board image in a Tuple (x, y)
    """

    def getBoardSize(self):
        """
        Returns:
            dimensions: a Tuple with the board dimensions
        """
        return (6, 6)

    """
    based on Othellogame.py
    Gets the number of all possible actions
    """

    def getActionSize(self):
        """
        Returns:
            actionssize: number of all moves
        """
        return len(self.all_moves)

    """
    based on Othellogame.py
    Returns the next state to given a board, player and move
    """

    def getNextState(self, board, player, move):
        """
        Input:
            board: current board image
            player: current player (1 or -1)
            move: move Tuple

        Returns:
            new_state: Tuple (new board, next player)
        """
        b = Board()
        b.pieces = np.copy(board)

        b.execute_move(player, move, self.all_moves)

        return (b.pieces, -player)

    """
    based on Othellogame.py
    Gets a vector of size == ActionSize that marks legal moves for the current
    board and player with 1
    """

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board image
            player current player (1 or -1)
        Returns:
            valid_moves: np array of ones and zeros marking the legal moves
        """
        b = Board()
        b.pieces = np.copy(board)

        valid_moves = b.get_legal_move_vector(player, self.all_moves)

        return np.array(valid_moves)

    """
        Returns the valid moves and it's vector representation
    """

    def getValidMovesAsTuple(self, board, player):
        return self.getValidMoves(board, player), self.all_moves

    """
    Determines if the game has ended for the given board and player.
    """

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)
        Returns:
            game_ended: 0 if game has not ended. 1 if player won, -1 if player
            lost, small non-zero value for draw.
        """
        assert (not isinstance(board, str))

        b = Board()
        b.pieces = np.copy(board)

        if b.pieces[4][1] >= 50:
            return 0.0001
        elif not b.has_legal_moves(player):
            return -1
        elif not b.has_legal_moves(-player):
            return 1
        elif len(b.get_player_pieces(player)) < 3 and b.pieces[4][0] == 18:
            return -1
        elif len(b.get_player_pieces(-player)) < 3 and b.pieces[4][0] == 18:
            return 1
        elif b.has_legal_moves(-player) and b.has_legal_moves(player):
            return 0

    """
    Multiplies each element with the given player, resulting in a canonical
    board from the perspective of the given player. The given players pieces
    are always represented as 1 in the Canonical Form.
    """

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)
        Returns:
            b: canonical board
        """
        b = np.zeros((6, 6), dtype=int)
        count_placements = copy.deepcopy(board[4][0])
        current_moves = copy.deepcopy(board[4][1])
        index = 0
        while index < 4:
            item = 0
            while item < 6:
                b[index][item] = board[index][item] * player
                item += 1
            index += 1

        b[4][0] = count_placements
        b[4][1] = current_moves
        return b

    """
    Gets some Symmetries by rotating the board three times, each time also
    adapting the legal moves vector to the new board
    """

    def getSymmetries(self, board, pi):
        """
        Input:
            board: the current board
            pi: the legal moves vector for the current board
        Returns:
            results: three board rotations
        """

        assert (len(pi) == len(self.all_moves))
        b = Board()
        b.pieces = np.copy(board)

        results = b.get_board_rotations(pi, self.all_moves, self.policy_rotation_vector)

        return results

    """
    Gets a String representation for the board, used for hashing in mcts
    """

    def stringRepresentation(self, board):
        """
        Input:
            board: the current board
        Returns:
            board_s: String representation of the board
        """
        board_s = ""
        index = 0
        i = 0
        while i < 4:
            while index < 6:
                board_s = board_s + str(board[i][index]) + ","
                index += 1
            index = 0
            i += 1
        board_s = board_s + str(board[4][0]) + ","
        board_s = board_s + str(board[4][1])

        return board_s

    """
    Gets a readable String representation for the board
    """

    def stringRepresentationReadable(self, board):
        """
        Input:
            board: the current board
        Returns:
            board_s: String representation of the board
        """
        board_s = ""
        index = 0
        i = 0
        while i < 4:
            while index < 6:
                board_s = board_s + str(board[i][index]) + ","
                index += 1
            index = 0
            i += 1
        board_s = board_s + str(board[4][0]) + ","
        board_s = board_s + str(board[4][1])

        return board_s

    @staticmethod
    def symbolic(value):
        if value == 1:
            return 'X'
        if value == -1:
            return 'O'
        return '*'

    @staticmethod
    def display(boardd):
        board = Board()
        board.pieces = np.copy(boardd)
        board, stuff = board.piecesToArray()
        assert (0 <= stuff[0] <= 18)
        assert (len(board) == 24)

        print(
            '{} _________________________ {} _________________________ {}'.format(NineMensMorrisGame.symbolic(board[0]),
                                                                                  NineMensMorrisGame.symbolic(board[1]),
                                                                                  NineMensMorrisGame.symbolic(
                                                                                      board[2])))
        print('|                           |                           |')
        print(
            '|        {} ________________ {} ________________ {}        |'.format(NineMensMorrisGame.symbolic(board[8]),
                                                                                  NineMensMorrisGame.symbolic(board[9]),
                                                                                  NineMensMorrisGame.symbolic(
                                                                                      board[10])))
        print('|        |                  |                  |        |')
        print('|        |        {} _______ {} _______ {}        |        |'.format(
            NineMensMorrisGame.symbolic(board[16]), NineMensMorrisGame.symbolic(board[17]),
            NineMensMorrisGame.symbolic(board[18])))
        print('|        |        |                   |        |        |')
        print('{} ______ {} ______ {}                   {} ______ {} ______ {}'.format(
            NineMensMorrisGame.symbolic(board[7]), NineMensMorrisGame.symbolic(board[15]),
            NineMensMorrisGame.symbolic(board[23]),
            NineMensMorrisGame.symbolic(board[19]), NineMensMorrisGame.symbolic(board[11]),
            NineMensMorrisGame.symbolic(board[3])))
        print('|        |        |                   |        |        |')
        print('|        |        {} _______ {} _______ {}        |        |'.format(
            NineMensMorrisGame.symbolic(board[22]), NineMensMorrisGame.symbolic(board[21]),
            NineMensMorrisGame.symbolic(board[20])))
        print('|        |                  |                  |        |')
        print('|        {} ________________ {} ________________ {}        |'.format(
            NineMensMorrisGame.symbolic(board[14]), NineMensMorrisGame.symbolic(board[13]),
            NineMensMorrisGame.symbolic(board[12])))
        print('|                           |                           |')
        print(
            '{} _________________________ {} _________________________ {}'.format(NineMensMorrisGame.symbolic(board[6]),
                                                                                  NineMensMorrisGame.symbolic(board[5]),
                                                                                  NineMensMorrisGame.symbolic(
                                                                                      board[4])))
