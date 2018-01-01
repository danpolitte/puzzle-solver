import math
from pprint import pprint

from PropositionSet import PropositionSet
import inference_rules


class LogicSolver:

    def __init__(self, board, verbose=False):
        self._board = board
        self._verbose = verbose

        # Prepare for the run start by enumerating sets & initial clues
        self._prop_sets = board_to_prop_sets(board)
        self._new_knowledge = {}
        for rnum, boardrow in enumerate(board):
            for cnum, v in enumerate(boardrow):
                if v != 0:
                    clue_text = create_1indexed_string(rnum, cnum, v - 1)  # v-1 because it's already 1-indexed
                    self._new_knowledge[clue_text] = True
        print("Initial knowledge: {} positive facts".format(len(self._new_knowledge)))
        if verbose:
            print("Initial knowledge:")
            pprint(self._new_knowledge)

    def run_iter(self):
        # The magic: run a turn on this solver.
        # Stop after first step that allows new insights. This way, we can avoid the expensive later
        # steps whenever possible.

        previous_knowledge = self._new_knowledge


        # Step 0: transform/reduce sets from previous info
        print('Step 0 (apply previous discoveries)')
        for datum, knownValue in previous_knowledge.items():
            for s in self._prop_sets:
                s.apply_information(datum, knownValue)

        # Can we make any new inferences from this?
        new_inferences = inference_rules.gather_all_inferences(self._prop_sets)

        # Step 1: transformations based on comparing pairs of sets (subset-based reduction)
        if len(new_inferences) == 0: # Only if no discoveries so far
            print('Step 1 (subset-reduction)')
            new_inferences, self._prop_sets = inference_rules.pair_reductions(self._prop_sets)

        # Step 2: adding sets using combining inference rules (under certain conditions)
        if len(new_inferences) == 0:  # Only if no discoveries so far
            print('Step 2 (triple-set combining)')
            new_inferences, self._prop_sets = inference_rules.triplet_reductions(self._prop_sets)

        # Make sure we carry new info to the next iteration
        self._new_knowledge = new_inferences

        # Wrap-up: are there any depleted sets we must clean up?
        self._prop_sets = [s for s in self._prop_sets if s.still_has_info()]

        # Wrap-up: update board if applicable
        for datum, knownValue in self._new_knowledge.items():
            # Only positive clues make a difference on the board
            if knownValue:
                r_1ind, c_1ind, v = parse_1indexed_string(datum)
                self._board[r_1ind - 1][c_1ind - 1] = v

        # Done with this iteration

    def get_board(self):
        return self._board

    def get_num_sets(self):
        return len(self._prop_sets)

    def is_done(self):
        # If this is True, no point to further iterations
        return len(self._prop_sets) == 0

    def get_last_discoveries(self):
        # Returns (pos_discoveries, neg_discoveries) tuple
        pos_discoveries = len([1 for k, v in self._new_knowledge.items() if v])
        neg_discoveries = len(self._new_knowledge) - pos_discoveries
        return pos_discoveries, neg_discoveries


# Auxiliary functions


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
    return str(r+1) + '_' + str(c+1) + '_' + str(v+1)


def parse_1indexed_string(datum):
    return [int(numstr) for numstr in datum.split('_')]
