#!/usr/bin/env python3

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
