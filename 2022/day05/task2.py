#!/usr/bin/env python3
#
# NOTE: I originally hard-coded the crates, but that felt too easy. So now
#       I parse them from the input. And I don't assume number of stacks.
#       Why not.
#
# This is similar to task1.py, with the exception that we can now move multiple
# crates at a time.
#
# For this task, we have stacks of crates, and instructions for moving those
# crates. The crates must be moved one-by-one from a stack. Almost a Towers of
# Hanoi sort of thing. So, moving [1][2][3] one-by-one would get us [3][2][1].
#
# Like my other tasks, I aim to keep performance high. I do need to keep track
# of all the stacks, but I process move instructions one-by-one.
#
# First, I parse out the initial stack configuration. I use a regex for this,
# which can match cargo or a blank area where cargo would be. I then just
# iterate through the results, inserting the cargo at the start of each stack.
#
# Once I'm in the move processing phase, I use another regex to parse out the
# move instruction. Then I just need to handle the move.
#
# The logic for this part is similar to task1.py, except I don't need to
# reverse the crates I'm extracting. I just extract them as-is and put them
# in the destination.
#
# That makes this code effectively identical to task1.py, minus a reverse().

import re


MOVE_RE = re.compile(r'^move (\d+) from (\d+) to (\d+)')
CRATES_RE = re.compile(r'(?:\[(?P<cargo>[A-Z])\]|   ) ?')


# Index 0 in a stack is the bottom-most item.
stacks = []

# Whether we're in the setup phase, parsing the initial stacks.
in_setup = True


with open('input', 'r') as fp:
    for line in fp.readlines():
        if in_setup:
            # Load in crate data.
            if line.lstrip().startswith('1 '):
                # We've reached the numbers row. We're done with setup.
                in_setup = False
            else:
                cargo_items = CRATES_RE.findall(line)

                if not stacks:
                    stacks = [
                        []
                        for i in cargo_items
                    ]

                for i, cargo in enumerate(cargo_items):
                    if cargo:
                        stacks[i].insert(0, cargo)
        else:
            # Process the moves.
            line = line.strip()

            if line:
                m = MOVE_RE.match(line)
                assert m, line

                move_count = int(m.group(1))
                move_from = int(m.group(2)) - 1
                move_to = int(m.group(3)) - 1

                stacks[move_to] += stacks[move_from][-move_count:]
                stacks[move_from] = stacks[move_from][:-move_count]


print(''.join(
    stack[-1]
    for stack in stacks
))
