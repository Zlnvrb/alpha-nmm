from __future__ import print_function

from itertools import product

from Game import Game
from .NineMensMorrisLogic import Board
import sys
import numpy as np
import copy

sys.path.append('..')


def to_single_position(zone, index):
    return zone * 8 + index


def get_zone(position):
    return int(position / 8)


def rotate(move):
    """
    Rotates move by 90 degrees
    :param move: (zoneOrigin, indexOrigin), (zoneMove, indexMove), (zoneCapture, indexCapture))
    :return: (zOriginRotated, ixOriginRotated), (zMoveRotated, ixMoveRotated), (zCaptureRotated, ixCaptureRotated))
    """
    # move = ((zoneOrigin, indexOrigin), (zoneMove, indexMove), (zoneCapture, indexCapture))

    origin = move[0]
    destination = move[1]
    captured = move[2]

    if origin is None:
        rotated_origin = None
    else:
        zone = get_zone(origin)
        rotated_origin = ((origin - 6) % 8) + zone * 8

    if destination is None:
        rotated_destination = None
    else:
        zone = get_zone(destination)
        rotated_destination = ((destination - 6) % 8) + zone * 8

    if captured is None:
        rotated_captured = None
    else:
        zone = get_zone(captured)
        rotated_captured = ((captured - 6) % 8) + zone * 8

    return rotated_origin, rotated_destination, rotated_captured


def get_all_moves_phase_zero():
    """
    :return: list of all possible moves in phase zero: Stone Placing and Capturing.
    Moves are of type: (None, destination, capture/None)
    First tuple represents where to place the stone. Third tuple represents which opponent's stone to capture
        in case a mill is created.
    """

    moves = []

    for zone in range(3):
        for index in range(8):
            # All possible Placements without Capture.
            moves.append((None, to_single_position(zone, index), None))

            # All possible Placements with Capture.
            for zone_capture in range(3):
                for index_capture in range(8):
                    if (zone, index) != (zone_capture, index_capture):
                        moves.append((None, to_single_position(zone, index),
                                      to_single_position(zone_capture, index_capture)))

    return list(moves)


def get_all_moves_phase_one():
    """
    :return: list of all possible moves in phase zero: Moving, Capturing and Flying
    Moves are of type: ((zoneOrigin, indexOrigin), (zoneOrigin, indexOrigin), (zoneCapture, indexCapture)/None)
    First and second tuples represent which stone to move to which space. Third tuple represents which opponent's
    stone to capture in case a mill is created.
    """

    moves = []
    for zone in range(3):
        for index in range(8):
            # All possible Moves in the same zone without Capture.
            index_target_1 = (index + 1) % 8
            index_target_2 = (index - 1) % 8
            moves.append((to_single_position(zone, index), to_single_position(zone, index_target_1), None))
            moves.append((to_single_position(zone, index), to_single_position(zone, index_target_2), None))

            # All possible Moves in the same zone with Capture.
            for zone_capture in range(3):
                for index_capture in range(8):
                    if (zone, index) != (zone_capture, index_capture):
                        if (zone, index_target_1) != (zone_capture, index_capture):
                            moves.append((to_single_position(zone, index),
                                          to_single_position(zone, index_target_1),
                                          to_single_position(zone_capture, index_capture)))
                        if (zone, index_target_2) != (zone_capture, index_capture):
                            moves.append((to_single_position(zone, index),
                                          to_single_position(zone, index_target_2),
                                          to_single_position(zone_capture, index_capture)))

            # Stones with even index (corners) are not connected to other zones.
            if not index % 2 == 0:
                if zone > 0:
                    # All possible Moves to a different zone without Capture.
                    zone_target_1 = zone - 1
                    moves.append((to_single_position(zone, index), to_single_position(zone_target_1, index), None))

                    # All possible Moves to a different zone with Capture.
                    for zone_capture in range(3):
                        for index_capture in range(8):
                            if (zone, index) != (zone_capture, index_capture) and (zone_target_1, index) != (
                                    zone_capture, index_capture):
                                moves.append((to_single_position(zone, index),
                                              to_single_position(zone_target_1, index),
                                              to_single_position(zone_capture, index_capture)))

                if zone < 2:
                    # All possible Moves to a different zone without Capture.
                    zone_target_2 = zone + 1
                    moves.append((to_single_position(zone, index), to_single_position(zone_target_2, index), None))

                    # All possible Moves to a different zone with Capture.
                    for zone_capture in range(3):
                        for index_capture in range(8):
                            if (zone, index) != (zone_capture, index_capture) and (zone_target_2, index) != (
                                    zone_capture, index_capture):
                                moves.append((to_single_position(zone, index),
                                              to_single_position(zone_target_2, index),
                                              to_single_position(zone_capture, index_capture)))

    return list(moves)


