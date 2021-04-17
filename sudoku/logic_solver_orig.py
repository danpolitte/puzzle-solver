# logic_solver.py: a propositional logic solving system

import math
from pprint import pprint
from time import perf_counter
import itertools


class LogicSolver:

    def __init__(self, verbose=False):
        self._verbose = verbose

        # Prepare for the run start by enumerating sets & initial clues
        self._prop_sets = []
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
        new_inferences = gather_all_inferences(self._prop_sets)

        # Step 1: transformations based on comparing pairs of sets (subset-based reduction)
        if len(new_inferences) == 0:  # Only if no discoveries so far
            print('Step 1 (subset-reduction)')
            new_inferences, self._prop_sets = pair_reductions(self._prop_sets)

        # Step 2: adding sets using combining inference rules (under certain conditions)
        if len(new_inferences) == 0:  # Only if no discoveries so far
            print('Step 2 (triple-set combining)')
            new_inferences, self._prop_sets = triplet_reductions(self._prop_sets)

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


"""
PropositionSet: Represents a set of logical propositions. The propositions can be any objects which
can be inserted into a set() and the set may have one of the following types:
- xor: exactly one of the propositions is True
- nor: none of the propositions is True
(The latter, of course, is a degenerate case that is mostly only useful internally.)
"""


class PropositionSet:
    def __init__(self, input_set, settype='xor'):
        self._type = settype
        self._set = input_set

    def __str__(self):
        return 'PropositionSet(type=' + self._type + ', ' + str(self._set) + ')'

    def __repr__(self):
        return str(self)

    """ 
        apply_information: transforms this set's contents to conform to the new information that a
        certain proposition has a given truth value
    """
    def apply_information(self, proposition, truth_value):
        if proposition in self._set:

            # XOR set actions
            if self._type == 'xor':
                if truth_value:
                    # One of our things is True, therefore the rest aren't
                    self._set.remove(proposition)
                    self._type = 'nor'
                else:
                    # One of our things is false: big deal
                    self._set.remove(proposition)

            # NOR set actions
            elif self._type == 'nor':
                if truth_value:
                    # This shouldn't be possible
                    # TODO: return some kinda contradiction object here
                    print('Contradiction reached: caller claims that object', proposition, 'in a NOR set is True!')
                else:
                    # One of our things is false: tell me about it
                    self._set.remove(proposition)

            else:
                print('Somehow a PropositionSet has invalid type', self._type, 'in apply_information!')

    """
        get_inferences: acquire a dictionary of the form {prop: truth_value, prop2: truth_value2 ... } describing any
        inferences that can be made from this set. This action removes the items used to make these inferences from the
        set.
    """
    def get_inferences(self):
        inferences = {}

        # XOR set inferences
        if self._type == 'xor':
            # If there's one thing left, it's True. If not, we have no idea.
            if len(self._set) == 1:
                last_prop = list(self._set)[0]
                inferences[last_prop] = True
                self._set.remove(last_prop)

        # NOR set inferences
        elif self._type == 'nor':
            # Everything is False, obviously
            for prop in self._set:
                inferences[prop] = False
            self._set.clear()

        return inferences

    """
        perform_subsetting_ops: modify this set or the other provided by argument, if one is a subset of the other.
        For example, if they're both XOR sets, and the other one's a subset of this, kill the elements of this one that
        they share (the remainder are now in a NOR relationship).
    """
    def perform_subsetting_ops(self, other):
        if self == other:
            return  # Nothing to do here, or the other way either
        if self._type == 'xor' and other.type() == 'xor':

            intersection = set.intersection(self._set, other.set())

            if len(intersection) == len(self.set()):
                # self is a (possibly improper) subset of other (other can be modified)
                #assert (self.set() <= other.set())
                other._set -= self._set
                other._type = 'nor'
            elif len(intersection) == len(other.set()):
                # other is a (proper) subset of self (self can be modified)
                #assert (self.set() > other.set())
                self._set -= other.set()
                self._type = 'nor'

    """
        still_has_info: provides a bool describing whether this set is no longer of use and may be terminated without
        loss of information.
    """
    def still_has_info(self):
        return len(self._set) > 0

    # Exposing this class's members to make external work easier

    def set(self):
        return self._set

    def type(self):
        return self._type


