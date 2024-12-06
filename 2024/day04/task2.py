#!/usr/bin/env python3
#
# Day 4, Task 2: https://adventofcode.com/2024/day/4
#
# Task 2 is a bit different from task 1. Instead of looking for XMAS strings,
# we're looking for a pair of "MAS" strings forming an "X" shape. These
# strings can be in either direciton.
#
# We'll be scanning looking for this. Instead of starting with an "X", we'll
# start with an "A" (the middle of a "MAS"). We then start looking at the
# corners adjacent to that, looking for an "M" and a "S". If we find 2 of
# these, then we found it!

def has_xmas(
    *,
    lines: list[str],
    x: int,
    y: int,
    width: int,
    height: int,
) -> bool:
    if lines[y][x] != 'A':
        # Nothing to find here.
        return False

    count: int = 0

    # We can inline all the corners we want to check. If we find "M" and "S"
    # at opposing corners, we have a "MAS"!
    for pos_x1, pos_y1, pos_x2, pos_y2 in ((x - 1, y - 1, x + 1, y + 1),
                                           (x + 1, y - 1, x - 1, y + 1),
                                           (x - 1, y + 1, x + 1, y - 1),
                                           (x + 1, y + 1, x - 1, y - 1)):
        if (0 <= pos_x1 < width and
            0 <= pos_x2 < width and
            0 <= pos_y1 < height and
            0 <= pos_y2 < height and
            lines[pos_y1][pos_x1] == 'M' and
            lines[pos_y2][pos_x2] == 'S'):
            # We found a "MAS"!
            count += 1

        if count == 2:
            return True

    return False


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
    # number of X-shaped MAS string pairs.
    for y, line in enumerate(lines):
        for x in range(len(line)):
            if has_xmas(lines=lines,
                        x=x,
                        y=y,
                        width=width,
                        height=height):
                answer += 1

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = find_all_xmas('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = find_all_xmas('input')
    print(f'Task answer: {answer}')
