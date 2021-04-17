# numbrix_solver.py: a Numbrix solver using logic_solver

from logic_solver import LogicSolver
from pprint import pprint
import itertools


class NumbrixSolver:

    # TODO this whole thing
    def __init__(self, board, verbose=False):
        # Setup
        self._board = board
        self._verbose = verbose
        self._logicsolver = LogicSolver(verbose)

        board_to_prop_sets(self._logicsolver, board, verbose)
        # Solve now
        self._solve()

    def _solve(self):

        print("Initial Board:")
        print_board(self._board)
        print()

        # The main loop

        pos_knowledge_count, neg_knowledge_count = 0, 0

        for iternum in itertools.count(0):

            pos_knowledge, neg_knowledge = self._logicsolver.get_knowledge()
            pos_knowledge_incr = len(pos_knowledge) - pos_knowledge_count
            neg_knowledge_incr = len(neg_knowledge) - neg_knowledge_count

            pos_knowledge_count, neg_knowledge_count = len(pos_knowledge), len(neg_knowledge)

            num_sets = self._logicsolver.get_num_sets()

            print('Starting Iteration #{}'.format(iternum + 1))
            print("Sets: {}".format(num_sets))
            print("Accounting for new knowledge: {} positive facts, {} negative.".format(pos_knowledge_incr,
                                                                                         neg_knowledge_incr))

            self._logicsolver.run_iter()

            print("Updated Board:")
            print_board(board)

            print()

            # Should we continue?
            if self._logicsolver.is_done():
                print("Puzzle complete!")
                break

        pos_knowledge, neg_knowledge = self._logicsolver.get_knowledge()

        pos_knowledge_incr = len(pos_knowledge) - pos_knowledge_count
        neg_knowledge_incr = len(neg_knowledge) - neg_knowledge_count

        num_sets = self._logicsolver.get_num_sets()

        print("Final Sets: {}".format(num_sets))
        print("Knowledge from last iteration: {} positive facts, {} negative.".format(pos_knowledge_incr,
                                                                                      neg_knowledge_incr))
        print('Finished')


def board_to_prop_sets(logicsolver, board, verbose=False):
    # Build listing of prop sets
    num_rows = len(board)
    num_cols = len(board[0])
    num_values = num_rows * num_cols

    # We'll think internally of the row and col numbers being 0, 1, ... n
    # and the values being 0, 1, ... (n^2)-1, but increase by one before showing the user

    # Build up list of sets relating propositions

    # Sets to require that each cell have only one value
    for r in range(num_rows):
        for c in range(num_cols):
            props = []
            for v in range(num_values):
                props.append(NumbrixProposition(r, c, v, True))
            logicsolver.add_equation(props, 'xor')

    # Sets to require that either a cell is something, or it is not
    for r in range(num_rows):
        for c in range(num_cols):
            for v in range(num_values):
                props = [NumbrixProposition(r, c, v, True), NumbrixProposition(r, c, v, False)]
                logicsolver.add_equation(props, 'xor')

    # Sets to require that each value be in only one cell
    for v in range(num_values):
        props = []
        for r in range(num_rows):
            for c in range(num_cols):
                props.append(NumbrixProposition(r, c, v, True))
        logicsolver.add_equation(props, 'xor')

    # Sets to require that a cell having a given value requires that its neighbors have the preceding and succeeding values
    for v in range(num_values):
        for r in range(num_rows):
            for c in range(num_cols):
                for v_neigh in [v-1, v+1]:
                    if v_neigh < 0 or v_neigh >= num_values:
                        continue  # OOB on value
                    # For this combo v,r,c, one of the neighbors has got to have the value v_neigh
                    # Simulates P -> Q using the synonym ~P V Q.

                    props = [NumbrixProposition(r, c, v, False)]
                    for r_neigh in [r-1, r+1]:
                        if r_neigh < 0 or r_neigh >= num_rows:
                            continue  # OOB on row
                        props.append(NumbrixProposition(r_neigh, c, v_neigh, True))
                    for c_neigh in [c-1, c+1]:
                        if c_neigh < 0 or c_neigh >= num_cols:
                            continue  # OOB on col
                        props.append(NumbrixProposition(r, c_neigh, v_neigh, True))
                    logicsolver.add_equation(props, 'or')

    # Take apart board's inital state and break into true propositions
    # TODO

    print("Initialized with {} sets.".format(logicsolver.get_num_sets()))
    # if verbose:
    #     print("Initial Sets:")
    #     pprint(prop_sets)


# NumbrixProposition: a proposition-holder for Numbrix solving. Comparable objects not meant to be edited after construction.


class NumbrixProposition:
    def __init__(self, row, col, value, truthval):
        self.row = row
        self.col = col
        self.value = value
        self.truthval = truthval

    def __eq__(self, other):
        if self.row != other.row:
            return False
        if self.col != other.col:
            return False
        if self.value != other.value:
            return False
        if self.truthval != other.truthval:
            return False
        return True

    def __hash__(self):
        return hash((self.row, self.col, self.value, self.truthval))

    def __str__(self):
        return "{}_{}_{}_{}".format(self.row, self.col, self.value, self.truthval)

    def __repr__(self):
        return str(self)


def main():
    # For testing
    s = LogicSolver()
    board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    board_to_prop_sets(s, board)
    pprint(s._prop_eqns)
    pass


if __name__ == "__main__":
    main()
