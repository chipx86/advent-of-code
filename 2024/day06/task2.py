#!/usr/bin/env python3
#
# Day 6, Task 2: https://adventofcode.com/2024/day/6
#
# In task 2, our goal is to get the guard stuck in an infinite loop by
# putting an obstruction *somewhere*.
#
# But that's not all. We don't just need to find a place to do this. We need
# to find EVERY place to do this!
#
# There's probably a brilliant way of doing this. I thought I had one, but
# it was flawed. So we're going with this:
#
# 1. For each position, place an obstruction in the way and re-walk from the
#    start.
#
# 2. Check if we loop in that simulation by tracking where we've been and
#    seeing if we hit a position + direction twice. That's a loop.
#
# 3. Record any unique obstructions that result in a loop, and use the total
#    as our answer.

from typing import Iterator, Optional


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


def walk_guard(
    *,
    start_x: int,
    start_y: int,
    dx: int,
    dy: int,
    width: int,
    height: int,
    obstacles: set[tuple[int, int]],
    obstruction: Optional[tuple[int, int]] = None,
) -> Iterator[tuple[int, int, int, int]]:
    pos_x = start_x
    pos_y = start_y

    # Keep walking until we break out of this by walking off the grid.
    while (0 <= pos_x < width and
           0 <= pos_y < height):
        yield pos_x, pos_y, dx, dy

        new_pos = (pos_x + dx,
                   pos_y + dy)

        if new_pos == obstruction or new_pos in obstacles:
            # We'd hit an obstacle. Turn right 90 degrees.
            dx, dy = rotate_right(dx, dy)
        else:
            pos_x, pos_y = new_pos


def does_path_loop(
    *,
    start_x: int,
    start_y: int,
    dx: int,
    dy: int,
    **kwargs,
) -> bool:
    seen: set[tuple[int, int, int, int]] = set()

    for pos_info in walk_guard(start_x=start_x,
                               start_y=start_y,
                               dx=dx,
                               dy=dy,
                               **kwargs):
        if pos_info in seen:
            # We looped!
            return True

        seen.add(pos_info)

    return False


def count_movement_positions(
    filename: str,
) -> int:
    obstacles: set[tuple[int, int]] = set()
    width: int = -1
    height: int = -1
    start_x: int = -1
    start_y: int = -1
    start_dx = 0
    start_dy = -1

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
                        start_x = x
                        start_y = y

        width = x + 1
        height = y + 1

    # We now know everything we need to about the board. Start walking.
    new_obstructions = set[tuple[int, int]]()

    for pos_x, pos_y, dx, dy in walk_guard(start_x=start_x,
                                           start_y=start_y,
                                           dx=start_dx,
                                           dy=start_dy,
                                           width=width,
                                           height=height,
                                           obstacles=obstacles):
        obstruction_pos = (pos_x + dx,
                           pos_y + dy)

        if (obstruction_pos not in obstacles and
            obstruction_pos not in new_obstructions):
            # We haven't tried placing an obstruction here. If we do, do we
            # loop infinitely?
            if does_path_loop(start_x=start_x,
                              start_y=start_y,
                              dx=start_dx,
                              dy=start_dy,
                              width=width,
                              height=height,
                              obstacles=obstacles,
                              obstruction=obstruction_pos):
                # This loops! Let's mark it.
                new_obstructions.add(obstruction_pos)

    return len(new_obstructions)


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = count_movement_positions('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = count_movement_positions('input')
    print(f'Task answer: {answer}')
