import numpy as np

coefficients_dict = {
    0: (1, 2),
    1: (-1, 1),
    2: (-1, -2)
}


def get_zone(position):
    return int(position / 8)


def is_corner_move(move):
    return move % 2 == 0


def check_not_previously_occupied(original, new_1, new_2):
    return original is None or (original != new_1 and original != new_2)


def get_missing_for_mill_corner_horizontal(position, zone):
    stone_for_mill_1 = (position + 1) % 8 + zone * 8
    stone_for_mill_2 = (position + 2) % 8 + zone * 8
    return stone_for_mill_1, stone_for_mill_2


def get_missing_for_mill_corner_vertical(position, zone):
    stone_for_mill_1 = (position - 1) % 8 + zone * 8
    stone_for_mill_2 = (position - 2) % 8 + zone * 8
    return stone_for_mill_1, stone_for_mill_2


def get_missing_for_mill_middle_horizontal(position, zone):
    stone_for_mill_1 = ((position - 1) % 8) + zone * 8
    stone_for_mill_2 = ((position + 1) % 8) + zone * 8
    return stone_for_mill_1, stone_for_mill_2


def get_missing_for_mill_middle_vertical(position, zone):
    coefficients = coefficients_dict[zone]
    stone_for_mill_1 = position + coefficients[0] * 8
    stone_for_mill_2 = position + coefficients[1] * 8
    return stone_for_mill_1, stone_for_mill_2


def get_adjacent(position):
    """
    Gets all adjacent positions for given position
    :return: list of adjacent positions
    """
    if position is not None and 0 <= position <= 23:
        zone = get_zone(position)
        adjacent = [((position - 1) % 8) + zone * 8, ((position + 1) % 8) + zone * 8]

        if not is_corner_move(position):
            potentials = [position + 8, position - 8]
            for potential in potentials:
                if 0 <= potential <= 23:
                    adjacent.append(potential)
        return adjacent
    return []