def get_all_moves_phase_two():
    """
    :return: list of all possible moves in phase two: Flying
    Moves are of type: ((zoneOrigin, indexOrigin), (zoneOrigin, indexOrigin), (zoneCapture, indexCapture)/None)
    First tuple represents where to place the stone. Third tuple represents which opponent's stone to capture
    in case a mill is created.
    """

    moves = []
    positions = list(product(range(3), range(8)))

    for origin, destination, capture in product(positions, repeat=3):
        if origin != destination and origin != capture and destination != capture:
            moves.append((to_single_position(origin[0], origin[1]),
                          to_single_position(destination[0], destination[1]),
                          None))
            moves.append((to_single_position(origin[0], origin[1]),
                          to_single_position(destination[0], destination[1]),
                          to_single_position(capture[0], capture[1])))

    return moves


def get_all_moves_phase_one_and_two():
    """
    :return: list of all possible moves in phase one and two: Moving, Capturing and Flying
    Moves are of type: ((zoneOrigin, indexOrigin), (zoneOrigin, indexOrigin), (zoneCapture, indexCapture)/None)
    First and second tuples represent which stone to move to which space. Third tuple represents which opponent's
    stone to capture in case a mill is created.
    """

    moves_phase_one = get_all_moves_phase_one()
    moves_phase_two = get_all_moves_phase_two()

    seen_moves = []

    for move in moves_phase_one + moves_phase_two:
        if move not in seen_moves:
            seen_moves.append(move)

    return seen_moves


def get_all_moves():
    """
    :return: A list of all possible moves in the game.
    """
    moves = get_all_moves_phase_zero() + get_all_moves_phase_one_and_two()
    return list(moves)


