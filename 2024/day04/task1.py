#!/usr/bin/env python3
#
# Day 4, Task 1: https://adventofcode.com/2024/day/4
#
# In today's first task, we're looking for the text "XMAS", which may run
# in any direction (North, North-East, East, South-East, South, South-West,
# West, North-West). There may be many of these, and any given location may
# contain many of these.
#
# To do this, we'll be iterating through each row and column in the input
# and ask for an XMAS count starting at that position.
#
# That XMAS counter function (count_xmas) will compute the row/column deltas
# to search and just scan in that direction. We need to avoid running out of
# bounds, but otherwise this is pretty straight-forward.


def count_xmas(
    *,
    lines: list[str],
    x: int,
    y: int,
    width: int,
    height: int,
) -> int:
    if lines[y][x] != 'X':
        # Nothing to find here.
        return 0

    count: int = 0

    # Set up our deltas for the directions we'll be scanning.
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                # We won't be moving, so skip it.
                continue

            # Scan until we determine we won't find at a location. We'll
            # be iterating through each letter we want to find in order,
            # navigating in that direction. If we run out of bounds or we
            # see any other character, we fail this.
            found = True

            for i, expected_c in enumerate('MAS', start=1):
                pos_x = x + (i * dx)
                pos_y = y + (i * dy)

                if (not (0 <= pos_x < width) or
                    not (0 <= pos_y < height) or
                    lines[pos_y][pos_x] != expected_c):
                    # We won't find it here, so skip.
                    found = False
                    break

            if found:
                count += 1

    return count


def find_all_xmas(
    filename: str,
) -> int:
    global board
    answer: int = 0

    with open(filename, 'r') as fp:
        lines = fp.readlines()

    width = len(lines[0])
    height = len(lines)

    # Go through each row, and then each character in the row, and count the
    # number of XMAS strings.
    for y, line in enumerate(lines):
        for x in range(len(line)):
            answer += count_xmas(lines=lines,
                                 x=x,
                                 y=y,
                                 width=width,
                                 height=height)

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = find_all_xmas('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = find_all_xmas('input')
    print(f'Task answer: {answer}')
