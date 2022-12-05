#!/usr/bin/env python3

import re


stacks = [
    ['T', 'D', 'W', 'Z', 'V', 'P'],
    ['L', 'S', 'W', 'V', 'F', 'J', 'D'],
    ['Z', 'M', 'L', 'S', 'V', 'T', 'B', 'H'],
    ['R', 'S', 'J'],
    ['C', 'Z', 'B', 'G', 'F', 'M', 'L', 'W'],
    ['Q', 'W', 'V', 'H', 'Z', 'R', 'G', 'B'],
    ['V', 'J', 'P', 'C', 'B', 'D', 'N'],
    ['P', 'T', 'B', 'Q'],
    ['H', 'G', 'Z', 'R', 'C'],
]


MOVE_RE = re.compile(r'^move (\d+) from (\d+) to (\d+)')


with open('input', 'r') as fp:
    for line in fp.readlines():
        m = MOVE_RE.match(line)
        assert m

        move_count = int(m.group(1))
        move_from = int(m.group(2)) - 1
        move_to = int(m.group(3)) - 1

        stacks[move_to] += stacks[move_from][-move_count:]
        stacks[move_from] = stacks[move_from][:-move_count]


print(''.join(
    crate[-1]
    for crate in stacks
))
