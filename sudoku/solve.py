# solve.py:

import sys
import math
from logic_solver import LogicSolver


def sudoku_logic_solver_driver(board, verbose):
    solver = LogicSolver(verbose)
    side_length = len(board)

    print("Initial Board:")
    print_board(solver.get_board())
    print()

    # The main loop.
    # Modify the sets based on our recent discoveries, and collect new discoveries based on it for next time.
    # Max iters: the number of variables we've got (N^3), so we can accomodate a rate of 1 inference/iter.
    iters_since_discovery = 0
    for iternum in range(side_length**3):

        num_pos_facts_added, num_neg_facts_added = solver.get_last_discoveries()
        num_sets = solver.get_num_sets()

        print('Starting Iteration #{}'.format(iternum+1))
        print("Sets: {}".format(num_sets))
        print("Accounting for new knowledge: {} positive facts, {} negative.".format(num_pos_facts_added, num_neg_facts_added))

        solver.run_iter()

        print("Updated Board:")
        print_board(board)

        print()

        # Should we continue?
        if solver.is_done():
            print("Puzzle complete!")
            break

    num_pos_facts_added, num_neg_facts_added = solver.get_last_discoveries()
    num_sets = solver.get_num_sets()

    print("Final Sets: {}".format(num_sets))
    print("Knowledge from last iteration: {} positive facts, {} negative.".format(num_pos_facts_added, num_neg_facts_added))
    print('Finished')


# TODO: this one should be part of board class when we make that
def print_board(board):
    board_size = len(board)
    block_size = int(math.sqrt(board_size))
    board_as_chars = [[(str(value) if value > 0 else ' ') for value in row] for row in board]

    # Insert dividers among columns
    for row in board_as_chars:
        for divider_col in range(board_size - block_size, 0, -block_size):
            row.insert(divider_col, '|')

    # Insert dividers among rows
    for divider_row in range(board_size - block_size, 0, -block_size):
        board_as_chars.insert(divider_row, ['-']*(board_size+block_size-1))

    printable_grid = '\n'.join([''.join(row) for row in board_as_chars])
    print(printable_grid)


def parse_character_as_sudoku_value(character):
    return int(character) if character.isdigit() else 0


def main(argv):

    # Get the board from the file in the first argument
    with open(argv[1]) as f:
        board = [[parse_character_as_sudoku_value(char) for char in row.strip()] for row in f]

        sudoku_logic_solver_driver(board, verbose=False)


if __name__ == "__main__":
    main(sys.argv)
