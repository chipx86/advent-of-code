#!/usr/bin/env python3
#
# NOTE: I originally hard-coded the crates, but that felt too easy. So now
#       I parse them from the input. And I don't assume number of stacks.
#       Why not.

import re


MOVE_RE = re.compile(r'^move (\d+) from (\d+) to (\d+)')
CRATES_RE = re.compile(r'(?:\[(?P<cargo>[A-Z])\]|   ) ?')

stacks = []
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
                # Process the moves.
                m = MOVE_RE.match(line)
                assert m

                move_count = int(m.group(1))
                move_from = int(m.group(2)) - 1
                move_to = int(m.group(3)) - 1

                stacks[move_to] += reversed(stacks[move_from][-move_count:])
                stacks[move_from] = stacks[move_from][:-move_count]


print(''.join(
    stack[-1]
    for stack in stacks
))