def pair_reductions(propsets):
    # subset-based reductions of XOR sets
    t_start = perf_counter()

    # Only XOR sets can benefit from this
    xor_sets = [s for s in propsets if s.type() == 'xor']
    for s1, s2 in itertools.combinations(xor_sets, 2):
        s1.perform_subsetting_ops(s2)
    # for s1 in xor_sets:
    #     for s2 in xor_sets:
    #         s1.perform_subsetting_ops(s2)

    t_elapsed = perf_counter() - t_start
    print('Pair redux of', len(propsets), 'in', t_elapsed)

    # Can we make any new inferences from this?
    new_inferences = gather_all_inferences(propsets)

    return new_inferences, propsets


def triplet_reductions(propsets):
    """
        A theorem on XOR sets: if we have two disjoint XOR sets A and C such that all elements of another set B are
        in one or the other (but certainly not in both), then we can legitimately form a new XOR set consisting of
        the elements in the union of A and C that are not in B, without changing the solution of the overall
        problem.
        We can take advantage of this by searching for groups of three sets that match this description and using
        them to spawn additional sets. This is equivalent to some kinds of advanced reasoning used by humans in
        Sudoku.
        Result = (A union C) - B = (A-B) union (C-D)
    """

    # TODO: time this operation, and make it more efficient

    new_sets = []

    # Only XOR sets can benefit from this
    xor_sets = [s for s in propsets if s.type() == 'xor']

    # t_start = perf_counter()
    # for outer_loop_iter, s1 in enumerate(xor_sets):
    #     # print('Starting step 2 outer iteration #{}'.format(outer_loop_iter))
    #     # s1 is our A
    #     set_a = s1.set()
    #
    #     # B must have overlap with A
    #     possible_bs = [b for b in xor_sets if not b.set().isdisjoint(set_a)]
    #     for s2 in possible_bs:
    #         # s2 is our B
    #         if set_a == s2.set():
    #             continue  # No point
    #         set_b = s2.set()
    #
    #         # C must overlap with B and not with A
    #         possible_cs = [c for c in xor_sets if ((not c.set().isdisjoint(set_b)) and c.set().isdisjoint(set_a))]
    #         for s3 in possible_cs:
    #             if s3.set() == set_a or s3.set() == set_b:
    #                 continue  # No point
    #             # s3 is our C
    #             set_c = s3.set()
    #             # C must contain all elements of B that A doesn't, and not intersect with A
    #             s3_must_include = set_b - set_a
    #             s3_must_not_include = set_a
    #             if len(s3_must_include - set_c) == 0 and len(s3_must_not_include & set_c) == 0:
    #                 # s1, s2, s3 are indeed suitable as A, B, C! Build our new set.
    #                 new_set = (
    #                           set_a | set_c) - set_b  # Everything in the side ones but not the middle one
    #                 new_sets.append(PropositionSet(new_set))

    t_start = perf_counter()
    for outer_loop_iter, s1 in enumerate(xor_sets):
        # print('Starting step 2 outer iteration #{}'.format(outer_loop_iter))
        # s1 is our A
        set_a = s1.set()

        # B must have overlap with A
        possible_bs = [b for b in xor_sets if not b.set().isdisjoint(set_a)]
        for s2 in possible_bs:
            # s2 is our B
            if set_a == s2.set():
                continue  # No point
            set_b = s2.set()

            # C must overlap with B and not with A
            possible_cs = [c for c in xor_sets if ((not c.set().isdisjoint(set_b)) and c.set().isdisjoint(set_a))]
            for s3 in possible_cs:
                if s3.set() == set_a or s3.set() == set_b:
                    continue  # No point
                # s3 is our C
                set_c = s3.set()
                # C must contain all elements of B that A doesn't, and not intersect with A
                s3_must_include = set_b - set_a
                s3_must_not_include = set_a
                if len(s3_must_include - set_c) == 0 and len(s3_must_not_include & set_c) == 0:
                    # s1, s2, s3 are indeed suitable as A, B, C! Build our new set.
                    new_set = PropositionSet((set_a | set_c) - set_b)  # Everything in the side ones but not the middle one

                    # To ease this process later, let's take care of subsettedness stuff relative to other sets we know of
                    for existing_set in xor_sets:
                        existing_set.perform_subsetting_ops(new_set)

                    new_sets.append(new_set)

    propsets_extended = propsets + new_sets

    t_elapsed = perf_counter() - t_start
    print('Triplet redux of', len(propsets), 'in', t_elapsed)

    # Can we make any new inferences from this?
    new_inferences = gather_all_inferences(propsets_extended)

    return new_inferences, propsets_extended


# Aux functions: inference gathering


def gather_all_inferences(prop_sets):
    inferences = {}
    for s in prop_sets:
        this_set_knowledge = s.get_inferences()
        # TODO: this would be a good time to check whether anything here contradicts previous knowledge
        inferences.update(this_set_knowledge)
    return inferences
