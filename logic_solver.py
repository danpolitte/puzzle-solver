# logic_solver.py: a propositional logic solving system


class LogicSolver:

    def __init__(self, verbose=False):
        self._verbose = verbose

        self._prop_eqns = []
        self._knowledge = {}

    def add_equation(self, proposition_list, eqn_type):
        # Adds an equation: the propositions in proposition_list will be related by the relation _type_ (XOR, OR, etc)
        self._prop_eqns.append(PropositionEqn(set(proposition_list), eqn_type))

    def add_true_propositions(self, proposition_list):
        # Marks all the propositions in the given iterable True in this solver
        self.add_knowledge({i: True for i in proposition_list})

    def add_false_propositions(self, proposition_list):
        # Marks all the propositions in the given iterable False in this solver
        self.add_knowledge({i: False for i in proposition_list})

    def add_knowledge(self, proposition_to_bool_dict):
        # Marks propositions True and False based on values in given dictionary
        # TODO: check for contradiction with previously known things here
        self._knowledge.update(proposition_to_bool_dict)

    def run_iter(self):
        # The magic: run a turn on this solver.
        # Stop after first type of inference that allows new insights. This way, we can avoid the expensive later
        # kinds whenever possible.

        # Step 0: transform/reduce sets from previous info
        print('Step 0 (apply previous discoveries)')
        for datum, knownValue in self._knowledge.items():
            for s in self._prop_eqns:
                s.apply_information(datum, knownValue)

        # Can we make any new inferences from this?
        new_inferences = gather_all_inferences(self._prop_eqns)

        # # Step 1: transformations based on comparing pairs of sets (subset-based reduction)
        # if len(new_inferences) == 0:  # Only if no discoveries so far
        #     print('Step 1 (subset-reduction)')
        #     new_inferences, self._prop_eqns = pair_reductions(self._prop_eqns)
        #
        # # Step 2: adding sets using combining inference rules (under certain conditions)
        # if len(new_inferences) == 0:  # Only if no discoveries so far
        #     print('Step 2 (triple-set combining)')
        #     new_inferences, self._prop_eqns = triplet_reductions(self._prop_eqns)

        # Update things known
        self.add_knowledge(new_inferences)

        # Wrap-up: are there any depleted sets we must clean up?
        self._prop_eqns = [s for s in self._prop_eqns if s.still_has_info()]

        # Done with this iteration

    def get_num_sets(self):
        return len(self._prop_eqns)

    def is_done(self):
        # If this is True, no point to further iterations
        return len(self._prop_eqns) == 0

    def get_knowledge(self):
        # Returns (pos_knowledge, neg_knowledge) tuple of all things we know so far
        pos_knowledge = {k: v for k, v in self._knowledge.items() if v}
        neg_knowledge = {k: v for k, v in self._knowledge.items() if not v}
        return pos_knowledge, neg_knowledge


def gather_all_inferences(prop_eqns):
    inferences = {}
    for s in prop_eqns:
        this_set_knowledge = s.get_inferences()
        # TODO: this would be a good time to check whether any pair of things added here contradict each other
        inferences.update(this_set_knowledge)
    return inferences


"""
PropositionEqn: Represents a set of logical propositions. The propositions can be any objects which
can be inserted into a set() and the set may have one of the following initial types (with n propositions):
- XOR (# true propoositions in [1,1])
- NOR (# true propoositions in [0,0])
- AND (# true propoositions in [n,n])
- OR (# true propoositions in [1,n])
- NAND (# true propoositions in [0,n-1])

"""


