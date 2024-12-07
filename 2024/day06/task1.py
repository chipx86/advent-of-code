#!/usr/bin/env python3
#
# Day 6, Task 1: https://adventofcode.com/2024/day/6
#
# In this task, we're walking a guard around a 2D grid with scattered
# obstacles. We're starting at a position, walking until we hit something,
# turning 90 degrees, and continuing on until we walk off the board.
# The answer is the number of distinct positions we hit.
#
# This is pretty trivial. We only need to know the starting position, the
# positions of each obstacle, the dimensions of the board, and the deltas
# for movement. We don't want to store the entire board, since that's a
# waste of memory -- we don't need data on empty spaces!
#
# We'll just loop until we're off the board, checking our obstacles set and
# otherwise updating positions. Every time we loop, we add the current
# position to our set (duplicates are weeded out automatically), and the
# length of that set is our answer.


def rotate_right(
    dx: int,
    dy: int,
) -> tuple[int, int]:
    if dx == 0:
        # We're going up or down. Go left or right.
        return -dy, 0
    else:
        # We're going left or right. Go up or down.
        return 0, dx


def count_movement_positions(
    filename: str,
) -> int:
    obstacles: set[tuple[int, int]] = set()
    width: int = -1
    height: int = -1
    pos_x: int = -1
    pos_y: int = -1

    OBSTACLE = ord(b'#')
    PLAYER = ord(b'^')
    SPACE = ord(b'.')

    # Read the board, looking for the starting position and any obstacles.
    # We won't load every byte of the board, since we don't care about the
    # empty spaces.
    with open(filename, 'rb') as fp:
        x = -1
        y = -1

        for y, line in enumerate(fp.readlines()):
            for x, c in enumerate(line):
                # Most will be a ".", so check that first.
                if c != SPACE:
                    if c == OBSTACLE:
                        obstacles.add((x, y))
                    elif c == PLAYER:
                        pos_x = x
                        pos_y = y

        width = x + 1
        height = y + 1

    # We now know everything we need to about the board. Start walking.
    positions: set[tuple[int, int]] = set()
    dx: int = 0
    dy: int = -1

    # Keep walking until we break out of this by walking off the grid.
    while (0 <= pos_x < width and
           0 <= pos_y < height):
        positions.add((pos_x, pos_y))
        new_x = pos_x + dx
        new_y = pos_y + dy

        if (new_x, new_y) in obstacles:
            # We'd hit an obstacle. Turn right 90 degrees.
            dx, dy = rotate_right(dx, dy)
        else:
            # We walked! Record the position in our set of distinct positions.
            pos_x = new_x
            pos_y = new_y

    return len(positions)


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = count_movement_positions('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = count_movement_positions('input')
    print(f'Task answer: {answer}')
