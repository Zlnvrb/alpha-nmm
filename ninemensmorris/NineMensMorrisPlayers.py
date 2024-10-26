import random


def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices


def input_to_valid_move_form(input):
    input_split = input.split(" ")
    return to_correct_type(
        input_split[0]), to_correct_type(input_split[1]), to_correct_type(input_split[2])


def to_correct_type(value):
    if value != 'none':
        return int(value)
    return value


class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valid_moves_vector = self.game.getValidMoves(board, 1)
        indices = find_indices(valid_moves_vector, 1)
        a = random.choice(indices)
        return a


class HumanNineMensMorrisPlayer():
    def __init__(self, game, show_valid_moves):
        self.game = game
        self.show_valid_moves = show_valid_moves

    def play(self, board):

        while True:
            valid_moves_vector, moves = self.game.getValidMovesAsTuple(board, 1)

            # Show all valid moves in canon form
            if self.show_valid_moves:
                valid_moves_indices = list([i for i, value in enumerate(valid_moves_vector) if value == 1])
                print([moves[i] for i in valid_moves_indices])

            user_input = input()
            move = input_to_valid_move_form(user_input)

            if move in moves:
                break
            else:
                print('Invalid')

        # Return index of move
        return moves.index(move)
