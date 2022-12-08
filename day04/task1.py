#!/usr/bin/env python3
#
# We need to find out how many assignment pairs fully contain each other.
#
# Each line of input contains two pairs, comma-separated. For example,
#
#     3-6,2-4
#
# We need to figure out the ranges of each, and see if one fully contains
# the other. Figure out how many ranges overlap fully.
#
# Like my other solutions, I go for performance here. Only process one line
# at a time, keep minimal state.
#
# For this, I'm grabbing each range, splitting it and converting to a list
# of lower and upper bounds. Note: I could easily use a regex here to simplify
# some of this if I wanted.
#
# I then just need to see if one range fully consumes another. Basic math.

num_full_overlaps = 0


with open('input', 'r') as fp:
    for line in fp.readlines():
        pairs = line.strip().split(',')
        assert len(pairs) == 2

        range1 = [int(i) for i in pairs[0].split('-')]
        range2 = [int(i) for i in pairs[1].split('-')]

        assert len(range1) == 2
        assert len(range2) == 2

        if ((range1[0] >= range2[0] and range1[1] <= range2[1]) or
            (range2[0] >= range1[0] and range2[1] <= range1[1])):
            num_full_overlaps += 1


print(f'Number of overlapped schedules = {num_full_overlaps}')
