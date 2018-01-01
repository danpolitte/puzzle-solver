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
        return 'PropoisitionSet(type=' + self._type + ', ' + str(self._set) + ')'

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
            return # Nothing to do here, or the other way either
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
