#!/usr/bin/env python3
#
# In this task, we need to go through a move list to help move a snake. Well,
# a rope. I'm calling it a snake. Deal with it. Don't make me add food for it
# to navigate and eat.
#
# The input shows the move direction and the number of steps to make. We'll be
# processing each step one-by-one for the whole *snake*.
#
# The plan of attack is to track the tail and head positions, update the head
# based on the move direction, and then update the tail appropriately.
#
# For the tail, we just compute a relative offset from the head. For both X
# and Y, we determine if:
#
# 1) Both the head and tail have the same value (giving us a delta of 0)
# 2) If the head is above the tail (delta = -1)
# 3) If the head is below the tail (delta = 1)
#
# These deltas are added to the tail's position. If the tail doesn't overlap
# the head, we set it as the new position and add the position to the visited
# set. Since this is a set, it will filter out duplicates.
#
# The relative position calculations are generic. They don't assume X and Y.
# We could add more dimensions if we wanted to. This would allow for 3D snake,
# or 4D snake, or 10D snake.
#
# Otherwise, pretty straight-forward. This task only has to track the head
# and tail, but task2.py will track arbitrary segment lengths. The code in
# task2.py could be used here, but this provides a nice, simpler way to
# understand that code.
#
# Performance-wise, very little needs to be tracked. Just coordinates of the
# head and tail, and each move line as it comes in. This could scale to any
# grid size, any number of instructions.

import re


MOVE_RE = re.compile(r'^(?P<direction>[UDLR]) (?P<move_count>\d+)$')


HEAD_MOVE_DELTAS = {
    'U': (0, -1),
    'D': (0, 1),
    'L': (-1, 0),
    'R': (1, 0),
}


head = (0, 0)
tail = (0, 0)


# Set the initial visiting position to the starting position.
visited_positions = {tail}


with open('input', 'r') as fp:
    for line in fp.readlines():
        m = MOVE_RE.match(line.rstrip())
        assert m

        direction = m.group('direction')
        move_count = int(m.group('move_count'))

        for move_i in range(move_count):
            # We'll start off by updating the head's position, based on the
            # delta for the move.
            head_delta = HEAD_MOVE_DELTAS[direction]
            head = (head[0] + head_delta[0],
                    head[1] + head_delta[1])

            # Figure out a relative directions between the head and the tail.
            # We'll use this to figure out which move needs to be made.
            #
            # We'll loop over the coordinates, just to reduce the amount of
            # code needed here. Also super useful for 5D snake! When's that
            # puzzle?
            rel = [0, 0]

            for rel_i, (prev_val, val) in enumerate(zip(head, tail)):
                if prev_val < val:
                    rel[rel_i] = -1
                elif prev_val > val:
                    rel[rel_i] = 1

            # Now that we have the relative move, build the new tail position.
            # If it doesn't overlap with the head, we we can set it.
            new_tail = (tail[0] + rel[0],
                        tail[1] + rel[1])

            if new_tail != head:
                tail = new_tail

                # Add the tail's position to the set of visited positions.
                # Since this is a set, we don't have to worry about duplicate
                # positions.
                visited_positions.add(tail)


print(f'Number of positions visited by the tail = {len(visited_positions)}')
