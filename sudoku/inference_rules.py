from PropositionSet import PropositionSet
from time import perf_counter
import itertools

# Inference_rules: functions for implementation of Sudoku logic_solver.
# All functions are of form (propsets) -> (inferences, propsets')
# (These functions guarantee that the input propsets won't be changed)


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
    print('Pair redux of',len(propsets),'in',t_elapsed)

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










