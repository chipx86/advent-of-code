#!/usr/bin/env python3
#
# Day 8, Task 1: https://adventofcode.com/2024/day/8
#
# This task is about finding 2 or more antennas of the same type on a 2D
# grid and then creating "antinodes" on either side of each pair, based on
# the distance between them.
#
# This is actually pretty straight-forward:
#
# 1. Assemble a list of all X, Y positions for all antennas of a given type.
#
# 2. Calculate each permutation of positions. For 3 pairs, we'd want to
#    consider A1,A2; A2,A1; A1,A3; A3,A1; A2,A3; A3,A2.
#
# 3. For each pair, calculate the distance between each, then create an
#    antinode at the first position in the pair minus the delta (as long as
#    this is within the bounds of the map).

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
            antinode_pos = (pos1_x - dx, pos1_y - dy)

            if (0 <= antinode_pos[0] < width and
                0 <= antinode_pos[1] < height):
                antinodes.add(antinode_pos)

    return len(antinodes)


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_antinode_locations('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = calc_antinode_locations('input')
    print(f'Task answer: {answer}')