class Board():
    """
    A NineMensMorris Board is represented as an array of size 6 x 6
    The element board[3][0] represents the number of stones placed
    The element board[3][1] represents the number of moves made thus far without any mills being formed.

    Board logic:
    The pieces are represented as
    -1/X for player one (red), 1/O for player 2 (green) and 0/* if there is no piece on the position

    The initial board:
        [[0,0,0,0,0,0,0,0],    -> zone 0
        [0,0,0,0,0,0,0,0],     -> zone 1
        [0,0,0,0,0,0,0,0],     -> zone 2
        [0,0,0,0,0,0,0,0]      -> misc

    Stone positions:
    - as index in flattened board (0 - 23)
    - as tuple (zone, index) ((0,0) - (2,7))

    Actions:
    Actions are stored in a list with elements of type:
        action = ((zoneOrigin, indexOrigin), (zoneDestination, indexDestination), (zoneCapture, indexCapture))
    """

    def __init__(self, pieces=None):
        """Set up initial board configuration."""
        self.n = 6
        self.m = 6
        self.pieces = np.array(pieces, dtype=int) if pieces is not None else np.zeros((self.n, self.m), dtype=int)

    def __getitem__(self, index):
        return self.pieces[index]

    def is_position_unoccupied(self, position):
        board = self.get_board_as_array()
        return board[position] == 0

    def get_board_as_array(self):
        """
        Retrieves only the stone positions as array of length 24
        """
        board_array = []
        board_array.extend(self.pieces[0])
        board_array.extend(self.pieces[1])
        board_array.extend(self.pieces[2])
        board_array.extend(self.pieces[3])

        assert (len(board_array) == 24)

        return board_array

    def get_stones_placed(self):
        """
        :return: number of stones that have been placed on the board thus far.
        """
        assert (0 <= self.pieces[4][0] <= 18)
        return self.pieces[4][0]

    def get_moves_made_without_mill(self):
        """
        :return: number of moves made thus far without a mill being created.
        """
        return self.pieces[4][1]

    def get_stones_and_misc(self):
        """
        Retrieves the separated stone positions as array of length 24 and misc info
        """
        board_array = self.get_board_as_array()

        return board_array, self.get_stones_placed(), self.get_moves_made_without_mill()

    def get_legal_move_vector(self, player, all_moves):
        """
        Valid moves vector for current player in current board state
        :param player: The current player
        :param all_moves: All possible moves array
        :return: 1/0 valid moves vector
        """

        legal_moves = self.get_legal_moves(player)
        legal_move_vector = [0] * len(all_moves)

        for move in legal_moves:
            index = all_moves.index(move)
            legal_move_vector[index] = 1
        return legal_move_vector

    def count_diff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == color:
                    count += 1
                if self[x][y] == -color:
                    count -= 1
        return count

    def get_legal_moves(self, player):
        """
        Finds which game phase player is in and retrieves the legal moves for this phase.
        :param player: The current player
        :return: Legal moves vector in current board state for current phase
        """

        game_phase = self.get_game_phase(player)
        # print(f"Game phase is {game_phase}")
        assert 0 <= game_phase <= 2

        if game_phase == 0:
            v = list(self.get_legal_moves_0(player))
            # print(f"Game phase 0: {v}")
            return v
        elif game_phase == 1:
            v = list(self.get_legal_moves_1(player))
            # print(f"Game phase 1: {v}")
            return v
        elif game_phase == 2:
            v = list(self.get_legal_moves_2(player))
            # print(f"Game phase 2: {v}")
            return v

    """
    Gets the current game phase for the current player and board
    """

    def get_game_phase(self, player):
        """
        Determines which game phase player is in based on the board.
        :param player: The current player
        :return: the game phase
        """

        stones = self.get_stones_placed()
        assert (0 <= stones <= 18)

        if stones < 18:
            return 0
        elif len(self.get_player_stones(player)) <= 3:
            return 2
        else:
            return 1

    def get_player_stones(self, player):
        """
        Gets the positions of the player's stones
        :param player: The current player
        :return: list of stone positions
        """

        board = self.get_board_as_array()
        positions = []
        index = 0
        while index < len(board):
            if board[index] == player:
                positions.append(index)
            index += 1
        return list(positions)

    def get_empty_spaces(self):
        """
        :return: List of all empty spaces on the board
        """

        board = self.get_board_as_array()

        spaces = [index for index, value in enumerate(board) if value == 0]

        return list(spaces)

    def get_possible_mills(self, moves, player):
        """
        :param moves: The possible moves (origin, destination)
        :param player: The current player
        :return: List of all moves that will make a mill on the board for current player
        """
        move_forms_mill = []

        for move in moves:
            if (move is not None) and 0 <= move[1] < 24:
                stone_position_orig = move[0]
                stone_position_new = move[1]
                zone = get_zone(stone_position_new)
                # Move to Corner
                if is_corner_move(stone_position_new):

                    # check horizontally
                    stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_corner_horizontal(stone_position_new,
                                                                                                zone)
                    if check_not_previously_occupied(stone_position_orig, stone_for_mill_1, stone_for_mill_2) and \
                            self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                        move_forms_mill.append(move)

                    # check vertically
                    stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_corner_vertical(stone_position_new, zone)
                    if check_not_previously_occupied(stone_position_orig, stone_for_mill_1, stone_for_mill_2) and \
                            self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                        move_forms_mill.append(move)

                # Move to Middle
                else:

                    # check horizontally
                    stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_middle_horizontal(stone_position_new,
                                                                                                zone)
                    if check_not_previously_occupied(stone_position_orig, stone_for_mill_1, stone_for_mill_2) and \
                            self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                        move_forms_mill.append(move)

                    # check vertically
                    stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_middle_vertical(stone_position_new, zone)
                    if check_not_previously_occupied(stone_position_orig, stone_for_mill_1, stone_for_mill_2) and \
                            self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                        move_forms_mill.append(move)

        return list(move_forms_mill)

    def check_player_occupies_on_board(self, player, pos_1, pos_2):
        """
        Checks if player occupies the given positions on the board
        """
        board = self.get_board_as_array()
        return board[pos_1] == player and board[pos_2] == player

    def check_for_mills(self, player):
        """
        :param player: The current player
        :return: List of all mills for current player
        """
        # TODO: Check if I should remove duplicates mill 0-1-2 is same as 1-0-2, 0-2-1, 1-2-0, 2-1-0, 2-0-1

        current_mills = []
        stone_positions = self.get_player_stones(player)

        for position in stone_positions:
            zone = get_zone(position)
            if is_corner_move(position):
                stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_corner_horizontal(position, zone)
                if self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                    current_mills.append((position, stone_for_mill_1, stone_for_mill_2))
                stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_corner_vertical(position, zone)
                if self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                    current_mills.append((position, stone_for_mill_1, stone_for_mill_2))

            else:
                stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_middle_horizontal(position, zone)
                if self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                    current_mills.append((position, stone_for_mill_1, stone_for_mill_2))

                stone_for_mill_1, stone_for_mill_2 = get_missing_for_mill_middle_vertical(position, zone)
                if self.check_player_occupies_on_board(player, stone_for_mill_1, stone_for_mill_2):
                    current_mills.append((position, stone_for_mill_1, stone_for_mill_2))

        return list(current_mills)

    def get_stones_outside_mills(self, player):
        """
        :param player: The current player
        :return: list of player's stones that are not in any mill
        """
        all_player_stones = self.get_player_stones(player)

        mills = self.check_for_mills(player)

        remaining_pieces = self.get_player_stones(player)

        for stone in all_player_stones:
            for mill in mills:
                if stone in mill and stone in remaining_pieces:
                    remaining_pieces.remove(stone)

        return list(remaining_pieces)

    def get_legal_moves_0(self, player):
        """
        Returns the valid moves vector for current player in current board state in phase 0
        :param player: The current player
        :return: Valid moves vector
        """

        possibilities_for_capture = self.get_stones_outside_mills(-player)

        empty_spaces = []
        for space in self.get_empty_spaces():
            empty_spaces.append((None, space))

        mill_moves = self.get_possible_mills(empty_spaces, player)

        moves = []

        for move in empty_spaces:
            if move in mill_moves:
                for opponent_stone in possibilities_for_capture:
                    moves.append((None, move[1], opponent_stone))
            else:
                moves.append((None, move[1], None))

        return list(moves)

    def get_legal_moves_1(self, player):
        """
        Returns the valid moves vector for current player in current board state in phase 1
        :param player: The current player
        :return: Valid moves vector
        """

        moves = []

        possibilities_for_capture = self.get_stones_outside_mills(-player)

        current_positions = self.get_player_stones(player)

        possible_moves = []

        for position in current_positions:
            adjacent = get_adjacent(position)
            for adjacent_position in adjacent:
                if self.is_position_unoccupied(adjacent_position):
                    possible_moves.append((position, adjacent_position))

        mill_moves = self.get_possible_mills(possible_moves, player)

        for move in possible_moves:
            if move in mill_moves:
                for opponent_stone in possibilities_for_capture:
                    moves.append((move[0], move[1], opponent_stone))
            else:
                moves.append((move[0], move[1], None))

        return list(moves)

    def get_legal_moves_2(self, player):
        """
        Returns the valid moves vector for current player in current board state in phase 1
        :param player: The current player
        :return: Valid moves vector
        """
        moves = []

        possibilities_for_capture = self.get_stones_outside_mills(-player)

        current_positions = self.get_player_stones(player)

        possible_moves = []

        empty_spaces = self.get_empty_spaces()

        for position in current_positions:
            for empty_position in empty_spaces:
                possible_moves.append((position, empty_position))

        mill_moves = self.get_possible_mills(possible_moves, player)

        for move in possible_moves:
            if move in mill_moves:
                for opponent_stone in possibilities_for_capture:
                    moves.append((move[0], move[1], opponent_stone))
            else:
                moves.append((move[0], move[1], None))

        return list(moves)

    def has_legal_moves(self, player) -> bool:
        """
        Checks if player can make any valid move in this board state
        :param player: The current player
        :return: Has valid moved
        """
        if len(self.get_legal_moves(player)) > 0:
            return True
        return False

    def get_board_rotations(self, pi, all_moves, policy_rotation_vector):
        """
        Rotates the board 3 times.
        :param pi: Vector of all valid moves
        :param all_moves: All possible moves
        :param policy_rotation_vector: The rotation policy for 90 degrees
        :return: The three rotations of the board along with the corresponding rotated valid moves vector
        """
        old_board, count, moves_without_mills = self.get_stones_and_misc()

        reshaped_board = np.reshape(old_board[:24], (3, 8))
        rotation_vector = 2

        rotated_results = []

        for _ in range(3):
            rotated_board = np.array([np.roll(zone, rotation_vector) for zone in reshaped_board])

            flat_rotated_board = rotated_board.flatten()

            rotated_pi = np.zeros(len(all_moves), dtype=int)
            for idx, move in enumerate(pi):
                rotated_pi[policy_rotation_vector[idx]] = move

            rotated_results.append((self.to_board(flat_rotated_board, [count, moves_without_mills]), rotated_pi))

            reshaped_board = rotated_board
            pi = rotated_pi

        return rotated_results

    def execute_move(self, player, move_index, all_moves) -> None:
        """
        Executes the given move.
        :param player: The current player
        :param move_index: The index of the move to be executed
        :param all_moves: List of all possible moves
        """
        move = all_moves[move_index]
        assert (len(move) == 3)  # move is a tuple of length 3
        board, count_placements, moves_without_mills = self.get_stones_and_misc()
        # print(f"EXECUTING MOVE: {move}. The board is now: {board}. The placements {count_placements}")

        if self.get_game_phase(player) == 0:
            count_placements += 1
        if move[0] is not None:
            board[move[0]] = 0
        if move[2] is not None:
            board[move[2]] = 0
            moves_without_mills = 0
        elif move[2] is None:
            moves_without_mills += 1
        board[move[1]] = player

        # print(f"DONE MOVE: {move}. The board is now: {board}. The placements {count_placements}")

        self.pieces = np.copy(self.to_board(board, [count_placements, moves_without_mills]))

    def to_board(self, board_array, misc):
        """
        :param board_array: The stone placements
        :param misc: Misc info about moves
        :return: board containing stone placements and misc
        """
        board = np.zeros((self.n, self.m), dtype=int)
        board[:4, :] = np.reshape(board_array, (4, 6))

        board[4, 0] = misc[0]
        board[4, 1] = misc[1]

        # print(f"NEW BOARD MADE: {board}")

        return board