class PropositionEqn:
    def __init__(self, input_list, settype='xor'):
        self._set = set(input_list)

        prop_count = len(self._set)

        if settype.lower() == 'xor':
            self._truecount = list(range(1, 1+1))
        elif settype.lower() == 'nor':
            self._truecount = list(range(0, 0+1))
        elif settype.lower() == 'and':
            self._truecount = list(range(prop_count, prop_count + 1))
        elif settype.lower() == 'or':
            self._truecount = list(range(1, prop_count + 1))
        elif settype.lower() == 'nand':
            self._truecount = list(range(0, (prop_count - 1) + 1))
        else:
            print("Invalid PropositionEqn type", settype, "! This will probably fail soon.")

    def __str__(self):
        if self.is_and():
            dominant_type = 'AND'
        elif self.is_nor():
            dominant_type = 'NOR'
        elif self.is_xor():
            dominant_type = 'XOR'
        elif self.is_or():
            dominant_type = 'OR'
        elif self.is_nand():
            dominant_type = 'NAND'
        else:
            dominant_type = None

        numtrue_string = dominant_type if dominant_type \
            else 'numtrue={}'.format(','.join(str(item) for item in self._truecount))

        return 'PropositionEqn(count={},{}: {})'\
            .format(len(self._set), numtrue_string, str(self._set))

    def __repr__(self):
        return str(self)

    # Functions to determine what basic types apply to this eqn. (Multiple might apply)

    def is_xor(self):
        return len(self._truecount) == 1 and self._truecount[0] == 1

    def is_nor(self):
        return len(self._truecount) == 1 and self._truecount[0] == 0

    def is_and(self):
        prop_count = len(self._set)
        return len(self._truecount) == 1 and self._truecount[0] == prop_count

    def is_or(self):
        prop_count = len(self._set)
        our_counts = set(self._truecount)
        true_or_counts = set(range(1, prop_count+1))
        return our_counts == true_or_counts

    def is_nand(self):
        prop_count = len(self._set)
        our_counts = set(self._truecount)
        true_nand_counts = set(range(0, (prop_count-1)+1))
        return our_counts == true_nand_counts

    """ 
        apply_information: transforms this equation's contents to conform to the new information that a
        certain proposition has a given truth value
    """
    def apply_information(self, proposition, truth_value):
        if proposition in self._set:

            self._set.remove(proposition)

            # Update possible numbers of true propositions left
            if truth_value:  # proposition was true
                # Subtract one from everything
                self._truecount = [i-1 for i in self._truecount]
            # If the proposition was false, counts remain the same

            # Restrict to range [0, n], the only values that make sense
            prop_count = len(self._set)
            self._truecount = list(filter(lambda c: 0 <= c <= prop_count, self._truecount))

            # Check validity of possible numbers of true propositions left

            if len(self._truecount) == 0:
                print('apply_information: contradiction reached!')
                # TODO: account for this gracefully

    """
        get_inferences: acquire a dictionary of the form {prop: truth_value, prop2: truth_value2 ... } describing any
        inferences that can be made from this set. This action removes the items used to make these inferences from the
        set.
    """
    def get_inferences(self):
        inferences = {}

        # If the set has collapsed to either an AND set or a NOR set, we can infer the values of everything left

        if self.is_and():
            for prop in self._set:
                inferences[prop] = True
            self._set.clear()
        elif self.is_nor():
            # Everything is False, obviously
            for prop in self._set:
                inferences[prop] = False
            self._set.clear()

        return inferences

    """
        still_has_info: provides a bool describing whether this set is no longer of use and may be terminated without
        loss of information.
    """
    def still_has_info(self):
        return len(self._set) > 0

    # Exposing this class's members to make external work easier

    def set(self):
        return self._set


def main():
    # For testing
    s = LogicSolver()
    s.add_equation(['p0', 'p1'], 'xor')
    s.add_equation(['q0', 'q1'], 'xor')
    s.add_equation(['p0', 'q1'], 'or')
    s.add_true_propositions(['p1'])

    for i in range(7):
        print()
        print(i)
        print(s._knowledge)
        print(s._prop_eqns)

        s.run_iter()

        if s.is_done():
            print('Done!')
            break


if __name__ == "__main__":
    main()