class NineMensMorrisGame(Game):
    # Player 1 as X, Player 2 as O
    symbolic_representation = {
        -1: "O",
        +0: "*",
        +1: "X"
    }
    """
    Initializes the board size, list of all possible moves, the policy rotation vector and
    the number of moves without a mill to determine a draw
    """

    def __init__(self):
        super().__init__()
        self.n = 6
        self.m = 6
        self.all_moves = get_all_moves()
        self.policy_rotation_vector = self.get_policy_rotation_by_90()
        self.MAX_MOVES_WITHOUT_MILL = 20

    def get_policy_rotation_by_90(self):
        """
        :return: Lookup list for the rotation of all possible moves by 90 degrees
        """

        rotation_90 = [-1] * len(self.all_moves)

        for move_index in range(len(self.all_moves)):
            move = self.all_moves[move_index]
            rotated_move = rotate(move)
            new_index = self.all_moves.index(rotated_move)
            rotation_90[move_index] = new_index

        return rotation_90

    def getInitBoard(self):
        """
        :return: The initial board configuration
        """
        b = Board()

        return b.pieces

    def getBoardSize(self) -> tuple:
        """
        :return: board dimensions
        """
        return self.n, self.m

    def getActionSize(self):
        """
        :return: number of all possible moves
        """
        return len(self.all_moves)

    def getNextState(self, board, player, move):
        """
        Executes a move and returns the new board state and the next player
        :param board: The current board
        :param player: The current player (1 or -1)
        :param move: The move to be made
        :return: The new board after the move and the next player
        """
        b = Board(board)

        b.execute_move(player, move, self.all_moves)

        return b.pieces, -player

    def getValidMovesAsTuple(self, board, player):
        # print(f"BOARD IS CURRENTLY {board}")
        valid_moves_vector = self.getValidMoves(board, player)
        moves = self.all_moves
        valid_moves_indices = list([i for i, value in enumerate(valid_moves_vector) if value == 1])
        valid_moves = [moves[i] for i in valid_moves_indices]
        return valid_moves_vector, valid_moves, moves

    def getValidMoves(self, board, player):
        """
        :param board: The current board
        :param player: The current player
        :return: Vector of all valid moves the current player can make in this board state.
        """
        b = Board(board)

        valid_moves = b.get_legal_move_vector(player, self.all_moves)

        return np.array(valid_moves)

    def getGameEnded(self, board, player) -> float:
        """
        Determines if and how the game has ended.
        :param board: The current board
        :param player: The current player
        :return:
        0 - game has not ended; 1 - current player won; -1 - current player lost; 0.0001 - draw
        """

        assert (not isinstance(board, str))

        b = Board(board)

        if b.get_moves_made_without_mill() >= self.MAX_MOVES_WITHOUT_MILL:
            return 0.0001
        elif not b.has_legal_moves(player):
            return -1
        elif not b.has_legal_moves(-player):
            return 1
        elif len(b.get_player_stones(player)) < 3 and b.get_stones_placed() == 18:
            return -1
        elif len(b.get_player_stones(-player)) < 3 and b.get_stones_placed() == 18:
            return 1
        elif b.has_legal_moves(-player) and b.has_legal_moves(player):
            return 0

    def getCanonicalForm(self, board, player):
        """
        Transforms the board to canonical form from the current player's perspective
        :param board: The current board
        :param player: The current player
        :return: The board in canonical form
        """

        # If you don't want misc to be taken here
        # b = Board()
        # b.pieces = np.copy(board)
        #
        # stone_board, _, _ = b.get_stones_and_misc()
        # canon_board = player * stone_board
        # return canon_board

        b = Board(board)

        count_placements = b.get_stones_placed()
        current_moves = b.get_moves_made_without_mill()

        canon_board = player * board

        canon_board[4][0] = count_placements
        canon_board[4][1] = current_moves

        # print(f"Canon board is {canon_board}")
        return canon_board

    def getSymmetries(self, board, pi):
        """
        Gets symmetries by rotating the board 3 times, each time also adapting the legal moves vector to the new board.
        :param board: The current board
        :param pi: Vector of valid moves from current board
        :return: Three board rotations and corresponding valid moves vector
        """

        assert (len(pi) == len(self.all_moves))
        b = Board(board)

        results = b.get_board_rotations(pi, self.all_moves, self.policy_rotation_vector)

        return results

    def stringRepresentation(self, board):
        """
        Used for hashing in MCTS.
        :param board: The current board
        :return: String representation of the board
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
    def display(board_array) -> None:
        """
        Displays the board.
        :param board_array: The current board
        """
        board = Board()
        board.pieces = np.copy(board_array)
        board, stones, _ = board.get_stones_and_misc()

        red = "\033[31m"
        green = "\033[32m"
        reset = "\033[0m"

        def symbolic(value):
            if value == 1:
                return f"{red}X{reset}"
            if value == -1:
                return f"{green}O{reset}"
            return '*'

        print(
            '{} _________________________ {} _________________________ {}'.format(symbolic(board[0]),
                                                                                  symbolic(board[1]),
                                                                                  symbolic(
                                                                                      board[2])))
        print('|                           |                           |')
        print(
            '|        {} ________________ {} ________________ {}        |'.format(symbolic(board[8]),
                                                                                  symbolic(board[9]),
                                                                                  symbolic(
                                                                                      board[10])))
        print('|        |                  |                  |        |')
        print('|        |        {} _______ {} _______ {}        |        |'.format(
            symbolic(board[16]), symbolic(board[17]),
            symbolic(board[18])))
        print('|        |        |                   |        |        |')
        print('{} ______ {} ______ {}                   {} ______ {} ______ {}'.format(
            symbolic(board[7]), symbolic(board[15]),
            symbolic(board[23]),
            symbolic(board[19]), symbolic(board[11]),
            symbolic(board[3])))
        print('|        |        |                   |        |        |')
        print('|        |        {} _______ {} _______ {}        |        |'.format(
            symbolic(board[22]), symbolic(board[21]),
            symbolic(board[20])))
        print('|        |                  |                  |        |')
        print('|        {} ________________ {} ________________ {}        |'.format(
            symbolic(board[14]), symbolic(board[13]),
            symbolic(board[12])))
        print('|                           |                           |')
        print(
            '{} _________________________ {} _________________________ {}'.format(symbolic(board[6]),
                                                                                  symbolic(board[5]),
                                                                                  symbolic(
                                                                                      board[4])))

# def main():
#     game = NineMensMorrisGame()
#     board = board = [
#         [0, 1, -1, 0, -1, 1, 1, 0],
#         [0, 0, -1, 1, 1, 0, -1, -1],
#         [1, 1, -1, -1, -1, -1, 1, 1],
#         [18, 25, 26, 27, 28, 29, 30, 31]
#     ]
#     moves1 = game.getValidMoves(board, 1)
#     b = Board(board)
#     v = b.get_board_rotations(np.zeros(len(game.all_moves)), game.all_moves, game.policy_rotation_vector)
#
#
#     # print(v)
#     # game.display(board)
#
#
# if __name__ == "__main__":
#     main()
