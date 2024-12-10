#!/usr/bin/env python3
#
# Day 8, Task 2: https://adventofcode.com/2024/day/8
#
# In Task 2, we're doing roughly the same thing as Task 1, but we're also
# going to repeat the antinodes along the path, equally-spaced.
#
# Same approach as in Task 1, but we just repeat until we're out of bounds,
# continuously offsetting by the delta.
#
# I honestly spent far more time trying to understand the task description
# than figuring out the solution. The wording was not clear to me at the
# time. Ah well.

from collections import defaultdict
from itertools import permutations


def calc_antinode_locations(
    filename: str,
) -> int:
    antennas = defaultdict[int, list[tuple[int, int]]](list)
    antinodes = set[tuple[int, int]]()

    BLANK = ord(b'.')

    x = -1
    y = -1

    with open(filename, 'rb') as fp:
        for y, line in enumerate(fp):
            for x, c in enumerate(line.rstrip()):
                if c != BLANK:
                    pos = (x, y)
                    antennas[c].append(pos)

    width = x + 1
    height = y + 1

    for antenna_type, locations in antennas.items():
        for (pos1_x, pos1_y), (pos2_x, pos2_y) in permutations(locations, r=2):
            dx = pos2_x - pos1_x
            dy = pos2_y - pos1_y

            antinodes.add((pos1_x, pos1_y))

            antinode_x = pos1_x - dx
            antinode_y = pos1_y - dy

            while (0 <= antinode_x < width and
                   0 <= antinode_y < height):
                antinodes.add((antinode_x, antinode_y))
                antinode_x = antinode_x - dx
                antinode_y = antinode_y - dy

    return len(antinodes)


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_antinode_locations('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = calc_antinode_locations('input')
    print(f'Task answer: {answer}')
