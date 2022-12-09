#!/usr/bin/env python3
#
# In this task, we need to go through a move list to help move a snake. Well,
# a rope. I'm calling it a snake. Deal with it. Don't make me add food for it
# to navigate and eat.
#
# The input shows the move direction and the number of steps to make. We'll be
# processing each step one-by-one for the whole *snake*.
#
# The plan of attack is to track coordinates for each segment of the snake,
# updating the head based on the move direction, and then going through each
# segment up through the tail and calculating new positions based on the
# previous segment.
#
# For each non-head segment, we just compute a relative offset from the
# previous segment. For both X and Y, we determine if:
#
# 1) Both the previous segment and current segment have the same value
#    (giving us a delta of 0)
# 2) If the previous segment is above the current segment (delta = -1)
# 3) If the previous segment is below the current segment (delta = 1)
#
# These deltas are added to the segment. If the segment doesn't overlap the
# the previous segment, we set it as the new position.
#
# When we're done with all the segments, we add the tail position to the
# visisted set. This happens even if the tail does not move. It's a no-op in
# this case, since we're using a set, and that will filter duplicates.
#
# The relative position calculations are generic. They don't assume X and Y.
# We could add more dimensions if we wanted to. This would allow for 3D snake,
# or 4D snake, or 10D snake.
#
# This isn't much more complicated than task1.py. It just doesn't hard-code the
# head and tail. It does process the head specially, but every other segment
# is simply part of a loop.
#
# Performance-wise, very little needs to be tracked. Just coordinates of each
# segment, and each move line as it comes in. This could scale to any grid
# size, any number of instructions, and number of segments.

import re


MOVE_RE = re.compile(r'^(?P<direction>[UDLR]) (?P<move_count>\d+)$')

NUM_PARTS = 10

HEAD_MOVE_DELTAS = {
    'U': (0, -1),
    'D': (0, 1),
    'L': (-1, 0),
    'R': (1, 0),
}


# The segments of the snake start at the head and end at the tail.
segments = [
    (0, 0)
    for i in range(NUM_PARTS)
]

# Set the initial visiting position to the starting position.
visited_positions = {segments[0]}


with open('input', 'r') as fp:
    for line in fp.readlines():
        m = MOVE_RE.match(line.rstrip())
        assert m

        direction = m.group('direction')
        move_count = int(m.group('move_count'))

        for move_i in range(move_count):
            # We'll start off by updating the head's position, based on the
            # delta for the move.
            rel = HEAD_MOVE_DELTAS[direction]
            head = segments[0]
            segments[0] = (head[0] + rel[0],
                           head[1] + rel[1])

            # Now we'll process each segment of the snake, from right after
            # the head through to the tail. Each segment will be updated
            # relative to the previous segment's position.
            for segment_i, segment in enumerate(segments[1:], start=1):
                prev_segment = segments[segment_i - 1]

                # Figure out a relative directions between the previous
                # segment and the current segment. We'll use this to figure out
                # which move needs to be made.
                #
                # We'll loop over the coordinates, just to reduce the amount
                # of code needed here. Also super useful for 5D snake! When's
                # that puzzle?
                rel = [0, 0]

                for rel_i, (prev_val, val) in enumerate(zip(prev_segment,
                                                            segment)):
                    if prev_val < val:
                        rel[rel_i] = -1
                    elif prev_val > val:
                        rel[rel_i] = 1

                # Now that we have the relative move, build the new segment
                # position. If it doesn't overlap with the previous segment,
                # we can set it.
                segment = (segment[0] + rel[0],
                           segment[1] + rel[1])

                if segment != prev_segment:
                    segments[segment_i] = segment

            # Add the tail's position to the set of visited positions. Since
            # this is a set, we don't have to worry about duplicate positions.
            visited_positions.add(segments[-1])


print(f'Number of positions visited by the tail = {len(visited_positions)}')
