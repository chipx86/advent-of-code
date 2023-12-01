#!/usr/bin/env python3
#
# https://adventofcode.com/2023/day/1#part2
#
# Oh no, some of those numbers are spelled out as words! Well, fish sticks.
#
# We'll need to rethink our ENTIRE APPROACH! Good job, elves. Can't find good
# help these days.. *mumble*
#
# So in this task, we need to consider not only 0..9, but also 'one', 'two',
# 'three', 'four', 'five', 'six', 'seven', 'eight', and 'nine.'
#
# But not 'zero', 'eleventy', or 'infinity-squared'. Phew.
#
# Let's think about some approaches:
#
# 1. We could go through the string and do a search-and-replace for each of
#    these.
#
#    Oof, but this is slow. Why search-and-replace strings that aren't even
#    there?
#
# 2. We could pre-process the ENTIRE file at once!
#
#    Except this is really the same problem as #1. We'd just be changing
#    things across the whole file several times. Non-starter.
#
# 2. We could scan as we go, see if we're matching a spelling, and then
#    storing as a number when matched.
#
#    This is the approach I choose to take, because it's kind of interesting,
#    and should be fast.
#
#    We're going to do this with a little Trie (a prefix tree).

def trie_approach():
    # Our trie needs are simple, but we do need two of them: One for
    # forward-search, one for reverse. This is just to let us more easily
    # walk backwards in each string.
    #
    # Each node will be assigned a tuple of (is_leaf, value):
    #
    #     If is_leaf is True, the value is the number we want.
    #
    #     If is_leaf is False, the value is the next node in the tree.
    #
    # This will look like:
    #
    #     'o': (False, {
    #         'n': (False, {
    #             'e': (True, '1'),
    #         }),
    #     }),
    #     ...
    #
    # We could just assign dicts or ints and use isinstance checks for each
    # value, but that's less efficient.
    #
    # NOTE: We know that none of these words contain another word as a subset,
    #       which lets us simplify things a bit. We're just going to assume
    #       the leaf is always a valid number.
    #
    #       If this wasn't the case, we'd assume a different approach (we could
    #       avoid storing values and use a separate dictionary to map the words
    #       to values, for instance, but then we'd also have to look back to
    #       avoid a greedy match).
    #
    #       I'm choosing to go this route I described above, given the
    #       constraints of this task.
    forward_trie = {}
    reverse_trie = {}

    # To build this, we'll first iterate through all supported words and their
    # numeric values.
    for i, word in enumerate(('one', 'two', 'three', 'four', 'five',
                              'six', 'seven', 'eight', 'nine'),
                             start=1):
        # Then, we'll build the forward and reverse tries. The logic is the
        # same for both, but we'll reverse the string for the revers trie.
        for trie, chars in ((forward_trie, word),
                            (reverse_trie, word[::-1])):
            # Build parent nodes for all but the last character.
            for c in chars[:-1]:
                is_leaf, trie = trie.setdefault(c, (False, {}))
                assert not is_leaf

            # And then build the leaf for the last character.
            trie.setdefault(chars[-1], (True, str(i)))

    # Let's define a function that can scan for digits or completed words,
    # based on our trie trees.
    def find_number(chars, trie):
        node = trie
        match_len = 0
        i = 0

        while i < len(chars):
            c = chars[i]
            i += 1

            if '0' <= c <= '9':
                # We found a 0..9 match.
                return c

            # We're going to look into the trie, based on this character and
            # where we may already be in the trie.
            try:
                is_leaf, node = node[c]
            except KeyError:
                # There's nothing on this level. We now need to consider
                # the following:
                #
                # 1. Have we matched anything at all yet?
                #
                # 2. Are we in the wrong subset of a word? E.g., we have the
                #    string "neveno" (this is reversed) and were considering
                #    "neves' ("seven") but wanted "eno" ("one").
                #
                #    In this case, we need to try more combinations. We can
                #    discard the first captured character and re-walk.
                #
                # 3. How far up the tree do we need to go?
                #
                # This is pretty simple, really. If we've matched something,
                # clear away the first character and then backtrack to try
                # again, starting at the top of the trie.
                #
                # If we haven't matched anything, we'll just move on to the
                # next character as normal.
                if match_len > 0:
                    i -= match_len
                    match_len = 0
                    node = trie

                continue

            # If we're here, we ventured deeper into the trie. We'll now check
            # whether we're at a leaf or a parent node somewhere.
            if is_leaf:
                # We found a completed word. We're done! We can return its
                # value.
                return node

            match_len += 1

        # We found... nothing? Logic error or test input error.
        assert False, f'No match in "{chars}". Fix your code!'

    # We can now start processing lines.
    total = 0

    with open('input', 'r') as fp:
        for line in fp:
            digit1 = find_number(line, trie=forward_trie)
            digit2 = find_number(line[::-1], trie=reverse_trie)

            total += int(digit1 + digit2)

    return total


total = trie_approach()
print(f'Answer = {total}')
