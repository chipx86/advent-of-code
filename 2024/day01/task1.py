#!/usr/bin/env python3
#
# Day 1, Task 1: https://adventofcode.com/2024/day/1
#
# Looks like we're back to mismanaged Christmas shenanigans! And only we
# can save Christmas.
#
# Our first task is simple. We have two lists of locations (integers) and
# they're not a match. We need to:
#
# 1. Match up the two lowest numbers from the list and calculate the delta
#    for each, then the second-lowest. Third. Etc.
#
# 2. Sum the deltas. That's our answer.
#
# I'm aiming for *reasonably* optimal solutions this year that are reasonable.
# There are ways to optimize this for lowest memory usage, lowest runtime,
# fewest operations performed, etc. My goal is to make code that is readable
# but doesn't take a long time to run.
#
# For our first task, we're going to read out the lists into two arrays,
# sort them, and then run through the results and calculate the sum of each
# delta in one last go.

def calc_distances(
    input_filename: str,
) -> int:
    location_ids1: list[int] = []
    location_ids2: list[int] = []

    # Read through the input, populating two lists of IDs.
    with open(input_filename, 'r') as fp:
        for line in fp:
            parts = line.split('   ')
            assert len(parts) == 2

            location_ids1.append(int(parts[0]))
            location_ids2.append(int(parts[1]))

    # Sort these from lowest numbers to highest.
    location_ids1 = sorted(location_ids1)
    location_ids2 = sorted(location_ids2)

    # Go through these lists one last time, calculating the deltas and
    # summing them up in one go.
    return sum(
        max(location_id1, location_id2) - min(location_id1, location_id2)
        for location_id1, location_id2 in zip(location_ids1, location_ids2)
    )


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_distances('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = calc_distances('input')
    print(f'Task answer: {answer}')
