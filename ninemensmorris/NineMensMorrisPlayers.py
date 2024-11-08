import random


def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices


def input_to_valid_move_form(given_input):
    input_split = given_input.split(" ")
    return to_correct_type(
        input_split[0]), to_correct_type(input_split[1]), to_correct_type(input_split[2])


def to_correct_type(value):
    if value != 'none':
        return int(value)
    return None


class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valid_moves_vector, moves, _ = self.game.getValidMovesAsTuple(board, 1)
        # print(f"Valid moves: {moves}")
        indices = find_indices(valid_moves_vector, 1)
        a = random.choice(indices)
        return a


class GreedyNineMensMorrisPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valid_moves_vector = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valid_moves_vector[a] == 0:
                continue
            next_board, _ = self.game.getNextState(board, 1, a)
            score = self.game.getScore(next_board, 1)
            candidates += [(-score, a)]
        candidates.sort()
        return candidates[0][1]


class HumanNineMensMorrisPlayer():
    def __init__(self, game, show_valid_moves):
        self.game = game
        self.show_valid_moves = show_valid_moves

    def play(self, board):

        while True:
            valid_moves_vector, valid_moves, all_moves = self.game.getValidMovesAsTuple(board, 1)
            # print(f"Valid moves: {valid_moves}")

            user_input = input()
            move = input_to_valid_move_form(user_input)

            if move in all_moves:
                break
            else:
                print('Invalid')

        # Return index of move
        return all_moves.index(move)
