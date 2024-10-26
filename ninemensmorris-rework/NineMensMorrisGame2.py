from __future__ import print_function
import sys

sys.path.append('..')
from Game import Game
from ninemensmorris.NineMensMorrisLogic import Board
import numpy as np
import copy

'''
Implementation of the Game Class for NineMensMorris
'''


class NineMensMorrisGame(Game):
    # Player 1 as X, Player 2 as O
    symbolic_representation = {
        -1: "O",
        +0: "*",
        +1: "X"
    }
    """
    inititalizes the list of all possible moves, the policy rotation vector and
    the number of moves without a mill to determine a draw
    """

    def __init__(self):
        super().__init__()
        self.n = 4
        self.m = 8
        self.all_moves = self.get_all_moves()
        self.policy_rotation_vector = self.get_policy_roation90()
        self.MAX_MOVES_WITHOUT_MILL = 200

    """
    Gets the list of all possible moves
    """

    def get_all_moves(self):
        """
        Returns:
           moves: A list with all possible moves for the game
        """
        moves = self.get_all_moves_phase_zero() + self.get_all_moves_phase_one_and_two()
        return list(moves)

    """
    Gets the lookup list for the rotation of the vector of legal moves
    """

    def get_policy_roation90(self):
        """
        Returns:
            rotation90: lookup list for the rotation of the legal moves vector
        """

        rotation90 = [-1] * len(self.all_moves)

        i = 0
        while i < len(self.all_moves):
            move = self.all_moves[i]
            rotatedmove = self.rotate(move)
            newindex = self.all_moves.index(rotatedmove)
            rotation90[i] = newindex

            i += 1

        return rotation90

    """
    Rotates a move by 90 degrees
    """

    def rotate(self, move):
        """
        Input:
            move: Tuple (origin, destination, piece to take)
        Returns:
            rot_move: Tuple (neworigin, newdestination, newpiece to take)
        """
        if move[0] == 'none':
            neworigin = 'none'

        elif move[0] in [6, 7, 14, 15, 22, 23]:
            neworigin = move[0] - 6

        else:
            neworigin = move[0] + 2

        if move[1] in [6, 7, 14, 15, 22, 23]:
            newdestination = move[1] - 6

        else:
            newdestination = move[1] + 2

        if move[2] == 'none':
            newenemy = 'none'

        elif move[2] in [6, 7, 14, 15, 22, 23]:
            newenemy = move[2] - 6

        else:
            newenemy = move[2] + 2

        return (neworigin, newdestination, newenemy)

    """
    Generates all possible moves for game phase zero
    """

    def get_all_moves_phase_zero(self):
        """
        Returns:
            moves: list of all possible move Tuples in phase zero: Stone Placing and Capturing.
            Elements are of type: ((zoneOrigin, indexOrigin), None, (zoneToTake, indexToTake))
            First Tuple represents where to place the stone. Third Tuple represents which stone of the opponent to take
            in case a mill is created.
        """

        moves = []

        for zone in range(3):
            for index in range(8):
                # All possible Placements without Capture.
                moves.append(((zone, index), None, None))

                # All possible Placements with Capture.
                for zone_capture in range(3):
                    for index_capture in range(8):
                        if (zone, index) != (zone_capture, index_capture):
                            moves.append(((zone, index), None, (zone_capture, index_capture)))

        return list(moves)

    """
    Generates all possible moves for game phase one and two
    """

    def get_all_moves_phase_one_and_two(self):
        """
        Returns:
            moves: list of all possible move Tuples in phases one and two: Moving, Capturing and Flying
        """

        moves = []
        for zone in range(3):
            for index in range(8):
                # All possible Moves in the same zone without Capture.
                index_target_1 = index + 1 % 8
                index_target_2 = index - 1 % 8
                moves.append(((zone, index), (zone, index_target_1), None))
                moves.append(((zone, index), (zone, index_target_2), None))

                # All possible Moves in the same zone with Capture.
                for zone_capture in range(3):
                    for index_capture in range(8):
                        if (zone, index) != (zone_capture, index_capture):
                            if (zone, index_target_1) != (zone_capture, index_capture):
                                moves.append(((zone, index), (zone, index_target_1), (zone_capture, index_capture)))
                            if (zone, index_target_2) != (zone_capture, index_capture):
                                moves.append(((zone, index), (zone, index_target_2), (zone_capture, index_capture)))

                # Stones with even index (corners) are not connected to other zones.
                if not index % 2 == 0:
                    if zone > 0:
                        # All possible Moves to a different zone without Capture.
                        zone_target_1 = zone - 1
                        moves.append(((zone, index), (zone_target_1, index), None))

                        # All possible Moves to a different zone with Capture.
                        for zone_capture in range(3):
                            for index_capture in range(8):
                                if (zone, index) != (zone_capture, index_capture) and (zone_target_1, index) != (
                                        zone_capture, index_capture):
                                    moves.append(((zone, index), (zone_target_1, index), (zone_capture, index_capture)))

                    if zone < 2:
                        # All possible Moves to a different zone without Capture.
                        zone_target_2 = zone + 1
                        moves.append(((zone, index), (zone_target_2, index), None))

                        # All possible Moves to a different zone with Capture.
                        for zone_capture in range(3):
                            for index_capture in range(8):
                                if (zone, index) != (zone_capture, index_capture) and (zone_target_2, index) != (
                                        zone_capture, index_capture):
                                    moves.append(((zone, index), (zone_target_2, index), (zone_capture, index_capture)))

        return list(moves)

    """
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
    Gets the size of the board image in a Tuple (x, y)
    """

    def getBoardSize(self) -> tuple:
        """
        Returns:
            dimensions: a Tuple with the board dimensions
        """
        return (6, 6)

    """
    Gets the number of all possible actions
    """

    def getActionSize(self):
        """
        Returns:
            actionssize: number of all moves
        """
        return len(self.all_moves)

    """
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
    based on Othellogame.py
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
    Based on Othellogame.py
    Multiplies each element with the given player, resulting in a canonical
    board from the perspective of the given player. The given players pieces
    are always represented as 1 in the Canonical Form.
    Note: no true canonical form
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
    Based on Othellogame.py
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
    def display(boardd):
        board = Board()
        board.pieces = np.copy(boardd)
        board, stuff = board.piecesToArray()
        assert (0 <= stuff[0] <= 18)
        assert (len(board) == 24)

        print('{} ________________________ {} ________________________ {}'.format(board[0], board[1], board[2]))
        print('|                           |                           |')
        print('|        {} _______________ {} _______________ {}        |'.format(board[8], board[9], board[10]))
        print('|        |                  |                  |        |')
        print('|        |        {} ______ {} ______ {}        |        |'.format(board[16], board[17], board[18]))
        print('|        |        |                   |        |        |')
        print('{} _____ {} _____ {}                  {} _____ {} _____ {}'.format(board[7], board[15], board[23],
                                                                                  board[19], board[11], board[3]))
        print('|        |        |                   |        |        |')
        print('|        |        {} ______ {} ______ {}        |        |'.format(board[22], board[21], board[20]))
        print('|        |                  |                  |        |')
        print('|        {} _______________ {} _______________ {}        |'.format(board[14], board[13], board[12]))
        print('|                           |                           |')
        print('{} ________________________ {} ________________________ {}'.format(board[6], board[5], board[4]))
