# sudoku_solver.py: a Sudoku solver using logic_solver

import math

class SudokuSolver:

    # TODO this whole thing
    def __init__(self, board, verbose=False):
        self._board = board
        self._verbose = verbose
        self._prop_sets = board_to_prop_sets(board,verbose)
        pass
        self._solve()

    def _solve(self):
        pass

def board_to_prop_sets(board, verbose=False):
    # Build listing of prop sets
    side_length = len(board)  # To be an argument later, or inferred from input board
    if len(board[0]) != side_length:
        print('Error: the board has different horizontal and vertical sizes!')
        return

    block_size = int(math.sqrt(side_length))  # cells along a side of a block
    block_count = block_size  # number of blocks in each direction

    # Build up list of sets relating propositions. All the initial group will be XOR sets.
    prop_sets = []
    # Sets to require uniqueness of each cell's value
    for r in range(side_length):
        for c in range(side_length):
            new_set = set()
            for v in range(side_length):
                new_set.add(create_1indexed_string(r, c, v))
            prop_sets.append(PropositionSet(new_set))

    # Sets to require that each row only contain each value exactly once
    for r in range(side_length):
        for v in range(side_length):
            new_set = set()
            for c in range(side_length):
                new_set.add(create_1indexed_string(r, c, v))
            prop_sets.append(PropositionSet(new_set))

    # Sets to require that each column only contain each value exactly once
    for c in range(side_length):
        for v in range(side_length):
            new_set = set()
            for r in range(side_length):
                new_set.add(create_1indexed_string(r, c, v))
            prop_sets.append(PropositionSet(new_set))

    # Sets to require that each block only contain each value exactly once
    for v in range(side_length):
        for block_index_horiz in range(block_count):
            for block_index_vert in range(block_count):
                new_set = set()
                for row_within_block in range(block_size):
                    r = block_index_vert * block_size + row_within_block
                    for col_within_block in range(block_size):
                        c = block_index_horiz * block_size + col_within_block
                        new_set.add(create_1indexed_string(r, c, v))
                prop_sets.append(PropositionSet(new_set))

    print("Initialized with {} sets.".format(len(prop_sets)))
    if verbose:
        print("Initial Sets:")
        pprint(prop_sets)

    return prop_sets


def create_1indexed_string(r, c, v):
    # Create a string describing a possibility with 1-indexed values, from 0-indexed inputs
    return str(r + 1) + '_' + str(c + 1) + '_' + str(v + 1)


def parse_1indexed_string(datum):
    return [int(numstr) for numstr in datum.split('_')]
